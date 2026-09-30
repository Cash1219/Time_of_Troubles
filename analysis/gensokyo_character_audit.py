"""Audit named Touhou assets, startup placement, and a minimal NZ border repair.

Default: refresh the read-only character report. --fix-nz transfers only the
two reused North Island province colours; it does not edit map textures.
"""
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from population_arable_prototype import spans
from west_coast_draft import ownership
from gensokyo_cultures_v1 import NAMES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/drafts'

# Explicit franchise membership avoids conflating Konno Junko / Shinomiya
# Kaguya / Akiyama Yukari with similarly named Touhou characters.
ROSTER = {
    'HAKR': [('Tohou_Reimu', '博丽灵梦')],
    'HITO': [('Tohou_Keine', '上白泽慧音'), ('Tohou_Jyoon', '依神女苑'),
             ('Usami_Sumireko', '宇佐见堇子')],
    'YKYM': [('Tohou_Aya', '射命丸文'), ('Himekaidou_Hatate', '姬海棠果'),
             ('Tohou_Nitori', '河城荷取'), ('Tohou_Minoriko', '秋穣子')],
    'MRYA': [('Yasaka_Kanako', '八坂神奈子'), ('Moriya_Suwako', '泄矢诹访子'),
             ('Kochiya_Sanae', '东风谷早苗')],
    'MFSR': [('Kirisame_Marisa', '雾雨魔理沙'), ('Alice_Margatroid', '爱丽丝·玛格特罗依德')],
    'RDMK': [('Remilia_Scarlet', '蕾米莉亚·斯卡蕾特'), ('Patchouli_Knowledge', '帕秋莉·诺蕾姬'),
             ('Izayoi_Sakuya', '十六夜咲夜'), ('Hong_Meiling', '红美铃'),
             ('Flandre_Scarlet', '芙兰朵露·斯卡蕾特')],
    'EITR': [('Houraisan_Kaguya', '蓬莱山辉夜'), ('Yagokoro_Eirin', '八意永琳'),
             ('Udongein_Inaba_Reisen', '铃仙·优昙华院·因幡'), ('Inaba_Tewi', '因幡帝'),
             ('Fujiwara_Mokou', '藤原妹红')],
    'CHRD': [('Komeiji_Satori', '古明地觉'), ('Komeiji_Koishi', '古明地恋')],
    'KYTO': [('Tohou_Suika', '伊吹萃香')],
    'BYKR': [('Saigyouji_Yuyuko', '西行寺幽幽子'), ('Konpaku_Youmu', '魂魄妖梦')],
    'HIGN': [('Shiki_Eiki_Yamaxanadu', '四季映姬·亚玛萨那度'), ('Onozuka_Komachi', '小野塚小町')],
    'KZNH': [('Kazami_Yuuka', '风见幽香')],
    'TENG': [('Hinanawi_Tenshi', '比那名居天子'), ('Nagae_Iku', '永江衣玖')],
    'YKMF': [('Tohou_Yukari', '八云紫')],
    'YSSK': [('Mystia_Lorelei', '米斯蒂娅·萝蕾拉')],
}
PLACEHOLDERS = [('JNKF', '纯狐', 'tot_gensokyo_junko_name'),
                ('HCTI', '赫卡提亚', 'tot_gensokyo_hecatia_name')]
GAPS = {
    'MYRN': ('圣白莲', '寅丸星、娜兹玲', '寺院共同体；先补领袖，再补财政与商贸角色'),
    'SHRM': ('丰聪耳神子', '物部布都、苏我屠自', '神子领导，布都与屠自补执行和军事'),
    'MKAI': ('神绮', '梦子', '魔界需要自身领袖，不应继续借用其他势力人物'),
    'UKDO': ('摩多罗隐岐奈', '丁礼田舞、尔子田里乃', '后户主神与两名助手；作为同一势力'),
    'RNGN': ('埴安神袿姬', '杖刀偶磨弓', '创造者与埴轮军团负责人；作为同一势力'),
    'MIST': ('琪露诺', '大妖精', '势力名已有，但尚无专属琪露诺角色素材'),
    'MTOU': ('绵月丰姬或稀神探女', '绵月依姬及另一位月都代表', '三人足以支撑月都；无需按角色拆国'),
}
ROLES = {
    'HAKR': '灵梦负责博丽自身事务；由八云府主持盟约',
    'HITO': '慧音负责教育与治理；女苑为商贸利益代表；堇子作为外界往来人物，适合事件出场',
    'YKYM': '文与果负责天狗政治和新闻；荷取负责河童工程；穣子负责农业。首脑可先用文代理',
    'MRYA': '神奈子领导，诹访子为内部另一支力量，早苗负责对外与信仰',
    'MFSR': '魔理沙任统治者，爱丽丝任知识分子领袖；保留一个国家',
    'RDMK': '蕾米莉亚领导并任地主领袖；咲夜治理；帕秋莉研究；美铃军事；芙兰为地主归属继承人',
    'EITR': '辉夜领导；永琳研究；铃仙执行与军事；帝代表兔族；妹红为竹林中的独立或反对人物',
    'CHRD': '觉领导，恋以特殊角色或事件参与；优先补能源相关角色',
    'KYTO': '萃香暂任鬼族代表；补勇仪后可按旧都政治调整，萃香可作为博丽往来人物',
    'BYKR': '幽幽子领导，妖梦负责军事与执行',
    'HIGN': '映姬领导与裁决，小町负责渡运',
    'KZNH': '幽香领导；暂可保留一位命名角色，其他岗位使用普通角色',
    'TENG': '天子领导，衣玖负责沟通与秩序',
    'YKMF': '紫任八云府统治者并主持共同体；建议补蓝和橙执行与地方事务',
    'YSSK': '米斯蒂娅负责餐饮与经营；不为增加角色数再拆国家',
}


def fix_nz():
    path = ROOT / 'common/history/states/00_states.txt'
    source = path.read_text(encoding='utf-8-sig')
    before = ownership(source)
    transfer = {'xC25D9D', 'x3BCC0A'}
    if all(before[p][1] == 'JNKF' for p in transfer):
        print('NZ repair already applied')
        return
    assert all(before[p] == ['STATE_NORTH_ISLAND', 'MTOU'] for p in transfer)
    sm, body, end = next(spans(source, r's:STATE_NORTH_ISLAND\s*=\s*\{'))
    edits = []
    for cm, cb, ce in spans(body, r'create_state\s*=\s*\{'):
        tag = re.search(r'country\s*=\s*c:(\w+)', cb)[1]
        pm = re.search(r'owned_provinces\s*=\s*\{([^}]+)\}', cb)
        provinces = set(re.findall(r'x[0-9A-Fa-f]{6}', pm[1]))
        if tag == 'MTOU':
            provinces -= transfer
        elif tag == 'JNKF':
            provinces |= transfer
        else:
            continue
        base = cm.end()
        edits.append((base + pm.start(1), base + pm.end(1), ' ' + ' '.join(sorted(provinces)) + ' '))
    assert len(edits) == 2
    for lo, hi, replacement in sorted(edits, reverse=True):
        body = body[:lo] + replacement + body[hi:]
    # Match ends at the actual opening brace, even when a prior comment has braces.
    updated = source[:sm.end()] + body + source[end-1:]
    after = ownership(updated)
    assert set(before) == set(after)
    changes = {p: [before[p], after[p]] for p in before if before[p] != after[p]}
    assert set(changes) == transfer
    assert all(after[p] == ['STATE_NORTH_ISLAND', 'JNKF'] for p in transfer)
    ni = next(b for _, b, _ in spans(updated, r's:STATE_NORTH_ISLAND\s*=\s*\{'))
    codes = re.findall(r'x[0-9A-Fa-f]{6}', re.sub(r'#[^\n]*', '', ni))
    assert len(codes) == len(set(codes)) == 35
    backup = ROOT / 'docs/backups' / ('nz_fragment_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True)
    shutil.copy2(path, backup / path.name)
    path.write_text(updated, encoding='utf-8-sig')
    OUT.joinpath('nz_fragment_repair.json').write_text(json.dumps({
        'backup': str(backup), 'changes': changes,
        'reason': 'Province colours reused by distant islands and North Island mainland; southern moon mainland spur was isolated.',
        'map_texture_changed': False, 'population_buildings_resources_changed': False,
        'island_pixels': {'xC25D9D': 111, 'x3BCC0A': 9, 'x1080F0_already_JNKF': 1},
        'mainland_largest_component_pixels_after': {'MTOU': 4087, 'JNKF': 3506},
        'note': 'Small naturally offshore islands remain geographically separated by sea; no disconnected mainland moon spur remains.'
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print('NZ repair: exactly 2 provinces MTOU -> JNKF; no other ownership changes')


def git_origin(key, path):
    result = subprocess.run(['git', 'log', '--reverse', '--format=%h %ad %s', '--date=short',
                             '-S', key, '--', path], cwd=str(ROOT), capture_output=True, encoding='utf-8')
    return result.stdout.splitlines()[0] if result.stdout.strip() else 'uncommitted / not found'


def validate_market():
    bloc = ROOT.joinpath('common/history/power_blocs/tot_gensokyo_power_bloc.txt').read_text(encoding='utf-8-sig')
    assert 'c:YKMF ?=' in bloc
    assert 'identity = identity_tot_gensokyo_charter' in bloc
    members = re.findall(r'\bmember\s*=\s*c:(\w+)', bloc)
    assert len(members) == len(set(members)) == 23 and set(members) == set(NAMES) - {'YKMF'}
    assert set(re.findall(r'\b(?:principle|add_principle)\s*=\s*(\w+)', bloc)) == {
        'principle_tot_gensokyo_boundary_1', 'principle_tot_gensokyo_autonomy_1',
        'principle_tot_gensokyo_gods_1'}
    identity = ROOT.joinpath('common/power_bloc_identities/tot_gensokyo_charter.txt').read_text(encoding='utf-8-sig')
    assert 'power_bloc_customs_union_bool = yes' in identity
    principles = ROOT.joinpath('common/power_bloc_principles/tot_gensokyo_charter.txt').read_text(encoding='utf-8-sig')
    assert 'power_bloc_disallow_war_bool = no' in principles
    assert 'country_join_power_bloc_member_in_plays_bool = no' in principles
    gods = next(b for _, b, _ in spans(principles, r'principle_tot_gensokyo_gods_1\s*=\s*\{'))
    assert 'member_modifier' in gods and 'interest_group_ig_devout_pol_str_mult = 0.5' in gods
    assert 'country_clergymen_pol_str_mult' not in gods
    diplomacy = ROOT.joinpath('common/history/diplomacy/tot_gensokyo_subjects.txt').read_text(encoding='utf-8-sig')
    assert 'create_diplomatic_pact' not in re.sub(r'#[^\n]*', '', diplomacy)
    for path in ['common/history/power_blocs/tot_gensokyo_power_bloc.txt',
                 'common/history/buildings/tot_gensokyo_market_ports.txt', 'common/history/states/00_states.txt']:
        source = ROOT.joinpath(path).read_text(encoding='utf-8-sig')
        clean = re.sub(r'#[^\n]*', '', source)
        assert clean.count('{') == clean.count('}')
        assert all(line == line.rstrip() for line in source.splitlines()), path
    owners = ownership(ROOT.joinpath('common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    counts = {tag: sum(v == ['STATE_NORTH_ISLAND', tag] for v in owners.values()) for tag in ['MTOU', 'JNKF']}
    assert counts == {'MTOU': 21, 'JNKF': 14}
    return dict(status='static validation passed; not game-tested', bloc_members=24,
                protectorates=0, host='YKMF', independent_members=24,
                common_market_identity='identity_tot_gensokyo_charter',
                native_customs_union_effect=True, ni_provinces=counts,
                added_ports=len(re.findall(r'building\s*=\s*"building_port"',
                    (ROOT / 'common/history/buildings/tot_gensokyo_market_ports.txt').read_text(encoding='utf-8-sig'))),
                principle_count=3, devout_interest_group_political_strength_bonus=0.5,
                join_restriction='Explicit whitelist of 24 country tags; no culture check')


def audit():
    paths = {
        'trait': 'common/character_traits/tot_characters.txt',
        'portrait': 'gfx/portraits/portrait_modifiers/tot_portrait.txt',
        'gene': 'common/genes/tot_genes_special_accessories_misc.txt',
        'accessory': 'gfx/portraits/accessories/tot_props.txt',
        'entity': 'gfx/models/props/anime/tot_prophet_anime.asset',
        'recognition_trigger': 'common/scripted_triggers/tot_character.txt',
    }
    texts = {k: ROOT.joinpath(v).read_text(encoding='utf-8-sig') for k, v in paths.items()}
    histories = {str(p.relative_to(ROOT)): re.sub(r'#[^\n]*', '', p.read_text(encoding='utf-8-sig'))
                 for p in ROOT.joinpath('common/history/characters').glob('*.txt')}
    characters = []
    for tag, group in ROSTER.items():
        for stem, name in group:
            trait = 'tot_' + stem + '_trait'
            prop = 'tot_prophet_' + stem
            checks = {k: (trait if k in {'trait', 'portrait', 'recognition_trigger'} else prop) in t
                      for k, t in texts.items()}
            texture = ROOT / 'gfx/models/props/anime' / (prop + '_diffuse.dds')
            checks['texture'] = texture.exists()
            startup = [p for p, t in histories.items() if re.search(r'\b' + trait + r'\b', t)]
            assert len(startup) == 1
            matching = [b for _, b, _ in spans(histories[startup[0]], r'create_character\s*=\s*\{')
                        if re.search(r'\b' + trait + r'\b', b)]
            assert len(matching) == 1
            group_trait = 'tot_group_sheet_019_trait' in matching[0]
            assert group_trait
            characters.append(dict(name=name, trait=trait, suggested_country=tag,
                assets=checks, history_files=startup, recent=stem=='Mystia_Lorelei',
                gensokyo_group_trait=group_trait,
                origin=git_origin(trait, paths['trait'])))
    assert len(characters) == 35
    assert all(all(c['assets'].values()) for c in characters), 'Incomplete portrait/trait chain'
    for tag, name, key in PLACEHOLDERS:
        startup = [p for p, t in histories.items() if key in t]
        assert len(startup) == 1
        matching = [b for _, b, _ in spans(histories[startup[0]], r'create_character\s*=\s*\{') if key in b]
        assert len(matching) == 1 and 'tot_group_sheet_019_trait' in matching[0]
        characters.append(dict(name=name, suggested_country=tag, assets={}, history_files=startup,
            recent=True, placeholder=True, gensokyo_group_trait=True, origin=git_origin(key, startup[0])))
    total = dict(asset_ready=35, name_only_placeholders=2, unique_named_characters=37,
                 dedicated_startup_characters=sum(bool(c['history_files']) for c in characters),
                 countries=24, countries_with_suggested_existing_assets=len(ROSTER),
                 countries_with_placeholder_leaders=2, countries_without_core_character=len(GAPS))
    total['characters_with_gensokyo_group_trait'] = sum(c['gensokyo_group_trait'] for c in characters)
    assert len(ROSTER) + len(PLACEHOLDERS) + len(GAPS) == 24
    OUT.joinpath('gensokyo_market_character_validation.json').write_text(json.dumps(
        dict(market=validate_market(), characters=total), ensure_ascii=False, indent=2), encoding='utf-8')
    OUT.joinpath('gensokyo_characters_current.json').write_text(json.dumps(
        dict(counts=total, characters=characters, proposed_gaps=GAPS, source_files=paths),
        ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 幻想乡角色实装与后续建议（2026-09-29）', '',
        '统计口径：东方正作及旧作的命名角色；专属特质、立绘配件、纹理、基因和识别触发器均核查。',
        '已恢复 35 名既有角色的开局历史；除用户指定的芙兰地主归属继承人外，政治归属按归档历史保留，后续补充角色仍为建议。', '',
        '**24 国；35 名有完整专属素材；另有纯狐、赫卡提亚两个占位角色；合计 37 名。**',
        '当前开局创建 37 人：35 名恢复角色，加上既有的纯狐与赫卡提亚两个占位角色。',
        '37 人均持有“幻想乡”通用特质；本轮补齐原先遗漏的 10 人。两名占位角色仍没有专属立绘和个人特质。',
        '普通自动生成角色与界面立绘不计入东方命名角色。', '',
        '## 已有角色安排', '', '| 国家 | 已有角色 | 当前安排及后续建议 |', '|---|---|---|']
    for tag, group in ROSTER.items():
        names = '、'.join(n + ('【近期新增完整素材】' if s=='Mystia_Lorelei' else '') for s, n in group)
        lines.append('| {} | {} | {} |'.format(NAMES[tag], names, ROLES[tag]))
    for tag, name, _ in PLACEHOLDERS:
        lines.append('| {} | {}【近期新增占位】 | 已任开局领袖；暂无专属立绘与角色特质 |'.format(NAMES[tag], name))
    lines += ['', '依神女苑归人里、堇子作为往来人物、萃香暂作旧都代表，都是玩法分配建议，不是声称她们在正作中担任这些国家职务。',
        '不把妹红、爱丽丝或河童单独拆国；主要人物为领导与核心班底，少数人物允许事件出场。', '',
        '## 下一批先补什么', '', '| 优先补领袖的国家 | 第一位 | 第二批班底 | 目的 |', '|---|---|---|---|']
    for tag, (leader, team, reason) in GAPS.items():
        lines.append('| {} | {} | {} | {} |'.format(NAMES[tag], leader, team, reason))
    lines += ['',
        '第一批补七个国家的核心代表，解决有国家但没领袖素材的问题。月都先选一位代表，其余两位稍后补。',
        '同时补齐纯狐、赫卡提亚的专属立绘和特质，不能继续把占位角色当作完成。',
        '第二优先级：灵乌路空、火焰猫燐（能源与地灵殿执行）；星熊勇仪（旧都）；八云蓝（八云府）；克劳恩皮丝（赫卡提亚与纯狐剧情联系）。',
        '第三优先级：稗田阿求、本居小铃、犬走椛、秋静叶、橙、大妖精，以及寺院和神灵庙的其余班底。',
        '已有红魔馆五人、永远亭五人、魔法森林两人，足以先做势力内容；不再优先给这些国家堆角色。', '',
        '## 最近新增的角色', '',
        '- 米斯蒂娅：`eb57dc9`（2026-09-25）新增完整特质、立绘与纹理；本轮恢复开局创建。',
        '- 纯狐、赫卡提亚：`d489e8a`（2026-09-29）新增命名占位领袖；通用特质和默认立绘。',
        '- 其他 34 人属于既有素材，本轮恢复开局创建，不属于新制作角色。', '',
        '## 共同市场与月都小岛', '',
        '八云府主持幻想乡共同体，八云紫任主持国统治者。自定义身份提供 `power_bloc_customs_union_bool = yes`。',
        '幻想乡由 24 个独立成员组成；取消原先的受保护国关系。幻想乡共同体身份保障共同市场，乡内贸易、势力自治、众神眷恋为开局原则，允许内部战争且不强制跟战。众神眷恋为所有成员（含主持国）提供 +50% 宗教利益集团政治力量。本地价格、港口、运输和基础设施仍按原版处理，电力仍只能本州使用。',
        '加入资格是这 24 个国家标签的固定名单，不按文化、宗教、人口或角色特质判断；其他原版加入条件仍适用。',
        '天界原本没有开局港口，本轮在斐济、瓦努阿图各补一级基础港口；运输效率仍取决于雇佣、投入品与市场运行。',
        '这项历史改动需要重新开局；已有存档不会自动重放开局历史。静态检查不能替代游戏内市场与原则检查。',
        '小岛不是刻意安排的月都据点：`xC25D9D`、`x3BCC0A`同时出现在北岛本土和地图另一端的离岸岛屿；`x1080F0`还有一个像素，原已属纯狐。',
        '前两个省份改归纯狐，远岛归属统一，并消除北岛南端被纯狐隔开的月都本土色块。北岛现为月都 21 省份、纯狐 14 省份。',
        '没有修改底图；自然离岸岛屿仍需海上连接，不能把它们描述成陆地连续。人口、建筑与资源未因这两个省份转让而重新分配。', '',
        '## 逐人核查', '', '| 角色 | 特质键 | 专属素材 | 开局创建 | 首次加入该特质的提交 |', '|---|---|---|---|---|']
    for c in characters:
        lines.append('| {}{} | {} | {} | {} | {} |'.format(c['name'], '【近期新增】' if c['recent'] else '',
            c.get('trait', '无'), '占位' if c.get('placeholder') else '完整',
            '、'.join(c['history_files']) or '未创建', c['origin']))
    lines += ['', '## 设定参考', '',
        '后户主神与两名助手可见 [东方天空璋角色资料](https://en.touhouwiki.net/wiki/Hidden_Star_in_Four_Seasons/Characters)。',
        '灵长园的袿姬与磨弓可见 [东方鬼形兽角色资料](https://en.touhouwiki.net/wiki/Wily_Beast_and_Weakest_Creature/Characters)。',
        '月都人物可见 [东方绀珠传角色资料](https://en.touhouwiki.net/wiki/Legacy_of_Lunatic_Kingdom/Characters)。',
        '这些页面转载或整理原作角色资料；本报告的职业、政治职务与补充顺序属于模组设计建议。', '']
    OUT.joinpath('gensokyo_characters_current.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(total, ensure_ascii=False))


if __name__ == '__main__':
    if '--fix-nz' in sys.argv:
        fix_nz()
    audit()
