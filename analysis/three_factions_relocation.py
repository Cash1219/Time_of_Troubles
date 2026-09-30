"""Relocate Kyoto, Divine Spirit Mausoleum, and Myouren Temple.

Run --preview to write a review map, --apply once to install with backups,
or --check to validate the installed version. State geometry is unchanged.
"""

import collections
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import lake_coast_revision as lake
import west_coast_draft as west
from gensokyo_cultures_v1 import records, replace_blocks
from population_arable_prototype import spans
from ridge_sanzu_revision import history_block

ROOT = west.ROOT
OUT = west.OUT
CTX = lake.CTX
MANIFEST = OUT / 'three_factions_relocation.json'
STATE_HISTORY = 'common/history/states/00_states.txt'
COUNTRIES = 'common/country_definitions/tot_countries.txt'
POPS = 'common/history/pops/13_australasia.txt'
BUILDINGS = 'common/history/buildings/tot_gensokyo_eastern_industry.txt'
FILES = (STATE_HISTORY, COUNTRIES, POPS, BUILDINGS)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def split_block(text, state, tag):
    """Remove and return one region_state block from a history state."""
    candidates = [(match, body, end) for match, body, end in
                  spans(text, r's:(STATE_\w+)\s*=\s*\{')
                  if match[1] == state and re.search(r'region_state:' + tag + r'\s*=\s*\{', body)]
    assert len(candidates) == 1, (state, tag, len(candidates))
    state_match, _, b = candidates[0]
    a = state_match.start()
    outer = text[a:b]
    match = re.search(r'(?m)^[ \t]*region_state:' + tag + r'\s*=\s*\{', outer)
    assert match
    end = west.close(outer, outer.index('{', match.start()))
    block = outer[match.start():end].strip()
    outer = outer[:match.start()] + outer[end:]
    return text[:a] + outer + text[b:], block


def append_block(text, state, block):
    a, b = west.block(text, 's:' + state)
    outer = text[a:b]
    pos = outer.rfind('}')
    lines = block.splitlines()
    normalized = [lines[0]] + [line[2:] if line.startswith('\t\t') else line
                                for line in lines[1:]]
    indented = '\n'.join('\t\t' + line for line in normalized)
    outer = outer[:pos].rstrip() + '\n' + indented + '\n\t' + outer[pos:]
    return text[:a] + outer + text[b:]


def target_ownership(before):
    coords, adj = CTX['coords'], CTX['adj']
    after = {province: list(value) for province, value in before.items()}
    for province, (state, tag) in before.items():
        if tag == 'KYTO':
            assert state == 'STATE_WESTERN_AUSTRALIA'
            after[province][1] = 'BYKR'
        elif tag == 'SHRM':
            assert state == 'STATE_SOUTH_AUSTRALIA'
            after[province][1] = 'KZNH'
        elif tag == 'MYRN':
            assert state == 'STATE_NEW_SOUTH_WALES'
            after[province][1] = 'SHRM'
        elif (state == 'STATE_SOUTH_AUSTRALIA' and tag == 'CHRD'
              and coords[province][0] < 7155):
            after[province][1] = 'KYTO'
    # A compact inland district east of the old Myouren pocket.
    seed = 'x20093A'
    assert before[seed] == ['STATE_NEW_SOUTH_WALES', 'HITO']
    assert any(before[q][1] == 'MYRN' for q in adj[seed])
    selected = {seed}
    while len(selected) < 13:
        candidates = {q for p in selected for q in adj[p]
                      if before.get(q) == ['STATE_NEW_SOUTH_WALES', 'HITO']
                      and q not in selected and coords[q][0] < 7420
                      and coords[q][1] < 2900}
        assert candidates
        selected.add(min(candidates, key=lambda p:
            ((coords[p][0] - 7380) ** 2 + (coords[p][1] - 2860) ** 2, p)))
    for province in selected:
        after[province][1] = 'MYRN'
    assert len([p for p, v in after.items() if v == ['STATE_SOUTH_AUSTRALIA', 'KYTO']]) == 26
    audit(before, after)
    return after


def audit(before, after):
    adj = CTX['adj']
    for tag in ('KYTO', 'BYKR', 'KZNH', 'SHRM', 'MYRN', 'HITO'):
        components = west.components([p for p in adj if after[p][1] == tag], adj)
        assert len(components) == 1, (tag, [len(g) for g in components])
    chireiden = west.components([p for p in adj if after[p][1] == 'CHRD'], adj)
    old_chireiden = west.components([p for p in adj if before[p][1] == 'CHRD'], adj)
    assert [len(g) for g in chireiden[1:]] == [len(g) for g in old_chireiden[1:]] == [2]
    assert all(before[p][0] == after[p][0] for p in before)
    for tag, state in [('KYTO', 'STATE_SOUTH_AUSTRALIA'),
                       ('MYRN', 'STATE_NEW_SOUTH_WALES'),
                       ('SHRM', 'STATE_NEW_SOUTH_WALES')]:
        assert {st for st, owner in after.values() if owner == tag} == {state}
    assert sum(v[1] == 'HITO' for v in before.values()) - sum(v[1] == 'HITO' for v in after.values()) == 13
    return {tag: sum(v[1] == tag for v in after.values())
            for tag in ('KYTO', 'BYKR', 'CHRD', 'KZNH', 'SHRM', 'MYRN', 'HITO')}


def preview():
    before = lake.current()
    after = target_ownership(before)
    lake.PREFIX = 'three_factions_relocation_preview'
    lake.preview(after)
    return before, after


def edit_texts(originals, before, after):
    texts = {rel: raw.decode('utf-8-sig') for rel, raw in originals.items()}
    changed_states = ('STATE_WESTERN_AUSTRALIA', 'STATE_SOUTH_AUSTRALIA',
                      'STATE_NEW_SOUTH_WALES')
    texts[STATE_HISTORY] = replace_blocks(
        texts[STATE_HISTORY], r's:(STATE_\w+)\s*=\s*\{',
        lambda match, body: (
            lambda new: new[new.index('{') + 1:new.rfind('}')]
        )(history_block(match[1], after, body)) if match[1] in changed_states else body)
    # Avoid preserving whitespace-only lines from the previous large state blocks.
    texts[STATE_HISTORY] = replace_blocks(
        texts[STATE_HISTORY], r's:(STATE_\w+)\s*=\s*\{',
        lambda match, body: re.sub(r'\n{3,}', '\n\n', re.sub(r'(?m)^[ \t]+$', '', body))
        if match[1] in changed_states else body)
    assert west.ownership(texts[STATE_HISTORY]) == after

    for tag, capital in [('KYTO', 'STATE_SOUTH_AUSTRALIA'),
                         ('SHRM', 'STATE_NEW_SOUTH_WALES')]:
        a, b = west.block(texts[COUNTRIES], tag)
        block = texts[COUNTRIES][a:b]
        block, count = re.subn(r'capital\s*=\s*STATE_\w+', 'capital = ' + capital, block)
        assert count == 1
        if tag == 'SHRM':
            block = block.replace('人间之里西侧沿海', '人间之里西侧内陆')
        texts[COUNTRIES] = texts[COUNTRIES][:a] + block + texts[COUNTRIES][b:]

    for rel in (POPS, BUILDINGS):
        source = texts[rel]
        source, kyoto = split_block(source, 'STATE_WESTERN_AUSTRALIA', 'KYTO')
        source, mausoleum = split_block(source, 'STATE_SOUTH_AUSTRALIA', 'SHRM')
        if rel == BUILDINGS:
            kyoto = kyoto.replace('STATE_WESTERN_AUSTRALIA', 'STATE_SOUTH_AUSTRALIA')
            mausoleum = mausoleum.replace('STATE_SOUTH_AUSTRALIA', 'STATE_NEW_SOUTH_WALES')
            # South Australia has sulfur capacity but no coal capacity. Keep three mine levels.
            kyoto = kyoto.replace('building_coal_mine', 'building_sulfur_mine')
            assert 'building_port' in mausoleum
            port_parts = [(m, body, end) for m, body, end in spans(mausoleum, r'create_building\s*=\s*\{')
                          if 'building_port' in body]
            assert len(port_parts) == 1
            m, _, end = port_parts[0]
            mausoleum = mausoleum[:m.start()] + mausoleum[end:]
            # The former Mausoleum port belongs to the recipient of its old coast.
            regions = [(m, body, end) for m, body, end in spans(source, r's:(STATE_\w+)\s*=\s*\{')
                       if m[1] == 'STATE_SOUTH_AUSTRALIA' and 'region_state:KZNH' in body]
            assert len(regions) == 1
            sm, _, b = regions[0]
            a = sm.start()
            region = source[a:b]
            m = re.search(r'region_state:KZNH\s*=\s*\{', region)
            assert m
            e = west.close(region, region.index('{', m.start()))
            kzn = region[m.start():e]
            port_parts = [(pm, body, end) for pm, body, end in spans(kzn, r'create_building\s*=\s*\{')
                          if 'building_port' in body]
            assert len(port_parts) == 1
            pm, _, end = port_parts[0]
            port = kzn[pm.start():end]
            port, count = re.subn(r'levels\s*=\s*1\b', 'levels = 2', port)
            assert count == 1
            kzn = kzn[:pm.start()] + port + kzn[end:]
            region = region[:m.start()] + kzn + region[e:]
            source = source[:a] + region + source[b:]
        source = append_block(source, 'STATE_SOUTH_AUSTRALIA', kyoto)
        source = append_block(source, 'STATE_NEW_SOUTH_WALES', mausoleum)
        source = re.sub(r'(?m)^[ \t]+$', '', source)
        texts[rel] = source
    return texts


def validate_payload(originals, texts, after):
    """Check the census, state ownership, capitals, and migrated industries."""
    prior = records(originals[POPS].decode('utf-8-sig'))
    present = records(texts[POPS])
    key = lambda row: (row['tag'], row['culture'], row['religion'])
    assert collections.Counter({k: sum(row['size'] for row in prior if key(row) == k)
                                for k in {key(row) for row in prior}}) == collections.Counter(
        {k: sum(row['size'] for row in present if key(row) == k)
         for k in {key(row) for row in present}})
    for row in present:
        if row['tag'] in ('KYTO', 'SHRM', 'MYRN'):
            assert [row['state'], row['tag']] in after.values(), row
    for tag in ('KYTO', 'SHRM', 'MYRN'):
        a, b = west.block(texts[COUNTRIES], tag)
        capital = re.search(r'capital\s*=\s*(STATE_\w+)', texts[COUNTRIES][a:b])[1]
        assert [capital, tag] in after.values(), (tag, capital)
    original_buildings = originals[BUILDINGS].decode('utf-8-sig')
    assert texts[BUILDINGS].count('create_building') == original_buildings.count('create_building') - 1
    assert texts[BUILDINGS].count('building_sulfur_mine') == original_buildings.count('building_sulfur_mine') + 2
    assert texts[BUILDINGS].count('building_coal_mine') == original_buildings.count('building_coal_mine') - 2
    for rel in (POPS, BUILDINGS):
        for state_match, body, _ in spans(texts[rel], r's:(STATE_\w+)\s*=\s*\{'):
            for region_match, _, _ in spans(body, r'region_state:(\w+)\s*=\s*\{'):
                if region_match[1] in ('KYTO', 'SHRM', 'MYRN'):
                    assert [state_match[1], region_match[1]] in after.values()
    # The earlier 30% homeland rule still holds after moving two whole populations.
    all_pops = present[:]
    for path in (ROOT / 'common/history/pops').glob('*.txt'):
        if path.name != '13_australasia.txt':
            all_pops += records(path.read_text(encoding='utf-8-sig'))
    for state in ('STATE_SOUTH_AUSTRALIA', 'STATE_WESTERN_AUSTRALIA',
                  'STATE_NEW_SOUTH_WALES'):
        total = sum(row['size'] for row in all_pops if row['state'] == state)
        body = next(body for match, body, _ in
                    spans(texts[STATE_HISTORY], r's:(STATE_\w+)\s*=\s*\{')
                    if match[1] == state)
        for culture in re.findall(r'add_homeland\s*=\s*cu:(\w+)', body):
            amount = sum(row['size'] for row in all_pops
                         if row['state'] == state and row['culture'] == culture)
            assert amount * 100 >= total * 30, (state, culture, amount, total)


def apply():
    assert not MANIFEST.exists(), 'Already applied; use --check.'
    originals = {rel: (ROOT / rel).read_bytes() for rel in FILES}
    before = west.ownership(originals[STATE_HISTORY].decode('utf-8-sig'))
    after = target_ownership(before)
    texts = edit_texts(originals, before, after)
    validate_payload(originals, texts, after)
    for rel, content in texts.items():
        stripped = re.sub(r'#[^\n]*', '', content)
        assert stripped.count('{') == stripped.count('}'), rel
    backup = ROOT / 'docs/backups' / ('three_factions_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for rel, raw in originals.items():
        path = backup / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    hashes = {}
    for rel, content in texts.items():
        raw = originals[rel]
        new = content.replace('\r\n', '\n').encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            new = b'\xef\xbb\xbf' + new
        (ROOT / rel).write_bytes(new)
        hashes[rel] = {'before': digest(raw), 'after': digest(new)}
    MANIFEST.write_text(json.dumps({
        'backup': str(backup), 'hashes': hashes,
        'province_changes': {p: [before[p], after[p]] for p in before if before[p] != after[p]},
        'country_provinces': audit(before, after),
        'notes': ['three former Kyoto coal-mine levels become sulfur-mine levels',
                  'the old Mausoleum port level transfers to Sunflower Field'],
    }, ensure_ascii=False, indent=2), encoding='utf-8')


def check():
    report = json.loads(MANIFEST.read_text(encoding='utf-8'))
    later_path = OUT / 'east_four_way_revision.json'
    later = json.loads(later_path.read_text(encoding='utf-8')) if later_path.exists() else None
    newest_path = OUT / 'eientei_outline_revision.json'
    newest = json.loads(newest_path.read_text(encoding='utf-8')) if newest_path.exists() else None
    def stage_bytes(rel):
        current = (ROOT / rel).read_bytes()
        if newest and rel in newest['hashes']:
            assert digest(current) == newest['hashes'][rel]['after'], rel
            current = (Path(newest['backup']) / rel).read_bytes()
            assert digest(current) == newest['hashes'][rel]['before'], rel
        if later and rel in later['hashes']:
            raw = (Path(later['backup']) / rel).read_bytes()
            assert digest(current) == later['hashes'][rel]['after'], rel
            assert digest(raw) == later['hashes'][rel]['before'], rel
            return raw
        return current
    for rel, values in report['hashes'].items():
        assert digest(stage_bytes(rel)) == values['after'], rel
    before = west.ownership((Path(report['backup']) / STATE_HISTORY).read_text(encoding='utf-8-sig'))
    after = west.ownership(stage_bytes(STATE_HISTORY).decode('utf-8-sig'))
    changes = {p: [before[p], after[p]] for p in before if before[p] != after[p]}
    assert changes == report['province_changes']
    audit(before, after)
    for tag in ('KYTO', 'SHRM', 'MYRN'):
        states = {state for state, owner in after.values() if owner == tag}
        assert len(states) == 1
        a, b = west.block((ROOT / COUNTRIES).read_text(encoding='utf-8-sig'), tag)
        assert re.search(r'capital\s*=\s*(STATE_\w+)', (ROOT / COUNTRIES).read_text(encoding='utf-8-sig')[a:b])[1] in states
    print(json.dumps({'status': 'static validation passed; not game-tested',
                      'changed_provinces': len(changes),
                      'country_provinces': report['country_provinces']}, ensure_ascii=False))


def rebuild():
    """Reformat the installed migration from its saved pre-change files."""
    report = json.loads(MANIFEST.read_text(encoding='utf-8'))
    originals = {}
    for rel, values in report['hashes'].items():
        assert digest((ROOT / rel).read_bytes()) == values['after'], rel
        originals[rel] = (Path(report['backup']) / rel).read_bytes()
        assert digest(originals[rel]) == values['before'], rel
    before = west.ownership(originals[STATE_HISTORY].decode('utf-8-sig'))
    after = target_ownership(before)
    texts = edit_texts(originals, before, after)
    validate_payload(originals, texts, after)
    for rel, content in texts.items():
        raw = originals[rel]
        new = content.replace('\r\n', '\n').encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):
            new = b'\xef\xbb\xbf' + new
        (ROOT / rel).write_bytes(new)
        report['hashes'][rel]['after'] = digest(new)
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    check()


if __name__ == '__main__':
    if '--preview' in sys.argv:
        preview()
    elif '--apply' in sys.argv:
        apply()
        check()
    elif '--rebuild' in sys.argv:
        rebuild()
    else:
        check()
