"""Check active mod PM goods registration and custom Chinese technology keys."""
from collections import defaultdict
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
parser = runpy.run_path(str(ROOT/'tools/audit_pop_demands.py'))
definitions, blocks = parser['definitions'], parser['blocks']
VANILLA = parser['VANILLA']


def merged(folder):
    return {**definitions(VANILLA, folder), **definitions(ROOT, folder)}


def main():
    goods = merged('common/goods')
    custom_goods = set(definitions(ROOT, 'common/goods')) - set(definitions(VANILLA, 'common/goods'))
    modifiers = merged('common/modifier_type_definitions')
    pms = merged('common/production_methods')
    groups = merged('common/production_method_groups')
    buildings = merged('common/buildings')
    scope = {r['building'] for r in json.loads((ROOT/'analysis/round_review.json').read_text(encoding='utf-8'))['summary']}
    errors, active, used = [], set(), set()
    for building in scope:
        for group in dict(blocks(buildings[building]))['production_method_groups'].split():
            for pm in dict(blocks(groups[group]))['production_methods'].split():
                active.add(pm)
                if re.search(r'(?m)^\s*default\s*=', pms[pm]):
                    errors.append(f'{pm}: use is_default, not default')
                for key, good in re.findall(r'\b(goods_(?:input|output)_(\w+)_(?:add|mult))\s*=', pms[pm]):
                    used.add(key)
                    if good not in goods:
                        errors.append(f'{pm}: missing good {good}')
                    # Vanilla goods have engine-generated keys as well as explicit definitions.
                    if good in custom_goods and key not in modifiers:
                        errors.append(f'{pm}: missing registered modifier {key}')
    techs = set(definitions(ROOT, 'common/technology/technologies')) - set(definitions(VANILLA, 'common/technology/technologies'))
    labels = defaultdict(list)
    for path in (ROOT/'localization').rglob('*.yml'):
        if 'simp_chinese' not in str(path):
            continue
        for key in re.findall(r'^\s*([\w]+):\d*\s+"', path.read_text(encoding='utf-8-sig', errors='replace'), re.M):
            labels[key].append(path.relative_to(ROOT).as_posix())
    for tech in techs:
        for key in [tech, tech+'_desc']:
            matches = labels[key]
            if len(matches) != 1:
                errors.append(f'{key}: expected one Chinese definition, got {matches}')
            else:
                path = ROOT/matches[0]
                raw = path.read_bytes()
                if not raw.startswith(b'\xef\xbb\xbf'):
                    errors.append(f'{key}: Chinese localization lacks UTF-8 BOM')
                if raw.decode('utf-8-sig').splitlines()[0] != 'l_simp_chinese:':
                    errors.append(f'{key}: wrong language header')
    assert errors == [], '\n'.join(sorted(set(errors)))
    print(f'PASS: {len(scope)} buildings, {len(active)} PMs, {len(used)} goods modifier keys, {len(techs)} technologies.')
    print('Amusement PMGs: '+', '.join(dict(blocks(buildings['building_amusement_park']))['production_method_groups'].split()))
    print('Breeding output per level: '+', '.join(re.search(r'goods_output_ornamental_animals_add\s*=\s*(\d+)',pms[k])[1]
          for k in dict(blocks(groups['pmg_tot_animal_breeding']))['production_methods'].split()))


if __name__=='__main__':
    main()
