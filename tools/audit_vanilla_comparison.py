"""Audit ALL vanilla buildings without mod overrides, then compare current mod."""
from pathlib import Path
from collections import defaultdict
from itertools import product
import contextlib
import csv
import io
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parser = runpy.run_path(str(ROOT / 'docs/drafts/_audit_single_tech.py'))
V, blocks, vals = parser['V'], parser['blocks'], parser['vals']

def definitions(folder):
    result = {}
    for p in sorted((V / folder).glob('*.txt')):
        for key, body, path in blocks(p):
            result[key] = body
    return result

def clean(body):
    return '\n'.join(line.split('#', 1)[0] for line in body.splitlines())

def inner(body, key):
    m = re.search(r'\b' + key + r'\s*=\s*\{', body)
    if not m:
        return ''
    depth, end = 1, m.end()
    while depth and end < len(body):
        depth += (body[end] == '{') - (body[end] == '}')
        end += 1
    return body[m.end():end-1]

buildings = definitions('common/buildings')
groups = definitions('common/production_method_groups')
pms = definitions('common/production_methods')
goods = definitions('common/goods')
prices = {k: float(re.search(r'\bcost\s*=\s*([\d.]+)', clean(b))[1]) for k, b in goods.items() if re.search(r'\bcost\s*=\s*([\d.]+)', clean(b))}
wages = {}
for k, b in definitions('common/pop_types').items():
    m = re.search(r'\bwage_weight\s*=\s*([\d.]+)', clean(b))
    if m and re.search(r'\bpaid_private_wage\s*=\s*yes', clean(b)):
        wages[k] = float(m[1])
labels = {}
for p in (V / 'localization/simp_chinese').rglob('*.yml'):
    for k, v in re.findall(r'^\s*((?:building_|pm_)[\w]+):\d*\s+"([^"\n]*)"', p.read_text(encoding='utf-8-sig', errors='replace'), re.M):
        labels[k] = v

def label(k):
    return labels.get(k, k)

effects = {}
for n, b in pms.items():
    code = clean(b)
    bm = inner(code, 'building_modifiers')
    workforce = inner(bm, 'workforce_scaled')
    amounts, mults, jobs = defaultdict(float), defaultdict(float), defaultdict(float)
    for d, g, q in re.findall(r'\bgoods_(input|output)_(\w+)_add\s*=\s*([-+\d.]+)', workforce):
        amounts[d, g] += float(q)
    for d, g, q in re.findall(r'\bgoods_(input|output)_(\w+)_mult\s*=\s*([-+\d.]+)', bm):
        mults[d, g] += float(q)
    for d, q in re.findall(r'\bbuilding_goods_(input|output)_mult\s*=\s*([-+\d.]+)', bm):
        mults[d, '*'] += float(q)
    for k, q in re.findall(r'\bbuilding_employment_(\w+)_add\s*=\s*([-+\d.]+)', bm):
        jobs[k] += float(q)
    throughput = sum(float(q) for q in re.findall(r'\bbuilding_throughput_add\s*=\s*([-+\d.]+)', bm))
    effects[n] = amounts, mults, jobs, throughput

def calculate(selection):
    amounts, mults, jobs = defaultdict(float), defaultdict(float), defaultdict(float)
    throughput = 1.0
    for n in selection:
        a, m, j, t = effects[n]
        for k, q in a.items(): amounts[k] += q
        for k, q in m.items(): mults[k] += q
        for k, q in j.items(): jobs[k] += q
        throughput += t
    totals = defaultdict(float)
    for (d, g), q in amounts.items():
        totals[d] += q * prices[g] * (1 + mults[d, '*'] + mults[d, g]) * throughput
    I, O, N = totals['input'], totals['output'], sum(jobs.values())
    valid = N > 0 and all(q >= 0 for q in jobs.values())
    wage = sum(q * wages.get(k, 0) / 52 for k, q in jobs.items())
    return dict(selection=list(selection), input=I, output=O, difference=O-I, employees=N,
                occupations=dict(jobs), wage=wage, after_wage=O-I-wage, valid_staff=valid,
                margin=(O-I)/O*100 if O > 0 else None, annual=(O-I)*52/N if valid else None)

categories = {
    'bg_light_industry': '轻工业', 'bg_heavy_industry': '重工业',
    'bg_military_industry': '军用制造', 'bg_staple_crops': '农业', 'bg_ranching': '农业',
    'bg_plantations': '种植园', 'bg_mining': '资源开采', 'bg_logging': '资源开采',
    'bg_rubber': '资源开采', 'bg_whaling': '资源开采', 'bg_fishing': '资源开采',
    'bg_oil_extraction': '资源开采', 'bg_service': '城市服务', 'bg_arts': '艺术',
    'bg_power': '电力', 'bg_construction': '非商品／公共', 'bg_government': '非商品／公共',
    'bg_military': '非商品／公共', 'bg_monuments': '非商品／公共',
}
rows, combos, automation, warnings = [], [], [], []
for building, b in sorted(buildings.items()):
    gs = vals(b, 'production_method_groups')
    opts = [vals(groups[g], 'production_methods') for g in gs]
    if not gs or any(not ns for ns in opts):
        warnings.append(building + ': no PM groups/options')
        rows.append(dict(building=building, name=label(building), category='无生产组', combinations=0))
        continue
    for ns in opts:
        for n in ns:
            if n not in effects:
                raise ValueError('Unknown PM: ' + n)
    baseline, high, unautomated = [], [], []
    for group, ns in zip(gs, opts):
        default = next((n for n in ns if re.search(r'\bis_default\s*=\s*yes', clean(pms[n]))), ns[0])
        neutral = next((n for n in ns if n.endswith('no_effect')), None)
        regular = [n for n in ns if 'principle' not in n]
        first, last = (neutral, neutral) if 'principle' in group and neutral else (default, (regular or ns)[-1])
        baseline.append(first)
        high.append(last)
        first_jobs = sum(effects[first][2].values())
        last_jobs = sum(effects[last][2].values())
        unautomated.append(first if last_jobs < first_jobs else last)
        for old, new in zip(ns, ns[1:]):
            freed = sum(effects[old][2].values()) - sum(effects[new][2].values())
            if freed > 0:
                cost = sum(q * prices[g] for (d, g), q in effects[new][0].items() if d == 'input') - sum(q * prices[g] for (d, g), q in effects[old][0].items() if d == 'input')
                automation.append(dict(building=building, group=group, old=old, new=new, freed=freed, cost=cost, per1000=cost*1000/freed))
    cs = [calculate(s) for s in product(*opts)]
    combos.extend(dict(building=building, **c) for c in cs)
    useful = [c for c in cs if c['output'] > 0 and c['annual'] is not None]
    m = re.search(r'\bbuilding_group\s*=\s*(\w+)', clean(b))
    bg = m[1] if m else ''
    category = categories.get(bg, '自给' if 'subsistence' in bg else '其他／公共')
    rows.append(dict(building=building, name=label(building), group=bg, category=category, combinations=len(cs),
                     baseline=calculate(baseline), highest=calculate(high), unautomated=calculate(unautomated),
                     maximum=max(useful, key=lambda c: c['annual']) if useful else None,
                     minimum=min(useful, key=lambda c: c['annual']) if useful else None,
                     min_output=min(c['output'] for c in cs), max_output=max(c['output'] for c in cs)))

out = ROOT / 'analysis'
(out / 'vanilla_all_buildings.json').write_text(json.dumps(dict(buildings=rows, automation=automation, warnings=warnings), ensure_ascii=False, indent=2), encoding='utf-8')
with (out / 'vanilla_all_combinations.csv').open('w', encoding='utf-8-sig', newline='') as f:
    fields = ['building', 'input', 'output', 'difference', 'employees', 'margin', 'annual', 'wage', 'after_wage', 'valid_staff', 'selection']
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for c in combos:
        w.writerow({k: ';'.join(c[k]) if k == 'selection' else c[k] for k in fields})
def fmt(x):
    return '—' if x is None else f'{x:.2f}'.rstrip('0').rstrip('.')

lines = ['# 原版全部建筑：纯原版基准复核', '',
         f'读取本机原版文件，完全不叠加模组定义、商品价格或PM覆盖。共{len(rows)}种建筑、{len(combos)}种PM组合。', '',
         '每级满员、基础价，计入PM商品修正及直接吞吐量。人均年产值=(产出-投入)×52/员工，不扣工资；参考工资另列。非商品建筑的零产出不代表无用途。', '',
         '比较基准优先默认PM，无默认用首档；最高档取末档。两者的特殊集团原则组优先使用无效果档；全组合极值仍包含集团原则、法律和转产的理论搭配，不代表所有国家能开启。没有模拟开局实际PM、市场、规模经济、州修正、科技法律、招聘或公共财政。', '',
         '“无省工最高档”仅将员工减少的PM组保持比较基准，其余取最高档；有些采收/冷藏组同时影响产量，故不是所有建筑的最大产出。', '',
         '## 全部建筑汇总', '',
         '| 类别 | 建筑 | 组合数 | 基准投入→产出 | 人数 | 年产值 | 最高档投入→产出 | 人数 | 毛利 | 年产值 | 全组合最高年产值 |',
         '|---|---|---:|---|---:|---:|---|---:|---:|---:|---:|']
for r in sorted(rows, key=lambda r: (r['category'], r['building'])):
    if not r['combinations']:
        lines.append(f"| {r['category']} | {r['name']} | 0 | — | — | — | — | — | — | — | — |")
        continue
    d, h, mx = r['baseline'], r['highest'], r['maximum']
    lines.append(f"| {r['category']} | {r['name']} | {r['combinations']} | {fmt(d['input'])}→{fmt(d['output'])} | {fmt(d['employees'])} | {fmt(d['annual'])} | {fmt(h['input'])}→{fmt(h['output'])} | {fmt(h['employees'])} | {fmt(h['margin'])} | {fmt(h['annual'])} | {fmt(mx['annual']) if mx else '—'} |")
lines += ['', '## 无省工最高档对照', '', '| 建筑 | 投入→产出 | 员工 | 毛利 | 人均年产值 | PM |', '|---|---|---:|---:|---:|---|']
for r in rows:
    if not r['combinations']: continue
    h = r['unautomated']
    if h['output'] <= 0: continue
    lines.append(f"| {r['name']} | {fmt(h['input'])}→{fmt(h['output'])} | {fmt(h['employees'])} | {fmt(h['margin'])} | {fmt(h['annual'])} | {'＋'.join(label(n) for n in h['selection'])} |")
lines += ['', '## 所有相邻省工档成本', '', '仅比较相邻PM的直接投入和员工数量，未扣除兼有的增产效益；负成本项须结合燃料替换或产量变化解释。', '',
          '| 建筑 | PM变化 | 释放员工 | 额外投入/周 | 每省1000人成本 |', '|---|---|---:|---:|---:|']
for r in automation:
    lines.append(f"| {label(r['building'])} | {label(r['old'])}→{label(r['new'])} | {fmt(r['freed'])} | {fmt(r['cost'])} | {fmt(r['per1000'])} |")
(out / 'vanilla_all_buildings.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(json.dumps(dict(buildings=len(rows), combinations=len(combos), warnings=warnings,
                      commercial=[dict(building=r['building'], name=r['name'], category=r['category'],
                                       baseline=r['baseline']['annual'], highest=r['highest']['annual'],
                                       highest_output=r['highest']['output'], highest_staff=r['highest']['employees'])
                                  for r in rows if r['combinations'] and r['category'] in ['轻工业','重工业','军用制造','城市服务','艺术','电力','农业','种植园','资源开采']]), ensure_ascii=True, indent=2))
