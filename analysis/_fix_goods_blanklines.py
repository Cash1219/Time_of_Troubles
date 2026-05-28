import re
from pathlib import Path

p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore').replace('\r\n','\n').replace('\r','\n')
lines=[ln.rstrip() for ln in text.split('\n')]

out=[]
for ln in lines:
    s=ln.strip()
    if not s:
        continue
    if re.match(r'^pm_goods_[a-z0-9_]+\s*=\s*\{', s) and out:
        out.append('')
    out.append(ln)

text='\r\n'.join(out).rstrip()+'\r\n'
p.write_text(text, encoding='utf-8-sig')
print('normalized blank lines in goods.txt')
