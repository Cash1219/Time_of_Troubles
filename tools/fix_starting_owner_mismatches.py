"""Repair stale region owners without changing populations, PMs or level totals."""
import json
import re
from pathlib import Path
from collections import Counter
import audit_starting_building_losses as audit
from building_history_config import parse_items, children, value

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'analysis/starting_building_review_20261009/after_owner_fix'
TARGETS = {
    'STATE_BREST': ('POL','VLG'),
    'STATE_NEW_YORK': ('HHWO','NRHD'),
    'STATE_KENTUCKY': ('USAF','SLOF'),
    'STATE_TRANSJORDAN': ('TJOR','MYG'),
    'STATE_LEBANON': ('LEBN','MYG'),
    'STATE_SYRIA': ('DMAS','MYG'),
    'STATE_MOSUL': ('MOSL','KIVO'),
    'STATE_DEIR_EZ_ZOR': ('DEZR','KIVO'),
    'STATE_SAKHALIN': ('EZO','AIN'),
}


def signature(records):
    return Counter((r['state'],r['building'],r['levels'],tuple(r['pms']),tuple(r['conditions'])) for r in records)


def population_signature():
    result=Counter()
    for p in audit.files('common/history/pops',True):
        for root in audit.parsed(p):
            if root[0]!='POPS': continue
            for state in root[1]:
                if not state[0].startswith('s:'): continue
                for region in state[1]:
                    for pop in children(region,'create_pop'):
                        result[(state[0],repr(pop[1]))]+=1
    # Parser offsets differ after edits; only scalar contents are semantic.
    return Counter((s,re.sub(r', \d+, \d+\)', ')',v)) for s,v in result.elements())


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    before,_=audit.buildings(True)
    pop_before=population_signature()
    owners=audit.owners(True)
    changes=[]
    pending={}
    for folder,root_name in [('common/history/buildings','BUILDINGS'),('common/history/pops','POPS')]:
        for p in sorted((ROOT/folder).glob('*.txt')):
            raw=p.read_bytes()
            text=raw.decode('utf-8-sig')
            edits=[]
            for root in parse_items(text)[0]:
                if root[0]!=root_name: continue
                for state in root[1]:
                    s=state[0].removeprefix('s:')
                    if s not in TARGETS: continue
                    old,new=TARGETS[s]
                    assert new in owners[s],(s,new)
                    for region in children(state,'region_state:'+old):
                        start,end=region[2],region[3]
                        chunk=text[start:end]
                        fixed=chunk.replace('region_state:'+old,'region_state:'+new,1)
                        ownership_edits=[]
                        if root_name=='BUILDINGS':
                            for b in children(region,'create_building'):
                                for own in children(b,'add_ownership'):
                                    for part in own[1]:
                                        # Existing company shares can be foreign-owned.
                                        if part[0]=='company': continue
                                        if value(part,'country')!='c:'+old: continue
                                        owner_region=value(part,'region')
                                        if part[0]=='building' and owner_region and owner_region!=s: continue
                                        fragment=text[part[2]:part[3]]
                                        replacement=re.sub(r'(\bcountry\s*=\s*"?c:)'+old+r'\b',r'\g<1>'+new,fragment)
                                        ownership_edits.append((part[2]-start,part[3]-start,replacement))
                            # All tags have equal length except some destinations;
                            # use original offsets before replacing the region header.
                            fixed=chunk
                            for lo,hi,replacement in reversed(ownership_edits):
                                fixed=fixed[:lo]+replacement+fixed[hi:]
                            fixed=fixed.replace('region_state:'+old,'region_state:'+new,1)
                        edits.append((start,end,fixed))
                        changes.append({'file':p.relative_to(ROOT).as_posix(),'state':s,'old':old,'new':new,'kind':root_name,'line':text.count('\n',0,start)+1,'ownership_parts_retargeted':len(ownership_edits)})
            if edits:
                for start,end,fixed in reversed(edits): text=text[:start]+fixed+text[end:]
                parse_items(text) # Validate the complete edited file before writing.
                pending[p]=(raw, (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8'))
    csv_path=ROOT/'config/building_start_config.csv'
    raw=csv_path.read_bytes()
    old=b'B0024,yes,STATE_NEW_YORK,HHWO,'
    new=b'B0024,yes,STATE_NEW_YORK,NRHD,'
    if old in raw:
        assert raw.count(old)==1
        pending[csv_path]=(raw,raw.replace(old,new))
    try:
        for p,(_,new_bytes) in pending.items(): p.write_bytes(new_bytes)
        after,_=audit.buildings(True)
        assert signature(before)==signature(after),'Building levels/PMs changed'
        assert pop_before==population_signature(),'Population sizes/cultures/religions changed'
        assert not [r for r in after if r['owner'] not in owners.get(r['state'],{})]
        assert not audit.population_mismatches(owners)
        from building_history_config import load_config,inventory,canonical
        rows=load_config()
        actual,issues=inventory()
        assert not issues,issues
        assert Counter(canonical(r) for r in actual)==Counter(canonical(r) for r in rows if r['enabled']=='yes'),'Configured building history and CSV differ'
    except Exception:
        for p,(old_bytes,_) in pending.items(): p.write_bytes(old_bytes)
        raise
    (OUTPUT/'repair_manifest.json').write_text(json.dumps({'changes':changes,'modified_files':[p.relative_to(ROOT).as_posix() for p in pending],'building_levels_before':sum(r['levels'] for r in before),'building_levels_after':sum(r['levels'] for r in after),'company_shares':'NY stage retains HHWO company ownership; geographic owner is NRHD','sakhalin_decision':'AIN owns the Sakhalin port hub x2492AA; former EZO population is 601 Ainu and 39 Japanese'},ensure_ascii=False,indent=2),encoding='utf-8')
    audit.OUT=OUTPUT
    audit.main()
    print('PASS: no building/population owner mismatches; levels, PMs and demographics preserved; CSV matches history.')


if __name__=='__main__': main()
