import re
from pathlib import Path

mod_root=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT")
van_root=Path(r"D:\Steam\steamapps\common\Victoria 3\game")

def parse_goods_costs(folder: Path):
    costs={}
    for p in folder.rglob('*.txt'):
        t=p.read_text(encoding='utf-8-sig',errors='ignore')
        for m in re.finditer(r'(?ms)^\s*([A-Za-z0-9_]+)\s*=\s*\{(.*?)\n\s*\}', t):
            k,b=m.group(1),m.group(2)
            cm=re.search(r'(?m)^\s*cost\s*=\s*([0-9]+(?:\.[0-9]+)?)',b)
            if cm: costs[k]=float(cm.group(1))
    return costs

costs=parse_goods_costs(van_root/'common'/'goods')
mod_goods=mod_root/'common'/'goods'
if mod_goods.exists():
    costs.update(parse_goods_costs(mod_goods))

f=mod_root/'common'/'production_methods'/'goods.txt'
lines=f.read_text(encoding='utf-8-sig',errors='ignore').splitlines()

blocks=[]
i=0
while i<len(lines):
    line=lines[i]
    m=re.match(r'^\s*(pm_goods_[a-z0-9_]+)\s*=\s*\{',line)
    if not m:
        i+=1; continue
    key=m.group(1)
    depth=line.count('{')-line.count('}')
    b=[line]
    i+=1
    while i<len(lines) and depth>0:
        b.append(lines[i])
        depth += lines[i].count('{')-lines[i].count('}')
        i+=1
    blocks.append((key,'\n'.join(b)))

rows=[]
for key,body in blocks:
    if key.endswith('_null'): continue
    in_v=0.0; out_v=0.0
    for m in re.finditer(r'goods_(input|output)_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)',body):
        io,good,qty=m.group(1),m.group(2),float(m.group(3))
        price=costs.get(good,0.0)
        val=qty*price
        if io=='input': in_v+=val
        else: out_v+=val
    if in_v==0 and out_v==0: continue
    gross=out_v-in_v
    roi=(gross/in_v*100.0) if in_v else 0.0
    rows.append((key,round(in_v),round(out_v),round(gross),round(roi,2)))

for r in sorted(rows):
    print(f"{r[0]}\t投入={r[1]}\t产出={r[2]}\t毛利={r[3]}\t毛利率={r[4]}%")
