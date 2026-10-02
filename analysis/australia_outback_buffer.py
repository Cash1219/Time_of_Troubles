"""Return the impassable inland cavern surface to a neutral native buffer.

The Chireiden lift hub stays owned and populated. The buffer gets a small,
contiguous strip of real land on its western edge as its settled homeland.
"""

import collections
import json
import re
import sys

import west_coast_draft as map_tools


WESTERN_BUFFER = {
    'xE2581E', 'x373D37', 'xD7EF8D', 'xC9A151', 'x36F14D',
    'x02C2F2', 'xD5E673', 'x873C4B', 'x03B26C', 'x030E6E',
    'x7E10D2', 'x032B24', 'x944AD9', 'x36B60E', 'x3AC495',
}
HUB = 'x37ACCC'
HISTORY = map_tools.HISTORY
POPS = map_tools.ROOT / 'common/history/pops/13_australasia.txt'
DEFINITIONS = map_tools.ROOT / 'common/country_definitions/tot_countries.txt'
LOCALIZATION = map_tools.ROOT / 'localization/replace/simp_chinese/common/core/tot_countries_l_simp_chinese.yml'
REGIONS = map_tools.ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt'
CONTEXT = json.loads((map_tools.OUT / 'west_coast_context.json').read_text(encoding='utf-8'))


def state_block(state, owners, old):
    groups = collections.defaultdict(list)
    for province, (region, tag) in owners.items():
        if region == state:
            groups[tag].append(province)
    result = 's:' + state + ' = {\n'
    for tag, provinces in sorted(groups.items()):
        result += '\tcreate_state = {\n\t\tcountry = c:' + tag + '\n\t\towned_provinces = {\n'
        for index in range(0, len(provinces), 12):
            result += '\t\t\t' + ' '.join(sorted(provinces)[index:index + 12]) + '\n'
        result += '\t\t}\n\t}\n'
    result += ''.join('\t' + line.strip() + '\n' for line in old.splitlines()
                      if 'add_claim' in line or 'add_homeland' in line)
    if 'add_homeland = cu:aborigine' not in result:
        result += '\tadd_homeland = cu:aborigine\n'
    return result + '}\n'


def write_preserved(path, original, text):
    newline = '\r\n' if b'\r\n' in original else '\n'
    data = text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8')
    path.write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b'') + data)


def revised():
    original = {path: path.read_bytes() for path in (HISTORY, POPS, DEFINITIONS, LOCALIZATION)}
    history = original[HISTORY].decode('utf-8-sig')
    before = map_tools.ownership(history)
    cavern = 'STATE_CHIREIDEN_CAVERN_ZONE'
    west = 'STATE_WESTERN_AUSTRALIA'
    region_text = REGIONS.read_text(encoding='utf-8-sig')
    start, end = map_tools.block(region_text, cavern)
    impassable = {code.upper().replace('X', 'x') for code in map_tools.PROV.findall(
        re.search(r'\bimpassable\s*=\s*\{([^}]+)', region_text[start:end])[1])}
    assert len(impassable) == 466
    assert {p for p, value in before.items() if value == [cavern, 'CHRD']} == impassable | {HUB}
    assert all(before[p] == [west, 'RNGN'] for p in WESTERN_BUFFER)
    assert len(map_tools.components(WESTERN_BUFFER, CONTEXT['adj'])) == 1
    remaining = {p for p, value in before.items() if value == [west, 'RNGN']} - WESTERN_BUFFER
    assert len(map_tools.components(remaining, CONTEXT['adj'])) == 1
    assert any(q in impassable for p in WESTERN_BUFFER for q in CONTEXT['adj'][p])
    after = {p: list(value) for p, value in before.items()}
    for province in impassable | WESTERN_BUFFER:
        after[province][1] = 'WTI'
    for state in (cavern, west):
        start, end = map_tools.block(history, 's:' + state)
        history = history[:start] + state_block(state, after, history[start:end]) + history[end:]
    assert map_tools.ownership(history) == after

    pops = original[POPS].decode('utf-8-sig')
    start, end = map_tools.block(pops, 's:' + west)
    old = pops[start:end]
    assert 'region_state:WTI' not in old
    insert_at = old.rfind('\n\t}')
    assert insert_at > 0
    old = old[:insert_at] + ('\n\t\tregion_state:WTI = {\n'
                              '\t\t\tcreate_pop = { culture = aborigine size = 5000 }\n'
                              '\t\t}') + old[insert_at:]
    pops = pops[:start] + old + pops[end:]

    definitions = original[DEFINITIONS].decode('utf-8-sig')
    assert not re.search(r'(?m)^WTI\s*=', definitions)
    definitions += ('\nWTI = { # 澳洲内陆原住民缓冲地\n'
                    '\tcolor = { 104 108 101 }\n'
                    '\ttier = principality\n'
                    '\tcountry_type = decentralized\n'
                    '\tcultures = { aborigine }\n'
                    '\tcapital = STATE_WESTERN_AUSTRALIA\n}\n')
    localization = original[LOCALIZATION].decode('utf-8-sig')
    assert not re.search(r'(?m)^ WTI:', localization)
    localization += '\n WTI: "阿南古荒原"\n WTI_ADJ: "阿南古"\n'
    return original, {HISTORY: history, POPS: pops, DEFINITIONS: definitions,
                      LOCALIZATION: localization}, after


if __name__ == '__main__':
    original, texts, owners = revised()
    if '--apply' in sys.argv:
        for path, text in texts.items():
            write_preserved(path, original[path], text)
    print(json.dumps({'wasteland_provinces': 466, 'settled_buffer_provinces': len(WESTERN_BUFFER),
                      'chireiden_cavern_hub': HUB, 'total_owners': len(owners)}, indent=2))
