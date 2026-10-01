"""Apply the second opening-industry pass once from explicit targets."""
from pathlib import Path
import re
import sys

from population_arable_prototype import spans

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'common/history/buildings/tot_gensokyo_eastern_industry.txt'

# Keep distilling concentrated in the Human Village's Victoria works and Hakugyokuro.
LEVELS = {
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_food_industry'): 6,
    ('STATE_VICTORIA', 'HITO', 'building_food_industry'): 2,
    ('STATE_NEW_SOUTH_WALES', 'HAKR', 'building_food_industry'): 4,
    ('STATE_NEW_SOUTH_WALES', 'YKYM', 'building_food_industry'): 2,
    ('STATE_SOUTH_AUSTRALIA', 'CHRD', 'building_food_industry'): 3,
    ('STATE_SOUTH_AUSTRALIA', 'KYTO', 'building_food_industry'): 2,
    ('STATE_WESTERN_AUSTRALIA', 'HIGN', 'building_food_industry'): 2,
    ('STATE_NORTHERN_TERRITORY', 'MKAI', 'building_food_industry'): 3,
    ('STATE_SOUTH_ISLAND', 'HCTI', 'building_food_industry'): 2,
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_textile_mill'): 5,
    ('STATE_NEW_SOUTH_WALES', 'HAKR', 'building_textile_mill'): 4,
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_textile_mill'): 3,
    ('STATE_NORTHERN_TERRITORY', 'MKAI', 'building_textile_mill'): 4,
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_furniture_manufactory'): 3,
    ('STATE_NEW_SOUTH_WALES', 'HAKR', 'building_furniture_manufactory'): 3,
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_furniture_manufactory'): 2,
    ('STATE_WESTERN_AUSTRALIA', 'RNGN', 'building_furniture_manufactory'): 3,
    ('STATE_NEW_SOUTH_WALES', 'HITO', 'building_construction_sector'): 3,
    ('STATE_NEW_SOUTH_WALES', 'HAKR', 'building_construction_sector'): 2,
    ('STATE_QUEENSLAND', 'YKYM', 'building_construction_sector'): 2,
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_construction_sector'): 2,
    ('STATE_NORTHERN_TERRITORY', 'MKAI', 'building_construction_sector'): 2,
}
DISTILLERIES = {
    ('STATE_VICTORIA', 'HITO', 'building_food_industry'),
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_food_industry'),
}
LUXURY_CLOTHES = {
    ('STATE_VICTORIA', 'RDMK', 'building_textile_mill'),
    ('STATE_WESTERN_AUSTRALIA', 'YKMF', 'building_textile_mill'),
}
LUXURY_FURNITURE = {
    ('STATE_QUEENSLAND', 'MFSR', 'building_furniture_manufactory'),
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_furniture_manufactory'),
}
HARDWOOD = {
    ('STATE_QUEENSLAND', 'MFSR', 'building_logging_camp'),
    ('STATE_WESTERN_AUSTRALIA', 'BYKR', 'building_logging_camp'),
}
NEW_CONSTRUCTION = {
    ('STATE_SOUTH_AUSTRALIA', 'CHRD'),
    ('STATE_TASMANIA', 'RDMK'),
}


def replace_building(body, key):
    state, tag, kind = key
    if key in LEVELS:
        target = LEVELS[key]
        ownership = re.search(r'\blevels\s*=\s*\d+', body)
        if ownership:
            body = body[:ownership.start()] + f'levels = {target}' + body[ownership.end():]
        else:
            assert key == ('STATE_VICTORIA', 'HITO', 'building_food_industry')
            needle = '\n\t\t\t\treserves = 1'
            assert needle in body
            owner = (f'\n\t\t\t\tadd_ownership = {{\n'
                     f'\t\t\t\t\tbuilding = {{ type = "building_financial_district" '
                     f'country = "c:{tag}" levels = {target} region = "{state}" }}\n'
                     f'\t\t\t\t}}')
            body = body.replace(needle, owner + needle, 1)
    if key in DISTILLERIES:
        assert '"pm_disabled_distillery"' in body
        body = body.replace('"pm_disabled_distillery"', '"pm_pot_stills"', 1)
    if key in LUXURY_CLOTHES:
        assert '"pm_no_luxury_clothes"' in body
        body = body.replace('"pm_no_luxury_clothes"', '"pm_craftsman_sewing"', 1)
    if key in LUXURY_FURNITURE:
        assert '"pm_no_luxuries"' in body
        body = body.replace('"pm_no_luxuries"', '"pm_luxury_furniture"', 1)
    if key in HARDWOOD:
        assert '"pm_no_hardwood"' in body
        body = body.replace('"pm_no_hardwood"', '"pm_hardwood"', 1)
    if kind == 'building_construction_sector':
        assert '"pm_wooden_buildings"' in body
        body = body.replace('"pm_wooden_buildings"', '"pm_iron_frame_buildings"', 1)
    return body


def apply():
    source = PATH.read_text(encoding='utf-8-sig')
    edits, seen = [], set()
    for state_match, state_body, _ in spans(source, r's:(STATE_\w+)\s*=\s*\{'):
        state = state_match[1]
        state_body_start = source.index('{', state_match.start()) + 1
        for region_match, region_body, region_end in spans(state_body, r'region_state:(\w+)\s*=\s*\{'):
            tag = region_match[1]
            region_body_start = state_body_start + state_body.index('{', region_match.start()) + 1
            for building_match, building_body, building_end in spans(region_body, r'create_building\s*=\s*\{'):
                kind = re.search(r'\bbuilding\s*=\s*"([^"]+)"', building_body)[1]
                key = (state, tag, kind)
                wanted = (key in LEVELS or key in DISTILLERIES or key in LUXURY_CLOTHES
                          or key in LUXURY_FURNITURE or key in HARDWOOD or kind == 'building_construction_sector')
                if not wanted:
                    continue
                assert key not in seen, key
                seen.add(key)
                start = region_body_start + building_match.start()
                end = region_body_start + building_end
                original = source[start:end]
                modified = replace_building(original, key)
                if modified != original:
                    edits.append((start, end, modified))
            if (state, tag) in NEW_CONSTRUCTION:
                assert (state, tag, 'building_construction_sector') not in seen
                spot = state_body_start + region_end - 1
                block = (f'\tcreate_building = {{\n'
                         f'\t\t\t\tbuilding = "building_construction_sector"\n'
                         f'\t\t\t\tactivate_production_methods = {{ "pm_iron_frame_buildings" }}\n'
                         f'\t\t\t\tadd_ownership = {{ country = {{ country = "c:{tag}" levels = 1 }} }}\n'
                         f'\t\t\t\treserves = 1\n\t\t\t}}\n\t\t')
                edits.append((spot, spot, block))
                seen.add((state, tag, 'building_construction_sector'))
    expected = set(LEVELS) | DISTILLERIES | LUXURY_CLOTHES | LUXURY_FURNITURE | HARDWOOD
    expected |= {(state, tag, 'building_construction_sector') for state, tag in NEW_CONSTRUCTION}
    assert expected <= seen, expected - seen
    for start, end, replacement in sorted(edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    PATH.write_text(source, encoding='utf-8-sig')
    print(f'updated {len(edits)} building entries')


if __name__ == '__main__':
    assert sys.argv[1:] == ['--apply']
    apply()
