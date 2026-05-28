import re
from pathlib import Path
p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig',errors='ignore')
# normalize all newlines (including broken \r\r\n)
text=text.replace('\r\r\n','\n').replace('\r\n','\n').replace('\r','\n')

lines=[ln.rstrip() for ln in text.split('\n')]
# remove empty lines inside, then keep one blank line between top-level pm blocks
nonblank=[ln for ln in lines if ln.strip()!='']
out=[]
first=True
for ln in nonblank:
    if re.match(r'^pm_goods_[a-z0-9_]+\s*=\s*\{', ln):
        if not first:
            out.append('')
        first=False
    out.append(ln)

clean='\r\n'.join(out).rstrip()+'\r\n'
p.write_text(clean, encoding='utf-8-sig')
print('goods.txt newline fixed')
