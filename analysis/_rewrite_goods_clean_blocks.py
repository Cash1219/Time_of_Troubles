import re
from pathlib import Path

p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore')
text=text.replace('\r\r\n','\n').replace('\r\n','\n').replace('\r','\n')
lines=[ln.rstrip() for ln in text.split('\n')]

blocks=[]
i=0
n=len(lines)
while i<n:
    line=lines[i]
    if not re.match(r'^\s*pm_goods_[a-z0-9_]+\s*=\s*\{', line):
        i+=1
        continue
    depth=line.count('{')-line.count('}')
    block=[line]
    i+=1
    while i<n and depth>0:
        ln=lines[i]
        depth += ln.count('{')-ln.count('}')
        block.append(ln)
        i+=1
    # remove empty lines in block
    block=[ln for ln in block if ln.strip()!='']
    blocks.append(block)

out=[]
for bi,b in enumerate(blocks):
    out.extend(b)
    if bi!=len(blocks)-1:
        out.append('')

new='\r\n'.join(out).rstrip()+'\r\n'
p.write_text(new, encoding='utf-8-sig')
print('rewrote goods.txt blocks=',len(blocks),'lines=',len(out))

# sanity preview
preview='\n'.join(new.replace('\r\n','\n').split('\n')[:40])
print('---PREVIEW---')
print(preview)
