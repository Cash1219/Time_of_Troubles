"""Install twelve shared Gensokyo cultures; preserve population and religion.

--apply runs once against the Japanese-culture population checkpoint.
--check validates the installed files against the recorded pre-change census.
--check-current also accepts the two documented NZ transfers and island ports.
No older map, population or industry generator is invoked.
"""
import collections
import datetime
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from population_arable_prototype import spans
from west_coast_draft import ownership

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/drafts'
PREFIX = 'tot_gensokyo_'
CULTURES = {
    'human': ('幻想乡人类', 'human', '194 158 95'),
    'youkai': ('幻想乡妖怪', 'youkai', '142 87 161'),
    'beast': ('兽妖', 'youkai', '168 124 72'),
    'tengu': ('天狗', 'youkai', '164 66 73'),
    'kappa': ('河童', 'youkai', '63 148 121'),
    'fairy': ('妖精', 'fairy', '104 183 184'),
    'rabbit': ('兔族', 'youkai', '204 166 189'),
    'lunarian': ('月人', 'lunar', '181 193 235'),
    'oni': ('鬼族', 'youkai', '158 93 57'),
    'spirit': ('幽冥亡灵', 'spirit', '193 212 219'),
    'animal_spirit': ('兽灵', 'spirit', '147 135 95'),
    'celestial': ('天人', 'celestial', '224 209 133'),
}
GROUPS = {'human': '人类传承', 'youkai': '妖怪传承', 'fairy': '妖精传承',
          'spirit': '幽冥传承', 'lunar': '月都传承', 'celestial': '天界传承'}
NAMES = {
    'HITO': '人间之里', 'HAKR': '博丽', 'YKYM': '妖怪之山', 'MRYA': '守矢',
    'MFSR': '魔法森林', 'EITR': '永远亭', 'YSSK': '夜雀食堂', 'MYRN': '命莲寺',
    'SHRM': '神灵庙', 'KZNH': '太阳花田', 'RDMK': '红魔馆', 'MIST': '冰之领地',
    'CHRD': '地灵殿', 'KYTO': '旧都', 'MKAI': '魔界', 'BYKR': '白玉楼',
    'HIGN': '彼岸', 'YKMF': '八云府', 'RNGN': '灵长园', 'UKDO': '后户之国',
    'MTOU': '月都', 'JNKF': '纯狐阵营', 'HCTI': '赫卡提亚地狱', 'TENG': '天界',
}
PLAN = {
    'HITO': dict(human=95, youkai=3, fairy=2),
    'HAKR': dict(human=65, youkai=20, fairy=10, beast=5),
    'YKYM': dict(tengu=40, kappa=30, youkai=15, beast=10, human=5),
    'MRYA': dict(human=40, tengu=20, kappa=15, youkai=15, fairy=10),
    'MFSR': dict(youkai=70, fairy=20, human=10),
    'EITR': dict(rabbit=75, human=20, youkai=5),
    'YSSK': dict(youkai=50, human=30, fairy=20),
    'MYRN': dict(human=45, youkai=45, beast=10),
    'SHRM': dict(human=75, youkai=15, spirit=10),
    'KZNH': dict(fairy=50, youkai=35, human=15),
    'RDMK': dict(fairy=50, youkai=35, human=15),
    'MIST': dict(fairy=80, youkai=15, human=5),
    'CHRD': dict(youkai=40, oni=25, beast=20, spirit=10, human=5),
    'KYTO': dict(oni=65, youkai=20, spirit=10, human=5),
    'MKAI': dict(youkai=80, fairy=15, human=5),
    'BYKR': dict(spirit=85, youkai=10, human=5),
    'HIGN': dict(spirit=80, oni=10, youkai=10),
    'YKMF': dict(youkai=45, beast=35, human=15, fairy=5),
    'RNGN': dict(animal_spirit=45, spirit=35, youkai=15, human=5),
    'UKDO': dict(youkai=40, human=35, fairy=25),
    'MTOU': dict(rabbit=65, lunarian=30, human=5),
    'JNKF': dict(fairy=45, spirit=30, youkai=20, human=5),
    'HCTI': dict(spirit=50, oni=30, fairy=15, youkai=5),
    'TENG': dict(celestial=65, human=20, youkai=10, fairy=5),
}
PRIMARY = {
    'HITO': ['human'], 'HAKR': ['human', 'youkai'],
    'YKYM': ['tengu', 'kappa', 'youkai'], 'MRYA': ['human', 'tengu', 'kappa'],
    'MFSR': ['youkai', 'fairy'], 'EITR': ['rabbit', 'human'],
    'YSSK': ['youkai', 'human'], 'MYRN': ['human', 'youkai'],
    'SHRM': ['human', 'spirit'], 'KZNH': ['youkai', 'fairy'],
    'RDMK': ['youkai', 'fairy', 'human'], 'MIST': ['fairy'],
    'CHRD': ['youkai', 'oni', 'beast'], 'KYTO': ['oni', 'youkai'],
    'MKAI': ['youkai', 'fairy'], 'BYKR': ['spirit'],
    'HIGN': ['spirit', 'youkai'], 'YKMF': ['youkai', 'beast'],
    'RNGN': ['spirit', 'animal_spirit'], 'UKDO': ['youkai', 'human', 'fairy'],
    'MTOU': ['lunarian', 'rabbit'], 'JNKF': ['youkai', 'fairy', 'spirit'],
    'HCTI': ['youkai', 'spirit', 'oni'], 'TENG': ['celestial', 'human'],
}
OVERRIDES = {
    ('STATE_NEW_SOUTH_WALES', 'YKYM'): dict(tengu=25, kappa=45, youkai=15, beast=10, human=5),
    ('STATE_QUEENSLAND', 'YKYM'): dict(tengu=45, kappa=25, youkai=15, beast=10, human=5),
    ('STATE_NEW_SOUTH_WALES', 'HITO'): dict(human=96, youkai=2, fairy=2),
    ('STATE_VICTORIA', 'HITO'): dict(human=92, youkai=5, fairy=3),
    ('STATE_NEW_SOUTH_WALES', 'EITR'): dict(rabbit=70, human=25, youkai=5),
    ('STATE_TASMANIA', 'RDMK'): dict(fairy=55, youkai=35, human=10),
    ('STATE_VICTORIA', 'RDMK'): dict(fairy=45, youkai=35, human=20),
    ('STATE_CHIREIDEN_CAPITAL', 'CHRD'): dict(youkai=50, oni=20, beast=15, spirit=10, human=5),
    ('STATE_CHIREIDEN_OASIS', 'CHRD'): dict(youkai=30, oni=20, beast=20, spirit=15, human=15),
    ('STATE_CHIREIDEN_GATE', 'CHRD'): dict(youkai=35, oni=15, beast=15, spirit=15, human=20),
    ('STATE_CHIREIDEN_WEST_GATE', 'CHRD'): dict(youkai=40, oni=20, beast=10, spirit=20, human=10),
    ('STATE_CHIREIDEN_NORTH_OASIS', 'CHRD'): dict(youkai=25, oni=25, beast=20, spirit=20, human=10),
    ('STATE_CHIREIDEN_CAVERN_ZONE', 'CHRD'): dict(youkai=40, oni=30, beast=20, spirit=10),
    ('STATE_SOUTH_AUSTRALIA', 'CHRD'): dict(youkai=45, oni=20, beast=15, spirit=15, human=5),
}
POP_PATH = 'common/history/pops/13_australasia.txt'
POP_PATHS = ['common/history/pops/12_indonesia.txt', POP_PATH]
STATE_PATH = 'common/history/states/00_states.txt'
DEF_PATH = 'common/country_definitions/tot_countries.txt'
CHAR_PATH = 'common/history/characters/tot_gensokyo_nz.txt'
REPORT = OUT / 'gensokyo_cultures_v1.json'


def field(body, key, default=None):
    m = re.search(r'\b' + key + r'\s*=\s*(\w+)', body)
    return m[1] if m else default


def records(source):
    result = []
    for sm, sb, _ in spans(source, r's:(STATE_\w+)\s*=\s*\{'):
        for tm, tb, _ in spans(sb, r'region_state:(\w+)\s*=\s*\{'):
            for _, pb, _ in spans(tb, r'create_pop\s*=\s*\{'):
                result.append(dict(state=sm[1], tag=tm[1], culture=field(pb, 'culture'),
                    religion=field(pb, 'religion'), size=int(field(pb, 'size'))))
    return result


def split(size, weights):
    assert sum(weights.values()) == 100 and set(weights) <= set(CULTURES)
    parts = {k: size * w // 100 for k, w in weights.items()}
    order = sorted(weights, key=lambda k: (-(size * weights[k] % 100), k))
    for k in order[:size - sum(parts.values())]:
        parts[k] += 1
    assert sum(parts.values()) == size
    return parts


def replace_blocks(source, pattern, transform):
    edits = []
    for m, body, end in spans(source, pattern):
        # The match ends at the actual opening brace. Its leading whitespace
        # can include masked comments containing other braces.
        opening = m.end() - 1
        edits.append((opening + 1, end - 1, transform(m, body)))
    for start, end, value in reversed(edits):
        source = source[:start] + value + source[end:]
    return source


def migrate_pops(source):
    def state(sm, sb):
        def region(tm, tb):
            if tm[1] not in PLAN:
                return tb
            weights = OVERRIDES.get((sm[1], tm[1]), PLAN[tm[1]])
            def convert(m):
                body = m[1]
                if field(body, 'culture') != 'japanese':
                    return m[0]
                assert set(re.findall(r'(\w+)\s*=', body)) <= {'culture', 'religion', 'size'}
                religion = field(body, 'religion', 'mahayana')  # Old Japanese default.
                return '\n\t\t\t'.join('create_pop = { culture = ' + PREFIX + k +
                    ' religion = ' + religion + ' size = ' + str(n) + ' }'
                    for k, n in split(int(field(body, 'size')), weights).items() if n)
            return re.sub(r'create_pop\s*=\s*\{([^{}]*)\}', convert, tb)
        return replace_blocks(sb, r'region_state:(\w+)\s*=\s*\{', region)
    return replace_blocks(source, r's:(STATE_\w+)\s*=\s*\{', state)


def generate_definitions():
    src = (ROOT / 'common/cultures/00_cultures.txt').read_text(encoding='utf-8-sig')
    japanese = next(body for _, body, _ in spans(src, r'(?m)^\s*japanese\s*=\s*\{'))
    naming = '\tname_format = last_first\n'
    for key in ['male_common_first_names', 'female_common_first_names',
                'noble_last_names', 'common_last_names', 'ethnicities']:
        body = next(b for _, b, _ in spans(japanese, r'\b' + key + r'\s*=\s*\{'))
        naming += '\t' + key + ' = {' + body + '}\n'
    naming += '\tgraphics = east_asian\n'
    culture_src = '# Shared population identities, not country-specific cultures.\n'
    trait_src = 'language_tot_gensokyo = {\n\ttype = language\n\ttrait_group = language_group_tot_gensokyo\n}\n\n'
    trait_src += 'tradition_tot_gensokyo = { type = tradition }\n\n'
    group_src = 'language_group_tot_gensokyo = { type = language }\n'
    for group in GROUPS:
        group_src += 'heritage_group_tot_gensokyo_' + group + ' = { type = heritage }\n'
    zh = {'language_tot_gensokyo': '幻想乡共同语', 'language_group_tot_gensokyo': '幻想乡语系',
          'tradition_tot_gensokyo': '幻想乡传统'}
    en = {'language_tot_gensokyo': 'Gensokyo Common', 'language_group_tot_gensokyo': 'Gensokyo Languages',
          'tradition_tot_gensokyo': 'Gensokyo Traditions'}
    for key, (name, group, color) in CULTURES.items():
        heritage = 'heritage_' + PREFIX + key
        culture_src += '\n' + PREFIX + key + ' = {\n\tcolor = rgb{ ' + color + ' }\n'
        culture_src += '\treligion = shinto\n\theritage = ' + heritage + '\n'
        culture_src += '\tlanguage = language_tot_gensokyo\n\ttraditions = { tradition_tot_gensokyo }\n'
        culture_src += naming + '}\n'
        trait_src += heritage + ' = {\n\ttype = heritage\n\ttrait_group = heritage_group_tot_gensokyo_' + group + '\n}\n\n'
        zh[PREFIX + key] = name
        zh[heritage] = name + '传承'
        en[PREFIX + key] = key.replace('_', ' ').title()
        en[heritage] = en[PREFIX + key] + ' Heritage'
    for group, name in GROUPS.items():
        zh['heritage_group_tot_gensokyo_' + group] = name
        en['heritage_group_tot_gensokyo_' + group] = group.title() + ' Heritage'
    def loc(language, values):
        return 'l_' + language + ':\n' + ''.join(' ' + k + ': "' + v + '"\n' for k, v in values.items())
    return {
        'common/cultures/tot_gensokyo_cultures.txt': culture_src,
        'common/discrimination_traits/tot_gensokyo_cultures.txt': trait_src,
        'common/discrimination_trait_groups/tot_gensokyo_cultures.txt': group_src,
        'localization/replace/simp_chinese/common/core/tot_gensokyo_cultures_l_simp_chinese.yml': loc('simp_chinese', zh),
        'localization/english/tot_gensokyo_cultures_l_english.yml': loc('english', en),
    }


def census(rows, key):
    result = collections.Counter()
    for row in rows:
        result[key(row)] += row['size']
    return result


def effective_religion(row):
    if row['religion']:
        return row['religion']
    assert row['culture'] == 'japanese', row
    return 'mahayana'


def verify(before, after, states_before, states_after, defs, defs_before, allowed_ownership_changes=None, homeland_threshold=None):
    assert census(before, lambda r: (r['state'], r['tag'])) == census(after, lambda r: (r['state'], r['tag']))
    old_foreign = [r for r in before if r['culture'] != 'japanese' or r['tag'] not in PLAN]
    new_foreign = [r for r in after if not r['culture'].startswith(PREFIX)]
    assert old_foreign == new_foreign, 'Non-fantasy cohorts changed'
    old_fantasy = [r for r in before if r['culture'] == 'japanese' and r['tag'] in PLAN]
    new_fantasy = [r for r in after if r['culture'].startswith(PREFIX)]
    assert census(old_fantasy, lambda r: (r['state'], r['tag'], effective_religion(r))) == census(new_fantasy, lambda r: (r['state'], r['tag'], r['religion']))
    assert all(r['culture'] != 'japanese' for r in after if r['tag'] in PLAN)
    assert len(set(r['culture'] for r in new_fantasy)) == 12
    owners_before, owners_after = ownership(states_before), ownership(states_after)
    actual_changes = {p: [owners_before.get(p), owners_after.get(p)]
                      for p in set(owners_before) | set(owners_after)
                      if owners_before.get(p) != owners_after.get(p)}
    assert actual_changes == (allowed_ownership_changes or {}), 'Unexpected province ownership changes'
    pairs = {tuple(v) for v in owners_after.values()}
    for row in new_fantasy:
        assert (row['state'], row['tag']) in pairs
    parsed_defs = {m[1]: b for m, b, _ in spans(defs, r'(?m)^\s*([A-Z0-9]{3,4})\s*=\s*\{')}
    for tag, primary in PRIMARY.items():
        actual = re.search(r'cultures\s*=\s*\{([^}]+)\}', parsed_defs[tag])[1].split()
        assert actual == [PREFIX + k for k in primary]
        assert set(actual) <= {r['culture'] for r in new_fantasy if r['tag'] == tag}
    state_bodies = {m[1]: b for m, b, _ in spans(states_after, r's:(STATE_\w+)\s*=\s*\{')}
    totals = census(after, lambda r: r['state'])
    amounts = census(after, lambda r: (r['state'], r['culture']))
    for row in new_fantasy:
        is_homeland = 'add_homeland = cu:' + row['culture'] in state_bodies[row['state']]
        if homeland_threshold is None:
            assert is_homeland
        else:
            assert is_homeland == (amounts[row['state'], row['culture']] * 100 >= totals[row['state']] * homeland_threshold)
    for tag, body in parsed_defs.items():
        if tag not in PLAN:
            old = next(b for m, b, _ in spans(defs_before, r'(?m)^\s*' + re.escape(tag) + r'\s*=\s*\{'))
            assert old == body
    return dict(population=sum(r['size'] for r in after if r['tag'] in PLAN),
        reclassified=sum(r['size'] for r in new_fantasy),
        retained=sum(r['size'] for r in after if r['tag'] in PLAN and not r['culture'].startswith(PREFIX)),
        countries=len(PLAN), cultures=12, population_by_state_owner_preserved=True,
        religion_by_state_owner_preserved=True, original_minorities_preserved=True,
        province_ownership_preserved=not actual_changes,
        documented_province_transfers=len(actual_changes), primary_cultures_valid=True, homelands_valid=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard_hashes():
    files = []
    for folder in ['map_data', 'common/history/buildings', 'common/buildings',
                   'common/production_methods', 'common/production_method_groups',
                   'common/religions', 'common/history/diplomacy']:
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file())
    files.append(ROOT / 'common/history/countries/tot_gensokyo_australasia.txt')
    return {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files}


def validate_definitions():
    culture_path = ROOT / 'common/cultures/tot_gensokyo_cultures.txt'
    trait_path = ROOT / 'common/discrimination_traits/tot_gensokyo_cultures.txt'
    group_path = ROOT / 'common/discrimination_trait_groups/tot_gensokyo_cultures.txt'
    cultures = {m[1]: b for m,b,_ in spans(culture_path.read_text(encoding='utf-8-sig'),
        r'(?m)^\s*(tot_gensokyo_\w+)\s*=\s*\{')}
    traits = {m[1]: b for m,b,_ in spans(trait_path.read_text(encoding='utf-8-sig'),
        r'(?m)^\s*((?:heritage|language|tradition)_\w+)\s*=\s*\{')}
    groups = {m[1]: b for m,b,_ in spans(group_path.read_text(encoding='utf-8-sig'),
        r'(?m)^\s*((?:heritage|language)_group_\w+)\s*=\s*\{')}
    assert set(cultures) == {PREFIX + k for k in CULTURES}
    for culture, body in cultures.items():
        assert field(body, 'heritage') in traits
        assert field(body, 'language') in traits
        assert field(body, 'religion') == 'shinto'
        assert 'tradition_tot_gensokyo' in re.search(r'traditions\s*=\s*\{([^}]+)\}', body)[1].split()
        assert 'taboos' not in body and 'obsessions' not in body
    for trait, body in traits.items():
        if field(body, 'type') in {'heritage', 'language'}:
            group = field(body, 'trait_group')
            assert group in groups and field(groups[group], 'type') == field(body, 'type')
    for path, language in [
        ('localization/replace/simp_chinese/common/core/tot_gensokyo_cultures_l_simp_chinese.yml', 'simp_chinese'),
        ('localization/english/tot_gensokyo_cultures_l_english.yml', 'english')]:
        raw = (ROOT / path).read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf')
        text = raw.decode('utf-8-sig')
        assert text.startswith('l_' + language + ':')
        keys = re.findall(r'^ (\w+):', text, re.M)
        assert len(keys) == len(set(keys))
        assert set(cultures) | set(traits) | set(groups) <= set(keys)
    character_source = (ROOT / CHAR_PATH).read_text(encoding='utf-8-sig')
    assert set(re.findall(r'culture\s*=\s*cu:(\w+)', character_source)) <= set(cultures)
    for path in [culture_path, trait_path, group_path]:
        assert all(line == line.rstrip() for line in path.read_text(encoding='utf-8-sig').splitlines())
    return True


def main():
    if '--check' in sys.argv or '--check-current' in sys.argv:
        report = json.loads(REPORT.read_text(encoding='utf-8'))
        backup = ROOT / report['backup']
        before = [r for p in POP_PATHS for r in records((backup / p).read_text(encoding='utf-8-sig'))]
        after = [r for p in POP_PATHS for r in records((ROOT / p).read_text(encoding='utf-8-sig'))]
        allowed_changes = None
        homeland_threshold = None
        cleanup = None
        relocation = None
        states_after_source = (ROOT / STATE_PATH).read_text(encoding='utf-8-sig')
        if '--check-current' in sys.argv:
            allowed_changes = {p: [['STATE_NORTH_ISLAND', 'MTOU'], ['STATE_NORTH_ISLAND', 'JNKF']]
                               for p in ['xC25D9D', 'x3BCC0A']}
            repair = json.loads((OUT / 'nz_fragment_repair.json').read_text(encoding='utf-8'))
            assert repair['changes'] == allowed_changes
            cleanup_path = OUT / 'gensokyo_map_cleanup.json'
            if cleanup_path.exists():
                from gensokyo_map_cleanup import check as check_cleanup
                check_cleanup()
                cleanup = json.loads(cleanup_path.read_text(encoding='utf-8'))
                assert not set(allowed_changes).intersection(cleanup['ownership_changes'])
                allowed_changes.update(cleanup['ownership_changes'])
                homeland_threshold = cleanup['homeland_threshold_percent']
                # Kanak's existing cohorts follow the island to TENG, without
                # changing any person's culture, religion or population size.
                before = [dict(row, tag='TENG') if row['state'] == 'STATE_KANAK' and row['tag'] == 'KNK'
                          else row for row in before]
            relocation_path = OUT / 'three_factions_relocation.json'
            if relocation_path.exists():
                from three_factions_relocation import check as check_relocation
                check_relocation()
                relocation = json.loads(relocation_path.read_text(encoding='utf-8'))
                stage = Path(relocation['backup'])
                after = [r for p in POP_PATHS for r in records(
                    (stage / p if p in relocation['hashes'] else ROOT / p).read_text(encoding='utf-8-sig'))]
                states_after_source = (stage / STATE_PATH).read_text(encoding='utf-8-sig')
        checks = verify(before, after, (backup / STATE_PATH).read_text(encoding='utf-8-sig'),
            states_after_source, (ROOT / DEF_PATH).read_text(encoding='utf-8-sig'),
            (backup / DEF_PATH).read_text(encoding='utf-8-sig'), allowed_changes, homeland_threshold)
        current_hashes = guard_hashes()
        if '--check-current' in sys.argv:
            if relocation:
                for rel, values in relocation['hashes'].items():
                    if rel not in current_hashes:
                        continue
                    assert current_hashes[rel] == values['after'], rel
                    if rel in report['unchanged_files']:
                        assert values['before'] == report['unchanged_files'][rel]
                        current_hashes[rel] = values['before']
                    else:
                        current_hashes.pop(rel)
                checks['documented_three_factions_relocation_valid'] = True
            port_path = 'common/history/buildings/tot_gensokyo_market_ports.txt'
            assert port_path not in report['unchanged_files']
            current_hashes.pop(port_path)
            ports = (ROOT / port_path).read_text(encoding='utf-8-sig')
            state_blocks = list(spans(ports, r's:(STATE_\w+)\s*=\s*\{'))
            port_states = {'STATE_FIJI', 'STATE_VANUATU'} | ({'STATE_KANAK'} if cleanup else set())
            assert {m[1] for m, _, _ in state_blocks} == port_states
            for _, body, _ in state_blocks:
                regions = list(spans(body, r'region_state:(\w+)\s*=\s*\{'))
                assert len(regions) == 1 and regions[0][0][1] == 'TENG'
                buildings = list(spans(regions[0][1], r'create_building\s*=\s*\{'))
                assert len(buildings) == 1
                b = buildings[0][1]
                assert re.search(r'\bbuilding\s*=\s*"building_port"', b)
                assert re.findall(r'levels\s*=\s*(\d+)', b) == ['1']
                assert re.findall(r'country\s*=\s*"c:(\w+)"', b) == ['TENG']
                assert re.search(r'activate_production_methods\s*=\s*\{\s*"pm_basic_port"\s*\}', b)
            checks['documented_island_port_levels'] = len(port_states)
            if cleanup:
                for rel, meta in cleanup['runtime_files'].items():
                    if rel not in current_hashes:
                        continue
                    if meta['before_sha256'] is None:
                        assert rel not in report['unchanged_files']
                        current_hashes.pop(rel)
                    elif rel in report['unchanged_files']:
                        assert meta['before_sha256'] == report['unchanged_files'][rel]
                        current_hashes[rel] = meta['before_sha256']
                checks['documented_map_cleanup_valid'] = True
                checks['homeland_threshold_percent'] = homeland_threshold
            charter_report = OUT / 'gensokyo_charter_installed.json'
            if charter_report.exists():
                # Accept only the exact installed charter, not arbitrary diplomacy edits.
                from gensokyo_charter_install import check as check_charter
                check_charter()
                charter = json.loads(charter_report.read_text(encoding='utf-8'))
                manifest = json.loads((Path(charter['backup']) / 'manifest.json').read_text(encoding='utf-8'))
                for rel in charter['runtime_files']:
                    if rel not in current_hashes:
                        continue
                    if rel in report['unchanged_files']:
                        assert rel in manifest['existing']
                        assert digest(Path(charter['backup']) / rel) == report['unchanged_files'][rel]
                        current_hashes[rel] = report['unchanged_files'][rel]
                    else:
                        assert rel in manifest['created']
                        current_hashes.pop(rel)
                checks['documented_charter_change_valid'] = True
        assert current_hashes == report['unchanged_files'], 'An unrelated runtime file changed'
        checks['culture_trait_localization_references_valid'] = validate_definitions()
        print(json.dumps(checks, ensure_ascii=False))
        return
    assert '--apply' in sys.argv, 'Use --apply or --check'
    assert set(PLAN) == set(PRIMARY) == set(NAMES)
    for weights in list(PLAN.values()) + list(OVERRIDES.values()):
        split(101, weights)
    original = {p: (ROOT / p).read_text(encoding='utf-8-sig') for p in POP_PATHS + [STATE_PATH, DEF_PATH, CHAR_PATH]}
    before = [r for p in POP_PATHS for r in records(original[p])]
    assert all(not r['culture'].startswith(PREFIX) for r in before), 'Already installed'
    payload = generate_definitions()
    for path in POP_PATHS:
        payload[path] = migrate_pops(original[path])
    after = [r for p in POP_PATHS for r in records(payload[p])]
    def country(m, body):
        if m[1] not in PRIMARY:
            return body
        return re.sub(r'cultures\s*=\s*\{[^}]*\}',
            'cultures = { ' + ' '.join(PREFIX + k for k in PRIMARY[m[1]]) + ' }', body, count=1)
    payload[DEF_PATH] = replace_blocks(original[DEF_PATH], r'(?m)^\s*([A-Z0-9]{3,4})\s*=\s*\{', country)
    homelands = collections.defaultdict(set)
    for row in after:
        if row['culture'].startswith(PREFIX):
            homelands[row['state']].add(row['culture'])
    def homeland(m, body):
        if m[1] not in homelands:
            return body
        return body.rstrip() + '\n' + ''.join('\t\tadd_homeland = cu:' + c + '\n'
            for c in sorted(homelands[m[1]])) + '\t'
    payload[STATE_PATH] = replace_blocks(original[STATE_PATH], r's:(STATE_\w+)\s*=\s*\{', homeland)
    # These two divine characters use a broad community culture temporarily.
    # This is not a claim that Junko or Hecatia is biologically a youkai.
    payload[CHAR_PATH] = original[CHAR_PATH].replace('culture = cu:japanese',
        '# Broad community identity; divine species is not represented by this culture.\n\t\t\tculture = cu:tot_gensokyo_youkai')
    checks = verify(before, after, original[STATE_PATH], payload[STATE_PATH], payload[DEF_PATH], original[DEF_PATH])
    for path, source in payload.items():
        stripped = re.sub(r'#[^\n]*', '', source)
        assert stripped.count('{') == stripped.count('}'), path
    unchanged = guard_hashes()
    backup = ROOT / ('docs/backups/gensokyo_cultures_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    for path in payload:
        current = ROOT / path
        if current.exists():
            target = backup / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current, target)
    for path, source in payload.items():
        current = ROOT / path
        current.parent.mkdir(parents=True, exist_ok=True)
        with current.open('w', encoding='utf-8-sig' if path.endswith('.yml') else 'utf-8', newline='\n') as f:
            f.write(source)
    assert guard_hashes() == unchanged
    checks['culture_trait_localization_references_valid'] = validate_definitions()
    counts = census(after, lambda r: (r['tag'], r['culture']))
    country_rows = {tag: dict(name=NAMES[tag], total=sum(r['size'] for r in after if r['tag'] == tag),
        primary=[PREFIX + k for k in PRIMARY[tag]],
        cultures={culture: n for (t, culture), n in counts.items() if t == tag}) for tag in PLAN}
    report = dict(status='applied; static validation passed; not game-tested',
        backup=str(backup.relative_to(ROOT)).replace('\\', '/'), checks=checks,
        cultures={PREFIX + k: v[0] for k, v in CULTURES.items()}, countries=country_rows,
        overrides=[dict(state=s, tag=t, weights=w) for (s,t),w in OVERRIDES.items()],
        unchanged_files=unchanged, changed_files=list(payload),
        notes=['Percentages are scenario design, not canon census.',
            'Only Japanese-culture Gensokyo cohorts are reclassified; other cultures retained.',
            'Japanese cohorts without an explicit religion retain their old mahayana default.',
            'New cultures have explicit homelands; normal homeland assimilation is blocked by native rules.',
            'Human/youkai magician distinction uses existing human/youkai cultures; rabbits share one culture.',
            'Junko and Hecatia use broad youkai community culture pending distinct divine character identity.',
            'All culture name pools and portraits use the existing Japanese template; no new visual assets.',
            'No production bonuses, obsessions or food taboos are added to the new cultures.'])
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 幻想乡文化 V1（已实装）', '',
        '12 种文化由 24 国共用。比例是模组设定，并非原作人口统计。', '',
        '只重新分配原日本文化人口；其他文化、各州各国人口与宗教人数保持不变。',
        '魔法使不单列；地上兔、月兔共用兔族文化。文化不附加生产修正或饮食禁忌。', '',
        '新文化使用幻想乡共同语；传承按人类、妖怪、妖精、幽冥、月都、天界分组，供后续政治筛选。',
        '主流文化表示社会核心，实际接纳程度仍由现有法律决定，未修改法律或利益集团。',
        '各文化在其开局居住州登记本土，利用原版本土规则阻止普通同化；特殊允许本土同化的机制仍可绕过。',
        '纯狐、赫卡提亚临时使用广义妖怪共同体文化，不代表两位神灵的生物种族归类；神灵身份等待角色体系完善。',
        '随机角色姓名与人物模型沿用日本文化模板；本轮没有新增妖精、兽耳等人物资产。', '',
        '## 核对结果', '',
        '- 总人口：{:,}；重新分类：{:,}；保留其他文化：{:,}。'.format(checks['population'], checks['reclassified'], checks['retained']),
        '- 州与国家人口、宗教人数、非日本文化居民均保持不变。',
        '- 省份归属、地形、资源、建筑、生产方式与外交配置保持不变。',
        '- 尚未启动游戏验证，请使用新的 1836 开局。', '',
        '## 各国文化人数', '', '| 国家 | 总人口 | 新文化组成（人数） |', '|---|---:|---|']
    for tag, data in country_rows.items():
        composition = '、'.join(CULTURES[c[len(PREFIX):]][0] + ' ' + format(n, ',')
            for c,n in data['cultures'].items() if c.startswith(PREFIX))
        lines.append('| ' + data['name'] + ' | ' + format(data['total'], ',') + ' | ' + composition + ' |')
    lines += ['', '详细按州配置和校验见同目录 gensokyo_cultures_v1.json。']
    (OUT / 'gensokyo_cultures_v1.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == '__main__':
    main()
