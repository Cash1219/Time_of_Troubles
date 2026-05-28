import re
from pathlib import Path

p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore').replace('\r\n','\n').replace('\r','\n')
lines=[ln.rstrip() for ln in text.split('\n')]

# drop all blank lines first
nonblank=[ln for ln in lines if ln.strip()!='']

# reinsert one blank line before each top-level pm block (except first)
out=[]
first=True
for ln in nonblank:
    if re.match(r'^pm_goods_[a-z0-9_]+\s*=\s*\{', ln):
        if not first:
            out.append('')
        first=False
    out.append(ln)

new='\r\n'.join(out).rstrip()+'\r\n'
p.write_text(new, encoding='utf-8-sig')
print('goods.txt compact formatting done')
