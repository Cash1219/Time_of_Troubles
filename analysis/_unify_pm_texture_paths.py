import re
from pathlib import Path

root = Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT")
target_dirs = [
    root / "common" / "production_methods",
    root / "common" / "production_method_groups",
]

block_start_re = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*\{')
texture_re = re.compile(r'^(\s*texture\s*=\s*")([^"]+)(".*)$')

changed_files = []
changed_lines = 0

for d in target_dirs:
    if not d.exists():
        continue
    for p in d.rglob('*.txt'):
        lines = p.read_text(encoding='utf-8-sig').splitlines(True)
        out = []
        current_key = None
        brace_depth = 0
        file_changed = False

        for line in lines:
            m_start = block_start_re.match(line)
            if m_start:
                # entering a new block
                key = m_start.group(1)
                current_key = key
                brace_depth = line.count('{') - line.count('}')
                out.append(line)
                continue

            if current_key is not None:
                # within active block
                m_tex = texture_re.match(line)
                if m_tex:
                    new_path = f'gfx/interface/icons/production_method_icons/{current_key}.dds'
                    new_line = f'{m_tex.group(1)}{new_path}{m_tex.group(3)}\n' if not line.endswith('\n') else f'{m_tex.group(1)}{new_path}{m_tex.group(3)}'
                    if new_line != line:
                        line = new_line
                        file_changed = True
                        changed_lines += 1

                brace_depth += line.count('{') - line.count('}')
                if brace_depth <= 0:
                    current_key = None
                    brace_depth = 0

            out.append(line)

        if file_changed:
            p.write_text(''.join(out), encoding='utf-8-sig')
            changed_files.append(str(p))

print(f'changed_files={len(changed_files)} changed_lines={changed_lines}')
for f in changed_files:
    print(f)
