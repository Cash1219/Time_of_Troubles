"""Replace several ruler-straight Australian borders with province-based curves.

The manifest crosses old colonial state lines while keeping every country in
its current region of Australia. No country, state region, resource, or hub is
created or removed. Run with --apply after reviewing the map preview.
"""

import collections
import json
import re
import sys

import west_coast_draft as map_tools


TRANSFER_GROUPS = {
    # The north-western and north-eastern vertical state lines.
    'UKDO': 'xEB33E0 x496C63 x95B834 xEF2A2F xFF6CAB',
    'MKAI': 'x0BC60B x0272A3 xD68CD6 xB88D8F x13B15E x0C61A7 xDBBA9A x43E2BC',
    'MRYA': 'xAA0A88 x1648A3 xA111C7',
    # South-western outback, northern ridge, and dry eastern slopes.
    'CHRD': '''xE3F266 xB828E8 xD00B01 x63B9AD x154243 xED6C3A xC04F4C xF0D3A9
        xA0F944 x068EEF x87D86F x88377F x25124E xF8AFCE x9DD644 x3623BB xB3A58A
        x194524 x86E23B x83420A x3DFB08 xFFDC67 xB938DB x7A2159 x8353FE
        xFE32CD xFA3609 x6C71E5 x4F4743
        x048DBF x19818E x1629D3 x2007B7 x642906 x6BBD1B xFFE893
        xF0194E xD9D32D x4FD1EF xA9C949 xF80313 xE85965 x0B16CD
        xB393C6 x570979 x8F751D xAC4B4D x03274B x1A44CA xC621A4
        xEEC767 xE8C984 xB73390 xDC539B''',
    # Small bends in the eastern interior and the south-eastern state line.
    'HITO': 'x14B847 xCC48C7',
    'MFSR': 'xA681A6 x482C38',
    'KZNH': 'xB6C06E x0F45F1 x225917',
}

TRANSFERS = {}
for new_tag, codes in TRANSFER_GROUPS.items():
    for province in codes.split():
        assert province not in TRANSFERS
        TRANSFERS[province] = new_tag

ROOT = map_tools.ROOT
HISTORY = map_tools.HISTORY
POPS = ROOT / 'common/history/pops/13_australasia.txt'
RAILWAYS = ROOT / 'common/history/buildings/tot_gensokyo_railways.txt'
REGIONS = ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt'
VANILLA_REGIONS = map_tools.GAME / 'map_data/state_regions/13_australasia.txt'
CONTEXT = json.loads((map_tools.OUT / 'west_coast_context.json').read_text(encoding='utf-8'))

# Fractions are deliberately low for desert and mountain border provinces.
# Existing residents are redistributed inside each state, so state totals stay exact.
POP_SHARES = {
    'STATE_WESTERN_AUSTRALIA': {'BYKR': {'CHRD': 0.02}},
    'STATE_NORTHERN_TERRITORY': {'MKAI': {'UKDO': 0.015, 'MRYA': 0.01, 'CHRD': 0.015}},
    'STATE_QUEENSLAND': {
        'MRYA': {'MKAI': 0.015, 'CHRD': 0.02},
        'YKYM': {'CHRD': 0.005},
        'MFSR': {'HITO': 0.01},
    },
    'STATE_VICTORIA': {'HITO': {'KZNH': 0.01}},
}


def clean_province(code):
    return code.upper().replace('X', 'x')


def state_ownership_block(state, owners, old):
    groups = collections.defaultdict(list)
    for province, (region, tag) in owners.items():
        if region == state:
            groups[tag].append(province)
    result = '\ts:' + state + ' = {\n'
    for tag, provinces in sorted(groups.items()):
        result += '\t\tcreate_state = {\n\t\t\tcountry = c:' + tag + '\n'
        result += '\t\t\towned_provinces = {\n'
        provinces.sort()
        for index in range(0, len(provinces), 12):
            result += '\t\t\t\t' + ' '.join(provinces[index:index + 12]) + '\n'
        result += '\t\t\t}\n\t\t}\n'
    result += ''.join('\t\t' + line.strip() + '\n' for line in old.splitlines()
                      if 'add_claim' in line or 'add_homeland' in line)
    return result + '\t}\n'


def find_region_state(section, tag):
    match = re.search(r'(?m)^\s*region_state:' + re.escape(tag) + r'\s*=\s*\{', section)
    if not match:
        return None
    return match.start(), map_tools.close(section, section.index('{', match.start()))


def split_population(text, state, plans):
    start, end = map_tools.block(text, 's:' + state)
    section = text[start:end]
    before_total = sum(int(n) for n in re.findall(r'\bsize\s*=\s*(\d+)', section))
    additions = collections.defaultdict(list)
    for donor, shares in plans.items():
        span = find_region_state(section, donor)
        assert span, (state, donor)
        a, b = span
        block = section[a:b]

        def move_pop(match):
            original = match[0]
            size_match = re.search(r'\bsize\s*=\s*(\d+)', original)
            assert size_match
            count = int(size_match[1])
            shifted = {}
            for recipient, fraction in shares.items():
                moved = round(count * fraction) if count >= 1000 else 0
                if moved:
                    shifted[recipient] = moved
                    additions[recipient].append(re.sub(
                        r'\bsize\s*=\s*\d+', 'size = ' + str(moved), original))
            remaining = count - sum(shifted.values())
            assert remaining > 0
            return re.sub(r'\bsize\s*=\s*\d+', 'size = ' + str(remaining), original)

        block = re.sub(r'create_pop\s*=\s*\{[^{}]*\}', move_pop, block)
        section = section[:a] + block + section[b:]

    for recipient, cohort_lines in additions.items():
        span = find_region_state(section, recipient)
        if span:
            a, b = span
            block = section[a:b]
            brace = block.rfind('}')
            block = block[:brace] + ''.join('\t\t\t' + line.strip() + '\n' for line in cohort_lines) + block[brace:]
            section = section[:a] + block + section[b:]
        else:
            brace = section.rfind('}')
            block = '\t\tregion_state:' + recipient + ' = {\n'
            block += ''.join('\t\t\t' + line.strip() + '\n' for line in cohort_lines)
            block += '\t\t}\n'
            section = section[:brace] + block + section[brace:]
    after_total = sum(int(n) for n in re.findall(r'\bsize\s*=\s*(\d+)', section))
    assert before_total == after_total, (state, before_total, after_total)
    return text[:start] + section + text[end:]


def add_railway(text, state, tag):
    start, end = map_tools.block(text, 's:' + state)
    section = text[start:end]
    assert not find_region_state(section, tag), (state, tag)
    brace = section.rfind('}')
    new = ('\t\tregion_state:' + tag + ' = {\n'
           '\t\t\tcreate_building = {\n'
           '\t\t\t\tbuilding = "building_railway"\n'
           '\t\t\t\tadd_ownership = { country = { country = "c:' + tag + '" levels = 1 } }\n'
           '\t\t\t\treserves = 1\n'
           '\t\t\t\tactivate_production_methods = { "pm_early_trains" "pm_wooden_passenger_carriages" }\n'
           '\t\t\t}\n\t\t}\n')
    section = section[:brace] + new + section[brace:]
    return text[:start] + section + text[end:]


def normalize_population_state(text, state):
    start, end = map_tools.block(text, 's:' + state)
    old = text[start:end]
    blocks = []
    for match in re.finditer(r'\bregion_state:(\w+)\s*=\s*\{', old):
        close = map_tools.close(old, old.index('{', match.start()))
        body = old[match.start():close]
        cohorts = re.findall(r'create_pop\s*=\s*\{[^{}]*\}', body)
        assert cohorts, (state, match[1])
        blocks.append((match[1], cohorts))
    assert len(blocks) == len(set(tag for tag, _ in blocks))
    new = '\ts:' + state + ' = {\n'
    for tag, cohorts in blocks:
        merged = collections.OrderedDict()
        for cohort in cohorts:
            size = int(re.search(r'\bsize\s*=\s*(\d+)', cohort)[1])
            key = re.sub(r'\bsize\s*=\s*\d+', 'size = 0', cohort.strip())
            if key not in merged:
                merged[key] = 0
            merged[key] += size
        new += '\t\tregion_state:' + tag + ' = {\n'
        new += ''.join('\t\t\t' + re.sub(r'\bsize\s*=\s*0', 'size = ' + str(size), key) + '\n'
                       for key, size in merged.items())
        new += '\t\t}\n'
    new += '\t}\n'
    assert sum(int(n) for n in re.findall(r'\bsize\s*=\s*(\d+)', old)) == sum(
        int(n) for n in re.findall(r'\bsize\s*=\s*(\d+)', new))
    return text[:start] + new + text[end:]


def normalize_railway_state(text, state):
    start, end = map_tools.block(text, 's:' + state)
    old = text[start:end]
    tags = re.findall(r'\bregion_state:(\w+)\s*=\s*\{', old)
    assert len(tags) == len(set(tags))
    assert old.count('building_railway') == len(tags)
    new = '\ts:' + state + ' = {\n'
    for tag in tags:
        new += ('\t\tregion_state:' + tag + ' = {\n'
                '\t\t\tcreate_building = {\n'
                '\t\t\t\tbuilding = "building_railway"\n'
                '\t\t\t\tadd_ownership = { country = { country = "c:' + tag + '" levels = 1 } }\n'
                '\t\t\t\treserves = 1\n'
                '\t\t\t\tactivate_production_methods = { "pm_early_trains" "pm_wooden_passenger_carriages" }\n'
                '\t\t\t}\n\t\t}\n')
    new += '\t}\n'
    return text[:start] + new + text[end:]


def write_preserved(path, original, text):
    newline = '\r\n' if b'\r\n' in original else '\n'
    data = text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8')
    path.write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b'') + data)


def revised():
    originals = {path: path.read_bytes() for path in (HISTORY, POPS, RAILWAYS)}
    history = originals[HISTORY].decode('utf-8-sig')
    before = map_tools.ownership(history)
    after = {province: list(owner) for province, owner in before.items()}
    assert len(TRANSFERS) == 77
    for province, new_tag in TRANSFERS.items():
        assert province in CONTEXT['coords']
        assert before[province][1] != new_tag
        after[province][1] = new_tag
        assert any(before[neighbor][1] == new_tag for neighbor in CONTEXT['adj'][province]) or any(
            neighbor in TRANSFERS and TRANSFERS[neighbor] == new_tag
            for neighbor in CONTEXT['adj'][province]), province
    assert {owner[1] for owner in before.values()} == {owner[1] for owner in after.values()}
    assert {province: owner for province, owner in before.items()
            if owner[0] in {'STATE_NORTH_ISLAND', 'STATE_SOUTH_ISLAND'}} == {
                province: owner for province, owner in after.items()
                if owner[0] in {'STATE_NORTH_ISLAND', 'STATE_SOUTH_ISLAND'}}

    region_text = REGIONS.read_text(encoding='utf-8-sig') + VANILLA_REGIONS.read_text(encoding='utf-8-sig')
    hubs = {clean_province(p) for p in re.findall(
        r'\b(?:city|port|farm|mine|wood)\s*=\s*"(x[0-9a-fA-F]{6})"', region_text)}
    assert not (TRANSFERS.keys() & hubs)
    affected_states = sorted({before[p][0] for p in TRANSFERS})
    for state in affected_states:
        start, end = map_tools.block(history, 's:' + state)
        history = history[:start] + state_ownership_block(state, after, history[start:end]) + history[end:]
    assert map_tools.ownership(history) == after
    for tag in sorted(set(TRANSFERS.values()) | {before[p][1] for p in TRANSFERS}):
        old = [p for p in CONTEXT['adj'] if before[p][1] == tag]
        new = [p for p in CONTEXT['adj'] if after[p][1] == tag]
        assert len(map_tools.components(new, CONTEXT['adj'])) <= len(
            map_tools.components(old, CONTEXT['adj'])), tag

    pops = originals[POPS].decode('utf-8-sig')
    for state, plans in POP_SHARES.items():
        pops = split_population(pops, state, plans)
        pops = normalize_population_state(pops, state)
    railways = originals[RAILWAYS].decode('utf-8-sig')
    new_pairs = sorted({tuple(after[p]) for p in TRANSFERS if tuple(after[p]) not in
                        {tuple(value) for value in before.values()}})
    assert len(new_pairs) == 7, new_pairs
    for state, tag in new_pairs:
        railways = add_railway(railways, state, tag)
    for state in sorted({state for state, _ in new_pairs}):
        railways = normalize_railway_state(railways, state)
    for path, text in ((HISTORY, history), (POPS, pops), (RAILWAYS, railways)):
        clean = re.sub(r'#[^\n]*', '', text)
        assert clean.count('{') == clean.count('}'), path
    return originals, {HISTORY: history, POPS: pops, RAILWAYS: railways}, new_pairs


if __name__ == '__main__':
    originals, texts, new_pairs = revised()
    if '--apply' in sys.argv:
        for path, body in texts.items():
            write_preserved(path, originals[path], body)
    print(json.dumps({'province_transfers': len(TRANSFERS), 'new_region_states': new_pairs,
                      'population_total': 'preserved'}, ensure_ascii=False, indent=2))
