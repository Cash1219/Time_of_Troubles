import re
from pathlib import Path

f=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
lines=f.read_text(encoding='utf-8-sig',errors='ignore').splitlines()

blocks=[]
i=0
while i<len(lines):
    m=re.match(r'^\s*(pm_goods_[a-z0-9_]+)\s*=\s*\{',lines[i])
    if not m:
        i+=1
        continue
    key=m.group(1)
    depth=lines[i].count('{')-lines[i].count('}')
    b=[lines[i]]
    i+=1
    while i<len(lines) and depth>0:
        b.append(lines[i])
        depth += lines[i].count('{')-lines[i].count('}')
        i+=1
    blocks.append((key,'\n'.join(b)))

for key,body in blocks:
    if key.endswith('_null'):
        continue
    ins=[]; outs=[]
    for m in re.finditer(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)',body):
        ins.append((m.group(1), m.group(2)))
    for m in re.finditer(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)',body):
        outs.append((m.group(1), m.group(2)))

    emp=[]
    total=0
    for m in re.finditer(r'building_employment_([a-z_]+)_add\s*=\s*(-?[0-9]+)',body):
        job=m.group(1); n=int(m.group(2));
        emp.append((job,n)); total += n

    if not ins and not outs and not emp:
        continue

    in_txt=' + '.join([f'{g}:{q}' for g,q in ins]) if ins else '-'
    out_txt=' + '.join([f'{g}:{q}' for g,q in outs]) if outs else '-'
    emp_txt=' + '.join([f'{j}:{n}' for j,n in emp]) if emp else '-'
    print(f'{key}\t人数合计={total}\t雇佣={emp_txt}\t投入数量={in_txt}\t产出数量={out_txt}')
