from pathlib import Path
import re

p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore')
text=text.replace('\r\n','\n').replace('\r','\n')

# split lines where texture is followed by next key on same line
text=re.sub(r'(texture\s*=\s*"[^"]+"\s*)(?=(unlocking_technologies\s*=|building_modifiers\s*=))', r'\1\n\t', text)

# fix cases like "dds"}\n to close on separate line style only for null blocks when collapsed
text=re.sub(r'(pm_goods_[a-z0-9_]+\s*=\s*\{\s*#.*?\n\s*texture\s*=\s*"[^"]+"\s*)\}', r'\1\n}', text, flags=re.S)

# normalize trailing spaces
lines=[ln.rstrip() for ln in text.split('\n')]

# collapse 3+ blank lines to max 2
out=[]
blank=0
for ln in lines:
    if ln.strip()=="":
        blank+=1
        if blank<=2:
            out.append("")
    else:
        blank=0
        out.append(ln)

text='\n'.join(out).rstrip()+'\n'
# back to CRLF for consistency in this repo on Windows
text=text.replace('\n','\r\n')
p.write_text(text, encoding='utf-8-sig')
print('formatted goods.txt')
