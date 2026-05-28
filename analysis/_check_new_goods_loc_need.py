import re
from pathlib import Path
root=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT")

# active new goods keys from tot_goods
raw=(root/'common'/'goods'/'tot_goods.txt').read_text(encoding='utf-8-sig',errors='ignore')
new_goods=[]
for m in re.finditer(r'(?m)^\s*([a-zA-Z0-9_]+)\s*=\s*\{', raw):
    k=m.group(1)
    # skip commented-out blocks by checking line startswith # before key
    line=raw[max(0,m.start()-80):m.start()].split('\n')[-1]
    if line.strip().startswith('#'):
        continue
    new_goods.append(k)
new_goods=list(dict.fromkeys(new_goods))

# used goods_input/output modifier keys in mod production methods
mods=set()
for p in (root/'common'/'production_methods').glob('*.txt'):
    t=p.read_text(encoding='utf-8-sig',errors='ignore')
    for m in re.finditer(r'goods_(input|output)_([a-zA-Z0-9_]+)_add\s*=', t):
        mods.add(f"goods_{m.group(1)}_{m.group(2)}_add")

loc=(root/'localization'/'simp_chinese'/'replace'/'tot_building_l_simp_chinese.yml').read_text(encoding='utf-8-sig',errors='ignore')
loc_keys=set(re.findall(r'(?m)^\s*([A-Za-z0-9_]+):\s*"', loc))

print('new_goods',new_goods)
print('missing_goods_name', [g for g in new_goods if g not in loc_keys])

# only for new goods modifiers
need=[]
for g in new_goods:
    for io in ('input','output'):
        k=f'goods_{io}_{g}_add'
        kd=f'{k}_desc'
        if k in mods and k not in loc_keys: need.append(k)
        if k in mods and kd not in loc_keys: need.append(kd)
print('missing_new_goods_modifier_loc',need)
