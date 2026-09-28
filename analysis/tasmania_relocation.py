"""Reviewed island relocation; retains state geometry, resources and sea links.

Dry run creates previews and validates a frozen, explicit province selection.
--apply backs up runtime files before changing ownership/capitals/history scopes.
"""
import collections
import datetime
import hashlib
import json
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import west_coast_draft as w
import lake_coast_revision as lc
from population_arable_prototype import spans, split_size, pop_entries

PREFIX = 'tasmania_relocation_v1'
RED = ['x3AEC95', 'xCCBB53', 'xA03BDF', 'xCC9C60', 'x49E501',
       'xF835BF', 'xC0CE2A', 'x904030']
ICE = ['x068859', 'xBD6CF3', 'xCDE174', 'x1B76C4', 'x3127E5',
       'x1BC4A6', 'xC312BF', 'xC47E1B']
STATES = {'STATE_TASMANIA', 'STATE_VICTORIA', 'STATE_SOUTH_AUSTRALIA',
          'STATE_NORTH_ISLAND', 'STATE_SOUTH_ISLAND'}
CAPITALS = {'RDMK': 'STATE_TASMANIA', 'MIST': 'STATE_VICTORIA',
            'MTOU': 'STATE_NORTH_ISLAND', 'TENG': 'STATE_FIJI'}
FILES = ['common/history/states/00_states.txt', 'common/country_definitions/tot_countries.txt',
         'common/history/pops/13_australasia.txt', 'common/history/buildings/13_australasia.txt']


def replace_state(text, state, replacement):
    match = next((m, end) for m, _, end in spans(text, r's:(STATE_\w+)\s*=\s*\{') if m[1] == state)
    m, end = match
    return text[:m.start()] + replacement + text[end:]


def state_history(state, owners, original):
    groups = collections.defaultdict(list)
    for province, (region, tag) in owners.items():
        if region == state:
            groups[tag].append(province)
    lines = ['s:{} = {{'.format(state)]
    for tag, provinces in sorted(groups.items()):
        lines += ['\t\tcreate_state = {', '\t\t\tcountry = c:' + tag, '\t\t\towned_provinces = {']
        provinces.sort()
        lines += ['\t\t\t\t' + ' '.join(provinces[i:i + 12]) for i in range(0, len(provinces), 12)]
        lines += ['\t\t\t}', '\t\t}']
    lines += ['\t\t' + line.strip() for line in original.splitlines()
              if 'add_homeland' in line or 'add_claim' in line]
    return '\n'.join(lines + ['\t}'])


def prepare_owners():
    before = lc.current()
    after = {p: list(v) for p, v in before.items()}
    assert {v[1] for v in before.values() if v[0] == 'STATE_TASMANIA'} == {'MTOU'}
    assert {v[1] for v in before.values() if v[0] in ('STATE_NORTH_ISLAND', 'STATE_SOUTH_ISLAND')} == {'TENG'}
    for p, (state, tag) in before.items():
        if tag in ('RDMK', 'MIST'):
            assert state == 'STATE_SOUTH_AUSTRALIA'
            after[p][1] = 'CHRD'
        elif state == 'STATE_TASMANIA':
            after[p][1] = 'RDMK'
        elif state in ('STATE_NORTH_ISLAND', 'STATE_SOUTH_ISLAND'):
            after[p][1] = 'MTOU'
    for p in RED + ICE:
        assert before[p][0] == 'STATE_VICTORIA' and before[p][1] in ('HITO', 'EITR')
        after[p][1] = 'RDMK' if p in RED else 'MIST'
    return before, after


def connectivity(after):
    links = {p: list(neighbors) for p, neighbors in lc.CTX['adj'].items()}
    for line in (w.ROOT / 'map_data/adjacencies.csv').read_text(encoding='utf-8-sig').splitlines():
        fields = line.split(';')
        if len(fields) < 3:
            continue
        a, b = [code.upper().replace('X', 'x') for code in fields[:2]]
        if a in links and b in links:
            links[a].append(b)
            links[b].append(a)
    report = {}
    for tag in ('RDMK', 'MIST', 'HITO', 'EITR', 'KZNH', 'MTOU'):
        ps = [p for p in links if after[p][1] == tag]
        groups = w.components(ps, links)
        assert len(groups) == 1, (tag, groups[1:])
        report[tag] = [len(g) for g in groups]
    assert after['x904030'][1] == after['x114030'][1] == 'RDMK'
    assert 'x114030' in links['x904030'], 'Existing Bass Strait route must remain usable'
    assert {after[p][1] for p in ICE} == {'MIST'}
    assert any(after[q][1] == 'RDMK' for p in ICE for q in links[p]), 'The two relocated factions must border each other'
    # The original mansion includes the two natural Kangaroo Island provinces.
    groups = w.components([p for p in links if after[p][1] == 'CHRD'], links)
    assert groups[1:] == [sorted(['xC58F87', 'xD0A0D0'])], groups[1:]
    report['CHRD'] = dict(mainland_connected=True, existing_kangaroo_island=['xC58F87', 'xD0A0D0'])
    return report


def transfer_population(text):
    # Existing residents remain in their state; explicit shares for the mainland
    # border revision avoid treating raw raster area as population density.
    transfers = {
        ('STATE_TASMANIA', 'MTOU'): {'RDMK': 1},
        ('STATE_NORTH_ISLAND', 'TENG'): {'MTOU': 1},
        ('STATE_SOUTH_ISLAND', 'TENG'): {'MTOU': 1},
        ('STATE_SOUTH_AUSTRALIA', 'RDMK'): {'CHRD': 1},
        ('STATE_SOUTH_AUSTRALIA', 'MIST'): {'CHRD': 1},
        ('STATE_VICTORIA', 'HITO'): {'HITO': 300000, 'RDMK': 200000, 'MIST': 100000},
        ('STATE_VICTORIA', 'EITR'): {'EITR': 600000, 'RDMK': 50000, 'MIST': 50000},
    }
    replacements = []
    for sm, body, end in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
        state = sm[1]
        if state not in STATES:
            continue
        groups = collections.defaultdict(collections.Counter)
        old_profiles = collections.Counter()
        for tm, owner, _ in spans(body, r'region_state:(\w+)\s*=\s*\{'):
            for _, pop, _ in spans(owner, r'create_pop\s*=\s*\{'):
                fields = dict(re.findall(r'(\w+)\s*=\s*(\w+)', pop))
                assert set(fields) <= {'culture', 'religion', 'size'}
                profile = (fields['culture'], fields.get('religion'))
                size = int(fields['size'])
                old_profiles[profile] += size
                for tag, count in split_size(size, transfers.get((state, tm[1]), {tm[1]: 1})).items():
                    groups[tag][profile] += count
        assert sum(sum(v.values()) for v in groups.values()) == sum(old_profiles.values())
        check = collections.Counter()
        lines = ['s:{} = {{'.format(state)]
        for tag, cohorts in sorted(groups.items()):
            lines.append('\t\tregion_state:{} = {{'.format(tag))
            for (culture, religion), size in sorted(cohorts.items(), key=lambda kv: (kv[0][0], kv[0][1] or '')):
                if size == 0:
                    continue
                check[culture, religion] += size
                fields = 'culture = {}'.format(culture) + (' religion = {}'.format(religion) if religion else '')
                lines.append('\t\t\tcreate_pop = {{ {} size = {} }}'.format(fields, size))
            lines.append('\t\t}')
        assert check == old_profiles, ('Population or culture changed', state)
        replacements.append((sm.start(), end, '\n'.join(lines + ['\t}'])))
    for start, end, body in reversed(replacements):
        text = text[:start] + body + text[end:]
    return text


def transfer_building_scopes(text):
    # Relabel existing structures in the places that fully change hands.
    # No new building, level or production method is introduced.
    transfers = {'STATE_TASMANIA': {'TAS': 'RDMK', 'MTOU': 'RDMK'},
                 'STATE_NORTH_ISLAND': {'TENG': 'MTOU'},
                 'STATE_SOUTH_ISLAND': {'TENG': 'MTOU'},
                 'STATE_SOUTH_AUSTRALIA': {'RDMK': 'CHRD', 'MIST': 'CHRD', 'SAS': 'CHRD', 'KAU': 'CHRD'}}
    for state, tags in transfers.items():
        for sm, body, end in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
            if sm[1] != state:
                continue
            old = text[sm.start():end]
            replacement = old
            for old_tag, new_tag in tags.items():
                replacement = re.sub(r'(region_state:|c:)' + old_tag + r'\b', r'\g<1>' + new_tag, replacement)
            text = text[:sm.start()] + replacement + text[end:]
            break
    return text


def preview(owners):
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    source = Image.open(w.GAME / 'map_data/provinces.png').convert('RGB')
    for suffix, bounds, scale in [('map', (6570, 2400, 8540, 3370), 1),
                                  ('detail', (7280, 2870, 7540, 3185), 4)]:
        rgb_source = np.asarray(source.crop(bounds), dtype=np.uint32)
        a = (rgb_source[:, :, 0] << 16) | (rgb_source[:, :, 1] << 8) | rgb_source[:, :, 2]
        rgb = np.full((*a.shape, 3), (55, 78, 88), dtype=np.uint8)
        for p, (_, tag) in owners.items():
            rgb[a == int(p[1:], 16)] = w.COLORS.get(tag, (220, 220, 211))
        edge = np.zeros(a.shape, bool)
        edge[:, 1:] |= a[:, 1:] != a[:, :-1]
        edge[1:, :] |= a[1:, :] != a[:-1, :]
        owned = np.any(rgb != (55, 78, 88), axis=2)
        rgb[edge & owned] = (45, 50, 50)
        im = Image.fromarray(rgb).resize((a.shape[1] * scale, a.shape[0] * scale))
        d = ImageDraw.Draw(im)
        names = dict(w.NAMES, MIST='冰之领地')
        for tag in names:
            codes = [int(p[1:], 16) for p, (_, owner) in owners.items() if owner == tag]
            yy, xx = np.where(np.isin(a, codes))
            if len(xx):
                x, y = int(np.mean(xx)) * scale, int(np.mean(yy)) * scale
                d.text((x, y), names[tag], font=font, anchor='mm', fill='black', stroke_width=1, stroke_fill='white')
        if suffix == 'detail':
            for p, q in [('x904030', 'x114030'), ('x114030', 'xBA7909')]:
                pts = [((lc.CTX['coords'][c][0] - bounds[0]) * scale,
                        (lc.CTX['coords'][c][1] - bounds[1]) * scale) for c in (p, q)]
                d.line(pts, fill=(242, 156, 94), width=4)
            d.text((25, im.height - 40), '橙线：现有海峡连接', font=font, fill='white')
        im.save(w.OUT / (PREFIX + '_' + suffix + '.png'))


def main():
    before, after = prepare_owners()
    connection_report = connectivity(after)
    originals = {path: (w.ROOT / path).read_bytes() for path in FILES}
    texts = {path: data.decode('utf-8-sig') for path, data in originals.items()}
    for state in sorted(STATES):
        m, _, end = next(v for v in spans(texts[FILES[0]], r's:(STATE_\w+)\s*=\s*\{') if v[0][1] == state)
        old = texts[FILES[0]][m.start():end]
        texts[FILES[0]] = replace_state(texts[FILES[0]], state, state_history(state, after, old))
    assert w.ownership(texts[FILES[0]]) == after
    for tag, capital in CAPITALS.items():
        start, end = w.block(texts[FILES[1]], tag)
        part = re.sub(r'capital\s*=\s*STATE_\w+', 'capital = ' + capital, texts[FILES[1]][start:end])
        if tag == 'RDMK': part = part.replace('# 雾之湖红魔领', '# 红魔馆：塔斯马尼亚本部与巴斯海峡对岸据点')
        if tag == 'MIST': part = part.replace('# 雾之湖', '# 冰之领地：巴斯海峡对岸海湾')
        if tag == 'MTOU': part = part.replace('# 月都前哨', '# 月都：新西兰两岛')
        if tag == 'TENG': part = part.replace('# 天界', '# 天界：斐济与瓦努阿图')
        texts[FILES[1]] = texts[FILES[1]][:start] + part + texts[FILES[1]][end:]
        assert any(state == capital and owner == tag for state, owner in after.values()), tag
    texts[FILES[2]] = transfer_population(texts[FILES[2]])
    texts[FILES[3]] = transfer_building_scopes(texts[FILES[3]])
    def building_signature(text):
        return collections.Counter(re.sub(r'(?:region_state:|c:)\w+', 'COUNTRY', body).strip()
                                   for _, body, _ in spans(text, r'create_building\s*=\s*\{'))
    assert building_signature(originals[FILES[3]].decode('utf-8-sig')) == building_signature(texts[FILES[3]])
    original_pops = {p: p.read_text(encoding='utf-8-sig') for p in (w.ROOT / 'common/history/pops').glob('*.txt')}
    before_entries = pop_entries(original_pops)
    after_entries = pop_entries({**original_pops, w.ROOT / FILES[2]: texts[FILES[2]]})
    profile = lambda rows: collections.Counter((state, culture, religion) for state, _, culture, religion, _ in rows)
    def totals(rows):
        result = collections.Counter()
        for state, tag, culture, religion, size in rows:
            result[state, culture, religion] += size
        return result
    assert totals(before_entries) == totals(after_entries)
    pairs = set(map(tuple, after.values()))
    country_pops = collections.Counter()
    for state, tag, _, _, size in after_entries:
        assert (state, tag) in pairs, (state, tag)
        country_pops[tag] += size
    assert sum(country_pops.values()) == 19610000
    assert sum(size for state, _, _, _, size in after_entries if state == 'STATE_CHIREIDEN_CAVERN_ZONE') == 10000
    # Province coverage must match the effective mod state definitions exactly.
    region = (w.ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt').read_text(encoding='utf-8-sig')
    for state in STATES:
        start, end = w.block(region, state)
        defined = set(p.upper().replace('X', 'x') for p in w.PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)', region[start:end])[1]))
        assert defined == {p for p, (st, _) in after.items() if st == state}, state
    for path, text in texts.items():
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}'), path
    changes = {p: dict(before=before[p], after=after[p]) for p in before if before[p] != after[p]}
    summary = dict(changed_provinces=len(changes), mainland_taken_from=dict(collections.Counter(before[p][1] for p in RED + ICE)),
                   country_populations=dict(country_pops), connectivity=connection_report, total_population=19610000,
                   capitals=CAPITALS, game_launch='not tested', resource_and_arable_changes=False,
                   population_policy='Existing residents stay in their states; mainland shares explicitly apportioned. No population added or deleted.')
    w.OUT.mkdir(parents=True, exist_ok=True)
    preview(after)
    (w.OUT / (PREFIX + '_manifest.json')).write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if '--apply' not in sys.argv:
        print('Validated dry run; runtime files unchanged.')
        return
    backup = w.ROOT / 'docs/backups' / ('tasmania_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for path, data in originals.items():
        assert (w.ROOT / path).read_bytes() == data, ('Concurrent change', path)
        dest = backup / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    for path, text in texts.items():
        text = text.replace('\r\n', '\n')
        if b'\r\n' in originals[path]: text = text.replace('\n', '\r\n')
        (w.ROOT / path).write_bytes((b'\xef\xbb\xbf' if originals[path].startswith(b'\xef\xbb\xbf') else b'') + text.encode('utf-8'))
    assert lc.current() == after
    written_pops = {p: p.read_text(encoding='utf-8-sig') for p in original_pops}
    assert collections.Counter(pop_entries(written_pops)) == collections.Counter(after_entries)
    summary.update(backup=str(backup), status='applied; static checks passed; new-save validation pending',
                   files=FILES, original_sha256={p: hashlib.sha256(data).hexdigest() for p, data in originals.items()})
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = ['# 红魔馆、冰之领地、月都与天界迁移第一版', '',
            '已实装；尚未进行游戏内新开局验证。', '',
            '- 红魔馆：塔斯马尼亚全岛及维多利亚西南8省，首都在塔斯马尼亚。',
            '- 冰之领地：维多利亚南部海湾及相邻内陆8省，首都在维多利亚，与红魔馆相邻。',
            '- 月都：接管新西兰南北两岛，首都在北岛。',
            '- 天界：保留东北方向的斐济、瓦努阿图，首都移到斐济。',
            '- 两者原南澳领地共57省移交地灵殿，地灵殿本部与地穴保持现有设置。', '',
            '大陆新增领地共16省，其中13省取自人里、3省取自永远亭。花田与博丽没有改动。发现会被切断的两个人里省份一并划给冰之领地，修复后人里、永远亭、冰之领地均保持连续。', '',
            '使用现有巴斯海峡连接，没有新增海峡、可通行沙漠或省份。红魔馆从大陆据点经西侧小岛可到塔斯马尼亚本岛。月都两岛也沿用现有海峡连接。地灵殿接管的原红魔馆领地包含原有袋鼠岛，属于自然离岛。', '',
            '人口随土地调整归属，州内文化／宗教总量及全域1,961万人保持不变；地穴仍为1万人。迁移后国家人口与上一版草案不同，需要继续平衡。现有建筑只同步归属，数量、生产方式、产业配置不变；耕地、矿藏、地形、河流和植被均未修改。', '',
            '| 国家 | 当前开局人口 |', '|---|---:|']
    for tag, size in sorted(country_pops.items(), key=lambda v: -v[1]):
        rows.append('| {}（{}） | {:,} |'.format('冰之领地' if tag == 'MIST' else w.NAMES[tag], tag, size))
    rows += ['', '备份：`{}`'.format(backup), '', '地图预览：tasmania_relocation_v1_map.png；南部省份详图：tasmania_relocation_v1_detail.png。', '']
    (w.OUT / (PREFIX + '.md')).write_text('\n'.join(rows), encoding='utf-8')
    print('Applied; backup:', backup)


if __name__ == '__main__':
    main()
