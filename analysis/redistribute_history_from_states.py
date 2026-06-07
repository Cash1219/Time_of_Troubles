from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATES_PATH = ROOT / "common/history/states/00_states.txt"
VANILLA_GAME_ROOT = Path(r"D:\Steam\steamapps\common\Victoria 3\game")
HISTORY_KINDS = ("pops", "buildings")


def decode_bytes(data: bytes) -> tuple[str, bool]:
    had_bom = data.startswith(b"\xef\xbb\xbf")
    return data.decode("utf-8-sig"), had_bom


def read_text(path: Path) -> str:
    return decode_bytes(path.read_bytes())[0]


def write_text(path: Path, text: str, had_bom: bool) -> None:
    path.write_text(text, encoding="utf-8-sig" if had_bom else "utf-8", newline="")


def git_show_text(path: Path) -> tuple[str, bool]:
    rel = path.relative_to(ROOT).as_posix()
    data = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT)
    return decode_bytes(data)


def base_history_text(path: Path) -> tuple[str, bool, str]:
    rel = path.relative_to(ROOT)
    vanilla_path = VANILLA_GAME_ROOT / rel
    if vanilla_path.exists():
        text, had_bom = decode_bytes(vanilla_path.read_bytes())
        return text, had_bom, str(vanilla_path)
    text, had_bom = git_show_text(path)
    return text, had_bom, f"HEAD:{rel.as_posix()}"


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
        name = match.group(1) if match.lastindex else ""
        yield {
            "name": name,
            "start": match.start(),
            "open": open_index,
            "close": close_index,
            "body": text[open_index + 1 : close_index],
        }


STATE_RE = r"^[ \t]*(?:s:)?(STATE_[A-Z0-9_]+)\s*=\s*\{"
REGION_RE = r"^[ \t]*region_state:([A-Z0-9_]+)\s*=\s*\{"
CREATE_STATE_RE = r"^[ \t]*create_state\s*=\s*\{"
COUNTRY_ASSIGN_RE = re.compile(r"(\bcountry\s*=\s*)(\"?c:)([A-Z0-9_]+)(\"?)")
REGION_ASSIGN_RE = re.compile(r"(\bregion\s*=\s*\")STATE_[A-Z0-9_]+(\")")


def parse_state_owners(states_text: str):
    result = {}
    for state_block in find_blocks(states_text, STATE_RE):
        owners = []
        province_counts = {}
        for create_block in find_blocks(state_block["body"], CREATE_STATE_RE):
            body = create_block["body"]
            country_match = re.search(r"\bcountry\s*=\s*c:([A-Z0-9_]+)", body)
            if not country_match:
                continue
            tag = country_match.group(1)
            provinces = re.findall(r"\bx[0-9A-Fa-f]{6}\b", body)
            owners.append(tag)
            province_counts[tag] = province_counts.get(tag, 0) + len(provinces)
        if owners:
            unique = []
            for owner in owners:
                if owner not in unique:
                    unique.append(owner)
            result[state_block["name"]] = {
                "owners": unique,
                "province_counts": province_counts,
                "primary": sorted(unique, key=lambda tag: (-province_counts.get(tag, 0), tag))[0],
            }
    return result


def choose_owner(state_info, old_region: str) -> str | None:
    if not state_info:
        return None
    owners = state_info["owners"]
    if len(owners) == 1:
        return owners[0]
    if old_region in owners:
        return old_region
    return state_info["primary"]


def rewrite_region_block(block_text: str, state: str, old_region: str, new_region: str, kind: str):
    changes = []
    rewritten = re.sub(
        rf"(\bregion_state:){re.escape(old_region)}(\s*=)",
        rf"\g<1>{new_region}\2",
        block_text,
        count=1,
    )
    if old_region != new_region:
        changes.append({"scope": "region_state", "from": old_region, "to": new_region})
    if kind == "buildings":
        before = rewritten
        old_countries = sorted({m.group(3) for m in COUNTRY_ASSIGN_RE.finditer(before)})

        def country_repl(match: re.Match) -> str:
            return f"{match.group(1)}{match.group(2)}{new_region}{match.group(4)}"

        rewritten = COUNTRY_ASSIGN_RE.sub(country_repl, rewritten)
        changed_countries = [tag for tag in old_countries if tag != new_region]
        if changed_countries:
            changes.append({"scope": "country", "from": changed_countries, "to": new_region})
        before = rewritten
        rewritten = REGION_ASSIGN_RE.sub(rf"\g<1>{state}\2", rewritten)
        if rewritten != before:
            changes.append({"scope": "ownership_region", "to": state})
    return rewritten, changes


def rewrite_history_file(base_text: str, kind: str, state_owners):
    file_changes = []
    rewritten = base_text
    state_blocks = list(find_blocks(base_text, STATE_RE))
    for state_block in reversed(state_blocks):
        state = state_block["name"]
        info = state_owners.get(state)
        if not info:
            continue
        state_text = rewritten[state_block["start"] : state_block["close"] + 1]
        region_blocks = list(find_blocks(state_text, REGION_RE))
        new_state_text = state_text
        for region_block in reversed(region_blocks):
            old_region = region_block["name"]
            new_region = choose_owner(info, old_region)
            if not new_region:
                continue
            region_text = new_state_text[region_block["start"] : region_block["close"] + 1]
            new_region_text, changes = rewrite_region_block(region_text, state, old_region, new_region, kind)
            if changes:
                file_changes.append({"state": state, "old_region": old_region, "new_region": new_region, "changes": changes})
            new_state_text = (
                new_state_text[: region_block["start"]]
                + new_region_text
                + new_state_text[region_block["close"] + 1 :]
            )
        rewritten = rewritten[: state_block["start"]] + new_state_text + rewritten[state_block["close"] + 1 :]
    return rewritten, file_changes


def rewrite_all():
    state_owners = parse_state_owners(read_text(STATES_PATH))
    report = {
        "state_owner_count": len(state_owners),
        "base_root": str(VANILLA_GAME_ROOT),
        "files": [],
        "multi_owner_states": {
            state: info for state, info in state_owners.items() if len(info["owners"]) > 1
        },
    }
    for kind in HISTORY_KINDS:
        folder = ROOT / f"common/history/{kind}"
        for path in sorted(folder.glob("*.txt")):
            try:
                base_text, had_bom, base_source = base_history_text(path)
            except subprocess.CalledProcessError:
                base_text = read_text(path)
                had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
                base_source = str(path)
            new_text, changes = rewrite_history_file(base_text, kind, state_owners)
            write_text(path, new_text, had_bom)
            report["files"].append({
                "kind": kind,
                "file": path.relative_to(ROOT).as_posix(),
                "base_source": base_source,
                "changes": len(changes),
                "details": changes[:100],
            })
    out = ROOT / "analysis/state_based_history_redistribution_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    summary = rewrite_all()
    print(json.dumps({
        "state_owner_count": summary["state_owner_count"],
        "files_changed": sum(1 for f in summary["files"] if f["changes"]),
        "total_changed_blocks": sum(f["changes"] for f in summary["files"]),
        "report": "analysis/state_based_history_redistribution_report.json",
    }, indent=2, ensure_ascii=False))
