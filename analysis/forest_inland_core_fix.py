"""Keep the forest inland and place the old underground anchor in the capital.

Explicit province lists reviewed against the province raster. Does not change
building eligibility, vegetation, resources, populations or desert terrain.
"""
import collections
import datetime
import json
import re
from PIL import Image
import west_coast_draft as w
import lake_coast_revision as lc
import ridge_sanzu_revision as rs

COAST = ['x027214', 'x276C93', 'x740B78', 'x91A2E2', 'xD060D0', 'xE8CAF7']
ANCHOR = 'x37ACCC'
PREFIX = 'forest_inland_core_v2'


def apply():
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    for p in COAST:
        assert before[p] == ['STATE_NEW_SOUTH_WALES', 'MFSR'], (p, before[p])
        after[p][1] = 'HITO'
    assert before['x1622EC'] == ['STATE_CHIREIDEN_CAVERN_ZONE', 'CHRD']
    assert before[ANCHOR] == ['STATE_QUEENSLAND', 'CHRD']
    after['x1622EC'][0] = 'STATE_CHIREIDEN_CAPITAL'
    after[ANCHOR][0] = 'STATE_CHIREIDEN_CAVERN_ZONE'
    changes = {p: dict(before=before[p], after=after[p]) for p in after if before[p] != after[p]}
    connectivity = {}
    for tag in ['HITO', 'MFSR', 'CHRD']:
        groups = w.components([p for p in lc.CTX['adj'] if after[p][1] == tag], lc.CTX['adj'])
        assert len(groups) == 1, (tag, groups[1:])
        connectivity[tag] = [len(g) for g in groups]
    assert len(w.components([p for p in lc.CTX['adj'] if after[p][0] == 'STATE_CHIREIDEN_CAPITAL'], lc.CTX['adj'])) == 1
    names = [rs.HISTORY, rs.MAP, rs.ADJ, rs.LOC]
    originals = {f: (w.ROOT / f).read_bytes() for f in names}
    texts = {f: b.decode('utf-8-sig') for f, b in originals.items()}
    states = sorted({v['before'][0] for v in changes.values()} | {v['after'][0] for v in changes.values()})
    for state in states:
        s, e = w.block(texts[rs.HISTORY], 's:' + state)
        old = texts[rs.HISTORY][s:e]
        texts[rs.HISTORY] = texts[rs.HISTORY][:s] + rs.history_block(state, after, old) + texts[rs.HISTORY][e:]
    def rewrite_list(state, remove, add):
        s, e = w.block(texts[rs.MAP], state)
        part = texts[rs.MAP][s:e]
        m = re.search(r'\bprovinces\s*=\s*\{([^}]+)\}', part)
        ps = w.PROV.findall(m[1])
        assert set(remove) <= set(ps)
        ps = sorted((set(ps) - set(remove)) | set(add))
        new = 'provinces = {\n' + ''.join('\t\t' + ' '.join(ps[i:i+10]) + '\n' for i in range(0, len(ps), 10)) + '\t}'
        part = part[:m.start()] + new + part[m.end():]
        if state == 'STATE_CHIREIDEN_CAVERN_ZONE':
            part = re.sub(r'((?:city|farm|mine|wood)\s*=\s*")x1622EC(")', r'\g<1>' + ANCHOR + r'\2', part)
        texts[rs.MAP] = texts[rs.MAP][:s] + part + texts[rs.MAP][e:]
    rewrite_list('STATE_QUEENSLAND', [ANCHOR], [])
    rewrite_list('STATE_CHIREIDEN_CAPITAL', [], ['x1622EC'])
    rewrite_list('STATE_CHIREIDEN_CAVERN_ZONE', ['x1622EC'], [ANCHOR])
    x, y, _ = lc.CTX['coords'][ANCHOR]
    image = Image.open(w.GAME / 'map_data/provinces.png').convert('RGB')
    assert 'x%02X%02X%02X' % image.getpixel((int(x), int(y))) == ANCHOR
    texts[rs.ADJ] += ('\nx1622EC;' + ANCHOR + ';sea;-1;7150;2760;' + str(int(x)) + ';' + str(int(y)) + ';;Chireiden capital to eastern cavern hub underground passage\n')
    texts[rs.LOC] = texts[rs.LOC].replace('HUB_NAME_STATE_CHIREIDEN_CAVERN_ZONE_city: "旧地狱升降井"',
                                         'HUB_NAME_STATE_CHIREIDEN_CAVERN_ZONE_city: "东缘地下主井"')
    assert w.ownership(texts[rs.HISTORY]) == after
    vanilla = (w.GAME / 'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    for state in states:
        source = texts[rs.MAP] if re.search(r'(?m)^' + state + r'\s*=', texts[rs.MAP]) else vanilla
        s, e = w.block(source, state)
        part = source[s:e]
        defined = set(w.PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)', part)[1]))
        assigned = [p for p, v in after.items() if v[0] == state]
        assert defined == set(assigned), state
        for m in re.finditer(r'\b(city|farm|mine|wood|port)\s*=\s*"(x[\dA-F]{6})"', part):
            assert m[2] in defined, (state, m[1], m[2])
    imp = {p for body in re.findall(r'\bimpassable\s*=\s*\{([^}]+)', texts[rs.MAP]) for p in w.PROV.findall(body)}
    assert 'x1622EC' not in imp and ANCHOR not in imp
    assert re.findall(r'\bimpassable\s*=\s*\{[^}]+\}', texts[rs.MAP]) == re.findall(r'\bimpassable\s*=\s*\{[^}]+\}', originals[rs.MAP].decode('utf-8-sig'))
    cavern = {p for p, v in after.items() if v[0] == 'STATE_CHIREIDEN_CAVERN_ZONE'}
    assert cavern - imp == {ANCHOR}
    # All existing gates and the replacement cavern hub reach the capital.
    links = {p: list(q) for p, q in lc.CTX['adj'].items()}
    for line in texts[rs.ADJ].splitlines():
        f = line.split(';')
        if len(f) > 2 and f[0] in links and f[1] in links:
            links[f[0]].append(f[1]); links[f[1]].append(f[0])
    groups = w.components([p for p in links if after[p][1] == 'CHRD' and p not in imp], links)
    main = next(g for g in groups if 'x6F472E' in g)
    assert {'x1622EC', ANCHOR, 'x5CDBBF', 'xD70795', 'x084DA5'} <= set(main)
    for f, text in texts.items():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}'), f
    backup = w.ROOT / 'docs/backups' / ('forest_core_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for f, b in originals.items():
        p = backup / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    for f, text in texts.items():
        text = text.replace('\r\n', '\n')
        if b'\r\n' in originals[f]:
            text = text.replace('\n', '\r\n')
        (w.ROOT / f).write_bytes((b'\xef\xbb\xbf' if originals[f].startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8'))
    assert lc.current() == after
    lc.PREFIX = PREFIX
    lc.preview(after)
    report = dict(backup=str(backup), changes=changes, connectivity=connectivity,
                  cavern_passable=[ANCHOR], checks=['state coverage', 'valid hubs', 'unchanged impassable provinces',
                  'continuous capital and country territory', 'capital and gate underground routes'], game_launch='not tested')
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    apply()
