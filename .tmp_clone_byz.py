import re
from pathlib import Path

p=Path(r"D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT/common/history/characters/byz - byz.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore')

# find BYZ block content
m=re.search(r'(?s)(c:BYZ\s*\?=\s*\{)(.*?)(\n\t\}\n\})', text)
if not m:
    raise SystemExit('BYZ block not found')
head, body, tail = m.group(1), m.group(2), m.group(3)

# extract create_character blocks at BYZ top level
blocks=[]
i=0
while True:
    cm=re.search(r'create_character\s*=\s*\{', body[i:])
    if not cm: break
    s=i+cm.start()
    bstart=i+cm.end()-1
    d=0
    j=bstart
    while j < len(body):
        c=body[j]
        if c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0:
                blocks.append(body[s:j+1])
                i=j+1
                break
        j+=1
    else:
        break

if not blocks:
    raise SystemExit('no create_character blocks found')

# make 10 copies for each existing block
new_parts=[body.rstrip()]
for idx,blk in enumerate(blocks, start=1):
    for n in range(1,11):
        b=blk
        # suffix first_name to avoid complete duplicates
        b=re.sub(r'(?m)^\s*first_name\s*=\s*"([^"]+)"', lambda mm: f'\t\t\tfirst_name = "{mm.group(1)}_clone{n}"', b, count=1)
        # keep as historical; do not set ruler/heir flags for clones to reduce conflicts
        b=re.sub(r'(?m)^\s*\b(ruler|heir)\s*=\s*yes\s*$', '', b)
        new_parts.append('\n\t\t'+b.strip()+'\n')

new_body='\n'.join(new_parts)+'\n'
new_text=text[:m.start(2)] + new_body + text[m.end(2):]
p.write_text(new_text, encoding='utf-8-sig')
print(f'base_blocks={len(blocks)} added={len(blocks)*10}')
