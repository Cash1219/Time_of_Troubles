"""Build/validate an eastern economy prototype; --apply writes runtime files.

No ownership, population or arable acreage changes. Existing unrelated building history
is retained. Historical colonies with no local land lose stale building scopes.
"""
import collections
import datetime
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from gensokyo_economy_audit import clean, blocks
from population_arable_prototype import spans
from west_coast_draft import ROOT, GAME, NAMES, close, ownership

OUT = ROOT / 'docs/drafts'
PREFIX = 'eastern_industry_v1'
CHECKPOINT = '7be45d6'
BACKUP_PREFIX = 'eastern_industry_before_'
HISTORY_LABEL = 'Eastern industry test v1'
ARABLE_ADDITIONS = {'VIC': ['building_opium_plantation']}
ALIASES = {
    'wheat': 'wheat_farm', 'ranch': 'livestock_ranch', 'cotton': 'cotton_plantation',
    'sugar': 'sugar_plantation', 'tea': 'tea_plantation', 'wine': 'vineyard',
    'opium': 'opium_plantation', 'wood': 'logging_camp', 'fish': 'fishing_wharf',
    'coal': 'coal_mine', 'iron': 'iron_mine', 'lead': 'lead_mine', 'sulfur': 'sulfur_mine',
    'food': 'food_industry', 'clothes': 'textile_mill', 'furniture': 'furniture_manufactory',
    'glass': 'glassworks', 'tools': 'tooling_workshop', 'paper': 'paper_mill',
    'steel': 'steel_mill', 'engines': 'motor_industry', 'fertilizer': 'chemical_plant',
    'shipyard': 'shipyard', 'government': 'government_administration', 'university': 'university',
    'construction': 'construction_sector', 'port': 'port', 'garden': 'botanical_garden',
    'temple': 'religious_center', 'izakaya': 'izakaya',
    'kappa_power': 'tot_kappa_power', 'fusion': 'tot_chireiden_fusion',
}
STATES = { 'NSW': 'STATE_NEW_SOUTH_WALES', 'VIC': 'STATE_VICTORIA',
    'QLD': 'STATE_QUEENSLAND', 'SA': 'STATE_SOUTH_AUSTRALIA', 'TAS': 'STATE_TASMANIA',
    'CORE': 'STATE_CHIREIDEN_CAPITAL' }
PLAN = [
    ('HITO', 'NSW', dict(wheat=25, ranch=10, cotton=7, sugar=2, tea=2, wine=2,
        food=5, clothes=4, furniture=2, paper=1, wood=3, iron=1, coal=2, tools=2,
        government=2, university=1, construction=2)),
    ('HITO', 'VIC', dict(wheat=8, ranch=3, food=2, clothes=1, government=1)),
    ('YKYM', 'QLD', dict(coal=6, iron=6, wood=5, tools=3, steel=3, engines=1,
        paper=1, ranch=2, clothes=1, government=2, university=1, port=1,
        construction=1, kappa_power=1)),
    ('YKYM', 'NSW', dict(coal=2, iron=1, wood=1, tools=1, steel=1, ranch=2,
        food=1, clothes=1, government=1, port=1)),
    ('MFSR', 'QLD', dict(wood=3, paper=3, furniture=1, garden=1, wheat=1,
        ranch=1, tools=1, government=1)),
    ('MFSR', 'NSW', dict(wood=2, paper=1, furniture=1, wheat=1, garden=1,
        tools=1, government=1)),
    ('MRYA', 'QLD', dict(wood=2, coal=2, iron=1, cotton=4, sugar=2, ranch=4,
        tea=1, wheat=3, tools=1, paper=1, temple=1, glass=1,
        government=1, port=1)),
    ('HAKR', 'NSW', dict(port=2, government=2, university=1, food=1, glass=1,
        shipyard=1, tools=1, wood=1, fish=1, wheat=2, wine=1, clothes=1,
        ranch=1, construction=1, temple=1)),
    ('MYRN', 'NSW', dict(wheat=3, ranch=2, cotton=1, food=1, wood=1,
        garden=1, temple=1, government=1)),
    ('EITR', 'VIC', dict(wood=3, ranch=2, wheat=2, tea=1, opium=2,
        clothes=1, garden=1, government=1, port=1)),
    ('EITR', 'NSW', dict(garden=1, tea=1, government=1)),
    ('RDMK', 'TAS', dict(wood=3, iron=1, lead=1, fish=1, wheat=1, opium=1,
        food=1, glass=1, shipyard=1, government=1, port=1)),
    ('RDMK', 'VIC', dict(wine=2, food=1, wood=1, fish=1, ranch=2, clothes=1,
        government=1, port=1)),
    ('MIST', 'VIC', dict(fish=1, ranch=1, garden=1, food=1, government=1, port=1)),
    ('YSSK', 'NSW', dict(izakaya=1, food=1, wine=1, wheat=1, government=1)),
    ('KZNH', 'SA', dict(wheat=2, wine=2, ranch=1, garden=3, fertilizer=1,
        glass=1, food=1, government=1, port=1)),
    ('SHRM', 'SA', dict(wheat=2, wine=1, ranch=1, glass=2, furniture=1,
        paper=1, temple=1, government=1, port=1)),
    ('CHRD', 'SA', dict(wheat=5, ranch=3, iron=3, lead=1, sulfur=2, wood=3,
        steel=2, tools=2, fertilizer=1, food=2, government=2, port=1, fusion=1)),
    ('CHRD', 'CORE', dict(tools=1, paper=1, engines=1, government=1)),
]
RESOURCE_UPDATES = {
    'NSW': dict(coal=80, iron=36, lead=24, wood=24),
    'QLD': dict(coal=60, iron=45, lead=45, wood=36),
    'VIC': dict(coal=30, sulfur=24, wood=24),
    'SA': dict(iron=30, lead=36, sulfur=60, wood=12),
    'TAS': dict(iron=15, lead=15, wood=12),
}
FIRST_PM = {'wood': 'pm_saw_mills', 'tools': 'pm_steel', 'paper': 'pm_pulp_press',
    'steel': 'pm_blister_steel_process', 'engines': 'pm_steam_engines',
    'government': 'pm_horizontal_drawer_cabinets', 'port': 'pm_basic_port',
    'coal': 'pm_atmospheric_engine_pump_building_coal_mine',
    'iron': 'pm_atmospheric_engine_pump_building_iron_mine',
    'lead': 'pm_atmospheric_engine_pump_building_lead_mine',
    'sulfur': 'pm_atmospheric_engine_pump_building_sulfur_mine'}
TECH_GRANTS = {
    'YKYM': ['watertube_boiler', 'rotary_valve_engine', 'electrical_generation'],
    'CHRD': ['watertube_boiler', 'rotary_valve_engine', 'electrical_generation', 'intensive_agriculture'],
    'KZNH': ['intensive_agriculture'],
}


def definitions(folder):
    result = {}
    for root in [GAME, ROOT]:
        for path in sorted((root / folder).glob('*.txt')):
            for m, body in blocks(clean(path.read_text(encoding='utf-8-sig')), r'(?m)^\s*([\w-]+)\s*=\s*\{'):
                result[m[1]] = body
    return result


def list_block(body, key):
    found = list(blocks(body, r'\b' + re.escape(key) + r'\s*=\s*\{'))
    return re.findall(r'[\w-]+', found[0][1]) if found else []


def patch_state_resources(source):
    replacements = []
    for m, body, end in spans(source, r'(?m)^\s*(STATE_\w+)\s*=\s*\{'):
        key = next((k for k, s in STATES.items() if s == m[1]), None)
        if key not in RESOURCE_UPDATES:
            continue
        updated = body
        for cm, cap, cap_end in spans(body, r'\bcapped_resources\s*=\s*\{'):
            data = {k: int(v) for k, v in re.findall(r'(building_\w+)\s*=\s*(\d+)', cap)}
            data.update({'building_' + ALIASES[k]: n for k, n in RESOURCE_UPDATES[key].items()})
            cap_text = 'capped_resources = {\n' + ''.join('        {} = {}\n'.format(k, n) for k, n in data.items()) + '    }'
            updated = body[:cm.start()] + cap_text + body[cap_end:]
            break
        assert updated != body or key in RESOURCE_UPDATES
        for building in ARABLE_ADDITIONS.get(key, []):
            if building not in list_block(updated, 'arable_resources'):
                updated = re.sub(r'(arable_resources\s*=\s*\{)', r'\1 "' + building + '"', updated, count=1)
        opening = source.index('{', m.start())
        replacements.append((opening + 1, end - 1, updated))
    for start, end, value in reversed(replacements):
        source = source[:start] + value + source[end:]
    return source


def main(apply=False):
    owners = ownership((ROOT / 'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    pairs = {tuple(value) for value in owners.values()}
    population = json.loads((OUT / 'industry_resources_current_20260929.json').read_text(encoding='utf-8'))
    bdefs, groups, pms = [definitions(d) for d in ('common/buildings', 'common/production_method_groups', 'common/production_methods')]
    techs = definitions('common/technology/technologies')
    starting = {k for k, body in techs.items() if re.search(r'\bera\s*=\s*era_1\b', body)}
    starting.update(['mechanical_tools', 'atmospheric_engine', 'dialectics', 'egalitarianism', 'corporate_charters'])
    selected = []
    for tag, state_key, levels in PLAN:
        state = STATES[state_key]
        assert (state, tag) in pairs, (state, tag)
        for alias, count in levels.items():
            kind = 'building_' + ALIASES[alias]
            assert kind in bdefs, kind
            chosen = []
            for group in list_block(bdefs[kind], 'production_method_groups'):
                candidates = list_block(groups[group], 'production_methods')
                assert candidates
                method = next((p for p in candidates if re.search(r'\bis_default\s*=\s*yes', pms[p])), candidates[0])
                override = FIRST_PM.get(alias)
                if override in candidates:
                    method = override
                if alias == 'wood' and ((tag == 'YKYM' and state_key == 'QLD') or (tag == 'CHRD' and state_key == 'SA')) and 'pm_electric_saw_mills' in candidates:
                    method = 'pm_electric_saw_mills'
                if alias == 'food' and tag in ('RDMK', 'YSSK') and 'pm_pot_stills' in candidates:
                    method = 'pm_pot_stills'
                assert method in pms
                chosen.append(method)
            available = starting | set(TECH_GRANTS.get(tag, []))
            for item in [bdefs[kind]] + [pms[p] for p in chosen]:
                missing = set(list_block(item, 'unlocking_technologies')) - available
                assert not missing, (tag, kind, missing)
            jobs = sum(sum(int(n) for n in re.findall(r'building_employment_\w+_add\s*=\s*(-?\d+)', pms[p])) for p in chosen)
            goods = collections.Counter()
            for p in chosen:
                for direction, good, amount in re.findall(r'goods_(input|output)_(\w+)_add\s*=\s*(-?\d+)', pms[p]):
                    goods[good] += int(amount) * (1 if direction == 'output' else -1)
            selected.append(dict(tag=tag, state=state, building=kind, levels=count,
                pms=chosen, jobs_per_level=jobs, total_jobs=jobs*count,
                goods_net={k: v*count for k, v in goods.items()}))
    job_totals = collections.Counter()
    regional_jobs = collections.Counter()
    net = collections.Counter()
    local_power = collections.Counter()
    for row in selected:
        job_totals[row['tag']] += row['total_jobs']
        regional_jobs[(row['state'], row['tag'])] += row['total_jobs']
        for good, n in row['goods_net'].items():
            net[good] += n
            if good == 'electricity':
                local_power[(row['state'], row['tag'])] += n
    for (state, tag), jobs in regional_jobs.items():
        pop = population['population_by_state'][state][tag]
        assert jobs <= pop * .25 * .8, (state, tag, jobs, pop)
    assert all(n >= 0 for n in local_power.values()), local_power
    # Remove old scopes only where they are superseded or have no actual owner.
    old_path = ROOT / 'common/history/buildings/13_australasia.txt'
    old = old_path.read_text(encoding='utf-8-sig')
    targets = {(STATES[s], t) for t, s, _ in PLAN}
    removals = []
    preserved_military = []
    for sm, body, _ in spans(old, r's:(STATE_\w+)\s*=\s*\{'):
        opening = old.index('{', sm.start()) + 1
        for tm, region_body, end in spans(body, r'region_state:(\w+)\s*=\s*\{'):
            pair = (sm[1], tm[1])
            if pair in targets or pair not in pairs:
                keep = []
                if pair in pairs:
                    for bm, bb, be in spans(region_body, r'create_building\s*=\s*\{'):
                        kind = re.search(r'\bbuilding\s*=\s*"?(building_\w+)', bb)
                        if kind and kind[1] in ('building_barrack', 'building_naval_base'):
                            keep.append('\t\t\t' + region_body[bm.start():be])
                            preserved_military.append(dict(state=sm[1], tag=tm[1], building=kind[1]))
                replacement = 'region_state:' + tm[1] + ' = {\n' + '\n'.join(keep) + '\n\t\t}' if keep else ''
                removals.append((opening + tm.start(), opening + end, replacement))
    for start, end, replacement in reversed(removals):
        old = old[:start] + replacement + old[end:]
    old = '\n'.join(line.rstrip() for line in old.splitlines()) + '\n'
    history = ['# ' + HISTORY_LABEL + ': generated from explicit current-owner plan.', 'BUILDINGS = {']
    for tag, skey, _ in PLAN:
        state = STATES[skey]
        history += ['\ts:{} = {{'.format(state), '\t\tregion_state:{} = {{'.format(tag)]
        for row in [r for r in selected if r['state'] == state and r['tag'] == tag]:
            history += ['\t\t\tcreate_building = {', '\t\t\t\tbuilding = "{}"'.format(row['building']),
                '\t\t\t\tactivate_production_methods = { ' + ' '.join('"{}"'.format(p) for p in row['pms']) + ' }']
            alias = next(a for a, b in ALIASES.items() if row['building'] == 'building_' + b)
            history += ['\t\t\t\tadd_ownership = {']
            if alias in ('government', 'university', 'port', 'construction', 'kappa_power', 'fusion', 'temple', 'garden', 'izakaya'):
                history += ['\t\t\t\t\tcountry = { country = "c:' + tag + '" levels = ' + str(row['levels']) + ' }']
            else:
                holder = 'building_manor_house' if alias in ('wheat', 'ranch', 'cotton', 'sugar', 'tea', 'wine', 'opium') else 'building_financial_district'
                history += ['\t\t\t\t\tbuilding = { type = "' + holder + '" country = "c:' + tag + '" levels = ' + str(row['levels']) + ' region = "' + state + '" }']
            history += ['\t\t\t\t}', '\t\t\t\treserves = 1', '\t\t\t}']
        history += ['\t\t}', '\t}']
    history += ['}', '']
    resource_path = ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt'
    resources = patch_state_resources(resource_path.read_text(encoding='utf-8-sig'))
    # Avoid re-applying by updating a separate, narrowly scoped history file.
    tech_history = ['COUNTRIES = {']
    for tag, tech_list in TECH_GRANTS.items():
        tech_history += ['\tc:' + tag + ' ?= {'] + ['\t\tadd_technology_researched = ' + t for t in tech_list] + ['\t}']
    tech_history += ['}', '']
    files = {old_path: old, ROOT / 'common/history/buildings/tot_gensokyo_eastern_industry.txt': '\n'.join(history),
        resource_path: resources, ROOT / 'common/history/countries/tot_gensokyo_electricity.txt': '\n'.join(tech_history)}
    # Assert unchanged provinces/arable and capacity/arable limits before writing.
    for m, before in blocks(clean(resource_path.read_text(encoding='utf-8-sig')), r'(?m)^\s*(STATE_\w+)\s*=\s*\{'):
        after = next(body for am, body in blocks(clean(resources), r'(?m)^\s*(STATE_\w+)\s*=\s*\{') if am[1] == m[1])
        for key in ('provinces', 'impassable', 'prime_land'):
            assert list_block(before, key) == list_block(after, key), (m[1], key)
        assert re.findall(r'\barable_land\s*=\s*(\d+)', before) == re.findall(r'\barable_land\s*=\s*(\d+)', after)
        cap = dict((k, int(n)) for _, cb in blocks(after, r'\bcapped_resources\s*=\s*\{') for k, n in re.findall(r'(building_\w+)\s*=\s*(\d+)', cb))
        prime = set(list_block(after, 'prime_land'))
        provinces = set(list_block(after, 'provinces'))
        arable = int(re.search(r'\barable_land\s*=\s*(\d+)', after)[1])
        for row in (r for r in selected if r['state'] == m[1]):
            if row['building'].endswith(('_farm', '_plantation', '_ranch', '_vineyard')):
                assert row['building'] in list_block(after, 'arable_resources'), (m[1], row['tag'], row['building'], 'not an allowed crop')
        for tag in {r['tag'] for r in selected if r['state'] == m[1]}:
            owned = {p for p, st in owners.items() if tuple(st) == (m[1], tag)}
            farm_levels = sum(r['levels'] for r in selected if r['state'] == m[1] and r['tag'] == tag and r['building'].endswith(('_farm', '_plantation', '_ranch', '_vineyard')))
            weighted = (len(owned) + 4*len(owned & prime)) / (len(provinces) + 4*len(prime))
            assert farm_levels <= int(arable*weighted), (m[1], tag, 'farms', farm_levels, arable*weighted)
            for building, n in cap.items():
                count = sum(r['levels'] for r in selected if r['state'] == m[1] and r['tag'] == tag and r['building'] == building)
                # Conservative estimate: check both plain and prime-weighted fractions.
                limit = max(1, int(n * min(len(owned)/len(provinces), weighted)))
                assert count <= limit, (m[1], tag, building, count, limit)
    backup = None
    if apply:
        backup = ROOT / 'docs/backups' / (BACKUP_PREFIX + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        backup.mkdir(parents=True)
        new_files = []
        support_files = [ROOT / p for p in ('common/buildings/tot_gensokyo_power.txt',
            'common/production_method_groups/tot_gensokyo_power.txt', 'common/production_methods/tot_gensokyo_power.txt',
            'localization/replace/simp_chinese/common/buildings/tot_gensokyo_power_l_simp_chinese.yml')]
        for path in files:
            if path.exists():
                dest = backup / path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
            else:
                new_files.append(str(path.relative_to(ROOT)))
        new_files.extend(str(p.relative_to(ROOT)) for p in support_files if not p.exists())
        (backup / 'new_files.json').write_text(json.dumps(new_files, indent=2), encoding='utf-8')
        for path, text in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    report = dict(applied=apply, checkpoint=CHECKPOINT, backup=str(backup) if backup else None,
        plan=selected, jobs_by_country=job_totals, net_goods_before_consumers_and_other_regions=dict(net),
        jobs_by_region=[dict(state=s, tag=t, jobs=n, population=population['population_by_state'][s][t]) for (s,t),n in regional_jobs.items()],
        local_power=[dict(state=s, tag=t, surplus=n) for (s,t),n in local_power.items()],
        removed_old_history_scopes=len(removals), preserved_military=preserved_military,
        warning='Static full-employment accounting; excludes urban centers, households, other regions, ownership-building employment, wages and prices. No in-game validation yet.')
    (OUT / (PREFIX + '_validation.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(applied=apply, buildings=len(selected), levels=sum(r['levels'] for r in selected),
        jobs=dict(job_totals), local_power=report['local_power'], net=dict(net), backup=report['backup']), ensure_ascii=False))


if __name__ == '__main__':
    main('--apply' in sys.argv)
