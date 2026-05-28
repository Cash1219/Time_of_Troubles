import re
from pathlib import Path
from collections import defaultdict
from openpyxl import Workbook

root = Path(r"D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT")
van_root = Path(r"D:/Steam/steamapps/common/Victoria 3/game")

loc_dir = root/'localization'/'simp_chinese'
mod_pm_dir = root/'common'/'production_methods'
van_pm_dir = van_root/'common'/'production_methods'
mod_pmg_dir = root/'common'/'production_method_groups'
van_pmg_dir = van_root/'common'/'production_method_groups'
mod_bld_dir = root/'common'/'buildings'
van_bld_dir = van_root/'common'/'buildings'
van_goods = van_root/'common'/'goods'/'00_goods.txt'
mod_goods_dir = root/'common'/'goods'


def iter_text_files(folder: Path):
    if not folder.exists():
        return
    for p in folder.rglob('*'):
        if p.is_file():
            yield p


def parse_top_blocks(text):
    blocks = {}
    i = 0
    pat = re.compile(r'(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{')
    n = len(text)
    while True:
        m = pat.search(text, i)
        if not m:
            break
        key = m.group(1)
        s = m.end()-1
        d = 0
        j = s
        while j < n:
            if text[j] == '{': d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0:
                    blocks[key] = text[s+1:j]
                    i = j+1
                    break
            j += 1
        else:
            break
    return blocks


def parse_loc(folder):
    loc = {}
    for f in folder.rglob('*.yml'):
        txt = f.read_text(encoding='utf-8-sig', errors='ignore')
        for line in txt.splitlines():
            s = line.strip()
            if not s or s.startswith('#') or s.startswith('l_simp_chinese:'):
                continue
            m = re.match(r'^([A-Za-z0-9_\.\-]+)\s*:\s*"(.*)"\s*$', s)
            if m:
                loc[m.group(1)] = m.group(2).replace('\\"','"').strip()
    return loc


def clean_comment_name(name: str):
    # remove accidental script fragments in comments such as 'texture = ...'
    name = name.strip()
    name = re.split(r'\btexture\b\s*=|\bicon\b\s*=|\bunlocking_technologies\b\s*=|\t', name, maxsplit=1)[0].strip()
    # trim trailing symbols
    name = re.sub(r'\s+$','',name)
    return name


def parse_comment_name_map(folder):
    out = {}
    pat = re.compile(r'(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*#\s*(.+?)\s*$')
    for f in iter_text_files(folder):
        txt = f.read_text(encoding='utf-8-sig', errors='ignore')
        for m in pat.finditer(txt):
            k = m.group(1)
            v = clean_comment_name(m.group(2))
            if v and k not in out:
                out[k] = v
    return out


def load_blocks(folder):
    out = {}
    for f in iter_text_files(folder):
        out.update(parse_top_blocks(f.read_text(encoding='utf-8-sig', errors='ignore')))
    return out


def load_goods_costs():
    costs = {}
    for k,b in parse_top_blocks(van_goods.read_text(encoding='utf-8-sig', errors='ignore')).items():
        m = re.search(r'(?m)^\s*cost\s*=\s*([0-9]+(?:\.[0-9]+)?)', b)
        if m: costs[k] = float(m.group(1))
    for f in iter_text_files(mod_goods_dir):
        for k,b in parse_top_blocks(f.read_text(encoding='utf-8-sig', errors='ignore')).items():
            m = re.search(r'(?m)^\s*cost\s*=\s*([0-9]+(?:\.[0-9]+)?)', b)
            if m: costs[k] = float(m.group(1))
    return costs


def extract_io(body):
    ins, outs = {}, {}
    for m in re.finditer(r'(?m)^\s*(?!#)goods_input_([A-Za-z0-9_]+)_add\s*=\s*([+-]?[0-9]+(?:\.[0-9]+)?)', body):
        g,v = m.group(1), float(m.group(2)); ins[g]=ins.get(g,0.0)+v
    for m in re.finditer(r'(?m)^\s*(?!#)goods_output_([A-Za-z0-9_]+)_add\s*=\s*([+-]?[0-9]+(?:\.[0-9]+)?)', body):
        g,v = m.group(1), float(m.group(2)); outs[g]=outs.get(g,0.0)+v
    return ins, outs

loc = parse_loc(loc_dir)
comment_names = {}
comment_names.update(parse_comment_name_map(mod_pm_dir))
comment_names.update(parse_comment_name_map(mod_pmg_dir))
comment_names.update(parse_comment_name_map(mod_bld_dir))

pm_v = load_blocks(van_pm_dir)
pm_m = load_blocks(mod_pm_dir)
pm_all = dict(pm_v); pm_all.update(pm_m)
new_pm = sorted([k for k in pm_m if k not in pm_v])

pmg_all = load_blocks(van_pmg_dir); pmg_all.update(load_blocks(mod_pmg_dir))
bld_all = load_blocks(van_bld_dir); bld_all.update(load_blocks(mod_bld_dir))

pm_to_pmg = defaultdict(set)
for pmg, body in pmg_all.items():
    m = re.search(r'(?ms)production_methods\s*=\s*\{(.*?)\}', body)
    if not m: continue
    for ln in m.group(1).splitlines():
        s = ln.strip()
        if not s or s.startswith('#'): continue
        s = s.split('#',1)[0].strip()
        if re.match(r'^[A-Za-z0-9_]+$', s):
            pm_to_pmg[s].add(pmg)

pmg_to_bld = defaultdict(set)
for bld, body in bld_all.items():
    m = re.search(r'(?ms)production_method_groups\s*=\s*\{(.*?)\}', body)
    if not m: continue
    for ln in m.group(1).splitlines():
        s = ln.strip()
        if not s or s.startswith('#'): continue
        s = s.split('#',1)[0].strip()
        if re.match(r'^[A-Za-z0-9_]+$', s):
            pmg_to_bld[s].add(bld)

# manual bridge for commented railway PMG
for pm in ('pm_no_magic','pm_railway_luotuomu','pm_railway_transport'):
    pm_to_pmg[pm].add('pmg_magic_railway')
pmg_to_bld['pmg_magic_railway'].add('building_railway')
comment_names.setdefault('pmg_magic_railway','魔法铁路方案')

costs = load_goods_costs()

def cn(key):
    return loc.get(key) or comment_names.get(key) or key

goods_alias = {
    'magictools': loc.get('magic_tools','魔导器'),
    'magic_mineral': loc.get('magic_mineral','魔法矿石'),
    'magic_energy': loc.get('magic_energy','魔力'),
    'magic_steels': loc.get('magic_steels','超冶金结构'),
    'omocha': loc.get('omocha','周边'),
}

def gcn(g):
    return loc.get(g) or goods_alias.get(g) or g

rows=[]
for pm in new_pm:
    ins, outs = extract_io(pm_all.get(pm,''))
    in_total = sum(q*costs.get(g,0.0) for g,q in ins.items())
    out_total = sum(q*costs.get(g,0.0) for g,q in outs.items())
    net = out_total - in_total
    roi = (net/in_total) if in_total else None
    for pmg in sorted(pm_to_pmg.get(pm) or ['(未匹配生产方式组)']):
        for bld in sorted(pmg_to_bld.get(pmg) or ['(未匹配建筑)']):
            rows.append([
                cn(bld), cn(pmg), cn(pm),
                '；'.join([f"{gcn(g)}*{q:g}" for g,q in sorted(ins.items())]),
                in_total,
                '；'.join([f"{gcn(g)}*{q:g}" for g,q in sorted(outs.items())]),
                out_total, net, roi
            ])

rows.sort(key=lambda r:(r[0],r[1],r[2]))

out = root/'analysis'/'mod_new_pm_cn_grouped_v3.xlsx'
wb=Workbook(); ws=wb.active; ws.title='建筑-生产方式组-生产方式'
ws.append(['建筑','生产方式组','生产方式','商品投入（中文）','商品投入总价格','商品产出（中文）','商品产出总价格','商品收益净值','收益率'])
for r in rows: ws.append(r)
for c in ws[1]: c.font = c.font.copy(bold=True)
for rr in ws.iter_rows(min_row=2,min_col=5,max_col=8):
    for c in rr: c.number_format='0.00'
for rr in ws.iter_rows(min_row=2,min_col=9,max_col=9):
    for c in rr: c.number_format='0.00%'
for i,w in {1:24,2:24,3:24,4:62,5:14,6:62,7:14,8:14,9:10}.items(): ws.column_dimensions[chr(64+i)].width=w
wb.save(out)

# validate
en=0; um=0
for r in rows:
    t=' | '.join([str(r[x] or '') for x in [0,1,2,3,5]])
    if '未匹配' in t: um+=1
    if re.search(r'\b(pm_|pmg_|building_)', t): en+=1
print(out)
print(f"rows={len(rows)} unmatched={um} key_english={en}")
