import re
from pathlib import Path
p=Path(r"D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT/common/history/characters/byz - byz.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore')

# remove cloned create_character blocks by first_name suffix _cloneN
pattern = re.compile(r'(?ms)\n\s*create_character\s*=\s*\{(?:(?!\n\s*create_character\s*=\s*\{|\n\s*\}\s*\}\s*$).)*?first_name\s*=\s*"[^"]+_clone\d+"(?:(?!\n\s*create_character\s*=\s*\{|\n\s*\}\s*\}\s*$).)*?\n\s*\}')
new_text = re.sub(pattern, '', text)

# cleanup extra blank lines
new_text = re.sub(r'\n{3,}', '\n\n', new_text)
p.write_text(new_text, encoding='utf-8-sig')

raw=p.read_text(encoding='utf-8-sig', errors='ignore')
total=len(re.findall(r'(?m)^\s*create_character\s*=\s*\{', raw))
clones=len(re.findall(r'(?m)^\s*first_name\s*=\s*"[^"]+_clone\d+"', raw))
print(f"create_character_total={total}")
print(f"clone_count={clones}")
