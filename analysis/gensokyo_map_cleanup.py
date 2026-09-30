"""Reviewed east-coast transfer, Kanak integration and state-trait/homeland cleanup.

--apply is a one-time, backed-up migration. Default validates the exact snapshot.
Preserves population cohorts, industries, resource limits and impassable land.
"""
import collections
import datetime
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from gensokyo_cultures_v1 import ROOT, NAMES, POP_PATHS, records, replace_blocks
from population_arable_prototype import spans
import west_coast_draft as w
import lake_coast_revision as lc
from ridge_sanzu_revision import history_block

GAME = w.GAME

REPORT = ROOT / 'docs/drafts/gensokyo_map_cleanup.json'
HISTORY = 'common/history/states/00_states.txt'
MAP = 'map_data/state_regions/tot_13_australasia_chireiden.txt'
COAST = {'xD74DB9': 'MFSR', 'xFD1F91': 'MFSR', 'x276C93': 'HAKR'}
PENALTIES = {'state_trait_australian_desert', 'state_trait_great_dividing_range',
             'state_trait_malaria', 'state_trait_severe_malaria',
             'state_trait_dry', 'state_trait_mountainous'}
FOREST = 'state_trait_tot_gensokyo_tasmanian_forest'
TRAIT_PATH = 'common/state_traits/tot_gensokyo_terrain.txt'
PORTS = 'common/history/buildings/tot_gensokyo_market_ports.txt'
TRAIT_LOCS = {
    'localization/replace/simp_chinese/map/tot_gensokyo_terrain_l_simp_chinese.yml':
        'l_simp_chinese:\n ' + FOREST + ': "塔斯马尼亚雨林"\n',
    'localization/english/tot_gensokyo_terrain_l_english.yml':
        'l_english:\n ' + FOREST + ': "Tasmanian Rainforest"\n',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def all_pops(texts=None):
    return [row for rel in POP_PATHS for row in records(
        texts[rel] if texts and rel in texts else (ROOT / rel).read_text(encoding='utf-8-sig'))]


def check():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    relocation_path = ROOT / 'docs/drafts/three_factions_relocation.json'
    relocation = json.loads(relocation_path.read_text(encoding='utf-8')) if relocation_path.exists() else None
    def stage_bytes(rel):
        if relocation and rel in relocation['hashes']:
            raw = (Path(relocation['backup']) / rel).read_bytes()
            assert sha(raw) == relocation['hashes'][rel]['before'], rel
            return raw
        return (ROOT / rel).read_bytes()
    for rel, meta in report['runtime_files'].items():
        assert sha(stage_bytes(rel)) == meta['after_sha256'], ('Snapshot changed', rel)
    before = w.ownership((Path(report['backup']) / HISTORY).read_text(encoding='utf-8-sig'))
    after = w.ownership(stage_bytes(HISTORY).decode('utf-8-sig'))
    actual = {p: [before.get(p), after.get(p)] for p in set(before) | set(after)
              if before.get(p) != after.get(p)}
    assert actual == report['ownership_changes']
    rows = all_pops({rel: stage_bytes(rel).decode('utf-8-sig')
                     for rel in POP_PATHS if relocation and rel in relocation['hashes']})
    totals = collections.Counter()
    amounts = collections.Counter()
    for row in rows:
        totals[row['state']] += row['size']
        amounts[row['state'], row['culture']] += row['size']
        if row['tag'] in NAMES:
            assert [row['state'], row['tag']] in after.values(), row
    source = stage_bytes(HISTORY).decode('utf-8-sig')
    for m, body, _ in spans(source, r's:(STATE_\w+)\s*=\s*\{'):
        if m[1] not in report['homelands']:
            continue
        actual_homelands = re.findall(r'add_homeland\s*=\s*cu:(\w+)', body)
        assert actual_homelands == report['homelands'][m[1]]['kept']
        for culture in actual_homelands:
            assert amounts[m[1], culture] * 100 >= totals[m[1]] * 30
    assert sum(row['size'] for row in rows if row['tag'] in NAMES) == 19666004
    assert not any(v[1] == 'KNK' for v in after.values())
    assert sum(v == ['STATE_KANAK', 'TENG'] for v in after.values()) == 3
    map_source = (ROOT / MAP).read_text(encoding='utf-8-sig')
    assert not PENALTIES.intersection(re.findall(r'"(state_trait_\w+)"', map_source))
    for rel, expected in TRAIT_LOCS.items():
        raw = (ROOT / rel).read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf') and raw.decode('utf-8-sig') == expected
    if relocation:
        from three_factions_relocation import check as check_relocation
        check_relocation()
    print(json.dumps(dict(status='static validation passed; not game-tested',
        transferred_provinces=len(actual), homelands_removed=report['homelands_removed'],
        population=19666004, impassable_preserved=True,
        resource_and_arable_limits_preserved=True), ensure_ascii=False))


def apply():
    assert not REPORT.exists(), 'Already applied; run without --apply to check.'
    paths = [HISTORY, MAP, *POP_PATHS, 'common/history/buildings/12_indonesia.txt', PORTS, TRAIT_PATH, *TRAIT_LOCS]
    originals = {rel: (ROOT / rel).read_bytes() if (ROOT / rel).exists() else None for rel in paths}
    texts = {rel: raw.decode('utf-8-sig') for rel, raw in originals.items() if raw is not None}
    before = w.ownership(texts[HISTORY])
    after = {p: list(v) for p, v in before.items()}
    for p, tag in COAST.items():
        assert before[p] == ['STATE_NEW_SOUTH_WALES', tag], (p, before[p])
        after[p][1] = 'YKYM'
    kanak = [p for p, v in before.items() if v == ['STATE_KANAK', 'KNK']]
    assert len(kanak) == 3
    for p in kanak:
        after[p][1] = 'TENG'
    for tag in ['MFSR', 'HAKR', 'YKYM']:
        groups = w.components([p for p in lc.CTX['adj'] if after[p][1] == tag], lc.CTX['adj'])
        old = w.components([p for p in lc.CTX['adj'] if before[p][1] == tag], lc.CTX['adj'])
        assert len(groups) <= len(old), (tag, groups)
    changed_states = {'STATE_NEW_SOUTH_WALES', 'STATE_KANAK'}
    def reassign(m, body):
        if m[1] not in changed_states:
            return body
        block = history_block(m[1], after, body)
        return block[block.index('{') + 1:block.rfind('}')]
    texts[HISTORY] = replace_blocks(texts[HISTORY], r's:(STATE_\w+)\s*=\s*\{', reassign)
    for rel in ['common/history/pops/12_indonesia.txt', 'common/history/buildings/12_indonesia.txt']:
        texts[rel] = replace_blocks(texts[rel], r's:(STATE_\w+)\s*=\s*\{',
            lambda m, b: b.replace('region_state:KNK', 'region_state:TENG') if m[1] == 'STATE_KANAK' else b)
    old_rows, rows = all_pops({rel: raw.decode('utf-8-sig') for rel, raw in originals.items() if raw}), all_pops(texts)
    expected_rows = [dict(row, tag='TENG') if row['state'] == 'STATE_KANAK' and row['tag'] == 'KNK'
                     else row for row in old_rows]
    assert rows == expected_rows, 'Population or religion cohorts changed'
    targets = {st for st, tag in after.values() if tag in NAMES}
    totals, amounts = collections.Counter(), collections.Counter()
    for row in rows:
        totals[row['state']] += row['size']
        amounts[row['state'], row['culture']] += row['size']
    homelands = {}
    def filter_homelands(m, body):
        if m[1] not in targets:
            return body
        current = re.findall(r'add_homeland\s*=\s*cu:(\w+)', body)
        kept = [c for c in current if totals[m[1]] and amounts[m[1], c] * 100 >= totals[m[1]] * 30]
        removed = [c for c in current if c not in kept]
        homelands[m[1]] = dict(kept=kept, removed=removed, total_population=totals[m[1]],
            shares={c: amounts[m[1], c] / totals[m[1]] if totals[m[1]] else 0 for c in current})
        return re.sub(r'(?m)^[ \t]*add_homeland\s*=\s*cu:(\w+)[ \t]*\n?',
                      lambda x: x[0] if x[1] in kept else '', body)
    texts[HISTORY] = replace_blocks(texts[HISTORY], r's:(STATE_\w+)\s*=\s*\{', filter_homelands)
    terrain_changes = {}
    def clean_traits(m, body):
        if m[1] not in targets:
            return body
        def trait_list(match):
            old = re.findall(r'"(\w+)"', match[1])
            new = [FOREST if t == 'state_trait_tasmanian_rainforest' else t for t in old if t not in PENALTIES]
            if new != old:
                terrain_changes[m[1]] = dict(before=old, after=new)
            return 'traits = { ' + ' '.join('"' + t + '"' for t in new) + ' }'
        return re.sub(r'\b(?:traits|state_traits)\s*=\s*\{([^}]*)}', trait_list, body)
    texts[MAP] = replace_blocks(texts[MAP], r'(?m)^\s*(STATE_\w+)\s*=\s*\{', clean_traits)
    vanilla = (GAME / 'map_data/state_regions/12_indonesia.txt').read_text(encoding='utf-8-sig')
    m, body, end = next(spans(vanilla, r'(?m)^(STATE_KANAK)\s*=\s*\{'))
    texts[MAP] = texts[MAP].rstrip() + '\n\nSTATE_KANAK = {' + clean_traits(m, body) + '}\n'
    texts[TRAIT_PATH] = ('# Keep the Tasmanian forest yield without the infrastructure penalty.\n'
        + FOREST + ' = {\n    icon = "gfx/interface/icons/state_trait_icons/resources_lumber.dds"\n'
        '    modifier = { goods_output_hardwood_mult = 0.2 }\n}\n')
    texts.update(TRAIT_LOCS)
    # A port is needed for this newly assigned island to reach the common market.
    port = '\n    s:STATE_KANAK = {\n        region_state:TENG = {\n            create_building = {\n                building = "building_port"\n                activate_production_methods = { "pm_basic_port" }\n                add_ownership = { country = { country = "c:TENG" levels = 1 } }\n                reserves = 1\n            }\n        }\n    }\n'
    closing = texts[PORTS].rfind('}')
    texts[PORTS] = texts[PORTS][:closing] + port + texts[PORTS][closing:]
    assert w.ownership(texts[HISTORY]) == after
    # State geometry, hub positions, resources and impassable sets stay identical.
    old_map = originals[MAP].decode('utf-8-sig')
    def without_traits(s):
        return re.sub(r'\b(?:traits|state_traits)\s*=\s*\{[^}]*}', '', s).strip()
    for sm, sb, _ in spans(old_map, r'(?m)^\s*(STATE_\w+)\s*=\s*\{'):
        new_body = next(b for nm, b, _ in spans(texts[MAP], r'(?m)^\s*(STATE_\w+)\s*=\s*\{') if nm[1] == sm[1])
        assert without_traits(sb) == without_traits(new_body), sm[1]
    new_kanak = next(b for nm, b, _ in spans(texts[MAP], r'(?m)^\s*(STATE_\w+)\s*=\s*\{') if nm[1] == 'STATE_KANAK')
    assert without_traits(body) == without_traits(new_kanak)
    changed = {rel: text for rel, text in texts.items()
               if originals.get(rel) is None or text != originals[rel].decode('utf-8-sig')}
    backup = ROOT / 'docs/backups' / ('gensokyo_map_cleanup_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    metadata = {}
    for rel, text in changed.items():
        assert re.sub(r'#[^\n]*', '', text).count('{') == re.sub(r'#[^\n]*', '', text).count('}'), rel
        raw = originals.get(rel)
        if raw is not None:
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        output = text.replace('\r\n', '\n').encode('utf-8')
        if rel.endswith('.yml') or (raw and raw.startswith(b'\xef\xbb\xbf')):
            output = b'\xef\xbb\xbf' + output
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / rel).write_bytes(output)
        metadata[rel] = dict(before_sha256=sha(raw) if raw is not None else None, after_sha256=sha(output))
    report = dict(backup=str(backup), runtime_files=metadata,
        ownership_changes={p: [before[p], after[p]] for p in before if before[p] != after[p]},
        terrain_changes=terrain_changes, homelands=homelands,
        homelands_removed=sum(len(v['removed']) for v in homelands.values()),
        homeland_threshold_percent=30, new_port_levels=1,
        population_moved_to_teng=56004, terrain_scope='State-trait penalties only; impassable provinces retained',
        status='applied; static validation only')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
    check()
