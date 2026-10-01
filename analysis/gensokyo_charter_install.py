"""Install the initial independent Gensokyo charter and restore archived characters.

--apply backs up existing targets once. Default checks the installed snapshot.
Political affiliations are restored from the last archived history, except
Flandre's explicitly requested landowner/heir assignment. --update installs
revision 2: that assignment, complete group traits, and the gods principle.
"""
import collections
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from population_arable_prototype import spans
from gensokyo_character_audit import ROSTER
from gensokyo_cultures_v1 import NAMES

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/Steam/steamapps/common/Victoria 3/game')
REPORT = ROOT / 'docs/drafts/gensokyo_charter_installed.json'
CHAR_PATH = 'common/history/characters/tot_gensokyo_characters.txt'
GROUP_TRAIT = 'tot_group_sheet_019_trait'
NZ_PATH = 'common/history/characters/tot_gensokyo_nz.txt'
LEADERS = {
    'HAKR': 'Tohou_Reimu', 'HITO': 'Tohou_Keine', 'YKYM': 'Tohou_Aya',
    'MRYA': 'Yasaka_Kanako', 'MFSR': 'Kirisame_Marisa', 'RDMK': 'Remilia_Scarlet',
    'EITR': 'Houraisan_Kaguya', 'CHRD': 'Komeiji_Satori', 'KYTO': 'Tohou_Suika',
    'BYKR': 'Saigyouji_Yuyuko', 'HIGN': 'Shiki_Eiki_Yamaxanadu',
    'KZNH': 'Kazami_Yuuka', 'TENG': 'Hinanawi_Tenshi', 'YKMF': 'Tohou_Yukari',
    'YSSK': 'Mystia_Lorelei',
}
CULTURES = {
    'Tohou_Reimu': 'human', 'Tohou_Keine': 'youkai', 'Tohou_Jyoon': 'youkai',
    'Usami_Sumireko': 'human', 'Tohou_Aya': 'tengu', 'Himekaidou_Hatate': 'tengu',
    'Tohou_Nitori': 'kappa', 'Tohou_Minoriko': 'youkai', 'Yasaka_Kanako': 'youkai',
    'Moriya_Suwako': 'youkai', 'Kochiya_Sanae': 'human', 'Kirisame_Marisa': 'human',
    'Alice_Margatroid': 'youkai', 'Remilia_Scarlet': 'youkai',
    'Patchouli_Knowledge': 'youkai', 'Izayoi_Sakuya': 'human', 'Hong_Meiling': 'youkai',
    'Flandre_Scarlet': 'youkai', 'Houraisan_Kaguya': 'lunarian',
    'Yagokoro_Eirin': 'lunarian', 'Udongein_Inaba_Reisen': 'rabbit',
    'Inaba_Tewi': 'rabbit', 'Fujiwara_Mokou': 'human', 'Komeiji_Satori': 'youkai',
    'Komeiji_Koishi': 'youkai', 'Tohou_Suika': 'oni', 'Saigyouji_Yuyuko': 'spirit',
    'Konpaku_Youmu': 'spirit', 'Shiki_Eiki_Yamaxanadu': 'youkai',
    'Onozuka_Komachi': 'youkai', 'Kazami_Yuuka': 'youkai', 'Hinanawi_Tenshi': 'celestial',
    'Nagae_Iku': 'youkai', 'Tohou_Yukari': 'youkai', 'Mystia_Lorelei': 'youkai',
}
IG_NAMES = dict(zip(['ig_landowners', 'ig_devout', 'ig_intelligentsia',
    'ig_industrialists', 'ig_armed_forces', 'ig_petty_bourgeoisie',
    'ig_rural_folk', 'ig_trade_unions'],
    ['地主', '宗教势力', '知识分子', '实业家', '军方', '小市民', '乡村民众', '工会']))


def clean(text):
    return re.sub(r'#[^\n]*', '', text)


def scalar(body, key):
    m = re.search(r'\b' + key + r'\s*=\s*("[^"\n]*"|[\w:.]+)', clean(body))
    return m[1] if m else None


def archived_characters():
    wanted = {'tot_' + stem + '_trait': (tag, stem, name)
              for tag, entries in ROSTER.items() for stem, name in entries}
    found = {}
    for filename in ['jap - japan.txt', 'jap - touhou_2.txt',
                     'ten - celestial realm.txt', 'yss - night sparrow diner.txt']:
        source = subprocess.check_output(['git', 'show',
            'f1c20fd^:common/history/characters/' + filename], cwd=str(ROOT)).decode('utf-8-sig')
        for _, body, _ in spans(source, r'create_character\s*=\s*\{'):
            matching = set(re.findall(r'\btot_\w+_trait\b', clean(body))) & set(wanted)
            if not matching:
                continue
            assert len(matching) == 1
            trait = matching.pop()
            assert trait not in found, ('duplicate archived character', trait)
            tag, stem, name = wanted[trait]
            traits = re.search(r'\btraits\s*=\s*\{([^}]+)\}', clean(body))[1].split()
            archived_traits = list(traits)
            if GROUP_TRAIT not in traits:
                traits.append(GROUP_TRAIT)
            ideology = scalar(body, 'ideology')
            # A version-renamed key: retain the old sovereignist position.
            resolved = 'ideology_sovereignist_leader' if ideology == 'ideology_sovereigntist' else ideology
            found[trait] = dict(tag=tag, stem=stem, name=name, source=filename,
                first_name=scalar(body, 'first_name'), last_name=scalar(body, 'last_name'),
                birth_date=scalar(body, 'birth_date'),
                archived_interest_group=scalar(body, 'interest_group'),
                interest_group='ig_landowners' if stem == 'Flandre_Scarlet' else scalar(body, 'interest_group'),
                archived_ideology=ideology, ideology=resolved, archived_traits=archived_traits, traits=traits,
                is_general=scalar(body, 'is_general') == 'yes',
                culture='tot_gensokyo_' + CULTURES[stem],
                religion=scalar(body, 'religion') or 'rel:shinto',
                ruler=LEADERS[tag] == stem, ig_leader=stem != 'Flandre_Scarlet',
                heir=stem == 'Flandre_Scarlet')
    assert set(found) == set(wanted), set(wanted) - set(found)
    return [found['tot_' + stem + '_trait'] for tag, entries in ROSTER.items() for stem, _ in entries]


def character_text(chars):
    lines = ['# Restored archived Touhou characters; ideologies are unchanged.',
             '# Calendar ages are scenario placeholders, not canon birth dates.',
             '# Meiling leads the armed forces; Flandre is the landowner-affiliated heir.',
             'CHARACTERS = {']
    for tag in ROSTER:
        lines.append('\tc:{} ?= {{'.format(tag))
        for c in [c for c in chars if c['tag'] == tag]:
            lines += ['\t\t# ' + c['name'], '\t\tcreate_character = {',
                '\t\t\thistorical = yes', '\t\t\tfirst_name = ' + c['first_name'],
                '\t\t\tlast_name = ' + c['last_name'], '\t\t\tbirth_date = ' + c['birth_date'],
                '\t\t\tfemale = yes']
            if c['ruler']:
                lines.append('\t\t\truler = yes')
            if c['heir']:
                lines.append('\t\t\their = yes')
            if c['ig_leader']:
                lines.append('\t\t\tig_leader = yes')
            if c['is_general']:
                lines.append('\t\t\tis_general = yes')
            if c['ideology']:
                lines.append('\t\t\tideology = ' + c['ideology'])
            lines += ['\t\t\tinterest_group = ' + c['interest_group'],
                '\t\t\tculture = cu:' + c['culture'], '\t\t\treligion = ' + c['religion'],
                '\t\t\ttraits = { ' + ' '.join(c['traits']) + ' }', '\t\t}']
        lines.append('\t}')
    lines += ['}', '']
    return '\n'.join(lines)


def files(chars):
    texts = {CHAR_PATH: character_text(chars)}
    # Fixed existing placeholder source, with the previously installed culture
    # conversion retained. Do not make snapshot validation trust current files.
    nz = subprocess.check_output(['git', 'show', 'd489e8a:' + NZ_PATH], cwd=str(ROOT)).decode('utf-8-sig')
    nz = nz.replace('\t\t\tculture = cu:japanese',
        '\t\t\t# Broad community identity; divine species is not represented by this culture.\n'
        '\t\t\tculture = cu:tot_gensokyo_youkai')
    nz = nz.replace('traits = { persistent }', 'traits = { persistent ' + GROUP_TRAIT + ' }')
    nz = nz.replace('traits = { charismatic }', 'traits = { charismatic ' + GROUP_TRAIT + ' }')
    texts[NZ_PATH] = nz
    texts['common/history/diplomacy/tot_gensokyo_subjects.txt'] = (
        '# Independent charter members: no initial Gensokyo subject pacts.\nDIPLOMACY = {\n}\n')
    lines = ['# Yakumo hosts the independent Gensokyo charter; Yukari is its national ruler.',
        'POWER_BLOCS = {', '\tc:YKMF ?= {', '\t\tcreate_power_bloc = {',
        '\t\t\tname = GENSOKYO_BARRIER_NETWORK', '\t\t\tmap_color = { 126 88 156 }',
        '\t\t\tfounding_date = 1836.1.1', '\t\t\tidentity = identity_tot_gensokyo_charter',
        '\t\t\tprinciple = principle_tot_gensokyo_boundary_1']
    lines += ['\t\t\tmember = c:' + tag for tag in NAMES if tag != 'YKMF']
    lines += ['\t\t}', '\t\tpower_bloc = {',
        '\t\t\tadd_principle = principle_tot_gensokyo_autonomy_1',
        '\t\t\tadd_principle = principle_tot_gensokyo_gods_1',
        '\t\t\tadd_cohesion_number = 100', '\t\t}', '\t}', '}', '']
    texts['common/history/power_blocs/tot_gensokyo_power_bloc.txt'] = '\n'.join(lines)
    texts['common/scripted_triggers/tot_gensokyo_charter.txt'] = (
        'tot_gensokyo_country_trigger = {\n\tOR = {\n' +
        ''.join('\t\tc:{} ?= this\n'.format(tag) for tag in NAMES) + '\t}\n}\n')
    texts['common/scripted_rules/zzzz_tot_gensokyo_charter.txt'] = '''# Keep native qualification outside the charter; Yakumo is the initial host.
REPLACE:can_lead_power_bloc = {
    OR = {
        country_rank >= rank_value:major_power
        c:YKMF ?= this
    }
}
# A small charter host must not make the community a weak rank-only bloc.
REPLACE:is_weak_power_bloc = {
    NOT = { has_identity = identity:identity_tot_gensokyo_charter }
    power_bloc_is_weak = yes
}
'''
    texts['common/power_bloc_identities/tot_gensokyo_charter.txt'] = '''identity_tot_gensokyo_charter = {
    icon = "gfx/interface/icons/central_identity_pillars_icons/trade_league.dds"
    background = "gfx/interface/power_blocs/backgrounds/pb_background_generic.dds"
    power_bloc_modifier = { power_bloc_customs_union_bool = yes }
    # Offset the native 500 influence cost of hosting; no prestige or output bonus.
    leader_modifier = { country_influence_add = 500 }
    non_leader_modifier = {}
    can_join = { tot_gensokyo_country_trigger = yes }
    can_leave = {
        custom_tooltip = {
            text = tot_gensokyo_exit_years_tt
            tenure_in_current_power_bloc_years >= 5
        }
        custom_tooltip = {
            text = tot_gensokyo_exit_peace_tt
            is_at_war = no
        }
        custom_tooltip = {
            text = tot_gensokyo_exit_cohesion_tt
            power_bloc = { current_cohesion_number < 20 }
        }
        custom_tooltip = {
            text = tot_gensokyo_exit_leverage_tt
            power_bloc = { leverage_advantage = { target = root value <= 30 } }
        }
    }
    possible = { c:YKMF ?= this }
    # Fixed founding principles for this first test; voting is not implemented.
    mandate_progress = { value = 0 }
    # Shared-market shortages, not rivalry with the host, erode basic cohesion.
    cohesion = {
        value = 70
        add = {
            value = scope:power_bloc.power_bloc_leader.market.market_number_goods_shortages
            multiply = -2
            desc = tot_gensokyo_cohesion_shortages
        }
        min = 0
        max = 100
    }
    ai_weight = { value = 0 }
}
'''
    texts['common/power_bloc_principles/tot_gensokyo_charter.txt'] = '''principle_tot_gensokyo_boundary_1 = {
    icon = "gfx/interface/icons/principles_icons/market_unification.dds"
    background = "gfx/interface/icons/principles_icons/principle_tier_1.dds"
    power_bloc_modifier = { power_bloc_invite_acceptance_add = 300 }
    member_modifier = { country_tech_spread_mult = 0.1 }
    ai_weight = { value = 0 }
}
principle_tot_gensokyo_autonomy_1 = {
    icon = "gfx/interface/icons/principles_icons/internal_trade.dds"
    background = "gfx/interface/icons/principles_icons/principle_tier_1.dds"
    power_bloc_modifier = { power_bloc_disallow_war_bool = no }
    member_modifier = {
        state_infrastructure_mult = 0.1
        country_join_power_bloc_member_in_defensive_plays_bool = no
        country_join_power_bloc_member_in_plays_bool = no
    }
    ai_weight = { value = 0 }
}
principle_tot_gensokyo_gods_1 = {
    icon = "gfx/interface/icons/principles_icons/sacred_civics.dds"
    background = "gfx/interface/icons/principles_icons/principle_tier_1.dds"
    # In the running version member_modifier affects all participants;
    # non_leader_modifier is the field restricted to countries other than the host.
    member_modifier = { interest_group_ig_devout_pol_str_mult = 0.5 }
    ai_weight = { value = 0 }
}
'''
    texts['common/power_bloc_principle_groups/tot_gensokyo_charter.txt'] = '''principle_group_tot_gensokyo_boundary = {
    primary_for_identity = identity_tot_gensokyo_charter
    unlocking_identity = identity_tot_gensokyo_charter
    levels = { principle_tot_gensokyo_boundary_1 }
}
principle_group_tot_gensokyo_autonomy = {
    unlocking_identity = identity_tot_gensokyo_charter
    levels = { principle_tot_gensokyo_autonomy_1 }
}
principle_group_tot_gensokyo_gods = {
    unlocking_identity = identity_tot_gensokyo_charter
    levels = { principle_tot_gensokyo_gods_1 }
}
'''
    # Preserve every native group's fields; only block them for this identity.
    native = (GAME / 'common/power_bloc_principle_groups/00_power_bloc_principle_groups.txt').read_text(encoding='utf-8-sig')
    blocks = ['# Native principles remain unchanged for every other identity.']
    for m, body, _ in spans(native, r'(principle_group_\w+)\s*=\s*\{'):
        blocks += ['REPLACE:' + m[1] + ' = {' + body.rstrip() +
            '\n\tblocking_identity = identity_tot_gensokyo_charter\n}', '']
    texts['common/power_bloc_principle_groups/zzzz_tot_gensokyo_native_exclusions.txt'] = '\n'.join(blocks)
    zh = {
        'identity_tot_gensokyo_charter': '幻想乡共同体',
        'identity_tot_gensokyo_charter_desc': '各势力通过幻想乡共同体共享市场与交流渠道，并保留独立政权。八云府主持共同事务；成员可按正常外交规则合作、结盟或交战，退出须满足共同体条件。',
        'principle_group_tot_gensokyo_boundary': '乡内贸易',
        'principle_group_tot_gensokyo_boundary_desc': '乡内贸易促进各势力分工与知识交流。共同市场由幻想乡共同体身份保障，本原则为所有成员提供10%技术传播加成，并使加入接受度增加300。加入资格与退出条件仍由共同体身份规定。',
        'principle_tot_gensokyo_boundary_1': '乡内贸易',
        'principle_tot_gensokyo_boundary_1_desc': '$principle_group_tot_gensokyo_boundary_desc$',
        'principle_group_tot_gensokyo_autonomy': '势力自治',
        'principle_group_tot_gensokyo_autonomy_desc': '成员独立自主，可按正常外交规则相互交战、合作或保持中立，不强制成员跟随战争。所有成员国基础设施增加10%。',
        'principle_tot_gensokyo_autonomy_1': '势力自治',
        'principle_tot_gensokyo_autonomy_1_desc': '$principle_group_tot_gensokyo_autonomy_desc$',
        'principle_group_tot_gensokyo_gods': '众神眷恋',
        'principle_group_tot_gensokyo_gods_desc': '众神的眷恋增强宗教利益集团在各势力中的政治影响。所有成员国，包括主持国，宗教利益集团政治力量增加50%。',
        'principle_tot_gensokyo_gods_1': '众神眷恋',
        'principle_tot_gensokyo_gods_1_desc': '$principle_group_tot_gensokyo_gods_desc$',
        'tot_gensokyo_exit_years_tt': '加入共同体至少五年',
        'tot_gensokyo_exit_peace_tt': '当前没有参与战争',
        'tot_gensokyo_exit_cohesion_tt': '共同体当前凝聚力低于20',
        'tot_gensokyo_exit_leverage_tt': '共同体对本国的优势不高于30',
        'tot_gensokyo_cohesion_shortages': '共同市场商品短缺',
    }
    en = dict(zip(zh, ['Gensokyo Community',
        'Independent governments share a market and channels of exchange. Yakumo hosts common affairs; members may cooperate, ally or fight under normal diplomatic rules. Departure is subject to community conditions.',
        'Internal Trade', 'Internal trade encourages specialization and the exchange of knowledge. The community identity guarantees the common market; this principle grants all members +10% Technology Spread and adds 300 invitation acceptance. The identity governs admission and departure.',
        'Internal Trade', '$principle_group_tot_gensokyo_boundary_desc$',
        'Member Autonomy', 'Independent members may fight, cooperate or remain neutral under normal diplomatic rules, without forced war participation. All participants gain +10% Infrastructure.',
        'Member Autonomy', '$principle_group_tot_gensokyo_autonomy_desc$',
        'Beloved by the Gods', 'Divine favor strengthens the Devout Interest Group. All participant countries, including the host, gain +50% Devout Interest Group Political Strength.',
        'Beloved by the Gods', '$principle_group_tot_gensokyo_gods_desc$',
        'Membership has lasted at least five years', 'The country is not at war',
        'Current bloc cohesion is below 20', 'Bloc leverage advantage over this country is at most 30',
        'Common-market goods shortages']))
    en['GENSOKYO_BARRIER_NETWORK'] = 'Gensokyo'
    for lang, loc, folder in [('simp_chinese', zh, 'replace/simp_chinese/common/diplomacy'),
                               ('english', en, 'english')]:
        texts['localization/' + folder + '/tot_gensokyo_charter_l_' + lang + '.yml'] = (
            'l_' + lang + ':\n' + ''.join(' {}: "{}"\n'.format(k, v) for k, v in loc.items()))
    return texts


def apply():
    chars = archived_characters()
    texts = files(chars)
    backup = ROOT / 'docs/backups' / ('gensokyo_charter_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    existing = []
    for rel, source in texts.items():
        path = ROOT / rel
        if path.exists():
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            existing.append(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding='utf-8-sig' if rel.endswith('.yml') else 'utf-8')
    backup.mkdir(parents=True, exist_ok=True)
    (backup / 'manifest.json').write_text(json.dumps(dict(existing=existing,
        created=sorted(set(texts)-set(existing))), ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(dict(characters=chars, backup=str(backup),
        runtime_files=sorted(texts), member_tags=sorted(NAMES), host='YKMF',
        revision=5,
        testing='Static validation only; a fresh in-game start is required.'),
        ensure_ascii=False, indent=2), encoding='utf-8')
    print('Installed 35 archived characters and the independent Yakumo-hosted charter.')


def check():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    chars = archived_characters()
    assert chars == report['characters']
    # Later Spell Card Rules work extends the charter principle and its names.
    extended = {
        'common/power_bloc_identities/tot_gensokyo_charter.txt',
        'common/power_bloc_principles/tot_gensokyo_charter.txt',
        'localization/english/tot_gensokyo_charter_l_english.yml',
        'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml',
    }
    for rel, expected in files(chars).items():
        source = (ROOT / rel).read_text(encoding='utf-8-sig')
        if rel not in extended:
            assert source == expected, ('snapshot differs', rel)
        assert clean(source).count('{') == clean(source).count('}'), rel
    records = list(spans((ROOT / CHAR_PATH).read_text(encoding='utf-8'), r'create_character\s*=\s*\{'))
    assert len(records) == 35
    assert len({(scalar(b, 'first_name'), scalar(b, 'last_name')) for _, b, _ in records}) == 35
    all_records = records + list(spans((ROOT / NZ_PATH).read_text(encoding='utf-8-sig'), r'create_character\s*=\s*\{'))
    assert len(all_records) == 37
    for _, body, _ in all_records:
        traits = re.search(r'\btraits\s*=\s*\{([^}]+)\}', clean(body))[1].split()
        assert traits.count(GROUP_TRAIT) == 1
    flandre = next(b for _, b, _ in records if 'tot_Flandre_Scarlet_trait' in b)
    assert scalar(flandre, 'heir') == 'yes' and scalar(flandre, 'interest_group') == 'ig_landowners'
    assert scalar(flandre, 'ig_leader') is None and scalar(flandre, 'ruler') is None
    igs = collections.Counter((c['tag'], c['interest_group']) for c in chars if c['ig_leader'])
    assert max(igs.values()) == 1, igs
    counts = collections.Counter(c['tag'] for c in chars if c['ruler'])
    assert set(counts) == set(ROSTER) and max(counts.values()) == 1
    keys = collections.defaultdict(set)
    for root in [GAME, ROOT]:
        for folder, pattern in [('ideologies', r'(ideology_\w+)'),
                               ('character_traits', r'(\w+)'), ('cultures', r'(\w+)')]:
            for path in (root / 'common' / folder).glob('*.txt'):
                text = clean(path.read_text(encoding='utf-8-sig'))
                keys[folder].update(re.findall(r'^\s*(?:REPLACE:)?'+pattern+r'\s*=\s*\{', text, re.M))
    for c in chars:
        assert not c['ideology'] or c['ideology'] in keys['ideologies'], c
        assert c['culture'] in keys['cultures'], c
        assert set(c['traits']) <= keys['character_traits'], set(c['traits'])-keys['character_traits']
        assert c['interest_group'] in IG_NAMES, c
    for rel in report['runtime_files']:
        text = (ROOT / rel).read_text(encoding='utf-8-sig')
        for asset in re.findall(r'(?:icon|background)\s*=\s*"([^"]+)"', text):
            assert (ROOT / asset).exists() or (GAME / asset).exists(), asset
    pb = (ROOT / 'common/history/power_blocs/tot_gensokyo_power_bloc.txt').read_text(encoding='utf-8')
    members = re.findall(r'\bmember\s*=\s*c:(\w+)', clean(pb))
    assert len(members) == 23 and set(members) == set(NAMES)-{'YKMF'}
    assert 'create_diplomatic_pact' not in clean((ROOT / 'common/history/diplomacy/tot_gensokyo_subjects.txt').read_text(encoding='utf-8'))
    assert 'identity_sovereign_empire' not in pb
    assert set(re.findall(r'\b(?:principle|add_principle)\s*=\s*(\w+)', pb)) == {
        'principle_tot_gensokyo_boundary_1', 'principle_tot_gensokyo_autonomy_1', 'principle_tot_gensokyo_gods_1'}
    gods_source = (ROOT / 'common/power_bloc_principles/tot_gensokyo_charter.txt').read_text(encoding='utf-8')
    gods = next(b for _, b, _ in spans(gods_source, r'principle_tot_gensokyo_gods_1\s*=\s*\{'))
    participant = next(b for _, b, _ in spans(gods, r'member_modifier\s*=\s*\{'))
    assert scalar(participant, 'interest_group_ig_devout_pol_str_mult') == '0.5'
    assert 'country_clergymen_pol_str_mult' not in gods
    assert 'interest_group_ig_devout_pol_str_mult' in (GAME / 'common/modifier_type_definitions/00_modifier_types.txt').read_text(encoding='utf-8-sig')
    assert 'participant_modifier' not in gods_source
    groups = (ROOT / 'common/power_bloc_principle_groups/tot_gensokyo_charter.txt').read_text(encoding='utf-8')
    assert groups.count('primary_for_identity') == 1
    assert groups.count('unlocking_identity') == 3
    assert 'country_tech_spread_mult = 0.1' in gods_source
    assert 'state_infrastructure_mult = 0.1' in gods_source
    assert 'country_can_impose_same_lawgroup_army_model_in_power_bloc_bool = yes' in gods_source
    identity = (ROOT / 'common/power_bloc_identities/tot_gensokyo_charter.txt').read_text(encoding='utf-8')
    assert 'has_law = law_type:law_tot_danmaku_warfare' in identity
    zh = (ROOT / 'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml').read_text(encoding='utf-8-sig')
    en = (ROOT / 'localization/english/tot_gensokyo_charter_l_english.yml').read_text(encoding='utf-8-sig')
    assert 'principle_group_tot_gensokyo_autonomy: "符卡规则"' in zh
    assert 'principle_group_tot_gensokyo_autonomy: "Spell Card Rules"' in en
    modifier_definitions = '\n'.join(p.read_text(encoding='utf-8-sig')
        for p in (GAME / 'common/modifier_type_definitions').glob('*.txt'))
    for _, body, _ in spans(gods_source, r'(?:member|power_bloc|leader)_modifier\s*=\s*\{'):
        for key in re.findall(r'\b(\w+)\s*=', clean(body)):
            assert re.search(r'\b' + key + r'\s*=\s*\{', modifier_definitions), key
    print('PASS: 37 Gensokyo group traits, Flandre landowner heir, 34 unique IG leaders, 24 independent members, 3 principles; references and icons valid.')


def update():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert report.get('revision', 1) == 1, 'Revision 2 already installed; run without --update to check.'
    chars = archived_characters()
    texts = files(chars)
    changed = [rel for rel, expected in texts.items()
        if not (ROOT / rel).exists() or (ROOT / rel).read_text(encoding='utf-8-sig') != expected]
    assert set(changed) == {CHAR_PATH, NZ_PATH, 'common/history/power_blocs/tot_gensokyo_power_bloc.txt',
        'common/power_bloc_principles/tot_gensokyo_charter.txt',
        'common/power_bloc_principle_groups/tot_gensokyo_charter.txt',
        'localization/english/tot_gensokyo_charter_l_english.yml',
        'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml'}, changed
    backup = ROOT / 'docs/backups' / ('gensokyo_charter_revision_2_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for rel in changed + ['docs/drafts/gensokyo_charter_installed.json']:
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    missing = [c['name'] for c in chars if GROUP_TRAIT not in c['archived_traits']]
    for rel in changed:
        (ROOT / rel).write_text(texts[rel], encoding='utf-8-sig' if rel.endswith('.yml') else 'utf-8')
    report.update(characters=chars, runtime_files=sorted(texts), revision=2,
        revision_2_backup=str(backup), group_traits_added=missing + ['纯狐', '赫卡提亚'],
        principles=['principle_tot_gensokyo_boundary_1', 'principle_tot_gensokyo_autonomy_1', 'principle_tot_gensokyo_gods_1'])
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Revision 2 installed; added group traits to {} characters.'.format(len(missing) + 2))


def update_principles():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert report['revision'] == 2, 'Expected revision 2; otherwise run without flags to check.'
    texts = files(archived_characters())
    changed = [rel for rel, expected in texts.items()
        if (ROOT / rel).read_text(encoding='utf-8-sig') != expected]
    assert set(changed) == {'common/history/power_blocs/tot_gensokyo_power_bloc.txt',
        'common/power_bloc_principles/tot_gensokyo_charter.txt',
        'common/power_bloc_principle_groups/tot_gensokyo_charter.txt',
        'localization/english/tot_gensokyo_charter_l_english.yml',
        'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml'}, changed
    backup = ROOT / 'docs/backups' / ('gensokyo_charter_revision_3_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for rel in changed + ['docs/drafts/gensokyo_charter_installed.json']:
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    for rel in changed:
        (ROOT / rel).write_text(texts[rel], encoding='utf-8-sig' if rel.endswith('.yml') else 'utf-8')
    report.update(revision=3, revision_3_backup=str(backup),
        parser_fix='participant_modifier rejected by live parser; member_modifier applies to all participants',
        primary_group='principle_group_tot_gensokyo_boundary',
        buffs={'country_tech_spread_mult': 0.1, 'state_infrastructure_mult': 0.1, 'country_clergymen_pol_str_mult': 0.5})
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Revision 3 installed: valid member modifiers, one primary group, two additional principles.')


def update_devout_bonus():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert report['revision'] == 3, 'Expected revision 3; otherwise run without flags to check.'
    texts = files(archived_characters())
    changed = [rel for rel, expected in texts.items()
        if (ROOT / rel).read_text(encoding='utf-8-sig') != expected]
    assert set(changed) == {'common/power_bloc_principles/tot_gensokyo_charter.txt',
        'localization/english/tot_gensokyo_charter_l_english.yml',
        'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml'}, changed
    backup = ROOT / 'docs/backups' / ('gensokyo_charter_revision_4_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for rel in changed + ['docs/drafts/gensokyo_charter_installed.json']:
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    for rel in changed:
        (ROOT / rel).write_text(texts[rel], encoding='utf-8-sig' if rel.endswith('.yml') else 'utf-8')
    report.update(revision=4, revision_4_backup=str(backup),
        buffs={'country_tech_spread_mult': 0.1, 'state_infrastructure_mult': 0.1,
               'interest_group_ig_devout_pol_str_mult': 0.5})
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Revision 4 installed: +50% Devout Interest Group political strength for all members.')


def update_names():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert report['revision'] == 4, 'Expected revision 4; otherwise run without flags to check.'
    texts = files(archived_characters())
    changed = [rel for rel, expected in texts.items()
        if (ROOT / rel).read_text(encoding='utf-8-sig') != expected]
    assert set(changed) == {'localization/english/tot_gensokyo_charter_l_english.yml',
        'localization/replace/simp_chinese/common/diplomacy/tot_gensokyo_charter_l_simp_chinese.yml'}, changed
    bloc_loc = 'localization/replace/simp_chinese/common/diplomacy/tot_power_bloc_l_simp_chinese.yml'
    backup = ROOT / 'docs/backups' / ('gensokyo_charter_revision_5_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for rel in changed + [bloc_loc, 'docs/drafts/gensokyo_charter_installed.json']:
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    for rel in changed:
        (ROOT / rel).write_text(texts[rel], encoding='utf-8-sig')
    source = (ROOT / bloc_loc).read_text(encoding='utf-8-sig')
    source, count = re.subn(r'(GENSOKYO_BARRIER_NETWORK:\s*)"[^"]*"', r'\1"幻想乡"', source)
    assert count == 1
    (ROOT / bloc_loc).write_text(source, encoding='utf-8-sig')
    report.update(revision=5, revision_5_backup=str(backup), display_name='幻想乡',
        identity_display_name='幻想乡共同体', primary_principle_display_name='乡内贸易')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Revision 5 installed: Gensokyo / Gensokyo Community / Internal Trade.')


if __name__ == '__main__':
    if '--apply' in sys.argv:
        assert not REPORT.exists(), 'Already installed; run without --apply to check.'
        apply()
    elif '--update' in sys.argv:
        update()
    elif '--update-principles' in sys.argv:
        update_principles()
    elif '--update-devout-bonus' in sys.argv:
        update_devout_bonus()
    elif '--update-names' in sys.argv:
        update_names()
    check()
