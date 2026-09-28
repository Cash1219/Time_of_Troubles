"""Manual border revision and restoration of the historical Hakurei bloc.

Dry run by default; --apply backs up changed runtime files. This is a frozen
revision for the Tasmania-relocation map, not a general province allocator.
"""
import collections
import datetime
import json
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import west_coast_draft as w
import lake_coast_revision as lc
from tasmania_relocation import replace_state, state_history
from population_arable_prototype import spans, split_size, pop_entries

PREFIX = 'southern_rebalance_v1'
STATES = {'STATE_NEW_SOUTH_WALES', 'STATE_VICTORIA', 'STATE_SOUTH_AUSTRALIA'}
CAPITALS = {'SHRM': 'STATE_NEW_SOUTH_WALES', 'KZNH': 'STATE_SOUTH_AUSTRALIA'}
FILES = ['common/history/states/00_states.txt',
         'common/country_definitions/tot_countries.txt',
         'common/history/pops/13_australasia.txt',
         'common/history/diplomacy/tot_gensokyo_subjects.txt',
         'common/history/power_blocs/tot_gensokyo_power_bloc.txt']
# Manually reviewed clusters on the province raster, with adjoining cut-off
# boundary provinces included explicitly. No Voronoi/radius allocation.
TRANSFERS = {
    'SHRM': ['x24AEFA', 'x73D224', 'x8A6B46', 'xE6C282', 'xBE5235',
             'x237F0D', 'xC24AAA', 'x698A94', 'xE6B9A2', 'x8D65DF',
             'x768B4D', 'xC15B4F', 'x2FE431'],
    'HAKR': ['x799B34', 'xCB67EC', 'x467A72', 'xC1F3AD',
             'xE8CAF7', 'x91A2E2', 'xD060D0', 'x276C93'],
    'RDMK': ['xC60700', 'x11C030', 'x880696'],
    'HITO': ['x2BD326', 'x68E6E2', 'xAFEC31'],
    'EITR': ['x5CAC91', 'xB6943C', 'xB905E5', 'xE86E1F'],
}


def prepare():
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    assert len([p for p, v in before.items() if v[1] == 'SHRM']) == 22
    assert len([p for p, v in before.items() if v[1] == 'KZNH']) == 7
    for p, (state, tag) in before.items():
        if tag == 'SHRM':
            assert state == 'STATE_SOUTH_AUSTRALIA'
            after[p][1] = 'KZNH'
        elif tag == 'KZNH':
            assert state == 'STATE_VICTORIA'
            after[p][1] = 'HITO'
    seen = set()
    for tag, provinces in TRANSFERS.items():
        for p in provinces:
            assert p not in seen
            seen.add(p)
            expected = ('HITO',) if tag == 'SHRM' else ('MFSR', 'HITO') if tag == 'HAKR' else ('EITR',) if tag == 'RDMK' else ('HAKR',)
            assert before[p][1] in expected, (p, before[p])
            after[p][1] = tag
    return before, after


def connected(after):
    links = {p: list(ns) for p, ns in lc.CTX['adj'].items()}
    for line in (w.ROOT / 'map_data/adjacencies.csv').read_text(encoding='utf-8-sig').splitlines():
        f = line.split(';')
        if len(f) < 3 or f[2] != 'sea':
            continue
        a, b = [v.upper().replace('X', 'x') for v in f[:2]]
        if a in links and b in links:
            links[a].append(b)
            links[b].append(a)
    result = {}
    for tag in ('SHRM', 'KZNH', 'HITO', 'HAKR', 'EITR', 'RDMK', 'MIST', 'MYRN', 'MFSR'):
        parts = w.components([p for p in links if after[p][1] == tag], links)
        assert len(parts) == 1, (tag, parts[1:])
        result[tag] = [len(p) for p in parts]
    assert any(after[q][1] == 'MYRN' for p in links if after[p][1] == 'SHRM' for q in links[p])
    for a, b in [('x904030', 'x114030'), ('x11C030', 'x97975E')]:
        assert after[a][1] == after[b][1] == 'RDMK' and b in links[a]
    return result


def population(text):
    # Keep each state's residents and culture/religion totals; provisional
    # country shares are explicit and do not use province pixel area.
    weights = {
        ('STATE_SOUTH_AUSTRALIA', 'SHRM'): {'KZNH': 1},
        ('STATE_VICTORIA', 'KZNH'): {'HITO': 1},
        ('STATE_VICTORIA', 'HAKR'): {'EITR': 1},
        ('STATE_VICTORIA', 'EITR'): {'EITR': 500001, 'RDMK': 100000},
        ('STATE_NEW_SOUTH_WALES', 'HITO'): {'HITO': 2520000, 'SHRM': 400000, 'HAKR': 80000},
        ('STATE_NEW_SOUTH_WALES', 'HAKR'): {'HAKR': 500000, 'HITO': 40000, 'EITR': 60000},
        ('STATE_NEW_SOUTH_WALES', 'MFSR'): {'MFSR': 225000, 'HAKR': 25000},
    }
    replacements = []
    for sm, body, end in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
        if sm[1] not in STATES:
            continue
        groups = collections.defaultdict(collections.Counter)
        old = collections.Counter()
        for tm, owner, _ in spans(body, r'region_state:(\w+)\s*=\s*\{'):
            for _, pop, _ in spans(owner, r'create_pop\s*=\s*\{'):
                f = dict(re.findall(r'(\w+)\s*=\s*(\w+)', pop))
                assert set(f) <= {'culture', 'religion', 'size'}
                profile = (f['culture'], f.get('religion'))
                size = int(f['size'])
                old[profile] += size
                for tag, n in split_size(size, weights.get((sm[1], tm[1]), {tm[1]: 1})).items():
                    groups[tag][profile] += n
        check = collections.Counter()
        lines = ['s:{} = {{'.format(sm[1])]
        for tag, profiles in sorted(groups.items()):
            lines.append('\t\tregion_state:{} = {{'.format(tag))
            for (culture, religion), size in sorted(profiles.items(), key=lambda kv: (kv[0][0], kv[0][1] or '')):
                if not size:
                    continue
                check[culture, religion] += size
                fields = 'culture = ' + culture + (' religion = ' + religion if religion else '')
                lines.append('\t\t\tcreate_pop = {{ {} size = {} }}'.format(fields, size))
            lines.append('\t\t}')
        assert check == old
        replacements.append((sm.start(), end, '\n'.join(lines + ['\t}'])))
    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    return text


def agriculture(owners):
    text = (w.ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt').read_text(encoding='utf-8-sig')
    result = {}
    for state in ('STATE_NEW_SOUTH_WALES', 'STATE_VICTORIA'):
        s, e = w.block(text, state)
        body = text[s:e]
        ps = [p for p, v in owners.items() if v[0] == state]
        match = re.search(r'prime_land\s*=\s*\{([^}]+)', body)
        prime = {p.upper().replace('X', 'x') for p in w.PROV.findall(match[1])} if match else set()
        mine = [p for p in ps if owners[p][1] == 'HITO']
        weights = lambda provinces: sum(5 if p in prime else 1 for p in provinces)
        arable = int(re.search(r'arable_land\s*=\s*(\d+)', body)[1])
        farm = re.search(r'\bfarm\s*=\s*"?(x[0-9A-Fa-f]{6})', body)[1].upper().replace('X', 'x')
        result[state] = dict(hito_provinces=len(mine), total_provinces=len(ps),
                             hito_prime_land=len(set(mine) & prime), total_prime_land=len(prime),
                             estimated_hito_arable=round(arable * weights(mine) / weights(ps), 2),
                             farm_hub= farm, farm_hub_owner=owners[farm][1])
    return result


def preview(owners):
    source = Image.open(w.GAME / 'map_data/provinces.png').convert('RGB')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    for suffix, bounds, scale in [('map', (6570, 2400, 8540, 3370), 1),
                                  ('detail', (7280, 2740, 7600, 3070), 3)]:
        a = np.asarray(source.crop(bounds), dtype=np.uint32)
        codes = (a[:, :, 0] << 16) | (a[:, :, 1] << 8) | a[:, :, 2]
        unique, inverse = np.unique(codes, return_inverse=True)
        palette = np.array([w.COLORS.get(owners.get('x{:06X}'.format(int(c)), ['', ''])[1], (55, 78, 88)) for c in unique], dtype=np.uint8)
        rgb = palette[inverse].reshape(a.shape)
        edge = np.zeros(codes.shape, bool)
        edge[:, 1:] |= codes[:, 1:] != codes[:, :-1]
        edge[1:, :] |= codes[1:, :] != codes[:-1, :]
        rgb[edge & np.any(rgb != (55, 78, 88), axis=2)] = (45, 50, 50)
        im = Image.fromarray(rgb).resize((codes.shape[1] * scale, codes.shape[0] * scale))
        draw = ImageDraw.Draw(im)
        for tag, name in dict(w.NAMES, MIST='冰之领地').items():
            ps = [int(p[1:], 16) for p, v in owners.items() if v[1] == tag]
            yy, xx = np.where(np.isin(codes, ps))
            if len(xx):
                draw.text((int(xx.mean()) * scale, int(yy.mean()) * scale), name, font=font, anchor='mm', fill='black', stroke_width=1, stroke_fill='white')
        im.save(w.OUT / (PREFIX + '_' + suffix + '.png'))


def main():
    before, after = prepare()
    connectivity = connected(after)
    originals = {path: (w.ROOT / path).read_bytes() if (w.ROOT / path).exists() else None for path in FILES}
    assert originals[FILES[3]] is None and originals[FILES[4]] is None, 'Revision already applied'
    texts = {path: data.decode('utf-8-sig') for path, data in originals.items() if data is not None}
    for state in sorted(STATES):
        m, _, end = next(v for v in spans(texts[FILES[0]], r's:(STATE_\w+)\s*=\s*\{') if v[0][1] == state)
        texts[FILES[0]] = replace_state(texts[FILES[0]], state, state_history(state, after, texts[FILES[0]][m.start():end]))
    assert w.ownership(texts[FILES[0]]) == after
    for tag, capital in CAPITALS.items():
        s, e = w.block(texts[FILES[1]], tag)
        body = re.sub(r'capital\s*=\s*STATE_\w+', 'capital = ' + capital, texts[FILES[1]][s:e])
        texts[FILES[1]] = texts[FILES[1]][:s] + body + texts[FILES[1]][e:]
    texts[FILES[2]] = population(texts[FILES[2]])
    tags = sorted(set(re.findall(r'c:(\w+)\s*\?=', (w.ROOT / 'common/history/countries/tot_gensokyo_australasia.txt').read_text(encoding='utf-8-sig'))))
    subjects = [tag for tag in tags if tag != 'HAKR']
    assert len(tags) == 22 and len(subjects) == 21
    for tag in tags:
        s, e = w.block(texts[FILES[1]], tag)
        capital = re.search(r'capital\s*=\s*(STATE_\w+)', texts[FILES[1]][s:e])[1]
        assert any(v == [capital, tag] for v in after.values()), (tag, capital)
    texts[FILES[3]] = '# 临时恢复幻想乡附属体系：博丽领导，后续可重新调整。\nDIPLOMACY = {\n\tc:HAKR ?= {\n' + ''.join('\t\tcreate_diplomatic_pact = { country = c:' + tag + ' type = vassal }\n' for tag in subjects) + '\t}\n}\n'
    texts[FILES[4]] = '''# 恢复旧版幻想乡结界盟约；附庸自动进入博丽的阵营。
POWER_BLOCS = {
    c:HAKR ?= {
        create_power_bloc = {
            name = GENSOKYO_BARRIER_NETWORK
            map_color = { 232 66 91 }
            founding_date = 1836.1.1
            identity = identity_sovereign_empire
            principle = principle_vassalization_1
        }
        power_bloc = { add_cohesion_number = 100 }
    }
}
'''
    for folder in ('diplomacy', 'power_blocs'):
        for path in (w.ROOT / ('common/history/' + folder)).glob('*.txt'):
            assert not re.search(r'c:(' + '|'.join(tags) + r')\b', re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig'))), path
    all_pops = {p: p.read_text(encoding='utf-8-sig') for p in (w.ROOT / 'common/history/pops').glob('*.txt')}
    old_rows = pop_entries(all_pops)
    new_rows = pop_entries({**all_pops, w.ROOT / FILES[2]: texts[FILES[2]]})
    def profiles(rows):
        c = collections.Counter()
        for st, _, culture, religion, n in rows: c[st, culture, religion] += n
        return c
    assert profiles(old_rows) == profiles(new_rows)
    country_pops = collections.Counter()
    pairs = set(map(tuple, after.values()))
    for st, tag, _, _, n in new_rows:
        assert (st, tag) in pairs, (st, tag)
        country_pops[tag] += n
    assert sum(country_pops.values()) == 19610000
    assert sum(n for st, _, _, _, n in new_rows if st == 'STATE_CHIREIDEN_CAVERN_ZONE') == 10000
    definitions = (w.ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt').read_text(encoding='utf-8-sig')
    for state in STATES:
        s, e = w.block(definitions, state)
        ps = {p.upper().replace('X', 'x') for p in w.PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)', definitions[s:e])[1])}
        assert ps == {p for p, v in after.items() if v[0] == state}
    for path, text in texts.items():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}'), path
    manifest = {p: dict(before=before[p], after=after[p]) for p in before if before[p] != after[p]}
    report = dict(changed_provinces=len(manifest), connectivity=connectivity,
                  country_populations=dict(country_pops), agriculture_before=agriculture(before),
                  agriculture_after=agriculture(after), capitals=CAPITALS,
                  bloc='GENSOKYO_BARRIER_NETWORK', leader='HAKR', subject_type='vassal', subjects=subjects,
                  total_population=19610000, cavern_population=10000,
                  industry_resources_arable_and_adjacencies='unchanged', game_launch='not tested')
    preview(after)
    w.OUT.mkdir(exist_ok=True, parents=True)
    (w.OUT / (PREFIX + '_manifest.json')).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    if '--apply' in sys.argv:
        backup = w.ROOT / ('docs/backups/southern_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        for path, data in originals.items():
            if data is not None:
                target = backup / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        backup.mkdir(exist_ok=True, parents=True)
        (backup / 'new_files.json').write_text(json.dumps([p for p, data in originals.items() if data is None], indent=2), encoding='utf-8')
        for path, text in texts.items():
            target = w.ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'\xef\xbb\xbf' + text.replace('\r\n', '\n').encode('utf-8'))
            assert target.read_text(encoding='utf-8-sig') == text.replace('\r\n', '\n')
        report['backup'] = str(backup)
        report['applied'] = True
    else:
        report['applied'] = False
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
