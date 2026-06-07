from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_RE = r"^[ \t]*(?:s:)?(STATE_[A-Z0-9_]+)\s*=\s*\{"
REGION_RE = r"^[ \t]*region_state:([A-Z0-9_]+)\s*=\s*\{"
CREATE_STATE_RE = r"^[ \t]*create_state\s*=\s*\{"
COUNTRY_ASSIGN_RE = re.compile(r"\bcountry\s*=\s*\"?c:([A-Z0-9_]+)\"?")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


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


def brace_depth_at(text: str, index: int) -> int:
    depth = 0
    in_quote = False
    escaped = False
    in_comment = False
    i = 0
    while i < index:
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
        i += 1
    return depth


def parse_state_owners():
    owners = {}
    for state_block in find_blocks(read_text(ROOT / "common/history/states/00_states.txt"), STATE_RE):
        tags = []
        for create_block in find_blocks(state_block["body"], CREATE_STATE_RE):
            match = re.search(r"\bcountry\s*=\s*c:([A-Z0-9_]+)", create_block["body"])
            if match and match.group(1) not in tags:
                tags.append(match.group(1))
        if tags:
            owners[state_block["name"]] = tags
    return owners


def audit():
    state_owners = parse_state_owners()
    region_mismatches = []
    building_country_mismatches = []
    duplicate_state_blocks = []
    missing_states = []
    all_blocks = []

    for kind in ("pops", "buildings"):
        for path in sorted((ROOT / f"common/history/{kind}").glob("*.txt")):
            text = read_text(path)
            for state_block in find_blocks(text, STATE_RE):
                state = state_block["name"]
                if brace_depth_at(text, state_block["start"]) == 1:
                    all_blocks.append({"kind": kind, "file": path.relative_to(ROOT).as_posix(), "state": state})
                owners = state_owners.get(state)
                if not owners:
                    missing_states.append({"kind": kind, "file": path.relative_to(ROOT).as_posix(), "state": state})
                    continue
                for region_block in find_blocks(state_block["body"], REGION_RE):
                    region = region_block["name"]
                    if region not in owners:
                        region_mismatches.append({
                            "kind": kind,
                            "file": path.relative_to(ROOT).as_posix(),
                            "state": state,
                            "region_state": region,
                            "state_owners": owners,
                        })
                    if kind == "buildings":
                        for country in sorted({m.group(1) for m in COUNTRY_ASSIGN_RE.finditer(region_block["body"])}):
                            if country != region:
                                building_country_mismatches.append({
                                    "file": path.relative_to(ROOT).as_posix(),
                                    "state": state,
                                    "region_state": region,
                                    "country": country,
                                })

    seen = {}
    for block in all_blocks:
        key = (block["kind"], block["state"])
        seen.setdefault(key, []).append(block["file"])
    for (kind, state), files in seen.items():
        if len(files) > 1:
            duplicate_state_blocks.append({"kind": kind, "state": state, "count": len(files), "files": sorted(set(files))})

    report = {
        "state_owner_count": len(state_owners),
        "region_mismatch_count": len(region_mismatches),
        "building_country_mismatch_count": len(building_country_mismatches),
        "missing_state_count": len(missing_states),
        "duplicate_state_block_count": len(duplicate_state_blocks),
        "region_mismatches": region_mismatches[:200],
        "building_country_mismatches": building_country_mismatches[:200],
        "missing_states": missing_states[:200],
        "duplicate_state_blocks": duplicate_state_blocks[:200],
    }
    out = ROOT / "analysis/state_based_history_audit_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({
        "region_mismatch_count": result["region_mismatch_count"],
        "building_country_mismatch_count": result["building_country_mismatch_count"],
        "missing_state_count": result["missing_state_count"],
        "duplicate_state_block_count": result["duplicate_state_block_count"],
        "report": "analysis/state_based_history_audit_report.json",
    }, indent=2, ensure_ascii=False))
