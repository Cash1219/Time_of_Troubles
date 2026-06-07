from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_RE = r"^[ \t]*(?:s:)?(STATE_[A-Z0-9_]+)\s*=\s*\{"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text_preserve_bom(path: Path, text: str) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
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


def find_state_blocks(text: str):
    for match in re.finditer(STATE_RE, text, flags=re.MULTILINE):
        open_index = text.find("{", match.end() - 1)
        if open_index == -1:
            continue
        close_index = matching_brace(text, open_index)
        yield {
            "state": match.group(1),
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


def load_occurrences(kind: str):
    occurrences = {}
    for path in sorted((ROOT / f"common/history/{kind}").glob("*.txt")):
        text = read_text(path)
        for block in find_state_blocks(text):
            if brace_depth_at(text, block["start"]) != 1:
                continue
            occurrences.setdefault(block["state"], []).append({
                "path": path,
                "start": block["start"],
                "open": block["open"],
                "close": block["close"],
                "body": block["body"],
            })
    return occurrences


def merge_group(kind: str, state: str):
    occurrences = sorted(load_occurrences(kind).get(state, []), key=lambda item: (item["path"].as_posix(), item["start"]))
    if len(occurrences) <= 1:
        return None
    keeper_path = occurrences[0]["path"]
    bodies_to_merge = []
    removals_by_file = {}
    for duplicate in occurrences[1:]:
        bodies_to_merge.append(duplicate["body"].strip("\r\n"))
        removals_by_file.setdefault(duplicate["path"], []).append((duplicate["start"], duplicate["close"] + 1))

    for path, spans in removals_by_file.items():
        text = read_text(path)
        for start, end in sorted(spans, reverse=True):
            while start > 0 and text[start - 1] in " \t":
                start -= 1
            if end < len(text) and text[end : end + 2] == "\r\n":
                end += 2
            elif end < len(text) and text[end] == "\n":
                end += 1
            text = text[:start] + text[end:]
        write_text_preserve_bom(path, text)

    keeper_text = read_text(keeper_path)
    keeper_blocks = [block for block in find_state_blocks(keeper_text) if block["state"] == state]
    if len(keeper_blocks) != 1:
        raise RuntimeError(f"expected one keeper for {kind} {state}, found {len(keeper_blocks)}")
    keeper = keeper_blocks[0]
    insertion = "\n" + "\n".join(bodies_to_merge) + "\n"
    keeper_text = keeper_text[: keeper["close"]] + insertion + keeper_text[keeper["close"] :]
    write_text_preserve_bom(keeper_path, keeper_text)
    return {
        "kind": kind,
        "state": state,
        "keeper": keeper_path.relative_to(ROOT).as_posix(),
        "merged_blocks": len(bodies_to_merge),
        "source_files": sorted({item["path"].relative_to(ROOT).as_posix() for item in occurrences[1:]}),
    }


def merge_all():
    report = []
    for kind in ("pops", "buildings"):
        while True:
            duplicate_states = [
                state for state, occ in load_occurrences(kind).items()
                if len(occ) > 1
            ]
            if not duplicate_states:
                break
            progress = False
            for state in sorted(duplicate_states):
                item = merge_group(kind, state)
                if item:
                    report.append(item)
                    progress = True
            if not progress:
                break
    out = ROOT / "analysis/state_based_history_duplicate_merge_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = merge_all()
    print(json.dumps({
        "merged_duplicate_groups": len(result),
        "merged_blocks": sum(item["merged_blocks"] for item in result),
        "report": "analysis/state_based_history_duplicate_merge_report.json",
    }, indent=2, ensure_ascii=False))
