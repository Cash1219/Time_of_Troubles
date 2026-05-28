import re
from pathlib import Path

mod_root=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT")
van_root=Path(r"D:\Steam\steamapps\common\Victoria 3\game")

def parse_costs(folder):
    costs={}
    for p in Path(folder).rglob('*.txt'):
        t=p.read_text(encoding='utf-8-sig',errors='ignore')
        for m in re.finditer(r'(?ms)^\s*([A-Za-z0-9_]+)\s*=\s*\{(.*?)\n\s*\}', t):
            k,b=m.group(1),m.group(2)
            cm=re.search(r'(?m)^\s*cost\s*=\s*([0-9]+(?:\.[0-9]+)?)', b)
            if cm:
                costs[k]=float(cm.group(1))
    return costs

costs=parse_costs(van_root/'common'/'goods')
costs.update(parse_costs(mod_root/'common'/'goods'))

f=mod_root/'common'/'production_methods'/'goods.txt'
lines=f.read_text(encoding='utf-8-sig',errors='ignore').replace('\r\n','\n').replace('\r','\n').split('\n')

blocks=[]
i=0
while i<len(lines):
    m=re.match(r'^\s*(pm_goods_[a-z0-9_]+)\s*=\s*\{', lines[i])
    if not m:
        i+=1; continue
    k=m.group(1)
    d=lines[i].count('{')-lines[i].count('}')
    b=[lines[i]]; i+=1
    while i<len(lines) and d>0:
        b.append(lines[i]); d += lines[i].count('{')-lines[i].count('}'); i+=1
    blocks.append((k,'\n'.join(b)))

rows=[]
for k,b in blocks:
    if k.endswith('_null'): continue
    ins=[]; outs=[]
    in_v=0; out_v=0
    for m in re.finditer(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)', b):
        g,q=m.group(1),float(m.group(2)); v=q*costs.get(g,0); ins.append((g,q,v)); in_v += v
    for m in re.finditer(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)', b):
        g,q=m.group(1),float(m.group(2)); v=q*costs.get(g,0); outs.append((g,q,v)); out_v += v
    if in_v==0 and out_v==0: continue
    gross=out_v-in_v
    roi=(gross/in_v*100) if in_v else 0
    rows.append((k, round(in_v), round(out_v), round(gross), round(roi,2)))

for r in sorted(rows):
    print(f"{r[0]}\t投入={r[1]}\t产出={r[2]}\t毛利={r[3]}\t毛利率={r[4]}%")
