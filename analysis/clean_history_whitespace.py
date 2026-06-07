from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def clean_file(path: Path) -> bool:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    original = raw.decode("utf-8-sig")
    lines = original.splitlines()
    while lines and lines[-1] == "":
        lines.pop()
    cleaned_lines = []
    for line in lines:
        line = line.rstrip(" \t")
        prefix_len = 0
        while prefix_len < len(line) and line[prefix_len] in " \t":
            prefix_len += 1
        prefix = line[:prefix_len]
        while " \t" in prefix:
            prefix = prefix.replace(" \t", "\t")
        cleaned_lines.append(prefix + line[prefix_len:])
    cleaned = "\n".join(cleaned_lines) + "\n"
    if cleaned == original:
        return False
    path.write_text(cleaned, encoding="utf-8-sig" if had_bom else "utf-8", newline="")
    return True


if __name__ == "__main__":
    files = list((ROOT / "common/history/buildings").glob("*.txt"))
    files += list((ROOT / "common/history/pops").glob("*.txt"))
    files += list((ROOT / "common/history/states").glob("*.txt"))
    changed = [path.relative_to(ROOT).as_posix() for path in files if clean_file(path)]
    print(f"cleaned_files={len(changed)}")
