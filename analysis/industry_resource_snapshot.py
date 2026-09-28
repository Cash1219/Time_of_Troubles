"""Snapshot effective Gensokyo economy data without changing runtime files."""
import collections
import json
import re
from gensokyo_economy_audit import blocks, clean, TAGS
from west_coast_draft import GAME, ROOT, NAMES, ownership

owners = ownership((ROOT / 'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
holdings = collections.defaultdict(collections.Counter)
for state, tag in owners.values():
    if tag in TAGS:
        holdings[state][tag] += 1
pairs = {(s, t) for s, tags in holdings.items() for t in tags}
pop = collections.Counter()
state_pop = collections.defaultdict(collections.Counter)
invalid_pops, buildings = [], []
for path in sorted((ROOT / 'common/history/pops').glob('*.txt')):
    for m, body in blocks(clean(path.read_text(encoding='utf-8-sig')), r's:(STATE_\w+)\s*=\s*\{'):
        if m[1] not in holdings:
            continue
        for t, part in blocks(body, r'region_state:(\w+)\s*=\s*\{'):
            sizes = [int(n) for n in re.findall(r'\bsize\s*=\s*(\d+)', part)]
            if (m[1], t[1]) in pairs:
                pop[t[1]] += sum(sizes)
                state_pop[m[1]][t[1]] += sum(sizes)
            elif sizes:
                invalid_pops.append([m[1], t[1], sum(sizes)])
definitions = {}
for directory in [GAME / 'map_data/state_regions', ROOT / 'map_data/state_regions']:
    for path in sorted(directory.glob('*.txt')):
        for m, body in blocks(clean(path.read_text(encoding='utf-8-sig')), r'(?m)^\s*(STATE_\w+)\s*=\s*\{'):
            if m[1] not in holdings:
                continue
            caps = {}
            for _, cap in blocks(body, r'\bcapped_resources\s*=\s*\{'):
                caps.update({k: int(v) for k, v in re.findall(r'(building_\w+)\s*=\s*(\d+)', cap)})
            arable = re.search(r'\barable_land\s*=\s*(\d+)', body)
            definitions[m[1]] = dict(arable=int(arable[1]) if arable else 0, caps=caps,
                discoveries=[r.strip() for _, r in blocks(body, r'\bresource\s*=\s*\{')],
                source=str(path))
for path in sorted((ROOT / 'common/history/buildings').glob('*.txt')):
    for m, body in blocks(clean(path.read_text(encoding='utf-8-sig')), r's:(STATE_\w+)\s*=\s*\{'):
        if m[1] not in holdings:
            continue
        for t, part in blocks(body, r'region_state:(\w+)\s*=\s*\{'):
            for _, entry in blocks(part, r'create_building\s*=\s*\{'):
                kind = re.search(r'\bbuilding\s*=\s*"?(building_\w+)', entry)
                level = re.search(r'\blevel\s*=\s*(\d+)', entry)
                buildings.append(dict(state=m[1], tag=t[1], building=kind[1] if kind else '?',
                    level=int(level[1]) if level else None, valid=(m[1], t[1]) in pairs))
caps_total = collections.Counter()
for data in definitions.values():
    caps_total.update(data['caps'])
report = dict(date='2026-09-29', population=sum(pop.values()),
    population_by_country={t: dict(name=NAMES[t], population=pop[t], workforce_estimate=pop[t]*0.25) for t in sorted(TAGS)},
    population_by_state=state_pop, arable_total=sum(d['arable'] for d in definitions.values()),
    capped_total=caps_total, states=definitions, buildings=buildings, invalid_pops=invalid_pops,
    caveat='Effective file definitions, not a loaded-game census. Resource capacities are state-region totals.')
out = ROOT / 'docs/drafts/industry_resources_current_20260929.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(dict(population=report['population'], arable=report['arable_total'], caps=caps_total,
    invalid_pops=invalid_pops, invalid_buildings=[b for b in buildings if not b['valid']]), ensure_ascii=False))
for s, d in definitions.items():
    print(s, 'POP', dict(state_pop[s]), 'LAND', d['arable'], 'CAPS', d['caps'])
