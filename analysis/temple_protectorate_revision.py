"""Swap temple territories and use the scoped Gensokyo protectorate definition."""
import collections
import datetime
import json
import re
import sys
import west_coast_draft as w
import lake_coast_revision as lc
import southern_rebalance as south
from population_arable_prototype import spans, pop_entries

PREFIX = 'temple_protectorate_v1'
FILES = ['common/history/states/00_states.txt',
         'common/history/pops/13_australasia.txt',
         'common/country_definitions/tot_countries.txt',
         'common/history/diplomacy/tot_gensokyo_subjects.txt']
SWAP = {'MYRN': 'SHRM', 'SHRM': 'MYRN'}
CAPITALS = {'MYRN': 'STATE_NEW_SOUTH_WALES', 'SHRM': 'STATE_SOUTH_AUSTRALIA'}


def main():
    originals = {p: (w.ROOT / p).read_bytes() for p in FILES}
    texts = {p: b.decode('utf-8-sig') for p, b in originals.items()}
    before = w.ownership(texts[FILES[0]])
    assert {v[0] for v in before.values() if v[1] == 'MYRN'} == {'STATE_SOUTH_AUSTRALIA'}
    assert {v[0] for v in before.values() if v[1] == 'SHRM'} == {'STATE_NEW_SOUTH_WALES'}
    texts[FILES[0]] = re.sub(r'c:(MYRN|SHRM)\b', lambda m: 'c:' + SWAP[m[1]], texts[FILES[0]])
    texts[FILES[1]] = re.sub(r'region_state:(MYRN|SHRM)\b', lambda m: 'region_state:' + SWAP[m[1]], texts[FILES[1]])
    after = w.ownership(texts[FILES[0]])
    for p in before:
        assert after[p] == [before[p][0], SWAP.get(before[p][1], before[p][1])]
    connectivity = south.connected(after)
    for tag, capital in CAPITALS.items():
        start, end = w.block(texts[FILES[2]], tag)
        part = re.sub(r'capital\s*=\s*STATE_\w+', 'capital = ' + capital, texts[FILES[2]][start:end])
        if tag == 'MYRN':
            part = part.replace('# 命莲寺', '# 命莲寺：人间之里西部内陆')
        else:
            part = re.sub(r'# 神灵庙[^\n]*', '# 神灵庙：人间之里西侧沿海', part)
        texts[FILES[2]] = texts[FILES[2]][:start] + part + texts[FILES[2]][end:]
        assert any(v == [capital, tag] for v in after.values())
    pacts_before = re.findall(r'country\s*=\s*c:(\w+)\s+type\s*=\s*vassal', texts[FILES[3]])
    assert len(pacts_before) == len(set(pacts_before)) == 21
    texts[FILES[3]] = texts[FILES[3]].replace('幻想乡附属体系', '幻想乡受保护国体系').replace('type = vassal', 'type = tot_gensokyo_protectorate')
    assert re.findall(r'country\s*=\s*c:(\w+)\s+type\s*=\s*tot_gensokyo_protectorate', texts[FILES[3]]) == pacts_before
    for path in ('common/subject_types/tot_gensokyo_protectorate.txt', 'common/diplomatic_actions/tot_gensokyo_protectorate.txt'):
        assert (w.ROOT / path).exists(), 'Install the scoped protectorate definitions first'
    assert 'type = vassal' not in texts[FILES[3]]
    # No temple building/formation block exists that needs to follow the swap.
    for folder in ('buildings', 'military_formations', 'characters'):
        for path in (w.ROOT / ('common/history/' + folder)).glob('*.txt'):
            assert not re.search(r'(?:c:|region_state:)(MYRN|SHRM)\b', path.read_text(encoding='utf-8-sig')), path
    pop_files = {p: p.read_text(encoding='utf-8-sig') for p in (w.ROOT / 'common/history/pops').glob('*.txt')}
    before_rows = pop_entries(pop_files)
    after_rows = pop_entries({**pop_files, w.ROOT / FILES[1]: texts[FILES[1]]})
    def profiles(rows):
        result = collections.Counter()
        for st, _, culture, religion, size in rows:
            result[st, culture, religion] += size
        return result
    assert profiles(before_rows) == profiles(after_rows)
    pairs = set(map(tuple, after.values()))
    country_pops = collections.Counter()
    for st, tag, _, _, size in after_rows:
        assert (st, tag) in pairs, (st, tag)
        country_pops[tag] += size
    assert sum(country_pops.values()) == 19610000
    assert south.agriculture(before) == south.agriculture(after)
    for p, text in texts.items():
        body = re.sub(r'#[^\n]*', '', text)
        assert body.count('{') == body.count('}'), p
    manifest = {p: dict(before=before[p], after=after[p]) for p in before if before[p] != after[p]}
    assert len(manifest) == 35
    report = dict(changed_provinces=len(manifest), subjects=sorted(pacts_before), leader='HAKR',
                  subject_type='subject_type_gensokyo_protectorate', diplomatic_action='tot_gensokyo_protectorate', capitals=CAPITALS, connectivity=connectivity,
                  country_populations=dict(country_pops), total_population=19610000,
                  hito_agriculture=south.agriculture(after), power_bloc='unchanged',
                  other_borders_resources_buildings_arable='unchanged',
                  country_recognition='unchanged; custom protectorate accepts existing Hakurei type and rank', game_launch='not tested')
    south.PREFIX = PREFIX
    south.preview(after)
    (w.OUT / (PREFIX + '_manifest.json')).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    report['applied'] = '--apply' in sys.argv
    if report['applied']:
        backup = w.ROOT / ('docs/backups/temple_protectorate_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        for p, data in originals.items():
            target = backup / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for p, text in texts.items():
            (w.ROOT / p).write_bytes(b'\xef\xbb\xbf' + text.replace('\r\n', '\n').encode('utf-8'))
        report['backup'] = str(backup)
        assert lc.current() == after
    (w.OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
