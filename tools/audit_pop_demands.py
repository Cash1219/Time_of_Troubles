"""Compare local vanilla and mod population needs; write audit artifacts only."""
from pathlib import Path
from collections import defaultdict
import json
import re

ROOT = Path(__file__).resolve().parents[1]
VANILLA = Path('D:/Steam/steamapps/common/Victoria 3/game')


def blocks(text):
    text = re.sub(r'#[^\n]*', '', text)
    result = []
    pattern = re.compile(r'([\w:-]+)\s*=\s*\{')
    pos = 0
    while match := pattern.search(text, pos):
        depth, end = 1, match.end()
        while depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        result.append((match[1], text[match.end():end-1]))
        pos = end
    return result


def scalars(body):
    # Nested blocks are removed before reading values at this level.
    while re.search(r'[\w:-]+\s*=\s*\{[^{}]*\}', body):
        body = re.sub(r'[\w:-]+\s*=\s*\{[^{}]*\}', '', body)
    return dict(re.findall(r'([\w:-]+)\s*=\s*("[^"\n]*"|[\w.+-]+)', body))


def definitions(root, folder):
    result = {}
    for path in sorted((root / folder).glob('*.txt')):
        for key, body in blocks(path.read_text(encoding='utf-8-sig')):
            result[key] = body
    return result


def needs(root):
    result = {}
    for key, body in definitions(root, 'common/pop_needs').items():
        result[key] = {
            'settings': scalars(body),
            'entries': {scalars(e)['goods']: scalars(e) for k, e in blocks(body) if k == 'entry'},
        }
    return result


def packages(root):
    return {k: {n: float(v) for n, v in scalars(dict(blocks(b))['goods']).items()}
            for k, b in definitions(root, 'common/buy_packages').items()}


def main():
    vanilla_needs, mod_overrides = needs(VANILLA), needs(ROOT)
    merged_needs = {**vanilla_needs, **mod_overrides}
    original_packages = packages(VANILLA)
    merged_packages = {k: dict(v) for k, v in original_packages.items()}
    injections = packages(ROOT)
    for key, values in injections.items():
        target = key.removeprefix('INJECT:')
        if key.startswith('INJECT:'):
            merged_packages.setdefault(target, {}).update(values)
        else:
            merged_packages[target] = values
    vg = definitions(VANILLA, 'common/goods')
    mg = definitions(ROOT, 'common/goods')
    goods = {k: scalars(v) for k, v in {**vg, **mg}.items()}
    labels = {}
    for directory in [VANILLA/'localization/simp_chinese', ROOT/'localization/replace/simp_chinese']:
        for path in directory.rglob('*.yml'):
            labels.update(re.findall(r'^\s*([\w]+):\d*\s+"([^"\n]*)"',
                          path.read_text(encoding='utf-8-sig', errors='replace'), re.M))
    name = lambda key: labels.get(key, key)
    members = defaultdict(list)
    for key, need in merged_needs.items():
        levels = [int(k.split('_')[1]) for k, v in merged_packages.items() if v.get(key, 0)>0]
        for good, entry in need['entries'].items():
            assert good in goods, (key, good)
            members[good].append(dict(need=key, first_wealth=min(levels) if levels else None, **entry))
    diffs = []
    for key, need in merged_needs.items():
        old = vanilla_needs.get(key, {'settings': {}, 'entries': {}})
        if need['settings'] != old['settings']:
            diffs.append(dict(need=key, kind='settings', old=old['settings'], new=need['settings']))
        for good in sorted(set(old['entries']) | set(need['entries'])):
            a, b = old['entries'].get(good), need['entries'].get(good)
            if a != b:
                diffs.append(dict(need=key, good=good, kind='entry', old=a, new=b))
    pms = {**definitions(VANILLA, 'common/production_methods'), **definitions(ROOT, 'common/production_methods')}
    groups = {**definitions(VANILLA, 'common/production_method_groups'), **definitions(ROOT, 'common/production_method_groups')}
    buildings = {**definitions(VANILLA, 'common/buildings'), **definitions(ROOT, 'common/buildings')}
    ordinary = {s['building']: s for s in json.loads((ROOT/'analysis/round_review.json').read_text(encoding='utf-8'))['summary']}
    selected_buildings = set(ordinary) | {'building_livestock_ranch'}
    consumers, producers = defaultdict(set), defaultdict(set)
    building_goods = {}
    for building in sorted(selected_buildings):
        body = buildings[building]
        pmgs = dict(blocks(body))['production_method_groups'].split()
        for pmg in pmgs:
            ids = dict(blocks(groups[pmg]))['production_methods'].split()
            for pm in ids:
                for direction, good, quantity in re.findall(r'goods_(input|output)_(\w+)_add\s*=\s*([-\d.]+)', pms[pm]):
                    if float(quantity)>0:
                        (consumers if direction=='input' else producers)[good].add(building)
        if building in ordinary:
            building_goods[building] = {}
            for tier in ['default', 'highest']:
                totals = defaultdict(float)
                selection = ordinary[building][tier]['selection']
                for pm in selection:
                    for good, quantity in re.findall(r'goods_output_(\w+)_add\s*=\s*([-\d.]+)', pms[pm]):
                        totals[good] += float(quantity)
                for good in list(totals):
                    mult = sum(float(v) for pm in selection for v in re.findall(r'goods_output_'+good+r'_mult\s*=\s*([-\d.]+)', pms[pm]))
                    common_mult = sum(float(v) for pm in selection for v in re.findall(r'building_goods_output_mult\s*=\s*([-\d.]+)', pms[pm]))
                    totals[good] *= (1+mult+common_mult)*ordinary[building][tier]['throughput']
                building_goods[building][tier] = dict(totals)
    custom = []
    for good in mg:
        custom.append(dict(good=good, name=name(good), price=float(goods[good]['cost']),
                           category=goods[good].get('category'), local=goods[good].get('local')=='yes', needs=members[good],
                           producers=sorted(producers[good]), consumers=sorted(consumers[good])))
    budget_rows=[]
    for wealth in range(1,100):
        key=f'wealth_{wealth}'
        if key not in original_packages: continue
        old, new=original_packages[key], merged_packages[key]
        budget_rows.append(dict(wealth=wealth, vanilla_leisure=old.get('popneed_leisure',0),
                               mod_leisure=new.get('popneed_leisure',0), vanilla_total=sum(old.values()),
                               mod_total=sum(new.values()), vanilla=old, mod=new))
    data=dict(need_diffs=diffs, custom_goods=custom, budgets=budget_rows, building_outputs=building_goods,
              notes=['INJECT packages modeled as nested scalar overrides; not a game-engine execution.',
                     'Output snapshots use existing audited representative selections; not current market supply.',
                     'Industrial usages cover 16 reviewed ordinary mod buildings plus vanilla livestock ranch.'])
    (ROOT/'analysis/pop_demand_audit_20261009.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 居民商品需求：原版与模组静态对照', '', '日期：2026-10-09。读取本机安装原版和当前模组文件；未改游戏定义。', '',
           '## 口径', '',
           '- 生活水平档位按 `wealth`。消费包数字是需求预算配置值，不是购买商品的件数。',
           '- `weight` 是基于供给份额的选择权重；`max_supply_share` 是供给份额对权重的作用上限，并非最终消费百分比硬上限；`min_supply_share` 是计算权重的最低供给份额系数，并非固定销量。依据原版 pop_needs 文件头注释。',
           '- INJECT 按嵌套标量覆盖的设计意图合并；尚未进游戏验证加载结果。没有模拟人口、供给、价格、文化痴迷、禁忌和品牌商品，因此不输出实际销量或可支撑建筑数。',
           '- 工业消费者范围：当前复核的16种普通模组建筑及原版畜牧场。其他暂放建筑和事件消费未计入。', '',
           '## 定义差异', '', '| 需求 | 商品 | 原版 | 模组 |', '|---|---|---|---|']
    fmt=lambda e:'—' if e is None else ' / '.join(e.get(k,'默认') for k in ['weight','max_supply_share','min_supply_share'])
    for d in diffs:
        if d['kind']=='entry':lines.append(f"| {name(d['need'])}（{d['need']}） | {name(d['good'])} | {fmt(d['old'])} | {fmt(d['new'])} |")
    lines+=['', '三列参数依次为：权重／供给份额作用上限／最低供给份额系数。未列出的原版条目与需求级设置保持不变。', '',
            '## 全部模组商品接入情况', '', '| 商品 | 基础价／分类 | 居民需求：起始档／权重／上限／最低系数 | 工业消费建筑 |', '|---|---|---|---|']
    for g in custom:
        need='；'.join(f"{name(e['need'])}：{e['first_wealth']} / {e.get('weight','默认')} / {e.get('max_supply_share','默认')} / {e.get('min_supply_share','默认')}" for e in g['needs']) or '无'
        use='、'.join(name(b) for b in g['consumers']) or '本次范围内无'
        locality=' / 本地' if g['local'] else ''
        lines.append(f"| {g['name']}（{g['good']}） | {g['price']:g} / {g['category']}{locality} | {need} | {use} |")
    lines+=['', '## 休闲消费包对照', '', '| 生活水平 | 原版休闲 | 模组休闲 | 增幅 | 原版全部预算 | 模组全部预算 | 总预算增幅 |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in budget_rows:
        if r['wealth']<=35 or r['wealth'] in [40,50,60,99]:
            change=(r['mod_leisure']/r['vanilla_leisure']-1)*100 if r['vanilla_leisure'] else None
            change_text=f'{change:.1f}%' if change is not None else ('新增' if r['mod_leisure'] else '—')
            lines.append(f"| {r['wealth']} | {r['vanilla_leisure']:g} | {r['mod_leisure']:g} | {change_text} | {r['vanilla_total']:g} | {r['mod_total']:g} | {(r['mod_total']/r['vanilla_total']-1)*100:.2f}% |")
    lines+=['', '## 代表性组合每级产出', '', '仅列模组商品。采用已有建筑审计的默认与最高组合，并计商品倍率和吞吐量；这些产量不能直接推出需求是否足够。', '', '| 建筑 | 默认组合 | 最高组合 |', '|---|---|---|']
    for b, outputs in building_goods.items():
        display=lambda d:'、'.join(f'{name(k)} {v:g}' for k,v in d.items() if k in mg and v>0) or '—'
        lines.append(f"| {name(b)} | {display(outputs['default'])} | {display(outputs['highest'])} |")
    (ROOT/'analysis/pop_demand_audit_20261009.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(changed_entries=len(diffs),custom_goods=len(custom),
                         no_pop_demand=[g['good'] for g in custom if not g['needs']],
                         budget_snapshots=[r for r in budget_rows if r['wealth'] in [10,15,20,25,30,31]]),ensure_ascii=False))


if __name__=='__main__':
    main()
