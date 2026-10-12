"""Apply the approved 42 plantation + 41 industry + 12 other opening compensation."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import audit_starting_building_losses as audit
from building_history_config import children, value, parse_items

ROOT = audit.ROOT
OUT = ROOT / 'analysis/british_overseas_assets_20261010'
MANIFEST = OUT / 'implemented_compensation.json'

def main():
    if MANIFEST.exists():
        raise SystemExit('Compensation already applied; refusing to add it twice.')
    before, _ = audit.buildings(True)
    vanilla, _ = audit.buildings(False)
    plan = []
    def add(category, state, building, levels, host='GBR'):
        plan.append(dict(category=category, state='STATE_'+state, building='building_'+building,
                         levels=levels, host=host))
    add('plantation', 'WEST_BENGAL', 'opium_plantation', 19, 'BIC')
    for building, levels in [('dye_plantation',11),('tobacco_plantation',5),
                            ('sugar_plantation',1),('banana_plantation',4),('silk_plantation',2)]:
        add('plantation', 'EAST_BENGAL', building, levels, 'BIC')
    for building, placements in [
        ('tooling_workshop',[('YORKSHIRE',2),('WEST_COUNTRY',3)]),
        ('steel_mill',[('YORKSHIRE',3),('MIDLANDS',3)]),
        ('motor_industry',[('YORKSHIRE',1),('MIDLANDS',3)]),
        ('textile_mill',[('LANCASHIRE',6),('YORKSHIRE',2)]),
        ('paper_mill',[('HOME_COUNTIES',4)]),
        ('furniture_manufactory',[('MIDLANDS',4)]),
        ('glassworks',[('HOME_COUNTIES',2),('EAST_ANGLIA',2)]),
        ('food_industry',[('HOME_COUNTIES',3),('WEST_COUNTRY',3)])]:
        for state, levels in placements:
            add('industry', state, building, levels)
    for state, building, levels in [
        ('YORKSHIRE','iron_mine',2),('MIDLANDS','iron_mine',2),
        ('HOME_COUNTIES','furniture_manufactory',1),('HOME_COUNTIES','trade_center',1),
        ('HIGHLANDS','whaling_station',1),('HIGHLANDS','logging_camp',3),
        ('HOME_COUNTIES','port',1),('WEST_COUNTRY','port',1)]:
        add('other',state,building,levels)
    totals = Counter()
    for r in plan: totals[r['category']] += r['levels']
    assert totals == {'plantation':42,'industry':41,'other':12}
    owners = audit.owners(True)
    definitions = audit.definitions('map_data/state_regions', True)
    pm_defs = audit.definitions('common/production_methods', True)
    files = {}; edits = defaultdict(list)
    for r in plan:
        assert r['host'] in owners[r['state']]
        existing = [b for b in before if (b['state'],b['owner'],b['building']) ==
                    (r['state'],r['host'],r['building']) and not b['conditions']]
        if existing:
            reference = existing[0]
        else:
            reference = next(b for b in before + vanilla if b['building']==r['building'] and
                             b['owner']==r['host'] and not b['conditions'])
        r['pms'] = reference['pms']
        assert all(pm in pm_defs for pm in r['pms'])
        r['ownership_kind'] = 'country' if r['building']=='building_port' else 'building'
        r['owner_building'] = 'building_manor_house' if r['category']=='plantation' else 'building_financial_district'
        node = definitions[r['state']]
        if r['category']=='plantation':
            arable = children(node,'arable_resources')[0][1]
            assert r['building'] in [x[0].strip('"') for x in arable]
        for caps in children(node,'capped_resources'):
            cap = value(caps,r['building'])
            if cap:
                used = sum(b['levels'] for b in before if b['state']==r['state'] and b['building']==r['building'])
                assert used+r['levels'] <= int(cap), (r,used,cap)
        path = Path(existing[0]['file']) if existing else next(
            Path(b['file']) for b in before if b['state']==r['state'] and b['owner']==r['host'] and not b['conditions'])
        assert path.is_relative_to(ROOT)
        if path not in files:
            files[path] = path.read_text(encoding='utf-8-sig')
        text = files[path]
        root = next(x for x in parse_items(text)[0] if x[0]=='BUILDINGS')
        state = next(x for x in root[1] if x[0]=='s:'+r['state'])
        region = next(x for x in state[1] if x[0]=='region_state:'+r['host'])
        own = '\n\t\t\t\t# Approved British overseas asset compensation (2026-10-10)\n\t\t\t\tadd_ownership = {\n'
        if r['ownership_kind']=='country':
            own += '\t\t\t\t\tcountry = { country = "c:GBR" levels = '+str(r['levels'])+' }\n'
        else:
            own += '\t\t\t\t\tbuilding = { type = "'+r['owner_building']+'" country = "c:GBR" levels = '+str(r['levels'])+' region = "STATE_HOME_COUNTIES" }\n'
        own += '\t\t\t\t}\n'
        if existing:
            target = next(x for x in children(region,'create_building') if value(x,'building')==r['building'])
            edits[path].append((target[3]-1,own))
        else:
            block = '\n\t\t\tcreate_building = {\n\t\t\t\tbuilding = "'+r['building']+'"'+own
            block += '\t\t\t\treserves = 1\n\t\t\t\tactivate_production_methods = { '+ ' '.join('"'+pm+'"' for pm in r['pms'])+' }\n\t\t\t}\n'
            edits[path].append((region[3]-1,block))
        r['file'] = str(path.relative_to(ROOT))
        r['before_levels'] = sum(b['levels'] for b in existing)
    for path, changes in edits.items():
        text = files[path]
        for pos, inserted in sorted(changes, key=lambda x:x[0], reverse=True):
            text = text[:pos]+inserted+text[pos:]
        parse_items(text)
        path.write_text(text,encoding='utf-8-sig',newline='')
    after, warnings = audit.buildings(True)
    def aggregate(bs):
        result=Counter()
        for b in bs: result[b['state'],b['owner'],b['building']] += b['levels']
        return result
    b0,b1 = aggregate(before),aggregate(after)
    expected=Counter()
    for r in plan: expected[r['state'],r['host'],r['building']] += r['levels']
    assert b1-b0 == expected and not b0-b1
    for r in plan:
        added=sum(o['levels'] for b in after if (b['state'],b['owner'],b['building'])==
                  (r['state'],r['host'],r['building']) for o in b['ownership'] if o['country']=='c:GBR')
        old=sum(o['levels'] for b in before if (b['state'],b['owner'],b['building'])==
                (r['state'],r['host'],r['building']) for o in b['ownership'] if o['country']=='c:GBR')
        assert added-old==r['levels']
    MANIFEST.write_text(json.dumps(dict(status='implemented',mode='compensation; source buildings retained',
        totals=dict(totals),placements=plan,validation='Exactly 95 added levels; all added ownership GBR; no removed levels; valid PM IDs and checked resource caps'),ensure_ascii=False,indent=2),encoding='utf-8-sig')
    print(json.dumps(dict(totals=dict(totals),changed_files=[str(p.relative_to(ROOT)) for p in files]),indent=2))

if __name__=='__main__':
    main()
