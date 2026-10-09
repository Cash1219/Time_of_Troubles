"""Inventory PM and PMG textures; keep missing and reused art distinct."""
from pathlib import Path
from collections import defaultdict, Counter
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
V = Path(r'D:\Steam\steamapps\common\Victoria 3\game')
parser = runpy.run_path(str(ROOT / 'docs/drafts/_audit_single_tech.py'))
blocks, vals = parser['blocks'], parser['vals']

def clean(body):
    return '\n'.join(line.split('#', 1)[0] for line in body.splitlines())

def definitions(folder, prefix):
    result = {}
    for root in (V, ROOT):
        for path in sorted((root / folder).glob('*.txt')):
            for key, body, _ in blocks(path):
                if key.startswith(prefix):
                    result[key] = (clean(body), path)
    return result

def local(path):
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False

labels = {}
for root in (V / 'localization/simp_chinese', ROOT / 'localization'):
    for path in sorted(root.rglob('*.yml')):
        labels.update(re.findall(r'^\s*(\w+):\d*\s+"([^"\n]*)"', path.read_text(encoding='utf-8-sig', errors='replace'), re.M))

buildings = definitions('common/buildings', 'building_')
groups = definitions('common/production_method_groups', 'pmg_')
pms = definitions('common/production_methods', 'pm_')
ordinary = {'building_amusement_park', 'building_aquarium', 'building_botanical_garden',
            'building_entertainment_press', 'building_game', 'building_goods', 'building_izakaya',
            'building_kissaten', 'building_livestock_ranch', 'building_musical_instrument',
            'building_publisher_press', 'building_religious_center', 'building_stage',
            'building_animal_breeding', 'building_pet_shop', 'building_zoo'}
# Read the prior commercial audit's actual building IDs rather than guessing aliases.
prior = json.loads((ROOT / 'analysis/round_review.json').read_text(encoding='utf-8'))
ordinary = {row['building'] for row in prior['summary']}
users, group_users = defaultdict(set), defaultdict(set)
for building, (body, source) in buildings.items():
    if not local(source):
        continue
    for group in vals(body, 'production_method_groups'):
        group_users[group].add(building)
        if group in groups:
            for pm in vals(groups[group][0], 'production_methods'):
                users[pm].add(building)

def texture_info(body):
    match = re.search(r'\btexture\s*=\s*"([^"]+)"', body)
    texture = match[1] if match else ''
    if not texture:
        status = 'no_texture'
    elif (ROOT / texture).is_file():
        status = 'mod_file'
    elif (V / texture).is_file():
        status = 'vanilla_file'
    else:
        status = 'missing_file'
    return texture, status

records = []
for pm, (body, source) in pms.items():
    if not local(source):
        continue
    texture, status = texture_info(body)
    bs = sorted(users[pm])
    scope = 'ordinary' if any(b in ordinary for b in bs) else 'other_building' if bs else 'unused'
    records.append(dict(pm=pm, name=labels.get(pm, pm), scope=scope, buildings=bs,
                        texture=texture, status=status, source=str(source.relative_to(ROOT)),
                        own_named_texture=Path(texture).stem == pm,
                        confirmed_placeholder=(source.name in ('tot_animal_breeding.txt', 'tot_pet_shop.txt', 'tot_dairy.txt', 'tot_religious_center.txt') and Path(texture).stem != pm)))

group_records = []
for group, (body, source) in groups.items():
    if not local(source):
        continue
    texture, status = texture_info(body)
    bs = sorted(group_users[group])
    group_records.append(dict(group=group, name=labels.get(group, group), buildings=bs,
                              scope='ordinary' if any(b in ordinary for b in bs) else 'other_building' if bs else 'unused',
                              texture=texture, status=status))

counts = {scope: dict(Counter(r['status'] for r in records if r['scope'] == scope))
          for scope in ('ordinary', 'other_building', 'unused')}
result = dict(counts=counts, pms=records, groups=group_records)
out = ROOT / 'analysis/pm_icon_inventory_20261009.json'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

lines = ['# PM 图标清单（2026-10-09）', '',
         '缺失指 texture 未定义或模组与原版均找不到引用文件；借用原版图标不计为缺失。文件存在不代表图案与当前 PM 含义匹配。', '',
         'ordinary：本轮16种普通经营建筑；other_building：社团、乐队总部、特殊及停用建筑；unused：仍有定义，但不在模组建筑现用 PMG 内。', '',
         '| 范围 | PM 数 | 模组文件存在 | 借用原版 | 文件缺失 | 无 texture |',
         '|---|---:|---:|---:|---:|---:|']
for scope, c in counts.items():
    lines.append('| {} | {} | {} | {} | {} | {} |'.format(scope, sum(c.values()), c.get('mod_file', 0), c.get('vanilla_file', 0), c.get('missing_file', 0), c.get('no_texture', 0)))
lines += ['', '## 全部缺失 PM', '', '| 范围 | PM | 名称 | 引用 |', '|---|---|---|---|']
for r in records:
    if r['status'] in ('missing_file', 'no_texture'):
        lines.append('| {scope} | {pm} | {name} | {texture} |'.format(**r))
lines += ['', '## 确认尚未制作对应专属图案的新增 PM', '',
          '以下经过源文件检查，全部借用其他建筑 PM 或原版图案。不是 DDS 缺失；不能据此判定已经完成美术。通用的普通仪式、简易设施等可继续共用通用图标。', '',
          '| PM | 名称 | 当前引用 |', '|---|---|---|']
for r in records:
    if r['scope'] == 'ordinary' and r['confirmed_placeholder']:
        lines.append('| {pm} | {name} | {texture} |'.format(**r))
lines += ['', '## 其他非同名图标引用，待人工核对', '',
          '包括无档、改名继承和有意共用，不能自动全部算作未制作。', '',
          '| PM | 名称 | 引用 |', '|---|---|---|']
for r in records:
    if r['scope'] == 'ordinary' and not r['own_named_texture'] and not r['confirmed_placeholder']:
        lines.append('| {pm} | {name} | {texture} |'.format(**r))
lines += ['', '## 普通建筑借用原版图标', '', '| PM | 名称 | 引用 |', '|---|---|---|']
for r in records:
    if r['scope'] == 'ordinary' and r['status'] == 'vanilla_file':
        lines.append('| {pm} | {name} | {texture} |'.format(**r))
lines += ['', '## 三个场馆当前启用 PM', '', '| 建筑 | PM | 名称 | 图标状态 | 引用 |', '|---|---|---|---|---|']
for b in ('building_zoo', 'building_amusement_park', 'building_aquarium'):
    for r in records:
        if b in r['buildings']:
            lines.append('| {} | {} | {} | {} | {} |'.format(labels.get(b, b), r['pm'], r['name'], r['status'], r['texture']))
lines += ['', '## 普通建筑缺失 PMG 图标', '', '| PMG | 名称 | 引用 |', '|---|---|---|']
for r in group_records:
    if r['scope'] == 'ordinary' and r['status'] in ('missing_file', 'no_texture'):
        lines.append('| {group} | {name} | {texture} |'.format(**r))
(ROOT / 'analysis/pm_icon_inventory_20261009.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps(counts))
for r in records:
    if r['status'] in ('missing_file', 'no_texture'):
        print(r['scope'], r['pm'], r['name'])
