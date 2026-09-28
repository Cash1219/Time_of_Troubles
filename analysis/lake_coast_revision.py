"""Hand-reviewed province relocation, leaving state geography/resources unchanged."""
import collections
import datetime
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import west_coast_draft as w

OUT = w.OUT
PREFIX = 'lake_coast_v2'
CTX = json.loads((OUT / 'west_coast_context.json').read_text(encoding='utf-8'))


def current():
    return w.ownership(w.HISTORY.read_text(encoding='utf-8-sig'))


def draft():
    before = current()
    after = {p: list(v) for p, v in before.items()}
    # Relocate the entire Garden, then select the contiguous belt north of Higan.
    for p, (state, tag) in before.items():
        if tag == 'RNGN':
            after[p][1] = 'WAS'
        if tag == 'MYRN':
            after[p][1] = 'HITO'
        if tag == 'SHRM':
            assert state == 'STATE_NORTH_ISLAND'
            after[p][1] = 'TENG'
        if tag == 'MIST':
            assert state == 'STATE_SOUTH_AUSTRALIA'
            after[p][1] = 'MYRN' if CTX['coords'][p][1] < 2900 else 'SHRM'
    for p, (state, tag) in before.items():
        if state == 'STATE_WESTERN_AUSTRALIA' and tag == 'WAS':
            x, y, _ = CTX['coords'][p]
            if y >= 2630:
                after[p][1] = 'RNGN'
    # Lake Gairdner's eastern shoreline; explicit IDs selected on province image.
    lake_east = ['xC15F2D', 'x6E4619', 'x27B268',
                 'xED145F', 'xC52B90', 'x3811BC']
    for p in lake_east:
        assert before[p] == ['STATE_SOUTH_AUSTRALIA', 'RDMK']
        after[p][1] = 'MIST'
    changes = {p: {'before': before[p], 'after': after[p]}
               for p in sorted(after) if before[p] != after[p]}
    (OUT / (PREFIX + '_manifest.json')).write_text(
        json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
    audit(after)
    preview(after)
    return after


def audit(owners):
    tags = ['RNGN', 'WAS', 'HIGN', 'MIST', 'RDMK', 'MYRN', 'SHRM', 'HITO']
    result = {}
    for tag in tags:
        ps = [p for p in CTX['adj'] if owners[p][1] == tag]
        groups = w.components(ps, CTX['adj'])
        neighbors = sorted({owners[q][1] for p in ps for q in CTX['adj'][p]
                            if owners[q][1] != tag})
        result[tag] = dict(provinces=len(ps), components=[len(g) for g in groups],
                           neighbors=neighbors,
                           small_components=groups[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    (OUT / (PREFIX + '_connectivity.json')).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def preview(owners):
    b = (6570, 2400, 7610, 3050)
    a = np.asarray(Image.open(w.GAME / 'map_data/provinces.png').convert('RGB').crop(b), dtype=np.uint32)
    a = (a[:, :, 0] << 16) | (a[:, :, 1] << 8) | a[:, :, 2]
    rgb = np.full((*a.shape, 3), (59, 80, 91), dtype=np.uint8)
    for p in CTX['coords']:
        rgb[a == int(p[1:], 16)] = w.COLORS.get(owners[p][1], (155, 155, 155))
    rgb[a == 0x01E1CB] = (65, 150, 195)
    edge = np.zeros(a.shape, bool)
    edge[:, 1:] |= a[:, 1:] != a[:, :-1]
    edge[1:, :] |= a[1:, :] != a[:-1, :]
    rgb[edge] = (70, 75, 75)
    im = Image.fromarray(rgb).resize((a.shape[1] * 2, a.shape[0] * 2))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    names = dict(w.NAMES, MIST='冰之领地')
    for tag in sorted(set(v[1] for v in owners.values())):
        ps = [p for p in CTX['coords'] if owners[p][1] == tag
              and b[0] <= CTX['coords'][p][0] < b[2]
              and b[1] <= CTX['coords'][p][1] < b[3]]
        if not ps:
            continue
        area = sum(CTX['coords'][p][2] for p in ps)
        x, y = [sum(CTX['coords'][p][k] * CTX['coords'][p][2] for p in ps) / area for k in (0, 1)]
        label = names.get(tag, tag)
        d.text(((x - b[0]) * 2, (y - b[1]) * 2), label,
               font=font, fill='black', stroke_width=1, stroke_fill='white')
    im.save(OUT / (PREFIX + '_map.png'))
    im.crop(((7100-b[0])*2, (2790-b[1])*2, (7390-b[0])*2, (3020-b[1])*2)).resize((870,690)).save(OUT / (PREFIX + '_lake_detail.png'))


def apply():
    changes = json.loads((OUT / (PREFIX + '_manifest.json')).read_text(encoding='utf-8'))
    files = ['common/history/states/00_states.txt',
             'common/country_definitions/tot_countries.txt',
             'localization/replace/simp_chinese/common/core/tot_countries_l_simp_chinese.yml',
             'common/history/pops/13_australasia.txt',
             'common/history/buildings/13_australasia.txt']
    originals = {f: (w.ROOT / f).read_bytes() for f in files}
    texts = {f: data.decode('utf-8-sig') for f, data in originals.items()}
    before = w.ownership(texts[files[0]])
    after = {p: list(v) for p, v in before.items()}
    for p, change in changes.items():
        assert before[p] == change['before'], 'Stale draft: ' + p
        assert change['before'][0] == change['after'][0], 'No state changes allowed'
        after[p] = change['after']
    check = audit(after)
    for tag in ['RNGN', 'WAS', 'HIGN', 'MIST', 'MYRN', 'SHRM', 'HITO']:
        assert len(check[tag]['components']) == 1, tag + ' has an enclave'
    # The two offshore Kangaroo Island provinces already belonged to the mansion.
    assert check['RDMK']['small_components'] == [
        sorted(['xC58F87', 'xD0A0D0'])], 'Unexpected mansion separation'
    for tag, neighbors in {'RNGN': ['HIGN'], 'MYRN': ['HITO', 'SHRM', 'MIST'],
                           'SHRM': ['HITO', 'MYRN'], 'MIST': ['RDMK', 'MYRN']}.items():
        assert set(neighbors) <= set(check[tag]['neighbors'])
    target_states = sorted({v['before'][0] for v in changes.values()})
    for state in target_states:
        start, end = w.block(texts[files[0]], 's:' + state)
        old = texts[files[0]][start:end]
        groups = collections.defaultdict(list)
        for p, (st, tag) in after.items():
            if st == state:
                groups[tag].append(p)
        new = 's:' + state + ' = {\n'
        for tag, ps in sorted(groups.items()):
            new += '\tcreate_state = {\n\t\tcountry = c:' + tag + '\n\t\towned_provinces = {\n'
            ps.sort()
            new += ''.join('\t\t\t' + ' '.join(ps[i:i+12]) + '\n' for i in range(0, len(ps), 12))
            new += '\t\t}\n\t}\n'
        new += '\n' + ''.join('\t' + line.strip() + '\n' for line in old.splitlines()
                              if 'add_homeland' in line or 'add_claim' in line)
        new += '}\n'
        texts[files[0]] = w.replace_block(texts[files[0]], 's:' + state, new)
    for tag in ('MYRN', 'SHRM'):
        start, end = w.block(texts[files[1]], tag)
        new = re.sub(r'capital\s*=\s*STATE_\w+', 'capital = STATE_SOUTH_AUSTRALIA',
                     texts[files[1]][start:end])
        if tag == 'SHRM':
            new = new.replace('神灵庙：新西兰北岛', '神灵庙：人间之里西侧')
        texts[files[1]] = texts[files[1]][:start] + new + texts[files[1]][end:]
    texts[files[2]], n = re.subn(r'(?m)^( MIST(?:_ADJ)?:) "雾之湖"', r'\1 "冰之领地"', texts[files[2]])
    assert n == 2
    # North Island inhabitants/buildings stay in place and pass to the caretaker.
    # Do not redistribute agriculture, resources, or populations elsewhere.
    for f in files[3:]:
        start, end = w.block(texts[f], 's:STATE_NORTH_ISLAND')
        new = texts[f][start:end].replace('region_state:SHRM', 'region_state:TENG')
        new = new.replace('c:SHRM', 'c:TENG')
        texts[f] = texts[f][:start] + new + texts[f][end:]
    assert w.ownership(texts[files[0]]) == after
    vanilla = (w.GAME / 'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    mod = (w.ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt').read_text(encoding='utf-8-sig')
    for state in target_states:
        source = mod if state in ('STATE_SOUTH_AUSTRALIA', 'STATE_WESTERN_AUSTRALIA') else vanilla
        s, e = w.block(source, state)
        defined = {p.upper().replace('X', 'x') for p in w.PROV.findall(
            re.search(r'\bprovinces\s*=\s*\{([^}]+)', source[s:e])[1])}
        s, e = w.block(texts[files[0]], 's:' + state)
        assigned = w.PROV.findall(texts[files[0]][s:e])
        assert len(assigned) == len(set(assigned)), 'Duplicate in ' + state
        assert defined == set(assigned), 'Coverage mismatch: ' + state
    for tag in ('MYRN', 'SHRM', 'MIST'):
        assert {st for st, owner in after.values() if owner == tag} == {'STATE_SOUTH_AUSTRALIA'}
    for tag in ('MYRN', 'SHRM', 'MIST', 'RNGN', 'HITO', 'RDMK', 'TENG'):
        s, e = w.block(texts[files[1]], tag)
        capital = re.search(r'capital\s*=\s*(STATE_\w+)', texts[files[1]][s:e])[1]
        assert any(st == capital and owner == tag for st, owner in after.values()), 'Capital: ' + tag
    # Confirm an actual passable province path through the proposed inland neighbors.
    impassable = set()
    for body in re.findall(r'\bimpassable\s*=\s*\{([^}]+)', mod):
        impassable.update(w.PROV.findall(body))
    allowed = {p for p in CTX['adj'] if after[p][1] in ('HAKR', 'HITO', 'MYRN', 'MIST')
               and p not in impassable}
    roots = [p for p in allowed if after[p][1] == 'HAKR']
    todo = collections.deque(roots)
    visited = set(roots)
    while todo:
        p = todo.popleft()
        for q in CTX['adj'][p]:
            if q in allowed and q not in visited:
                visited.add(q)
                todo.append(q)
    assert any(after[p][1] == 'MIST' for p in visited), 'No passable inland route'
    assert not any(p in impassable for p in after if after[p][1] == 'MIST')
    for f, text in texts.items():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}'), f
    backup = w.ROOT / 'docs/backups' / ('lake_coast_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    # Save all backups before the first game-file mutation.
    for f, data in originals.items():
        dest = backup / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    for f, text in texts.items():
        data = originals[f]
        text = text.replace('\r\n', '\n')
        if b'\r\n' in data:
            text = text.replace('\n', '\r\n')
        (w.ROOT / f).write_bytes((b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8'))
    assert current() == after
    report = dict(backup=str(backup), changed_provinces=len(changes),
                  checks='coverage, unique ownership, capitals, connectivity, passable inland route passed',
                  game_launch='not tested', files=files)
    (OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
    else:
        draft()
