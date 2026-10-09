"""Review enabled commercial buildings, including all combinations and PM throughput.

Only audit artifacts are written; no game definitions are modified.
"""
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
with contextlib.redirect_stdout(io.StringIO()):
    base = runpy.run_path(str(ROOT / 'tools/audit_all_mod_buildings.py'))
audit = base['audit']
tech = runpy.run_path(str(ROOT / 'docs/drafts/_audit_single_tech.py'))
T = tech['T']
vals, clean = audit['vals'], audit['clean']
pms, groups, buildings = audit['pms'], audit['groups'], audit['mod_buildings']
excluded = {'building_club', 'building_band_headquarter'}
scope = {
    k: v for k, v in buildings.items()
    if k not in excluded and 'golden_hall' not in k
    and not re.search(r'\bbuildable\s*=\s*no', clean(v[0]))
}

labels = dict(base['names'])
for root in [audit['VANILLA'] / 'localization/simp_chinese', ROOT / 'localization/replace/simp_chinese']:
    for p in root.rglob('*.yml'):
        for key, value in re.findall(r'^\s*((?:pm_|pmg_|building_)[\w]+):\d*\s+"([^"\n]*)"', p.read_text(encoding='utf-8-sig', errors='replace'), re.M):
            labels[key] = value

pop_types = audit['definitions']('common/pop_types', '')
wages = {}
for name, (body, _) in pop_types.items():
    m = re.search(r'\bwage_weight\s*=\s*([\d.]+)', clean(body))
    if m and re.search(r'\bpaid_private_wage\s*=\s*yes', clean(body)):
        wages[name] = float(m[1])

effects = audit['definitions']('common/scripted_effects', '')
country_bodies = defaultdict(list)
for root in [audit['VANILLA'], ROOT]:
    for p in (root / 'common/history/countries').glob('*.txt'):
        code = clean(p.read_text(encoding='utf-8-sig', errors='replace'))
        for m in re.finditer(r'\bc:(\w+)\s*\??=\s*\{', code):
            depth, end = 1, m.end()
            while depth and end < len(code):
                depth += (code[end] == '{') - (code[end] == '}')
                end += 1
            country_bodies[m[1]].append(code[m.end():end-1])

def starting_techs(tag):
    known, seen = set(), set()
    stack = list(country_bodies[tag])
    while stack:
        code = stack.pop()
        known.update(re.findall(r'\badd_technology_researched\s*=\s*(\w+)', code))
        for era in re.findall(r'\badd_era_researched\s*=\s*era_(\d+)', code):
            known.update(t for t, (e, parents) in T.items() if e == int(era))
        for effect in re.findall(r'\b(effect_starting_technology_\w+)\s*=\s*yes', code):
            if effect in effects and effect not in seen:
                seen.add(effect)
                stack.append(clean(effects[effect][0]))
    return known

def name(key):
    return labels.get(key, key)

def jobs(pm):
    result = defaultdict(float)
    for k, n in re.findall(r'\bbuilding_employment_(\w+)_add\s*=\s*([-+\d.]+)', clean(pms[pm][0])):
        result[k] += float(n)
    return result

def calculate(selection):
    I, O = base['values'](selection)
    staff = defaultdict(float)
    throughput = 1.0
    for pm in selection:
        for k, n in jobs(pm).items():
            staff[k] += n
        throughput += sum(float(n) for n in re.findall(r'\bbuilding_throughput_add\s*=\s*([-+\d.]+)', clean(pms[pm][0])))
    I, O = I * throughput, O * throughput
    N = sum(staff.values())
    wage = sum(n * wages.get(k, 0) / 52 for k, n in staff.items())
    return dict(selection=list(selection), input=I, output=O, difference=O-I,
                employees=N, occupations=dict(staff), wage=wage, after_wage=O-I-wage,
                throughput=throughput,
                margin=(O-I)/O*100 if O > 0 else None,
                annual=(O-I)*52/N if N > 0 else None)

issues = []
def issue(building, kind, detail, pm=''):
    issues.append(dict(building=building, kind=kind, detail=detail, pm=pm))

summaries = []
all_combos = []
opening = []
with (ROOT / 'config/building_start_config.csv').open(encoding='utf-8-sig', newline='') as f:
    config = list(csv.DictReader(f))

for building, (body, _) in sorted(scope.items()):
    gs = vals(body, 'production_method_groups')
    options, defaults = [], []
    for group in gs:
        group_texture = re.search(r'\btexture\s*=\s*"([^"]+)"', clean(groups[group][0]))
        if group_texture and not any((r / group_texture[1]).exists() for r in [ROOT, audit['VANILLA']]):
            issue(building, '缺少组纹理', group_texture[1], group)
        ns = vals(groups[group][0], 'production_methods')
        options.append(ns)
        ds = [n for n in ns if re.search(r'\bis_default\s*=\s*yes', clean(pms[n][0]))]
        if len(ds) > 1:
            issue(building, '多个默认PM', group)
        defaults.append(ds[0] if ds else ns[0])
        prior = None
        for n in ns:
            code, path = pms[n]
            code = clean(code)
            ts = vals(code, 'unlocking_technologies')
            if len(ts) > 1:
                issue(building, '多个科技门槛', str(ts), n)
            for t in ts:
                if t not in T:
                    issue(building, '未知科技', t, n)
            tex = re.search(r'\btexture\s*=\s*"([^"]+)"', code)
            if not tex or not any((r / tex[1]).exists() for r in [ROOT, audit['VANILLA']]):
                issue(building, '缺少纹理', tex[1] if tex else 'texture', n)
            if n not in labels:
                issue(building, '缺少中文名称', group, n)
            if code.count('{') != code.count('}'):
                issue(building, '括号不平衡', str(path), n)
            goods = base['pm_goods'][n]
            if sum(d == 'input' and q > 0 for (d, g), q in goods.items()) > 5:
                issue(building, '投入超过5种', str(goods), n)
            if audit['in_mod'](path):
                for (direction, good), amount in goods.items():
                    if amount % 5 and not n.startswith('pm_tot_dairy_'):
                        issue(building, '数量非5倍数', f'{direction} {good}={amount:g}', n)
            is_null = not goods and not jobs(n) and not base['pm_modifiers'][n]
            is_named_null = n.endswith(('_null', '_none')) or n == 'pm_no_secondary'
            if is_null or is_named_null:
                continue
            era = T[ts[0]][0] if len(ts) == 1 and ts[0] in T else None
            total_jobs = sum(jobs(n).values())
            output = sum(q * audit['prices'][g] for (d, g), q in goods.items() if d == 'output')
            if prior:
                pn, pe, pj, po = prior
                if era is not None and pe is not None and era <= pe:
                    issue(building, '时代未递增', f'{name(group)}：{name(pn)} E{pe} → {name(n)} E{era}', n)
                if era is None and pe is not None:
                    issue(building, '升级取消科技', f'{name(group)}：{name(pn)} → {name(n)}', n)
                if era is None and pe is None:
                    issue(building, '相邻营业档均无科技', f'{name(group)}：{name(pn)} → {name(n)}', n)
                if output < po:
                    issue(building, '单组产出总价下降', f'{name(pn)} {po:g} → {name(n)} {output:g}（须检查转产或修正）', n)
                if total_jobs > 0 and pj > 0 and total_jobs != pj:
                    issue(building, '同组营业员工变化', f'{name(pn)} {pj:g} → {name(n)} {total_jobs:g}（须区分主产与省工）', n)
            prior = n, era, total_jobs, output
    combinations = [calculate(s) for s in product(*options)]
    for c in combinations:
        if c['employees'] <= 0 or any(x < 0 for x in c['occupations'].values()):
            issue(building, '员工异常', str(c['occupations']), ';'.join(c['selection']))
        all_combos.append(dict(building=building, **c))
    default = calculate(defaults)
    highest = calculate([ns[-1] for ns in options])
    valid = [c for c in combinations if c['annual'] is not None and c['output'] > 0]
    low = [c for c in combinations if c['margin'] is not None and c['margin'] < 30]
    high = [c for c in combinations if c['margin'] is not None and c['margin'] > 70]
    losses = [c for c in combinations if c['difference'] < 0]
    summaries.append(dict(building=building, name=name(building), combinations=len(combinations),
                          default=default, highest=highest, below30=len(low), above70=len(high),
                          losses=len(losses), after_wage_losses=sum(c['after_wage'] < 0 for c in combinations),
                          minimum=min(valid, key=lambda c: c['annual']) if valid else None,
                          maximum=max(valid, key=lambda c: c['annual']) if valid else None,
                          minimum_staff=min(c['employees'] for c in combinations),
                          maximum_staff=max(c['employees'] for c in combinations)))
    for row in config:
        if row['building'] != building or row['enabled'] != 'yes':
            continue
        selected = row['production_methods'].split(';') if row['production_methods'] else []
        resolved = list(defaults)
        for pm in selected:
            memberships = [i for i, ns in enumerate(options) if pm in ns]
            if len(memberships) != 1:
                issue(building, '开局PM不属于当前组', f"{row['id']} {pm}", pm)
            else:
                resolved[memberships[0]] = pm
        if len(selected) != len(set(selected)):
            issue(building, '开局PM重复', row['id'])
        for i, ns in enumerate(options):
            if sum(pm in ns for pm in selected) > 1:
                issue(building, '开局同组多个PM', row['id'] + ' ' + gs[i])
        known = starting_techs(row['region_owner'])
        gates = vals(body, 'unlocking_technologies')
        for pm in resolved:
            gates.extend(vals(pms[pm][0], 'unlocking_technologies'))
        missing = sorted(set(gates) - known)
        if missing:
            issue(building, '开局科技待核对', row['id'] + ' ' + row['region_owner'] + ': ' + ', '.join(missing))
        opening.append(dict(id=row['id'], building=building, country=row['region_owner'],
                            state=row['state'], level=row['level'], **calculate(resolved)))

active_goods = set()
for c in all_combos:
    for pm in c['selection']:
        active_goods.update(g for (d, g) in base['pm_goods'][pm])
icon_sources = '\n'.join(p.read_text(encoding='utf-8-sig', errors='replace') for p in (ROOT / 'gui').rglob('*.gui'))
icon_names = set(re.findall(r'\bicon\s*=\s*"?(\w+)"?', icon_sources))
for good, (body, path) in audit['definitions']('common/goods', '').items():
    if not audit['in_mod'](path) or good not in active_goods:
        continue
    if good not in icon_names:
        issue('goods', '新商品缺少texticon', good)

era_profiles = []
for building, (body, _) in sorted(scope.items()):
    options = [vals(groups[g][0], 'production_methods') for g in vals(body, 'production_method_groups')]
    for era in range(1, 6):
        if any(T[t][0] > era for t in vals(body, 'unlocking_technologies')):
            continue
        selected = []
        for ns in options:
            allowed = [n for n in ns if all(T[t][0] <= era for t in vals(pms[n][0], 'unlocking_technologies'))]
            operating = [n for n in allowed if not n.endswith(('_null', '_none'))]
            selected.append((operating or allowed)[-1])
        era_profiles.append(dict(building=building, era=era, **calculate(selected)))

upgrade_drops = []
for building, (body, _) in sorted(scope.items()):
    gs = vals(body, 'production_method_groups')
    options = [vals(groups[g][0], 'production_methods') for g in gs]
    for index, ns in enumerate(options):
        operating = [n for n in ns if not n.endswith(('_null', '_none'))]
        for old, new in zip(operating, operating[1:]):
            if not any(d == 'output' and q > 0 for (d, g), q in base['pm_goods'][new].items()):
                continue
            era = max([T[t][0] for t in vals(pms[new][0], 'unlocking_technologies')] + [1])
            selected = []
            for choices in options:
                available = [n for n in choices if all(T[t][0] <= era for t in vals(pms[n][0], 'unlocking_technologies'))]
                nonnull = [n for n in available if not n.endswith(('_null', '_none'))]
                selected.append((nonnull or available)[-1])
            selected[index] = old
            before = calculate(selected)
            selected[index] = new
            after = calculate(selected)
            if before['margin'] is not None and after['margin'] is not None and before['margin'] - after['margin'] >= 10:
                upgrade_drops.append(dict(building=building, group=gs[index], old=old, new=new, before=before, after=after))

out = ROOT / 'analysis'
(out / 'round_review.json').write_text(json.dumps(dict(summary=summaries, issues=issues, opening=opening, era_profiles=era_profiles, upgrade_drops=upgrade_drops), ensure_ascii=False, indent=2), encoding='utf-8')
fields = ['building', 'input', 'output', 'difference', 'employees', 'margin', 'annual', 'wage', 'after_wage', 'throughput', 'selection']
with (out / 'round_review_combinations.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for c in all_combos:
        w.writerow({k: ';'.join(c[k]) if k == 'selection' else c[k] for k in fields})

def f(x):
    return '—' if x is None else f'{x:.2f}'.rstrip('0').rstrip('.')

lines = ['# 普通经营建筑：全量复核', '',
         '范围：启用且在模组中定义的普通经营建筑，包含改写的原版畜牧场。社团、乐队总部、金色大厅与合同、停用建筑不纳入。', '',
         '所有组合按每级满就业、基础价计算；合并商品修正，并计入PM直接吞吐量。排除市场、州修正、规模经济和科技/法律可用性筛选。工资以劳工年工资1、其余原版职业倍率估算，不等于游戏实际工资。', '',
         '开局科技另从国家历史显式研究及起始科技脚本展开核对；不模拟条件分支、运行时事件或科技前置自动补全。发现缺项列为待核对，不直接证明游戏中失效。texticon检查的是模组GUI图标声明。', '',
         '毛利30%—70%、年产值10和40—50为参照，不是所有组合的硬门槛；关闭生产、低主产配高自动化、宗教功能建筑须单独解释。', '',
         f"共{len(scope)}种建筑、{len(all_combos)}种组合、{len(opening)}条开局配置。", '',
         '## 默认和全高档', '',
         '| 建筑 | 组合数 | 默认投入→产出 | 默认员工 | 默认毛利 | 默认年产值 | 全高档投入→产出 | 全高档员工 | 全高档毛利 | 全高档年产值 | 低毛利／高毛利／商品亏损组合 |',
         '|---|---:|---|---:|---:|---:|---|---:|---:|---:|---|']
for s in summaries:
    d, h = s['default'], s['highest']
    lines.append(f"| {s['name']} | {s['combinations']} | {f(d['input'])}→{f(d['output'])} | {f(d['employees'])} | {f(d['margin'])}% | {f(d['annual'])} | {f(h['input'])}→{f(h['output'])} | {f(h['employees'])} | {f(h['margin'])}% | {f(h['annual'])} | {s['below30']}／{s['above70']}／{s['losses']} |")
lines += ['', '## 各时代可用最高营业档', '',
          '仅用era筛选当前组中可用的最高营业档，并开启可用副业务及最高设备；不等于国家已研究整时代全部科技，也不是最优利润解。', '',
          '| 建筑 | I时代年产值 | II时代 | III时代 | IV时代 | V时代 |',
          '|---|---:|---:|---:|---:|---:|']
for s in summaries:
    eras = {p['era']: p for p in era_profiles if p['building'] == s['building']}
    lines.append('| ' + s['name'] + ' | ' + ' | '.join(f(eras[e]['annual']) if e in eras else '未解锁' for e in range(1, 6)) + ' |')
lines += ['', '## 单组升档毛利下降至少10个百分点的代表组合', '',
          '固定其他组为新档所属时代可用的最高营业档，仅切换一个生产组；这不是对全部混搭升档的穷举。纯省工组无直接产出，另在组合中评价。毛利下降本身不判为错误。', '',
          '| 建筑 | 升档 | 毛利变化 | 年产值变化 |', '|---|---|---|---|']
for u in upgrade_drops:
    lines.append(f"| {name(u['building'])} | {name(u['old'])}→{name(u['new'])} | {f(u['before']['margin'])}%→{f(u['after']['margin'])}% | {f(u['before']['annual'])}→{f(u['after']['annual'])} |")
lines += ['', '## 最低与最高年产值组合', '']
for s in summaries:
    lines.append('### ' + s['name'])
    lines.append('')
    for title, k in [('最低', 'minimum'), ('最高', 'maximum')]:
        c = s[k]
        if c:
            lines.append(f"- {title}：{'＋'.join(name(n) for n in c['selection'])}；投入{f(c['input'])}、产出{f(c['output'])}、员工{f(c['employees'])}、毛利{f(c['margin'])}%、年产值{f(c['annual'])}、参考周工资{f(c['wage'])}、扣工资差额{f(c['after_wage'])}。")
    lines.append('')
lines += ['## 静态规则待核对项', '', '下列为机械筛选结果，未自动判定为设计错误。无档、自动化、转产、既有原版PM例外须结合职责判断。', '']
for x in issues:
    lines.append(f"- **{name(x['building'])}／{x['kind']}**：{name(x['pm']) if x['pm'] else ''}；{x['detail']}")
lines += ['', '## 开局实际组合', '', '| 配置 | 建筑 | 国家／州 | 等级 | PM | 投入→产出 | 员工 | 毛利 | 年产值 |', '|---|---|---|---:|---|---|---:|---:|---:|']
for r in opening:
    lines.append(f"| {r['id']} | {name(r['building'])} | {r['country']}／{r['state']} | {r['level']} | {'＋'.join(name(n) for n in r['selection'])} | {f(r['input'])}→{f(r['output'])} | {f(r['employees'])} | {f(r['margin'])}% | {f(r['annual'])} |")
(out / 'round_review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps(dict(buildings=len(scope), combinations=len(all_combos), opening=len(opening), issues=issues,
                     summary=[{k: s[k] for k in ['building', 'combinations', 'below30', 'above70', 'losses', 'minimum_staff', 'maximum_staff']} for s in summaries]), ensure_ascii=True, indent=2))
