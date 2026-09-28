"""Reviewed province manifest and a small Sanzu tributary on the vanilla river grid.

Run without arguments to prepare the preview; --apply uses that frozen manifest.
All original game files are backed up before any write.
"""
import collections
import datetime
import heapq
import json
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import west_coast_draft as w
import lake_coast_revision as lc

PREFIX = 'ridge_sanzu_v1'
WEST = 'STATE_CHIREIDEN_WEST_GATE'
GATE = ['x084DA5', 'xD68DC4']
HISTORY = 'common/history/states/00_states.txt'
MAP = 'map_data/state_regions/tot_13_australasia_chireiden.txt'
POPS = 'common/history/pops/13_australasia.txt'
BUILDINGS = 'common/history/buildings/13_australasia.txt'
STRATEGIC = 'common/strategic_regions/east_asia_strategic_regions.txt'
LOC = 'localization/replace/simp_chinese/map/tot_chireiden_states_l_simp_chinese.yml'
ADJ = 'map_data/adjacencies.csv'
DIP = 'common/history/diplomacy/00_subject_relationships.txt'
MIL = 'common/history/military_formations/00_generated_formations.txt'
MANIFEST = w.OUT / (PREFIX + '_manifest.json')


def prepare():
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    terrains = {m[1]: m[2] for m in re.finditer(
        r'(x[\da-fA-F]{6})\s*=\s*"([^"]+)"',
        (w.GAME / 'map_data/province_terrains.txt').read_text())}
    for p, (_, tag) in before.items():
        if tag not in ('WAS', 'MFSR', 'YKYM'):
            continue
        x, y, _ = lc.CTX['coords'][p]
        if tag == 'WAS':
            after[p][1] = 'MKAI' if x >= 6990 and y <= 2480 else 'RNGN' if y >= 2560 else 'UKDO'
        if tag == 'MFSR' and x >= 7505 and y <= 2808:
            after[p][1] = 'YKYM'
        if tag in ('MFSR', 'YKYM') and terrains[p] == 'desert' and x < 7390:
            if any(before[q][1] == 'CHRD' for q in lc.CTX['adj'][p]):
                after[p][1] = 'CHRD'
    # Two normal, adjoining provinces at the circled eastern edge of Higan.
    for p in GATE:
        assert before[p] == ['STATE_WESTERN_AUSTRALIA', 'HIGN']
        after[p] = [WEST, 'CHRD']
    changes = {p: dict(before=before[p], after=after[p]) for p in sorted(after)
               if before[p] != after[p]}
    MANIFEST.write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
    audit(before, after)
    lc.PREFIX = PREFIX
    lc.preview(after)
    rivers, river_report = river_draft()
    rivers.save(w.OUT / (PREFIX + '_rivers.png'), bits=8)
    river_preview(rivers, after)
    print(json.dumps(dict(changes=len(changes), river=river_report), indent=2))


def audit(before, after):
    result = {}
    for tag in ['UKDO', 'RNGN', 'MKAI', 'HIGN', 'CHRD', 'YKYM', 'MFSR']:
        ps = [p for p in lc.CTX['adj'] if after[p][1] == tag]
        groups = w.components(ps, lc.CTX['adj'])
        old = w.components([p for p in lc.CTX['adj'] if before[p][1] == tag], lc.CTX['adj'])
        if tag == 'MKAI':
            assert {frozenset(g) for g in groups[1:]} == {frozenset(g) for g in old[1:]}
        else:
            assert len(groups) == 1, (tag, groups[1:])
        result[tag] = dict(before=sum(v[1] == tag for v in before.values()),
                           after=len(ps), components=[len(g) for g in groups])
    assert not any(v[1] == 'WAS' for v in after.values())
    assert len(w.components(GATE, lc.CTX['adj'])) == 1
    assert any(after[q][1] == 'HIGN' for p in GATE for q in lc.CTX['adj'][p])
    assert any(after[q][1] == 'CHRD' and q not in GATE for p in GATE for q in lc.CTX['adj'][p])
    return result


def river_draft():
    """Follow the terrain downhill from the gate into the existing Higan river.

    Preserve the original indexed palette, source/merge conventions and global
    river network. The existing lower west-coast channel is widened slightly.
    """
    image = Image.open(w.GAME / 'map_data/rivers.png')
    a = np.array(image)
    assert image.mode == 'P' and image.size == (8192, 3616)
    Image.MAX_IMAGE_PIXELS = None
    height = np.array(Image.open(w.GAME / 'map_data/heightmap.png'))
    height = height[::2, ::2].astype(float)
    start = (6797, 2745)
    # Preserve the complete original tributary from (6803,2707) to its mouth.
    old_channel = {(6803, 2707)}
    todo = list(old_channel)
    while todo:
        x, y = todo.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q not in old_channel and 0 <= a[q[1], q[0]] <= 11:
                    old_channel.add(q)
                    todo.append(q)
    assert len(old_channel) > 100
    # Restrict to the small area between the gate and the downstream channel.
    bounds = (6735, 2725, 6805, 2754)
    # Gentle, hand-reviewed bends within the low valley; avoid a ruler-straight
    # tributary while retaining a strong penalty for crossing higher ridges.
    bends = [(6737, 2743), (6746, 2744), (6755, 2743), (6763, 2739),
             (6772, 2740), (6778, 2745), (6783, 2745), (6790, 2743), (6797, 2745)]
    dist = {start: 0}
    parents = {}
    heap = [(0, start)]
    goal = None
    while heap:
        cost, p = heapq.heappop(heap)
        if cost != dist[p]:
            continue
        if p in old_channel:
            goal = p
            break
        x, y = p
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            q = nx, ny = x + dx, y + dy
            if not (bounds[0] <= nx <= bounds[2] and bounds[1] <= ny <= bounds[3]):
                continue
            if a[ny, nx] != 255 and q not in old_channel:
                continue
            # Strong uphill penalty, plus a short route to the existing mouth.
            preferred_y = float(np.interp(nx, [v[0] for v in bends], [v[1] for v in bends]))
            weight = 1 + max(0, height[ny, nx] - height[y, x]) / 50 + abs(ny-preferred_y)*1.5
            new = cost + weight
            if new < dist.get(q, float('inf')):
                dist[q] = new
                parents[q] = p
                heapq.heappush(heap, (new, q))
    assert goal is not None
    path = [goal]
    while path[-1] != start:
        path.append(parents[path[-1]])
    path.reverse()
    out = a.copy()
    # Enlarge the existing medium and small channel without changing its route.
    for x, y in old_channel:
        if 3 <= out[y, x] <= 11:
            out[y, x] = max(5, min(int(out[y, x]) + 1, 6))
    for x, y in path[1:-1]:
        assert a[y, x] == 255
        out[y, x] = 3
    out[start[1], start[0]] = 0
    out[goal[1], goal[0]] = 1
    assert np.sum(out == 0) == np.sum(a == 0) + 1
    assert np.sum(out == 1) == np.sum(a == 1) + 1
    # The new source must be in the new gate, with a single river neighbour.
    provinces = Image.open(w.GAME / 'map_data/provinces.png').convert('RGB')
    code = 'x%02X%02X%02X' % provinces.getpixel(start)
    assert code in GATE, code
    result = Image.fromarray(out, mode='P')
    result.putpalette(image.getpalette())
    assert result.getpalette() == image.getpalette()
    report = dict(source=list(start), confluence=list(goal), new_branch_pixels=len(path),
                  old_channel_pixels=len(old_channel), changed_pixels=int(np.sum(out != a)),
                  source_height=int(height[start[1], start[0]]),
                  confluence_height=int(height[goal[1], goal[0]]),
                  local_uphill_steps=int(sum(height[q[1], q[0]] > height[p[1], p[0]]
                                            for p, q in zip(path, path[1:]))))
    (w.OUT / (PREFIX + '_river_manifest.json')).write_text(
        json.dumps(dict(report=report, path=path), indent=2), encoding='utf-8')
    return result, report


def river_preview(rivers, owners):
    b = (6650, 2670, 6850, 2800)
    p = np.array(Image.open(w.GAME / 'map_data/provinces.png').convert('RGB').crop(b), dtype=np.uint32)
    p = (p[:, :, 0] << 16) | (p[:, :, 1] << 8) | p[:, :, 2]
    a = np.array(rivers.crop(b))
    rgb = np.full((*p.shape, 3), (59, 80, 91), dtype=np.uint8)
    for code in lc.CTX['coords']:
        rgb[p == int(code[1:], 16)] = w.COLORS[owners[code][1]]
    edges = np.zeros(p.shape, bool)
    edges[:, 1:] |= p[:, 1:] != p[:, :-1]
    edges[1:, :] |= p[1:, :] != p[:-1, :]
    rgb[edges] = (60, 60, 60)
    rgb[a < 12] = (50, 140, 245)
    im = Image.fromarray(rgb).resize((1200, 780))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
    d.text((340, 350), '三途河', font=font, fill='white', stroke_width=1, stroke_fill='black')
    d.text((830, 440), '地灵殿西出口', font=font, fill='white', stroke_width=1, stroke_fill='black')
    d.text((200, 210), '彼岸', font=font, fill='white', stroke_width=1, stroke_fill='black')
    d.text((970, 640), '地穴地带', font=font, fill='white', stroke_width=1, stroke_fill='black')
    im.save(w.OUT / (PREFIX + '_west_detail.png'))


def history_block(state, owners, old=''):
    groups = collections.defaultdict(list)
    for p, (st, tag) in owners.items():
        if st == state:
            groups[tag].append(p)
    new = '\n\ts:' + state + ' = {\n'
    for tag, ps in sorted(groups.items()):
        ps.sort()
        new += '\t\tcreate_state = {\n\t\t\tcountry = c:' + tag + '\n\t\t\towned_provinces = {\n'
        new += ''.join('\t\t\t\t' + ' '.join(ps[i:i+12]) + '\n' for i in range(0, len(ps), 12))
        new += '\t\t\t}\n\t\t}\n'
    new += ''.join('\t\t' + line.strip() + '\n' for line in old.splitlines()
                   if ('add_homeland' in line or 'add_claim' in line) and 'c:WAS' not in line)
    if not old:
        new += '\t\tadd_homeland = cu:aborigine\n\t\tadd_homeland = cu:japanese\n'
    return new + '\t}\n'


def split_population(text, before, after):
    """Move only WAS's residents and the gate's share of Higan's residents.

    Preserve every culture's exact count, all other regions and existing entries.
    """
    s, e = w.block(text, 's:STATE_WESTERN_AUSTRALIA')
    part = text[s:e]
    gate_pops = []
    additions = collections.defaultdict(list)
    for tag in ['WAS', 'HIGN']:
        m = re.search(r'region_state:' + tag + r'\s*=\s*\{', part)
        end = w.close(part, part.index('{', m.start()))
        body = part[part.index('{', m.start())+1:end-1]
        original = [p for p in lc.CTX['coords'] if before[p] == ['STATE_WESTERN_AUSTRALIA', tag]]
        dest = collections.defaultdict(float)
        for p in original:
            dest[tuple(after[p])] += lc.CTX['coords'][p][2]
        total_area = sum(dest.values())
        retained = []
        for pm in re.finditer(r'create_pop\s*=\s*\{', body):
            pop = body[pm.start():w.close(body, body.index('{', pm.start()))]
            size = int(re.search(r'\bsize\s*=\s*(\d+)', pop)[1])
            allocation = {d: int(size*area/total_area) for d, area in dest.items()}
            residual = size - sum(allocation.values())
            ranking = sorted(dest, key=lambda d: (-(size*dest[d]/total_area-allocation[d]), d))
            for d in ranking[:residual]:
                allocation[d] += 1
            assert sum(allocation.values()) == size
            for (state, owner), n in allocation.items():
                if not n:
                    continue
                value = re.sub(r'\bsize\s*=\s*\d+', 'size = ' + str(n), pop)
                if state == WEST:
                    gate_pops.append(value)
                elif owner == tag:
                    retained.append(value)
                else:
                    additions[owner].append(value)
        replacement = '\n\t\tregion_state:' + tag + ' = {\n' + '\n'.join(retained) + '\n\t\t}\n' if retained else ''
        part = part[:m.start()] + replacement + part[end:]
    for tag, pops in additions.items():
        m = re.search(r'region_state:' + tag + r'\s*=\s*\{', part)
        if m:
            end = w.close(part, part.index('{', m.start()))
            part = part[:end-1] + '\n' + '\n'.join(pops) + '\n\t\t' + part[end-1:]
        else:
            pos = part.rfind('}')
            part = part[:pos] + '\n\t\tregion_state:' + tag + ' = {\n' + '\n'.join(pops) + '\n\t\t}\n' + part[pos:]
    text = text[:s] + part + text[e:]
    pos = text.rfind('}')
    text = text[:pos] + '\n\ts:' + WEST + ' = {\n\t\tregion_state:CHRD = {\n' + '\n'.join(gate_pops) + '\n\t\t}\n\t}\n' + text[pos:]
    return text


def pop_totals(text):
    totals = collections.Counter()
    for m in re.finditer(r'create_pop\s*=\s*\{', text):
        part = text[m.start():w.close(text, text.index('{', m.start()))]
        culture = re.search(r'culture\s*=\s*(\w+)', part)[1]
        totals[culture] += int(re.search(r'\bsize\s*=\s*(\d+)', part)[1])
    return totals


def apply():
    changes = json.loads(MANIFEST.read_text(encoding='utf-8'))
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    for p, change in changes.items():
        assert before[p] == change['before'], 'Stale manifest ' + p
        after[p] = change['after']
    connectivity = audit(before, after)
    names = [HISTORY, MAP, POPS, BUILDINGS, STRATEGIC, LOC, ADJ, DIP, MIL]
    originals = {f: (w.ROOT / f).read_bytes() if (w.ROOT / f).exists() else None for f in names}
    texts = {f: (data if data is not None else (w.GAME / f).read_bytes()).decode('utf-8-sig')
             for f, data in originals.items()}
    for state in sorted({v['before'][0] for v in changes.values()}):
        s, e = w.block(texts[HISTORY], 's:' + state)
        old = texts[HISTORY][s:e]
        texts[HISTORY] = texts[HISTORY][:s] + history_block(state, after, old) + texts[HISTORY][e:]
    pos = texts[HISTORY].rfind('}')
    texts[HISTORY] = texts[HISTORY][:pos] + history_block(WEST, after) + texts[HISTORY][pos:]
    s, e = w.block(texts[MAP], 'STATE_WESTERN_AUSTRALIA')
    part = texts[MAP][s:e]
    for p in GATE:
        part, n = re.subn(r'\b' + p + r'\b', '', part)
        assert n >= 1
    texts[MAP] = texts[MAP][:s] + part + texts[MAP][e:]
    texts[MAP] += '''
STATE_CHIREIDEN_WEST_GATE = {
    id = 3164
    subsistence_building = "building_subsistence_pasture"
    provinces = { x084DA5 xD68DC4 }
    city = "x084DA5"
    farm = "xD68DC4"
    mine = "x084DA5"
    wood = "xD68DC4"
    arable_land = 2
    arable_resources = { "building_livestock_ranch" }
}
'''
    s, e = w.block(texts[STRATEGIC], 'region_oceania')
    part = texts[STRATEGIC][s:e]
    custom = re.findall(r'(?m)^(STATE_CHIREIDEN_\w+)\s*=\s*\{', texts[MAP])
    part = re.sub(r'(\bstates\s*=\s*\{[^}]+)', lambda m: m[1] + ' ' + ' '.join(custom), part)
    texts[STRATEGIC] = texts[STRATEGIC][:s] + part + texts[STRATEGIC][e:]
    assert pop_totals(texts[POPS]) == pop_totals(split_population(texts[POPS], before, after))
    texts[POPS] = split_population(texts[POPS], before, after)
    for state in ['STATE_WESTERN_AUSTRALIA', WEST]:
        s, e = w.block(texts[POPS], 's:' + state)
        texts[POPS] = texts[POPS][:s] + '\n' + w.indent_block(texts[POPS][s:e]) + texts[POPS][e:]
    texts[POPS] = re.sub(r'(?m)[ \t]+$', '', texts[POPS])
    # The western remaining starting facilities pass to the coastal Hidden Realm.
    texts[BUILDINGS] = texts[BUILDINGS].replace('region_state:WAS', 'region_state:UKDO').replace('c:WAS', 'c:UKDO')
    texts[DIP], n = re.subn(r'\s*# Colony of Western Australia\s*create_diplomatic_pact\s*=\s*\{\s*country\s*=\s*c:WAS\s*type\s*=\s*colony\s*\}', '', texts[DIP])
    assert n == 1
    s, e = w.block(texts[DIP], 'c:WAS')
    texts[DIP] = texts[DIP][:s] + texts[DIP][e:]
    m = re.search(r'(?m)^\s*c:WAS\s*\?=\s*\{', texts[MIL])
    end = w.close(texts[MIL], texts[MIL].index('{', m.start()))
    texts[MIL] = texts[MIL][:m.start()] + texts[MIL][end:]
    texts[LOC] += '''
 STATE_CHIREIDEN_WEST_GATE: "三途河地底出口"
 HUB_NAME_STATE_CHIREIDEN_WEST_GATE_city: "三途河渡口"
 HUB_NAME_STATE_CHIREIDEN_WEST_GATE_farm: "西境补给站"
 HUB_NAME_STATE_CHIREIDEN_WEST_GATE_mine: "彼岸升降井"
 HUB_NAME_STATE_CHIREIDEN_WEST_GATE_wood: "渡口林地"
'''
    texts[ADJ] += '\nx084DA5;x1622EC;sea;-1;6797;2745;7150;2760;;Chireiden Sanzu western gate underground passage\n'
    assert w.ownership(texts[HISTORY]) == after
    targets = sorted({v['before'][0] for v in changes.values()} | {WEST})
    vanilla = (w.GAME / 'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    for state in targets:
        source = texts[MAP] if re.search(r'(?m)^' + state + r'\s*=', texts[MAP]) else vanilla
        s, e = w.block(source, state)
        defined = set(w.PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)', source[s:e])[1]))
        s, e = w.block(texts[HISTORY], 's:' + state)
        assigned = w.PROV.findall(texts[HISTORY][s:e])
        assert len(assigned) == len(set(assigned)), state
        assert defined == set(assigned), ('State coverage', state)
    for text in texts.values():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}')
        assert not re.search(r'\bc:WAS\b|region_state:WAS\b|WAS_army|WAS_fleet', text)
    definitions = (w.ROOT / 'common/country_definitions/tot_countries.txt').read_text(encoding='utf-8-sig')
    for tag in connectivity:
        s, e = w.block(definitions, tag)
        capital = re.search(r'capital\s*=\s*(STATE_\w+)', definitions[s:e])[1]
        assert any(v == [capital, tag] for v in after.values()), ('Capital', tag)
    # Validate each gate has a passable route into the cavern anchor, keeping the
    # desert's original impassable flags untouched.
    impassable = {p for body in re.findall(r'\bimpassable\s*=\s*\{([^}]+)', texts[MAP]) for p in w.PROV.findall(body)}
    assert not set(GATE) & impassable and 'x1622EC' not in impassable
    links = {p: list(v) for p, v in lc.CTX['adj'].items()}
    for line in texts[ADJ].splitlines():
        fields = line.split(';')
        if len(fields) >= 3 and fields[0] in links and fields[1] in links:
            links[fields[0]].append(fields[1]); links[fields[1]].append(fields[0])
    allowed = {p for p in links if after[p][1] == 'CHRD' and p not in impassable}
    group = next(g for g in w.components(allowed, links) if 'x1622EC' in g)
    assert set(GATE) <= set(group)
    river_file = 'map_data/rivers.png'
    river_original = (w.ROOT / river_file).read_bytes() if (w.ROOT / river_file).exists() else None
    assert river_original is None, 'Do not overwrite an existing river mod'
    river_bytes = (w.OUT / (PREFIX + '_rivers.png')).read_bytes()
    backup = w.ROOT / 'docs/backups' / ('ridge_sanzu_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for f, data in originals.items():
        if data is not None:
            dest = backup / f
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    (backup / 'new_files.json').write_text(json.dumps([f for f, v in originals.items() if v is None] + [river_file], indent=2), encoding='utf-8')
    for f, text in texts.items():
        original = originals[f] if originals[f] is not None else (w.GAME / f).read_bytes()
        text = text.replace('\r\n', '\n')
        if b'\r\n' in original:
            text = text.replace('\n', '\r\n')
        dest = w.ROOT / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8'))
    (w.ROOT / river_file).write_bytes(river_bytes)
    assert lc.current() == after
    report = dict(backup=str(backup), provinces_changed=len(changes), connectivity=connectivity,
                  checks=['province coverage', 'unique ownership', 'no new enclaves', 'valid capitals',
                          'western gate underground route', 'exact culture population totals preserved',
                          'WAS references removed in touched histories', 'original indexed river palette'],
                  game_launch='not tested', files=names + [river_file])
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    apply() if '--apply' in sys.argv else prepare()
