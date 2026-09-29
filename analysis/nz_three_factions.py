"""Apply an explicit contiguous New Zealand split, then refresh startup economy.

Run --apply once against checkpoint 2a5a25d. No Australian province changes.
"""
import collections
import datetime
import json
import re
import shutil
import sys
import western_industry_prototype
import eastern_industry_prototype as e
from population_arable_prototype import spans

SOUTH_NORTH_ISLAND = set('x0FDAD6 x1000F0 x1080F0 x160E3F x59DF28 x810EEB x9000F0 x9080F0 x91D53E xCCD9EE xD0B89C xEBB583'.split())
e.PREFIX = 'nz_three_factions_v1'
e.CHECKPOINT = '2a5a25d'
e.BACKUP_PREFIX = 'nz_economy_before_'
e.HISTORY_LABEL = 'Gensokyo startup industry with New Zealand three factions'
e.POPULATION_SNAPSHOT = 'population_after_nz_three_factions.json'
e.STATES.update(NI='STATE_NORTH_ISLAND', SI='STATE_SOUTH_ISLAND')
e.PLAN.extend([
    ('MTOU', 'NI', dict(wheat=1, ranch=1, wood=2, iron=1, coal=1,
        tools=1, paper=1, glass=1, government=1, port=1, university=1)),
    ('JNKF', 'NI', dict(wheat=1, ranch=1, wood=1, tools=1, glass=1,
        government=1, port=1)),
    ('HCTI', 'SI', dict(wheat=3, ranch=2, wood=3, fish=1, tools=1,
        paper=1, food=1, clothes=1, government=1, port=1)),
])


def replace_body(source, pattern, body):
    matches = list(spans(source, pattern))
    assert len(matches) == 1, pattern
    match, _, end = matches[0]
    opening = source.index('{', match.start())
    return source[:opening+1] + body + source[end-1:]


def state_creation(tag, provinces):
    return '\n\t\tcreate_state = {\n\t\t\tcountry = c:' + tag + '\n\t\t\towned_provinces = { ' + ' '.join(sorted(provinces)) + ' }\n\t\t}\n'


def connected(provinces, adjacency):
    seen = {next(iter(provinces))}
    queue = list(seen)
    while queue:
        for p in adjacency[queue.pop()]:
            if p in provinces and p not in seen:
                seen.add(p)
                queue.append(p)
    return seen == provinces


def apply_geography():
    root = e.ROOT
    state_path = root/'common/history/states/00_states.txt'
    state_source = state_path.read_text(encoding='utf-8-sig')
    owners = e.ownership(state_source)
    north = {p for p,v in owners.items() if v[0] == e.STATES['NI']}
    south = {p for p,v in owners.items() if v[0] == e.STATES['SI']}
    assert all(owners[p][1] == 'MTOU' for p in north|south), 'Already migrated or different baseline'
    assert SOUTH_NORTH_ISLAND < north
    context = json.loads((e.OUT/'west_coast_context.json').read_text(encoding='utf-8'))
    assert connected(SOUTH_NORTH_ISLAND, context['adj'])
    assert connected(north-SOUTH_NORTH_ISLAND, context['adj'])
    homeland = '\t\tadd_homeland = cu:australian\n\t\tadd_homeland = cu:maori\n\t'
    states = replace_body(state_source, r's:STATE_NORTH_ISLAND\s*=\s*\{',
        state_creation('MTOU',north-SOUTH_NORTH_ISLAND)+state_creation('JNKF',SOUTH_NORTH_ISLAND)+homeland)
    states = replace_body(states, r's:STATE_SOUTH_ISLAND\s*=\s*\{',state_creation('HCTI',south)+homeland)
    updated_owners = e.ownership(states)
    assert set(owners) == set(updated_owners)
    assert all(updated_owners[p] == v for p,v in owners.items() if p not in north|south)

    pop_path = root/'common/history/pops/13_australasia.txt'
    pops = pop_path.read_text(encoding='utf-8-sig')
    north_body = next(b for m,b,_ in spans(pops,r's:STATE_NORTH_ISLAND\s*=\s*\{'))
    regions = list(spans(north_body,r'region_state:MTOU\s*=\s*\{'))
    old_pop_body = regions[0][1]
    new_pop_bodies = []
    for tag, numer in [('MTOU',65),('JNKF',35)]:
        split = re.sub(r'(\bsize\s*=\s*)(\d+)',
            lambda m:m[1]+str(int(m[2])*numer//100 if tag=='MTOU' else int(m[2])-int(m[2])*65//100),old_pop_body)
        new_pop_bodies.append('\n\t\tregion_state:'+tag+' = {'+split+'\t\t}\n')
    pops = replace_body(pops,r's:STATE_NORTH_ISLAND\s*=\s*\{',''.join(new_pop_bodies)+'\t')
    pops = replace_body(pops,r's:STATE_SOUTH_ISLAND\s*=\s*\{',
        next(b for m,b,_ in spans(pops,r's:STATE_SOUTH_ISLAND\s*=\s*\{')).replace('region_state:MTOU','region_state:HCTI'))

    definitions_path = root/'common/country_definitions/tot_countries.txt'
    defs = definitions_path.read_text(encoding='utf-8-sig')
    assert not re.search(r'(?m)^\s*(JNKF|HCTI)\s*=',defs)
    defs = defs.replace('MTOU = { # 月都：新西兰两岛','MTOU = { # 月都：新西兰北岛北部')
    for tag,comment,color,state in [('JNKF','纯狐阵营：新西兰北岛南部','179 103 55',e.STATES['NI']),('HCTI','赫卡提亚地狱：新西兰南岛','110 72 112',e.STATES['SI'])]:
        defs += '\n'+tag+' = { # '+comment+'\n\tcolor = { '+color+' }\n\tcountry_type = unrecognized\n\ttier = principality\n\treligion = shinto\n\tcultures = { japanese }\n\tcapital = '+state+'\n}\n'
    country_path = root/'common/history/countries/tot_gensokyo_australasia.txt'
    country = country_path.read_text(encoding='utf-8-sig')
    insertion = ''.join('\n\tc:'+tag+' ?= {\n\t\teffect_starting_technology_tier_2_tech = yes\n\t\teffect_starting_politics_conservative = yes\n\t\tset_tax_level = medium\n\t}\n' for tag in ['JNKF','HCTI'])
    last = country.rfind('}')
    country = country[:last]+insertion+country[last:]
    diplomacy_path = root/'common/history/diplomacy/tot_gensokyo_subjects.txt'
    diplomacy = diplomacy_path.read_text(encoding='utf-8-sig').replace('\tc:HAKR ?= {',
        '\tc:HAKR ?= {\n\t\tcreate_diplomatic_pact = { country = c:JNKF type = tot_gensokyo_protectorate }\n\t\tcreate_diplomatic_pact = { country = c:HCTI type = tot_gensokyo_protectorate }')
    buildings_path = root/'common/history/buildings/13_australasia.txt'
    buildings = buildings_path.read_text(encoding='utf-8-sig')
    ni = next(b for m,b,_ in spans(buildings,r's:STATE_NORTH_ISLAND\s*=\s*\{'))
    ni = re.sub(r'(levels\s*=\s*)3\b',r'\g<1>2',ni,count=1)
    barrack = next(b for _,b,_ in spans(ni,r'create_building\s*=\s*\{') if 'building_barrack' in b)
    pure_barrack = barrack.replace('c:MTOU','c:JNKF')
    pure_barrack = re.sub(r'(levels\s*=\s*)2\b',r'\g<1>1',pure_barrack,count=1)
    ni += '\n\t\tregion_state:JNKF = {\n\t\t\tcreate_building = {'+pure_barrack+'}\n\t\t}\n\t'
    buildings = replace_body(buildings,r's:STATE_NORTH_ISLAND\s*=\s*\{',ni)
    buildings = buildings.replace('region_state:MTOU = {\n\t\t}\n\t}', 'region_state:HCTI = {\n\t\t}\n\t}')

    character_lines = ['# Calendar ages are scenario placeholders, not canon birth dates.', 'CHARACTERS = {']
    for tag,name,trait in [('JNKF','tot_gensokyo_junko_name','persistent'),('HCTI','tot_gensokyo_hecatia_name','charismatic')]:
        character_lines += ['\tc:'+tag+' ?= {','\t\tcreate_character = {','\t\t\thistorical = yes',
            '\t\t\tfirst_name = "'+name+'"','\t\t\tbirth_date = 1810.1.1','\t\t\tfemale = yes',
            '\t\t\truler = yes','\t\t\tig_leader = yes','\t\t\tinterest_group = ig_landowners',
            '\t\t\tculture = cu:japanese','\t\t\treligion = rel:shinto','\t\t\ttraits = { '+trait+' }','\t\t}','\t}']
    character_lines += ['}','']
    loc = 'l_simp_chinese:\n JNKF: "纯狐阵营"\n JNKF_ADJ: "纯狐阵营"\n HCTI: "赫卡提亚地狱"\n HCTI_ADJ: "赫卡提亚地狱"\n tot_gensokyo_junko_name: "纯狐"\n tot_gensokyo_hecatia_name: "赫卡提亚"\n'
    flags = ''.join(tag+' = {\n\tflag_definition = { coa = '+tag+' priority = 2000 }\n}\n' for tag in ['JNKF','HCTI'])
    coa = '\n'.join(tag+' = {\n\tpattern = "pattern_solid.tga"\n\tcolor1 = rgb { '+color+' }\n}\n' for tag,color in [('JNKF','179 103 55'),('HCTI','110 72 112')])
    files = {state_path:states,pop_path:pops,definitions_path:defs,country_path:country,diplomacy_path:diplomacy,
        buildings_path:buildings,root/'common/history/characters/tot_gensokyo_nz.txt':'\n'.join(character_lines),
        root/'localization/replace/simp_chinese/common/core/tot_gensokyo_nz_l_simp_chinese.yml':loc,
        root/'common/flag_definitions/tot_gensokyo_nz.txt':flags,root/'common/coat_of_arms/coat_of_arms/tot_gensokyo_nz.txt':coa}
    for path,text in files.items():
        if path.suffix=='.txt':assert e.clean(text).count('{') == e.clean(text).count('}'),str(path)
    backup = root/'docs/backups'/('nz_three_factions_before_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True)
    added=[]
    for path,text in files.items():
        if path.exists():
            dest=backup/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
        else:added.append(str(path.relative_to(root)))
    (backup/'new_files.json').write_text(json.dumps(added,indent=2),encoding='utf-8')
    for path,text in files.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding='utf-8-sig' if path.suffix=='.yml' else 'utf-8')

    population = collections.defaultdict(collections.Counter)
    for path in (root/'common/history/pops').glob('*.txt'):
        for sm,sb in e.blocks(e.clean(path.read_text(encoding='utf-8-sig')),r's:(STATE_\w+)\s*=\s*\{'):
            for tm,tb in e.blocks(sb,r'region_state:(\w+)\s*=\s*\{'):
                if (sm[1],tm[1]) in {tuple(v) for v in updated_owners.values()}:
                    for _,pb in e.blocks(tb,r'create_pop\s*=\s*\{'):
                        population[sm[1]][tm[1]]+=int(re.search(r'\bsize\s*=\s*(\d+)',pb)[1])
    assert sum(population[e.STATES[k]][t] for k,t in [('NI','MTOU'),('NI','JNKF'),('SI','HCTI')])==800000
    (e.OUT/e.POPULATION_SNAPSHOT).write_text(json.dumps({'population_by_state':population},ensure_ascii=False,indent=2),encoding='utf-8')
    manifest=dict(checkpoint=e.CHECKPOINT,backup=str(backup),north_moon=sorted(north-SOUTH_NORTH_ISLAND),north_junko=sorted(SOUTH_NORTH_ISLAND),south_hecatia=sorted(south),population={t:population[e.STATES[k]][t] for k,t in [('NI','MTOU'),('NI','JNKF'),('SI','HCTI')]})
    (e.OUT/'nz_three_factions_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply_geography()
        e.main(True)
    else:
        print('Explicit split prepared: Moon northern North Island, Junko southern North Island, Hecatia South Island. Run --apply once.')
