"""Read-only audit of current Gensokyo ownership, population and regional resources."""
import collections
import json
import re
from pathlib import Path

from west_coast_draft import GAME, ROOT, NAMES, close, ownership

OUT = ROOT / 'docs/drafts'
TAGS = set(NAMES) - {'WAS'}
POP_DRAFT = {
    'HITO': (360, '粮食、棉花、牲畜、食品与纺织；主要居民和内需中心'),
    'YKYM': (220, '煤、铁、木材；工具、机械和山地工业'),
    'CHRD': (160, '本部与绿洲服务地下矿业；特殊采矿、地热和地下交通另行定义'),
    'MKAI': (130, '北部农业、木材及综合工业；魔法制造作为后续特色'),
    'BYKR': (130, '西南粮食、果园、葡萄、畜牧与食品加工'),
    'RDMK': (120, '南澳制造、葡萄酒、玻璃与化工；本地矿种据地质再细分'),
    'MRYA': (100, '北部农牧、林业和工程产业；能源依赖实际设施'),
    'TENG': (100, '新西兰农牧、木材、渔业；群岛糖与热带园艺'),
    'EITR': (75, '林业、药用园艺与精细制造；医疗服务机制另做'),
    'MFSR': (70, '木材、园艺、工具与工艺品；进口煤铁，减少重工业自给'),
    'RNGN': (70, '西部矿业、陶瓷、建筑材料与加工制造；埴轮产能另做'),
    'HAKR': (70, '港口、贸易、服务和基础制造；维护结界作为特色机制'),
    'KZNH': (50, '观赏植物、果树、园艺；高附加值特色，不承担主粮供应'),
    'MYRN': (50, '农业、手工业与宗教设施；与人里保持贸易'),
    'KYTO': (50, '矿业配套、工具、酒类与南部交通'),
    'HIGN': (45, '沿海服务、渡运、渔业和少量加工；判决机制另做'),
    'UKDO': (45, '西北矿业物流、贸易与服务；后户空间不是免费无限运力'),
    'SHRM': (40, '工艺制造、宗教设施和有限农牧；与命莲寺区分产业侧重'),
    'YKMF': (35, '西岸交通、贸易与工艺品；结界能力留给机制'),
    'MTOU': (35, '塔斯马尼亚林业、农牧、港口与技术制造'),
    'MIST': (30, '湖岸园艺与冰相关设施；盐湖本身不提供淡水或海洋渔业'),
    'YSSK': (15, '食品、饮料、居酒屋与服务；依赖人里原料供应'),
}


def clean(text):
    return re.sub(r'#[^\n]*', '', text)


def blocks(text, pattern):
    for m in re.finditer(pattern, text):
        opening = text.index('{', m.start())
        yield m, text[opening + 1:close(text, opening) - 1]


def main():
    owners = ownership((ROOT / 'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    holdings = collections.defaultdict(collections.Counter)
    for state, tag in owners.values():
        if tag in TAGS:
            holdings[state][tag] += 1
    valid_pairs = {(state, tag) for state, tags in holdings.items() for tag in tags}
    entries = []
    for path in sorted((ROOT / 'common/history/pops').glob('*.txt')):
        text = clean(path.read_text(encoding='utf-8-sig'))
        for state_match, state_body in blocks(text, r's:(STATE_\w+)\s*=\s*\{'):
            state = state_match[1]
            if state not in holdings:
                continue
            for owner_match, owner_body in blocks(state_body, r'region_state:(\w+)\s*=\s*\{'):
                tag = owner_match[1]
                for _, pop in blocks(owner_body, r'create_pop\s*=\s*\{'):
                    size = re.search(r'\bsize\s*=\s*(\d+)', pop)
                    if not size:
                        raise ValueError('Unsupported population size: ' + str(path))
                    culture = re.search(r'\bculture\s*=\s*(\w+)', pop)
                    entries.append(dict(state=state, tag=tag, size=int(size[1]),
                                        culture=culture[1] if culture else 'mixed',
                                        source=str(path.relative_to(ROOT)),
                                        owner_matches=(state, tag) in valid_pairs))
    definitions = {}
    for directory in [GAME / 'map_data/state_regions', ROOT / 'map_data/state_regions']:
        for path in sorted(directory.glob('*.txt')):
            text = clean(path.read_text(encoding='utf-8-sig'))
            for m, body in blocks(text, r'(?m)^\s*(STATE_\w+)\s*=\s*\{'):
                if m[1] not in holdings:
                    continue
                capped = {}
                for _, cap_body in blocks(body, r'\bcapped_resources\s*=\s*\{'):
                    capped.update({key: int(value) for key, value in re.findall(r'(building_\w+)\s*=\s*(\d+)', cap_body)})
                discovered = []
                for _, resource_body in blocks(body, r'\bresource\s*=\s*\{'):
                    discovered.append(resource_body.strip())
                arable = re.search(r'\barable_land\s*=\s*(\d+)', body)
                definitions[m[1]] = dict(source=str(path), arable_land=int(arable[1]) if arable else 0,
                                         capped_resources=capped, discoverable_resources=discovered)
    region_buildings = []
    for path in sorted((ROOT / 'common/history/buildings').glob('*.txt')):
        text = clean(path.read_text(encoding='utf-8-sig'))
        for m, body in blocks(text, r's:(STATE_\w+)\s*=\s*\{'):
            if m[1] not in holdings:
                continue
            for tag_match, tag_body in blocks(body, r'region_state:(\w+)\s*=\s*\{'):
                for _, building_body in blocks(tag_body, r'create_building\s*=\s*\{'):
                    kind = re.search(r'\bbuilding\s*=\s*"?(building_\w+)', building_body)
                    region_buildings.append(dict(state=m[1], tag=tag_match[1], building=kind[1] if kind else 'unknown',
                                                 owner_matches=(m[1], tag_match[1]) in valid_pairs,
                                                 source=str(path.relative_to(ROOT))))
    countries = {}
    for tag in sorted(TAGS):
        countries[tag] = dict(name=NAMES[tag], provinces=sum(tags[tag] for tags in holdings.values()),
                              states=[state for state, tags in holdings.items() if tag in tags],
                              population_in_matching_history_scopes=sum(e['size'] for e in entries if e['tag'] == tag and e['owner_matches']))
    totals = collections.Counter()
    for data in definitions.values():
        totals.update(data['capped_resources'])
    report = dict(countries=countries, holdings={k: dict(v) for k, v in holdings.items()},
                  state_resources=definitions, population_entries=entries,
                  invalid_population_scopes=[e for e in entries if not e['owner_matches']],
                  population_written_total=sum(e['size'] for e in entries),
                  population_matching_owner_scopes=sum(e['size'] for e in entries if e['owner_matches']),
                  building_entries=region_buildings,
                  invalid_building_scopes=[e for e in region_buildings if not e['owner_matches']],
                  total_arable_land=sum(d['arable_land'] for d in definitions.values()),
                  total_capped_resources=dict(totals),
                  caveat='Matching history scopes are not a measurement of loaded in-game population; inherited files, script effects and engine behavior may differ. Resource totals belong to state regions, not individual countries.')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'gensokyo_economy_baseline.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    proposal = dict(status='initial baseline only; revise workforce budgets for restricted external immigration before implementation',
                    constraints=dict(external_immigration='highly restricted or prohibited in early game; exclude from workforce budget',
                                     migration_between_gensokyo_countries='undecided',
                                     base_workforce_ratio_for_estimates=0.25,
                                     illustrative_jobs_per_building_level=5000,
                                     cavern_policy=dict(regular_construction='unrestricted',
                                                        population_candidate_min=5000,
                                                        population_candidate_max=20000,
                                                        special_facility_jobs_per_level_min=100,
                                                        special_facility_jobs_per_level_max=300,
                                                        replaces_previous_cavern_population=400000,
                                                        revised_totals_not_confirmed=True)),
                    total_population=sum(v[0] * 10000 for v in POP_DRAFT.values()),
                    countries={tag: dict(name=NAMES[tag], population=population * 10000, role=role)
                               for tag, (population, role) in POP_DRAFT.items()})
    assert set(POP_DRAFT) == TAGS
    assert proposal['total_population'] == 20000000
    (OUT / 'gensokyo_population_proposal_v1.json').write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = ['| 势力 | 当前匹配归属的人口记录 | 开局人口草案 | 产业方向 |',
            '|---|---:|---:|---|']
    for tag, (population, role) in POP_DRAFT.items():
        name = '冰之领地' if tag == 'MIST' else NAMES[tag]
        rows.append('| {} | {:,} | {}万 | {} |'.format(name, countries[tag]['population_in_matching_history_scopes'], population, role))
    detail = '\n'.join(rows)
    intro = (OUT / 'gensokyo_population_resources_v1.md').read_text(encoding='utf-8')
    marker = '<!-- COUNTRY_TABLE -->'
    end_marker = '<!-- /COUNTRY_TABLE -->'
    if marker in intro:
        start = intro.index(marker) + len(marker)
        finish = intro.index(end_marker)
        intro = intro[:start] + '\n\n' + detail + '\n\n' + intro[finish:]
        (OUT / 'gensokyo_population_resources_v1.md').write_text(intro, encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['population_written_total', 'population_matching_owner_scopes', 'total_arable_land', 'total_capped_resources']}, ensure_ascii=False))
    print('Invalid pop blocks:', len(report['invalid_population_scopes']), 'Invalid building entries:', len(report['invalid_building_scopes']))
    for tag, data in countries.items():
        print(tag, data['name'], data['provinces'], data['population_in_matching_history_scopes'], ','.join(data['states']))


if __name__ == '__main__':
    main()
