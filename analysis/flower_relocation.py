"""Move the compact sunflower territory west of Eientei without changing state data."""
import collections
import datetime
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont
import west_coast_draft as w
import lake_coast_revision as lc

PREFIX = 'flower_v3'
FLOWER = ['x749129', 'x983611', 'xC67774', 'xF4CEF3', 'xC04012', 'x5DBF9E', 'xE0D3F9']


def prepare():
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    for p, (_, tag) in before.items():
        if tag == 'KZNH':
            after[p][1] = 'HITO'
    for p in FLOWER:
        assert before[p] == ['STATE_VICTORIA', 'HITO']
        after[p][1] = 'KZNH'
    vanilla = (w.GAME / 'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    s, e = w.block(vanilla, 'STATE_VICTORIA')
    prime = set(w.PROV.findall(re.search(r'prime_land\s*=\s*\{([^}]+)', vanilla[s:e])[1]))
    assert not (set(FLOWER) & prime), 'Avoid the vanilla prime-land provinces'
    for tag in ('KZNH', 'HITO', 'EITR'):
        ps = [p for p in lc.CTX['adj'] if after[p][1] == tag]
        groups = w.components(ps, lc.CTX['adj'])
        assert len(groups) == 1, (tag, groups[1:])
    neighbors = {after[q][1] for p in FLOWER for q in lc.CTX['adj'][p] if q not in FLOWER}
    assert {'HITO', 'EITR'} <= neighbors
    changes = {p: dict(before=before[p], after=after[p]) for p in sorted(after) if before[p] != after[p]}
    (w.OUT / (PREFIX + '_manifest.json')).write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
    lc.PREFIX = PREFIX
    lc.preview(after)
    full = Image.open(w.OUT / (PREFIX + '_map.png'))
    # The shared preview uses the fixed full-resolution map bounds (6570,2400,...).
    detail = full.crop(((7295-6570)*2, (2930-2400)*2, (7520-6570)*2, (3050-2400)*2)).resize((1125,600))
    detail.save(w.OUT / (PREFIX + '_detail.png'))
    stats = {}
    for tag in ('KZNH', 'HITO', 'MFSR', 'YKYM'):
        ps = [p for p in lc.CTX['coords'] if before[p][1] == tag]
        stats[tag] = dict(before=len(ps), after=sum(v[1] == tag for v in after.values()),
                          map_pixel_area_before=sum(lc.CTX['coords'][p][2] for p in ps))
    print(json.dumps(dict(stats=stats, selected=FLOWER, prime_land_taken=0, neighbors=sorted(neighbors)), indent=2))
    return before, after, changes, stats


def apply(before, after, changes, stats):
    names = ['common/history/states/00_states.txt', 'common/country_definitions/tot_countries.txt']
    originals = {f: (w.ROOT / f).read_bytes() for f in names}
    texts = {f: data.decode('utf-8-sig') for f, data in originals.items()}
    assert w.ownership(texts[names[0]]) == before
    targets = sorted({c['before'][0] for c in changes.values()})
    for state in targets:
        s, e = w.block(texts[names[0]], 's:' + state)
        old = texts[names[0]][s:e]
        groups = collections.defaultdict(list)
        for p, (st, tag) in after.items():
            if st == state:
                groups[tag].append(p)
        new = 's:' + state + ' = {\n'
        for tag, ps in sorted(groups.items()):
            ps.sort()
            new += '\tcreate_state = {\n\t\tcountry = c:' + tag + '\n\t\towned_provinces = {\n'
            new += ''.join('\t\t\t' + ' '.join(ps[i:i+12]) + '\n' for i in range(0, len(ps), 12))
            new += '\t\t}\n\t}\n'
        new += '\n' + ''.join('\t' + line.strip() + '\n' for line in old.splitlines()
                              if 'add_homeland' in line or 'add_claim' in line) + '}\n'
        texts[names[0]] = w.replace_block(texts[names[0]], 's:' + state, new)
    s, e = w.block(texts[names[1]], 'KZNH')
    new = re.sub(r'capital\s*=\s*STATE_\w+', 'capital = STATE_VICTORIA', texts[names[1]][s:e])
    texts[names[1]] = texts[names[1]][:s] + new + texts[names[1]][e:]
    assert w.ownership(texts[names[0]]) == after
    vanilla = (w.GAME / 'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    for state in targets:
        s, e = w.block(vanilla, state)
        defined = set(w.PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)', vanilla[s:e])[1]))
        s, e = w.block(texts[names[0]], 's:' + state)
        assigned = w.PROV.findall(texts[names[0]][s:e])
        assert len(assigned) == len(set(assigned))
        assert set(assigned) == defined
    assert [st for st, tag in after.values() if tag == 'KZNH'] == ['STATE_VICTORIA'] * len(FLOWER)
    for text in texts.values():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}')
    backup = w.ROOT / 'docs/backups' / ('flower_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for f, data in originals.items():
        dest = backup / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    for f, text in texts.items():
        text = text.replace('\r\n', '\n')
        if b'\r\n' in originals[f]:
            text = text.replace('\n', '\r\n')
        (w.ROOT / f).write_bytes((b'\xef\xbb\xbf' if originals[f].startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8'))
    assert lc.current() == after
    report = dict(backup=str(backup), changed_provinces=len(changes), stats=stats,
                  prime_land_taken=0, checks='coverage, uniqueness, connected borders and capital passed',
                  game_launch='not tested', files=names)
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    args = prepare()
    if '--apply' in sys.argv:
        apply(*args)
