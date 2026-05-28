import re
from pathlib import Path
root=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT")
pm_text=(root/'common'/'production_methods'/'goods.txt').read_text(encoding='utf-8-sig',errors='ignore')
pm_keys=set(re.findall(r'(?m)^\s*(pm_goods_[a-z0-9_]+)\s*=\s*\{',pm_text))
pmg_text=(root/'common'/'production_method_groups'/'goods.txt').read_text(encoding='utf-8-sig',errors='ignore')
pmg_refs=set(re.findall(r'\b(pm_goods_[a-z0-9_]+)\b',pmg_text))
loc_text=(root/'localization'/'simp_chinese'/'replace'/'tot_building_l_simp_chinese.yml').read_text(encoding='utf-8-sig',errors='ignore')
loc_keys=set(re.findall(r'(?m)^\s*(pm_goods_[A-Za-z0-9_]+):\s*"',loc_text))
print('groups_not_in_pm', sorted(k for k in pmg_refs if k.startswith('pm_goods_') and k not in pm_keys))
print('pm_not_in_loc', sorted(k for k in pm_keys if k not in loc_keys))
print('loc_extra', sorted(k for k in loc_keys if k not in pm_keys and not k.endswith('_null')))

bad=[]
for m in re.finditer(r'goods_(?:input|output)_[A-Za-z0-9_]+_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)', pm_text):
    v=float(m.group(1))
    if abs(v/5-round(v/5))>1e-9:
        bad.append(v)
print('non_multiple_of_5_count', len(bad))
