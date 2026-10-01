"""Apply the reviewed supply and territory pass to the current opening setup."""
from pathlib import Path
import re

from population_arable_prototype import spans
from west_coast_draft import ownership, components

ROOT = Path(__file__).resolve().parents[1]
BUILDINGS = ROOT / 'common/history/buildings/tot_gensokyo_eastern_industry.txt'
STATES = ROOT / 'common/history/states/00_states.txt'
POPS = ROOT / 'common/history/pops/12_indonesia.txt'
ISLAND_BUILDINGS = ROOT / 'common/history/buildings/12_indonesia.txt'
REGIONS = ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt'

# A narrow southern extension for Yakumo and a contiguous northern hinterland
# for Higan. Both donor territories remain connected.
WEST_MOVES = {
    'YKMF': 'x569B91 xAE9278 xF54ED3 x9F8D50 x6CACF6'.split(),
    'HIGN': 'xCA0C39 xF59CE1 xC61B3B x85C28A xC5CAFA xE3DE71 x3CBBDF xD4BD14'.split(),
}

# Existing entries: set final levels, never add a duplicate building type to a
# region_state. Agriculture stays within the existing expanded arable capacity.
LEVELS = {
    ('STATE_VICTORIA', 'HITO', 'building_food_industry'): 8,
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_sugar_plantation'): 5,
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_tea_plantation'): 5,
    ('STATE_QUEENSLAND', 'MRYA', 'building_sugar_plantation'): 5,
    ('STATE_QUEENSLAND', 'MRYA', 'building_tea_plantation'): 3,
    ('STATE_VICTORIA', 'EITR', 'building_wheat_farm'): 4,
    ('STATE_VICTORIA', 'EITR', 'building_tea_plantation'): 4,
    ('STATE_NEW_SOUTH_WALES', 'EITR', 'building_tea_plantation'): 3,
    ('STATE_WESTERN_AUSTRALIA', 'HIGN', 'building_wheat_farm'): 4,
    ('STATE_WESTERN_AUSTRALIA', 'HIGN', 'building_food_industry'): 4,
    ('STATE_WESTERN_AUSTRALIA', 'HIGN', 'building_fishing_wharf'): 2,
    ('STATE_WESTERN_AUSTRALIA', 'YKMF', 'building_wheat_farm'): 3,
    ('STATE_WESTERN_AUSTRALIA', 'YKMF', 'building_food_industry'): 3,
    ('STATE_WESTERN_AUSTRALIA', 'YKMF', 'building_textile_mill'): 3,
    ('STATE_WESTERN_AUSTRALIA', 'YKMF', 'building_glassworks'): 3,
    ('STATE_NORTHERN_TERRITORY', 'MKAI', 'building_sugar_plantation'): 6,
}

NEW = {
    ('STATE_VICTORIA', 'EITR'): [('building_sugar_plantation', 3), ('building_food_industry', 4), ('building_silk_plantation', 2)],
    ('STATE_NEW_SOUTH_WALES', 'EITR'): [('building_sugar_plantation', 2), ('building_food_industry', 2)],
    ('STATE_WESTERN_AUSTRALIA', 'HIGN'): [('building_vineyard', 2), ('building_textile_mill', 2)],
    ('STATE_WESTERN_AUSTRALIA', 'YKMF'): [('building_silk_plantation', 1)],
    ('STATE_SOLOMON_ISLANDS', 'TENG'): [('building_rice_farm', 2), ('building_fishing_wharf', 2), ('building_food_industry', 2), ('building_port', 1)],
    ('STATE_TONGA', 'TENG'): [('building_rice_farm', 2), ('building_fishing_wharf', 2), ('building_food_industry', 2), ('building_port', 1)],
    ('STATE_FIJI', 'TENG'): [('building_coffee_plantation', 2), ('building_fishing_wharf', 2), ('building_food_industry', 2)],
    ('STATE_VANUATU', 'TENG'): [('building_coffee_plantation', 2), ('building_fishing_wharf', 2), ('building_food_industry', 2)],
    ('STATE_KANAK', 'TENG'): [('building_lead_mine', 2), ('building_food_industry', 2)],
}

PMS = {
    'building_silk_plantation': '"default_building_silk_plantation" "pm_road_carts"',
    'building_sugar_plantation': '"default_building_sugar_plantation" "ox_driven_rollers_sugar" "slave_exploitation_sugar" "pm_road_carts"',
    'building_wheat_farm': '"pm_simple_farming" "pm_no_secondary" "pm_tools_disabled"',
    'building_rice_farm': '"pm_simple_farming_building_rice_farm" "pm_no_secondary" "pm_tools_disabled"',
    'building_vineyard': '"default_building_vineyard" "pm_road_carts"',
    'building_coffee_plantation': '"default_building_coffee_plantation" "pm_road_carts"',
    'building_fishing_wharf': '"pm_simple_fishing" "pm_unrefrigerated"',
    'building_food_industry': '"pm_bakery" "pm_disabled_canning" "pm_disabled_distillery" "pm_manual_dough_processing"',
    'building_textile_mill': '"pm_handsewn_clothes" "pm_no_luxury_clothes" "pm_traditional_looms"',
    'building_glassworks': '"pm_forest_glass" "pm_disabled_ceramics" "pm_manual_glassblowing"',
    'building_lead_mine': '"pm_atmospheric_engine_pump_building_lead_mine" "pm_no_explosives" "pm_no_steam_automation" "pm_road_carts"',
    'building_port': '"pm_basic_port"',
}


def replace_scoped(text, state, tag, kind, replacement):
    seen = []
    for sm, sb, _ in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
        if sm[1] != state:
            continue
        sb_start = text.index('{', sm.start()) + 1
        for rm, rb, _ in spans(sb, r'region_state:(\w+)\s*=\s*\{'):
            if rm[1] != tag:
                continue
            rb_start = sb_start + sb.index('{', rm.start()) + 1
            for bm, bb, be in spans(rb, r'create_building\s*=\s*\{'):
                if re.search(r'\bbuilding\s*=\s*"([^"]+)"', bb)[1] == kind:
                    start = rb_start + bm.start()
                    seen.append((start, rb_start + be))
    assert len(seen) == 1, (state, tag, kind, seen)
    s, e = seen[0]
    return text[:s] + replacement(text[s:e]) + text[e:]


def block_for(state, tag, kind, levels):
    owner = 'building = { type = "building_manor_house" country = "c:%s" levels = %d region = "%s" }' % (tag, levels, state) if kind.endswith(('farm','plantation','ranch','vineyard')) else 'building = { type = "building_financial_district" country = "c:%s" levels = %d region = "%s" }' % (tag, levels, state)
    if kind == 'building_port':
        owner = 'country = { country = "c:%s" levels = %d }' % (tag, levels)
    return ('\n\t\t\tcreate_building = {\n\t\t\t\tbuilding = "%s"\n\t\t\t\tactivate_production_methods = { %s }\n\t\t\t\tadd_ownership = { %s }\n\t\t\t\treserves = 1\n\t\t\t}' % (kind, PMS[kind], owner))


def add_scoped(text, state, tag, entries):
    for sm, sb, _ in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
        if sm[1] != state: continue
        sb_start = text.index('{', sm.start()) + 1
        for rm, rb, re_ in spans(sb, r'region_state:(\w+)\s*=\s*\{'):
            if rm[1] != tag: continue
            existing = {m[1] for m in re.finditer(r'\bbuilding\s*=\s*"(building_\w+)"', rb)}
            assert not existing.intersection(k for k,_ in entries), (state,tag,existing)
            at = sb_start + re_ - 1
            return text[:at] + ''.join(block_for(state,tag,k,n) for k,n in entries) + '\n\t\t' + text[at:]
    # New island region-state block: empty vanilla entries are in another file.
    body = '\n\ts:%s = {\n\t\tregion_state:%s = {' % (state,tag)
    body += ''.join(block_for(state,tag,k,n) for k,n in entries)
    body += '\n\t\t}\n\t}\n'
    assert text.rstrip().endswith('}'), 'BUILDINGS root not found'
    return text.rstrip()[:-1] + body + '}\n'


def update_buildings():
    text = BUILDINGS.read_text(encoding='utf-8-sig')
    for key, level in LEVELS.items():
        def edit(body):
            found = re.search(r'\blevels\s*=\s*\d+', body)
            assert found, key
            return body[:found.start()] + 'levels = %d' % level + body[found.end():]
        text = replace_scoped(text, *key, edit)
    for (state,tag), entries in NEW.items():
        text = add_scoped(text,state,tag,entries)
    BUILDINGS.write_text(text, encoding='utf-8-sig')


def replace_state_owner(text, state, old, new):
    for sm, sb, se in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
        if sm[1] != state: continue
        original = text[sm.start():se]
        updated = original.replace('country = c:'+old, 'country = c:'+new, 1)
        assert updated != original, (state,old)
        return text[:sm.start()] + updated + text[se:]
    raise AssertionError(state)


def update_states_and_pops():
    text = STATES.read_text(encoding='utf-8-sig')
    current = ownership(text)
    for target, provinces in WEST_MOVES.items():
        for p in provinces:
            assert current[p][0] == 'STATE_WESTERN_AUSTRALIA'
            old = current[p][1]
            # The province occurs twice in this file (province set and owner).
            for sm, sb, se in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
                if sm[1] != 'STATE_WESTERN_AUSTRALIA': continue
                for cm, cb, ce in spans(sb, r'create_state\s*=\s*\{'):
                    if re.search(r'country\s*=\s*c:'+old+r'\b', cb) and re.search(r'\b'+p+r'\b',cb,re.I):
                        cstart = text.index('{',sm.start())+1+cm.start()
                        original = text[cstart:cstart+(ce-cm.start())]
                        updated = re.sub(r'(?i)\b'+p+r'\b','',original,count=1)
                        text = text[:cstart]+updated+text[cstart+len(original):]
                        break
                else: continue
                break
            for sm, sb, se in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
                if sm[1] != 'STATE_WESTERN_AUSTRALIA': continue
                for cm, cb, ce in spans(sb, r'create_state\s*=\s*\{'):
                    if re.search(r'country\s*=\s*c:'+target+r'\b', cb):
                        cstart = text.index('{',sm.start())+1+cm.start()
                        original = text[cstart:cstart+(ce-cm.start())]
                        updated = re.sub(r'owned_provinces\s*=\s*\{',lambda m:m[0]+' '+p,original,count=1)
                        assert updated!=original
                        text = text[:cstart]+updated+text[cstart+len(original):]
                        break
                else: continue
                break
    for state,old in [('STATE_SOLOMON_ISLANDS','BLA'),('STATE_TONGA','TNG')]:
        text = replace_state_owner(text,state,old,'TENG')
    final = ownership(text)
    import json
    ctx = json.loads((ROOT/'docs/drafts/west_coast_context.json').read_text(encoding='utf-8'))
    for tag in ('YKMF','HIGN','BYKR','RNGN'):
        ps=[p for p,v in final.items() if v==['STATE_WESTERN_AUSTRALIA',tag]]
        assert len(components(ps,ctx['adj']))==1,tag
    for tag,provinces in WEST_MOVES.items():
        assert all(final[p]==['STATE_WESTERN_AUSTRALIA',tag] for p in provinces)
    STATES.write_text(text,encoding='utf-8-sig')
    pops = POPS.read_text(encoding='utf-8-sig')
    for old in ('BLA','TNG'):
        state = 'STATE_SOLOMON_ISLANDS' if old=='BLA' else 'STATE_TONGA'
        for sm,sb,se in spans(pops,r's:(STATE_\w+)\s*=\s*\{'):
            if sm[1]==state:
                original=pops[sm.start():se]
                new=original.replace('region_state:'+old,'region_state:TENG')
                assert new!=original
                pops=pops[:sm.start()]+new+pops[se:]
                break
    POPS.write_text(pops,encoding='utf-8-sig')
    oldbuild = ISLAND_BUILDINGS.read_text(encoding='utf-8-sig')
    for old,state in [('BLA','STATE_SOLOMON_ISLANDS'),('TNG','STATE_TONGA')]:
        for sm,sb,se in spans(oldbuild,r's:(STATE_\w+)\s*=\s*\{'):
            if sm[1]==state:
                original=oldbuild[sm.start():se]
                new=original.replace('region_state:'+old,'region_state:TENG')
                assert new!=original
                oldbuild=oldbuild[:sm.start()]+new+oldbuild[se:]
                break
    ISLAND_BUILDINGS.write_text(oldbuild,encoding='utf-8-sig')


def update_regions():
    text=REGIONS.read_text(encoding='utf-8-sig')
    for state in ('STATE_NEW_SOUTH_WALES','STATE_VICTORIA','STATE_WESTERN_AUSTRALIA'):
        for m,b,e in spans(text,r'(?m)^('+state+r')\s*=\s*\{'):
            original=text[m.start():e]
            updated=re.sub(r'(arable_resources\s*=\s*\{[^}]*)(\})',lambda x:x[1]+' "building_silk_plantation" '+x[2],original,count=1)
            assert updated!=original and updated.count('"building_silk_plantation"')==1
            text=text[:m.start()]+updated+text[e:]
            break
    REGIONS.write_text(text,encoding='utf-8-sig')


def check():
    import collections
    import json
    states = STATES.read_text(encoding='utf-8-sig')
    current = ownership(states)
    ctx = json.loads((ROOT/'docs/drafts/west_coast_context.json').read_text(encoding='utf-8'))
    assert len(current) == len(set(current))
    for tag, provinces in WEST_MOVES.items():
        assert all(current[p] == ['STATE_WESTERN_AUSTRALIA',tag] for p in provinces)
    for tag in ('YKMF','HIGN','BYKR','RNGN'):
        ps = [p for p,v in current.items() if v == ['STATE_WESTERN_AUSTRALIA',tag]]
        assert len(components(ps,ctx['adj'])) == 1,tag
    for state in ('STATE_SOLOMON_ISLANDS','STATE_TONGA'):
        assert {v[1] for v in current.values() if v[0] == state} == {'TENG'}
    province_mentions = collections.Counter()
    for sm,sb,_ in spans(states,r's:(STATE_\w+)\s*=\s*\{'):
        if sm[1] != 'STATE_WESTERN_AUSTRALIA': continue
        for cm,cb,_ in spans(sb,r'create_state\s*=\s*\{'):
            provinces = re.search(r'owned_provinces\s*=\s*\{([^}]*)',cb)[1]
            province_mentions.update(x.upper() for x in re.findall(r'\bx[0-9a-fA-F]{6}\b',provinces))
    assert all(n == 1 for n in province_mentions.values()), [p for p,n in province_mentions.items() if n != 1]
    assert len(province_mentions) == len([p for p,v in current.items() if v[0] == 'STATE_WESTERN_AUSTRALIA'])
    pops=POPS.read_text(encoding='utf-8-sig')
    oldbuild=ISLAND_BUILDINGS.read_text(encoding='utf-8-sig')
    for state, old in [('STATE_SOLOMON_ISLANDS','BLA'),('STATE_TONGA','TNG')]:
        for data in (pops,oldbuild):
            chunks=[sb for sm,sb,_ in spans(data,r's:(STATE_\w+)\s*=\s*\{') if sm[1]==state]
            assert len(chunks)==1 and 'region_state:TENG' in chunks[0] and 'region_state:'+old not in chunks[0]
    regions=REGIONS.read_text(encoding='utf-8-sig')
    for state in ('STATE_NEW_SOUTH_WALES','STATE_VICTORIA','STATE_WESTERN_AUSTRALIA'):
        chunks=[sb for sm,sb,_ in spans(regions,r'(?m)^(STATE_\w+)\s*=\s*\{') if sm[1]==state]
        assert len(chunks)==1 and '"building_silk_plantation"' in chunks[0]
    content=BUILDINGS.read_text(encoding='utf-8-sig')
    levels=collections.Counter()
    for sm,sb,_ in spans(content,r's:(STATE_\w+)\s*=\s*\{'):
        for rm,rb,_ in spans(sb,r'region_state:(\w+)\s*=\s*\{'):
            for bm,bb,_ in spans(rb,r'create_building\s*=\s*\{'):
                kind=re.search(r'\bbuilding\s*=\s*"(building_\w+)"',bb)[1]
                n=re.search(r'\blevels\s*=\s*(\d+)',bb)
                assert n, (sm[1],rm[1],kind)
                levels[(sm[1],rm[1],kind)] += int(n[1])
    for key,n in LEVELS.items(): assert levels[key]==n,(key,levels[key],n)
    for (state,tag),entries in NEW.items():
        for kind,n in entries: assert levels[(state,tag,kind)]==n,(state,tag,kind)
    # Full-employment marginal capacities, based on the installed vanilla PMs.
    result=dict(west_provinces={tag:len([p for p,v in current.items() if v==['STATE_WESTERN_AUSTRALIA',tag]]) for tag in ('YKMF','HIGN','BYKR','RNGN')},
                island_states=['STATE_SOLOMON_ISLANDS','STATE_TONGA'],
                new_levels=dict(sugar=13,tea=10,silk=3,pot_stills=6),
                nominal_added_output=dict(sugar=325,tea=200,silk=45,liquor=360),
                additional_sugar_for_distilleries=150)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    import sys
    assert sys.argv[1:] in (['--apply'],['--check'])
    if sys.argv[1:]==['--apply']:
        update_states_and_pops()
        update_regions()
        update_buildings()
    check()
