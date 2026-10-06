"""Generate a review-only PM technology proposal from the current mod and vanilla tree."""
import re
import runpy
from collections import Counter
from pathlib import Path

d = runpy.run_path(str(Path(__file__).with_name('_audit_single_tech.py')))
M, V, blocks, vals, T, P, G, ancestors = (d[k] for k in ('M', 'V', 'blocks', 'vals', 'T', 'P', 'G', 'ancestors'))

# These are proposals only. Nothing in common/production_methods is edited here.
changes = {
    'pm_goods_jewelry_premium': 'conveyors',
    'pm_goods_print_card': 'lathe',
    'pm_goods_print_post': 'chemical_bleaching',
    'pm_goods_print_art': 'aniline',
    'pm_goods_garage_gundam': 'shift_work',
    'pm_goods_garage_motor': 'telephone',
    'pm_kissaten_tool_watertube_boiler': 'watertube_boiler',
    'pm_kissaten_tool_flash_freezing': 'electrical_generation',
    'pm_botanical_garden_glasshouse_flowers': 'improved_fertilizer',
    'pm_botanical_garden_rare_greenhouse': 'nitrogen_fixation',
    'pm_botanical_garden_greenhouse_fruit_trees': 'improved_fertilizer',
    'pm_publisher_main_general_iron': 'mechanical_tools',
    'pm_publisher_main_general_steel': 'shift_work',
    'pm_publisher_main_general_electric': 'telephone',
    'pm_publisher_mass_magazine': 'camera',
    'pm_game_modern_arcade': 'telephone',
    'pm_game_modern_video': 'radio',
    'pm_game_disc_era': 'telephone',
    'pm_izakaya_hearth_banquet': 'modern_sewerage',
    'pm_izakaya_patron_rooms': 'corporate_charters',
    'pm_izakaya_iron_stoves_icehouse': 'mechanical_tools',
    'pm_izakaya_electric_cold_kitchen': 'telephone',
    'pm_religious_center_city_celebration': 'modern_sewerage',
    'pm_religious_center_electric_facilities': 'telephone',
    'pm_stage_media_magazines': 'mechanical_tools',
    'pm_stage_media_radio': 'telephone',
    'pm_stage_media_ip_collab': 'radio',
    'pm_amusement_ground_electric': 'electrical_generation',
    'pm_amusement_ground_dream': 'electrical_capacitors',
    'pm_amusement_ride_coaster': 'atmospheric_engine',
    'pm_amusement_ride_neon': 'electrical_generation',
    'pm_amusement_ride_ferris': 'electrical_capacitors',
    'pm_amusement_shop_collab': 'corporate_management',
    'pm_aquarium_ground_marine': 'modern_sewerage',
    'pm_aquarium_ground_tunnel': 'steel_frame_buildings',
    'pm_aquarium_ground_mega': 'elevator',
    'pm_aquarium_type_marine': 'atmospheric_engine',
    'pm_aquarium_type_reef': 'electrical_generation',
    'pm_aquarium_type_mammal': 'electrical_capacitors',
    'pm_aquarium_program_show': 'steel_frame_buildings',
    'pm_aquarium_program_theater': 'elevator',
    'pm_aquarium_program_research': 'camera',
    'pm_aquarium_program_documentary': 'film',
    'pm_zoo_type_predator': 'modern_sewerage',
    'pm_zoo_type_large': 'steel_frame_buildings',
    'pm_zoo_type_star': 'elevator',
    'pm_zoo_interaction_show': 'steel_frame_buildings',
    'pm_zoo_interaction_grand': 'elevator',
    'pm_zoo_education_conservation': 'camera',
    'pm_zoo_education_documentary': 'film',
}

reason = {
    'pm_goods_jewelry_premium': '批量装配手办；橡胶并非该档核心工艺',
    'pm_goods_print_card': '早期机械印制，作为漂白纸张前的工业档',
    'pm_goods_print_post': '漂白纸张与印制品质；承接车床',
    'pm_goods_print_art': '合成染料和彩色印刷；承接化学漂白',
    'pm_goods_garage_gundam': '标准化批量模型；承接机械化车间',
    'pm_goods_garage_motor': '电气零部件；电话科技继承轮班制与发电',
    'pm_kissaten_tool_watertube_boiler': '设备名直接对应水管锅炉',
    'pm_kissaten_tool_flash_freezing': '冷藏设备耗电；发电科技承接水管锅炉',
    'pm_botanical_garden_glasshouse_flowers': '改良肥料与温室花卉；承接精耕',
    'pm_botanical_garden_rare_greenhouse': '高投入稀有温室；固氮承接改良肥料，电力另由商品需求限制',
    'pm_botanical_garden_greenhouse_fruit_trees': '改良栽培；承接嫁接果树的精耕',
    'pm_publisher_main_general_iron': '机械化印刷与编辑设备',
    'pm_publisher_main_general_steel': '标准化分工；轮班制承接机械工具',
    'pm_publisher_main_general_electric': '电话编审网络；承接轮班制',
    'pm_publisher_mass_magazine': '插图与广告杂志；摄影技术',
    'pm_game_modern_arcade': '机电设备；电话科技继承机械工具与发电',
    'pm_game_modern_video': '电子传播技术；广播承接电话',
    'pm_game_disc_era': '电子媒介；电话科技承接发电',
    'pm_izakaya_hearth_banquet': '城市卫生支撑大型餐饮',
    'pm_izakaya_patron_rooms': '商务包间与企业经营',
    'pm_izakaya_iron_stoves_icehouse': '机械厨房设备；承接基础灶台',
    'pm_izakaya_electric_cold_kitchen': '电冷厨；电话科技继承机械工具与发电',
    'pm_religious_center_city_celebration': '城市基础设施；承接城市规划',
    'pm_religious_center_electric_facilities': '电气设施；电话科技继承机械工具与发电',
    'pm_stage_media_magazines': '机械化期刊印制',
    'pm_stage_media_radio': '电话传播网络；广播商品本身仍需供应',
    'pm_stage_media_ip_collab': '广播媒介扩大跨地域联动；承接电话',
    'pm_amusement_ground_electric': '电气化园区',
    'pm_amusement_ground_dream': '更复杂的电气游乐设施；承接发电',
    'pm_amusement_ride_coaster': '蒸汽动力设施；承接基础旋转木马',
    'pm_amusement_ride_neon': '电灯与霓虹设施；承接蒸汽动力',
    'pm_amusement_ride_ferris': '大型电动游乐设施；承接发电',
    'pm_amusement_shop_collab': '跨品牌商业管理；承接股份公司',
    'pm_aquarium_ground_marine': '海水循环和公共卫生设施',
    'pm_aquarium_ground_tunnel': '大型钢结构观览隧道；承接排水设施',
    'pm_aquarium_ground_mega': '大型多层场馆；承接钢框架',
    'pm_aquarium_type_marine': '海水泵送与温控设备',
    'pm_aquarium_type_reef': '电气化水质循环；承接蒸汽泵',
    'pm_aquarium_type_mammal': '更复杂的电气化维生设备；承接发电',
    'pm_aquarium_program_show': '结构化观演场所；承接城市排水',
    'pm_aquarium_program_theater': '大型多层剧场；承接钢框架',
    'pm_aquarium_program_research': '摄影记录；承接写实主义',
    'pm_aquarium_program_documentary': '纪录片；电影承接摄影',
    'pm_zoo_type_predator': '安全卫生的专门兽栏',
    'pm_zoo_type_large': '大型结构兽栏；承接城市卫生',
    'pm_zoo_type_star': '大型多层游客设施；承接钢框架',
    'pm_zoo_interaction_show': '结构化表演场所；承接城市排水',
    'pm_zoo_interaction_grand': '大型多层演出场所；承接钢框架',
    'pm_zoo_education_conservation': '摄影记录；承接写实主义',
    'pm_zoo_education_documentary': '纪录片；电影承接摄影',
}

# Vanilla localization is loaded first; mod translations override it.
loc = {}
files = list((V / 'localization/simp_chinese').rglob('*.yml'))
files += list((M / 'localization').rglob('*simp_chinese*.yml'))
for p in files:
    for line in p.read_text(encoding='utf-8-sig', errors='ignore').splitlines():
        m = re.match(r'^\s*([\w.-]+):\d*\s+"((?:[^"\\]|\\.)*)"', line)
        if m:
            loc[m.group(1)] = m.group(2)

def label(key):
    return loc.get(key, key).replace('|', '／')

buildings = []
for p in sorted((M / 'common/buildings').glob('*.txt')):
    for name, body, _ in blocks(p):
        if name.startswith('building_'):
            buildings.append((name, vals(body, 'production_method_groups')))
groups = dict(G)
used = {pm for names in groups.values() for pm in names if pm in P}
assert set(changes) <= used
vanilla_groups = {}
for p in (V / 'common/production_method_groups').glob('*.txt'):
    for name, body, _ in blocks(p):
        if name.startswith('pmg_'):
            vanilla_groups[name] = vals(body, 'production_methods')
vanilla_pm = {}
for p in (V / 'common/production_methods').glob('*.txt'):
    for name, body, _ in blocks(p):
        if name.startswith('pm_'):
            vanilla_pm[name] = vals(body, 'unlocking_technologies')

lines = [
    '# 模组建筑 PM 科技门槛逐项审核稿',
    '',
    '> 审核稿：以下“拟定”均未写入 PM 文件。当前栏是已恢复的旧版科技设定。',
    '',
    '> 讨论状态：电气化乐器保留旧版科技；游戏线和谷子线的拟定值只是备选，等待决定是否用新科技重排。咖啡厅配方与接待方式另见[咖啡厅与共性科技补充审核](cafe_and_shared_tech_review.md)。',
    '',
    '> 建筑覆盖：本清单包含全部 27 个建筑定义，其中四座特殊矿井与黄金殿建设工地当前 `buildable = no`。四种魔法矿物尚无下游 PM 投入，另见[四矿接入草案](four_mineral_integration_review.md)。',
    '',
    '> 科技方向：魔矿内容暂缓，不纳入本轮 PM 修改。专业接待业、组织化休闲娱乐和收窄后的“成套电器”仍只是共用科技候选；游戏与谷子科技候选也未定案。现有数值另见[当前 PM 基准价审核](current_pm_balance_20261004.md)。',
    '',
    '## 审核规则',
    '',
    '- 每个 PM 至多一个科技门槛；“无”表示开局或建筑解锁后可用。基础档和并列风格档可以无科技。',
    '- 同组升级档若有科技，后档科技必须在原版前置树中继承前档科技；时代数字相同也可有前置顺序。',
    '- 商品需求是另一层限制：例如电力、广播、电话商品可能晚于 PM 科技才有供应。这里逐项审核科技门槛，不改变投入产出。',
    '- 拟定优先使用原版科技，没有提议新科技。名称后括号中保留代码 ID 便于核对。',
    '',
    '## 建筑逐项清单',
    '',
]

def tech_text(t):
    return '无' if not t else f'{label(t)}（`{t}`，E{T[t][0]}）'

total = changed = missing_loc = vanilla_count = 0
for building, group_ids in buildings:
    lines += [f'### {label(building)}（`{building}`）', '']
    for group in group_ids:
        pm_names = groups.get(group, vanilla_groups.get(group))
        if pm_names is None:
            lines += [f'#### {label(group)}（`{group}`）：未找到 PMG 定义', '']
            continue
        lines += [f'#### {label(group)}（`{group}`）', '', '| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |', '|---:|---|---|---|---|']
        for n, pm in enumerate(pm_names, 1):
            if pm in P:
                current = P[pm][0][0] if P[pm][0] else None
                proposed = changes.get(pm, current)
                note = reason.get(pm, '保留原设定') if proposed != current else '保留原设定'
                total += 1
                changed += proposed != current
                missing_loc += pm not in loc
                proposed_text = tech_text(proposed)
                if proposed != current:
                    proposed_text = f'**{proposed_text}**'
                lines.append(f'| {n} | {label(pm)}（`{pm}`） | {tech_text(current)} | {proposed_text} | {note} |')
            else:
                techs = vanilla_pm.get(pm, [])
                current = techs[0] if techs else None
                vanilla_count += 1
                lines.append(f'| {n} | {label(pm)}（`{pm}`） | {tech_text(current)} | {tech_text(current)} | 原版 PM，模组复用 |')
        lines.append('')

lines += ['## 前置关系核验', '']
issues = []
for group, names in G:
    proposed = []
    for pm in names:
        if pm not in P:
            continue
        current = P[pm][0][0] if P[pm][0] else None
        proposed.append((pm, changes.get(pm, current)))
    for (a, ta), (b, tb) in zip(proposed, proposed[1:]):
        if ta and (not tb or ta == tb or ta not in ancestors(tb)):
            issues.append(f'{group}: {a} ({ta}) -> {b} ({tb})')
for pm, tech in changes.items():
    if tech not in T:
        issues.append(f'{pm}: unknown technology {tech}')
deferred = [x for x in issues if 'pmg_building_musical_instrument_main:' in x]
other_issues = [x for x in issues if x not in deferred]
lines += [f'- 模组定义且在 PMG 中使用的 PM：{total} 项；拟调整：{changed} 项。',
          f'- 建筑复用的原版 PM 条目：{vanilla_count} 项。',
          f'- 拟改组前置链冲突：{len(other_issues)} 项；电气化乐器保留旧版造成的既有跨分支例外：{len(deferred)} 项。']
if issues:
    lines += [''] + [f'- {x}' for x in issues]
lines += [f'- 缺少简体中文 PM 名称：{missing_loc} 项。', '']

out = Path(__file__).with_name('building_pm_tech_review.md')
out.write_text('\n'.join(lines), encoding='utf-8')
print(f'{out}: {total} PMs, {changed} changes, {len(other_issues)} new chain issues, {len(deferred)} deferred exceptions, {missing_loc} missing labels')
if other_issues:
    raise SystemExit(1)
