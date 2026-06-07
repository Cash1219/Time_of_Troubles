from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD_STATES = ROOT / "common/history/states/00_states.txt"
VANILLA_STATES = Path(r"D:\Steam\steamapps\common\Victoria 3\game\common\history\states\00_states.txt")
REPORT = ROOT / "analysis/state_structure_audit_report.json"

STATE_RE = r"^[ \t]*(?:s:)?(STATE_[A-Z0-9_]+)\s*=\s*\{"
CREATE_STATE_RE = r"^[ \t]*create_state\s*=\s*\{"
COUNTRY_RE = re.compile(r"\bcountry\s*=\s*c:([A-Z0-9_]+)")
PROVINCE_RE = re.compile(r"\bx[0-9A-Fa-f]{6}\b")
OWNED_PROVINCES_RE = re.compile(r"(\bowned_provinces\s*=\s*\{)([^{}]*)(\})", re.S)


def decode_bytes(data: bytes) -> tuple[str, bool]:
    return data.decode("utf-8-sig"), data.startswith(b"\xef\xbb\xbf")


def read_text(path: Path) -> str:
    return decode_bytes(path.read_bytes())[0]


def write_text(path: Path, text: str, had_bom: bool) -> None:
    path.write_text(text, encoding="utf-8-sig" if had_bom else "utf-8", newline="")


def matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_quote = False
    escaped = False
    in_comment = False
    i = open_index
    while i < len(text):
        ch = text[i]
        if in_comment:
            if ch in "\r\n":
                in_comment = False
            i += 1
            continue
        if in_quote:
            if ch == "\\" and not escaped:
                escaped = True
            elif ch == '"' and not escaped:
                in_quote = False
            else:
                escaped = False
            i += 1
            continue
        if ch == "#":
            in_comment = True
        elif ch == '"':
            in_quote = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unclosed block at {open_index}")


def find_blocks(text: str, pattern: str):
    for match in re.finditer(pattern, text, flags=re.MULTILINE):
        open_index = text.find("{", match.end() - 1)
        if open_index == -1:
            continue
        close_index = matching_brace(text, open_index)
        yield {
            "name": match.group(1) if match.lastindex else "",
            "start": match.start(),
            "open": open_index,
            "close": close_index,
            "body": text[open_index + 1 : close_index],
        }


def parse_states(text: str):
    states = {}
    for state_block in find_blocks(text, STATE_RE):
        create_states = []
        for create_block in find_blocks(state_block["body"], CREATE_STATE_RE):
            country = COUNTRY_RE.search(create_block["body"])
            if not country:
                continue
            create_states.append({
                "country": country.group(1),
                "provinces": PROVINCE_RE.findall(create_block["body"]),
                "body": create_block["body"],
                "start": create_block["start"],
                "open": create_block["open"],
                "close": create_block["close"],
            })
        homeland_matches = re.findall(r"\badd_homeland\s*=\s*cu:([a-zA-Z0-9_]+)", state_block["body"])
        states[state_block["name"]] = {
            "create_states": create_states,
            "owners": sorted({item["country"] for item in create_states}),
            "province_set": sorted({prov.upper() for item in create_states for prov in item["provinces"]}),
            "homelands": sorted(set(homeland_matches)),
        }
    return states


def duplicate_country_groups(states):
    issues = []
    for state, info in sorted(states.items()):
        by_country = {}
        for item in info["create_states"]:
            by_country.setdefault(item["country"], []).append(item)
        for country, items in sorted(by_country.items()):
            if len(items) > 1:
                issues.append({
                    "state": state,
                    "country": country,
                    "create_state_count": len(items),
                    "province_count": sum(len(item["provinces"]) for item in items),
                })
    return issues


def japan_states(states):
    return sorted(
        state for state, info in states.items()
        if "JAP" in info["owners"] or "japanese" in info["homelands"]
    )


def compare_states(mod_states, vanilla_states):
    added = sorted(set(mod_states) - set(vanilla_states))
    removed = sorted(set(vanilla_states) - set(mod_states))
    province_diffs = []
    owner_diffs = []
    for state in sorted(set(mod_states) & set(vanilla_states)):
        mod = mod_states[state]
        vanilla = vanilla_states[state]
        if mod["owners"] != vanilla["owners"]:
            owner_diffs.append({"state": state, "mod": mod["owners"], "vanilla": vanilla["owners"]})
        mod_provs = set(mod["province_set"])
        vanilla_provs = set(vanilla["province_set"])
        if mod_provs != vanilla_provs:
            province_diffs.append({
                "state": state,
                "mod_only_count": len(mod_provs - vanilla_provs),
                "vanilla_only_count": len(vanilla_provs - mod_provs),
                "mod_only": sorted(mod_provs - vanilla_provs)[:50],
                "vanilla_only": sorted(vanilla_provs - mod_provs)[:50],
            })
    return added, removed, owner_diffs, province_diffs


def build_create_state(country: str, provinces: list[str], template_body: str) -> str:
    province_text = " ".join(dict.fromkeys(provinces))
    body = OWNED_PROVINCES_RE.sub(rf"\1 {province_text} \3", template_body, count=1)
    if body == template_body:
        lines = [line for line in template_body.splitlines() if not COUNTRY_RE.search(line)]
        body = "\n".join(lines).rstrip() + f"\n\t\t\towned_provinces = {{ {province_text} }}\n\t\t"
    if not COUNTRY_RE.search(body):
        body = "\n\t\t\tcountry = c:" + country + body
    return "create_state = {" + body + "}"


def merge_duplicate_country_create_states(text: str):
    changed = []
    rewritten = text
    for state_block in reversed(list(find_blocks(text, STATE_RE))):
        state_text = rewritten[state_block["start"] : state_block["close"] + 1]
        create_blocks = list(find_blocks(state_text, CREATE_STATE_RE))
        by_country = {}
        for block in create_blocks:
            country = COUNTRY_RE.search(block["body"])
            if country:
                by_country.setdefault(country.group(1), []).append(block)
        if not any(len(items) > 1 for items in by_country.values()):
            continue
        new_state_text = state_text
        for country, items in sorted(by_country.items(), reverse=True):
            if len(items) <= 1:
                continue
            provinces = []
            for item in items:
                provinces.extend(PROVINCE_RE.findall(item["body"]))
            replacement = build_create_state(country, provinces, items[0]["body"])
            for item in reversed(items[1:]):
                start = item["start"]
                end = item["close"] + 1
                while start > 0 and new_state_text[start - 1] in " \t":
                    start -= 1
                if end < len(new_state_text) and new_state_text[end : end + 2] == "\r\n":
                    end += 2
                elif end < len(new_state_text) and new_state_text[end] == "\n":
                    end += 1
                new_state_text = new_state_text[:start] + new_state_text[end:]
            first = items[0]
            new_state_text = new_state_text[: first["start"]] + replacement + new_state_text[first["close"] + 1 :]
            changed.append({"state": state_block["name"], "country": country, "merged_blocks": len(items)})
        rewritten = rewritten[: state_block["start"]] + new_state_text + rewritten[state_block["close"] + 1 :]
    return rewritten, changed


def audit(fix: bool):
    mod_raw = MOD_STATES.read_bytes()
    mod_text, had_bom = decode_bytes(mod_raw)
    vanilla_text = read_text(VANILLA_STATES)
    mod_states = parse_states(mod_text)
    vanilla_states = parse_states(vanilla_text)
    added, removed, owner_diffs, province_diffs = compare_states(mod_states, vanilla_states)
    report = {
        "vanilla_states_path": str(VANILLA_STATES),
        "mod_state_count": len(mod_states),
        "vanilla_state_count": len(vanilla_states),
        "duplicate_country_create_state_count": len(duplicate_country_groups(mod_states)),
        "duplicate_country_create_states": duplicate_country_groups(mod_states),
        "states_added_vs_vanilla": added,
        "states_removed_vs_vanilla": removed,
        "owner_diff_count": len(owner_diffs),
        "owner_diffs": owner_diffs[:500],
        "province_diff_count": len(province_diffs),
        "province_diffs": province_diffs[:500],
        "japan_states_mod": japan_states(mod_states),
        "japan_states_vanilla": japan_states(vanilla_states),
        "japan_owner_diffs": [item for item in owner_diffs if item["state"] in set(japan_states(mod_states) + japan_states(vanilla_states))],
        "japan_province_diffs": [item for item in province_diffs if item["state"] in set(japan_states(mod_states) + japan_states(vanilla_states))],
    }
    if fix:
        fixed_text, changes = merge_duplicate_country_create_states(mod_text)
        write_text(MOD_STATES, fixed_text, had_bom)
        report["fix_applied"] = True
        report["merged_duplicate_country_groups"] = changes
        fixed_states = parse_states(fixed_text)
        report["duplicate_country_create_state_count_after_fix"] = len(duplicate_country_groups(fixed_states))
    else:
        report["fix_applied"] = False
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "duplicate_country_create_state_count": report["duplicate_country_create_state_count"],
        "owner_diff_count": report["owner_diff_count"],
        "province_diff_count": report["province_diff_count"],
        "japan_owner_diff_count": len(report["japan_owner_diffs"]),
        "japan_province_diff_count": len(report["japan_province_diffs"]),
        "fix_applied": fix,
        "report": REPORT.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    audit("--fix" in sys.argv)
