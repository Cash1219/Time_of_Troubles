"""Inventory and generate opening placements for this mod's buildings.

The CSV is the editable configuration. `migrate` relocates current mod building
records into one generated history file. Later, edit CSV and run `generate`.
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/building_start_config.csv'
CATALOG = ROOT / 'config/building_catalog.csv'
OUTPUT = ROOT / 'common/history/buildings/tot_configured_mod_buildings.txt'
FIELDS = [
    'id', 'enabled', 'state', 'region_owner', 'building', 'level', 'ownership',
    'owner_country', 'owner_building', 'owner_region', 'reserves',
    'production_methods', 'source_file', 'source_line', 'notes',
]


def skip_space(s, i):
    while i < len(s):
        if s[i].isspace():
            i += 1
        elif s[i] == '#':
            i = s.find('\n', i)
            if i < 0:
                return len(s)
        else:
            break
    return i


def token(s, i):
    i = skip_space(s, i)
    if i >= len(s):
        return None, i, i
    start = i
    if s[i] == '"':
        i += 1
        while i < len(s):
            if s[i] == '\\':
                i += 2
            elif s[i] == '"':
                return s[start:i + 1], start, i + 1
            else:
                i += 1
        raise ValueError('Unclosed string')
    if s[i] in '{}=':
        return s[i], i, i + 1
    while i < len(s) and not s[i].isspace() and s[i] not in '{}=#"':
        i += 1
    return s[start:i], start, i


def parse_items(s, start=0, stop_at_close=False):
    items = []
    i = start
    while True:
        key, ks, ke = token(s, i)
        if key is None:
            if stop_at_close:
                raise ValueError('Unclosed block')
            return items, i
        if key == '}':
            if not stop_at_close:
                raise ValueError('Unexpected close')
            return items, ke
        eq, _, ee = token(s, ke)
        if eq != '=':
            # Bare values are legal inside simple arrays such as PM lists.
            items.append((key, None, ks, ke))
            i = ke
            continue
        val, vs, ve = token(s, ee)
        if val == '{':
            children, end = parse_items(s, ve, True)
            items.append((key, children, ks, end))
            i = end
        elif val is not None:
            items.append((key, val.strip('"'), ks, ve))
            i = ve
        else:
            raise ValueError('Missing value after ' + key)


def children(node, key):
    return [item for item in node[1] if item[0] == key] if isinstance(node[1], list) else []


def value(node, key, default=''):
    matches = children(node, key)
    return matches[0][1] if matches and isinstance(matches[0][1], str) else default


def defined_buildings():
    found = set()
    for p in (ROOT / 'common/buildings').glob('*.txt'):
        s = p.read_text(encoding='utf-8-sig')
        for item in parse_items(s)[0]:
            if item[0].startswith('building_'):
                found.add(item[0])
    return found


def inventory():
    defined = defined_buildings()
    rows = []
    exceptional = []
    for p in sorted((ROOT / 'common/history/buildings').glob('*.txt')):
        s = p.read_text(encoding='utf-8-sig')
        for root in parse_items(s)[0]:
            if root[0] != 'BUILDINGS':
                continue
            for state in root[1]:
                if not state[0].startswith('s:') or not isinstance(state[1], list):
                    continue
                for region in state[1]:
                    if not region[0].startswith('region_state:') or not isinstance(region[1], list):
                        continue
                    for building in children(region, 'create_building'):
                        name = value(building, 'building')
                        if name not in defined:
                            continue
                        ownership = children(building, 'add_ownership')
                        owner_country = owner_building = owner_region = ''
                        kind = ''
                        level = 0
                        if len(ownership) == 1:
                            owner_parts = ownership[0][1]
                            if isinstance(owner_parts, list) and len(owner_parts) == 1:
                                kind, owned, _, _ = owner_parts[0]
                                if isinstance(owned, list):
                                    wrapper = (kind, owned, 0, 0)
                                    level = int(value(wrapper, 'levels', '0'))
                                    owner_country = value(wrapper, 'country')
                                    owner_building = value(wrapper, 'type')
                                    owner_region = value(wrapper, 'region')
                        if not kind or level <= 0:
                            exceptional.append(f'{p.name}:{s.count(chr(10), 0, building[2]) + 1} {name}: ownership/level')
                        pms = children(building, 'activate_production_methods')
                        if len(pms) > 1:
                            exceptional.append(f'{p.name}:{s.count(chr(10), 0, building[2]) + 1} {name}: multiple PM lists')
                        pm_names = [x[0].strip('"') for x in pms[0][1]] if pms and isinstance(pms[0][1], list) else []
                        allowed = {'building', 'add_ownership', 'activate_production_methods', 'reserves'}
                        extra = {x[0] for x in building[1]} - allowed
                        if extra:
                            exceptional.append(f'{p.name}:{s.count(chr(10), 0, building[2]) + 1} {name}: extra {extra}')
                        rows.append({
                            'id': f'B{len(rows) + 1:04}', 'enabled': 'yes',
                            'state': state[0][2:], 'region_owner': region[0].split(':', 1)[1],
                            'building': name, 'level': level, 'ownership': kind,
                            'owner_country': owner_country, 'owner_building': owner_building,
                            'owner_region': owner_region, 'reserves': value(building, 'reserves', '1'),
                            'production_methods': ';'.join(pm_names),
                            'source_file': p.relative_to(ROOT).as_posix(),
                            'source_line': s.count('\n', 0, building[2]) + 1,
                            'notes': '',
                        })
    return rows, exceptional


def export():
    if OUTPUT.exists():
        raise SystemExit('History is already managed by CSV; edit the CSV and run generate')
    rows, exceptional = inventory()
    if exceptional:
        raise SystemExit('Unsupported records:\n' + '\n'.join(exceptional))
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row['building'] for row in rows)
    with CATALOG.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['building', 'opening_instances', 'opening_levels', 'configured'])
        for name in sorted(defined_buildings()):
            writer.writerow([name, counts[name], sum(int(r['level']) for r in rows if r['building'] == name), 'yes' if counts[name] else 'no'])
    print(json.dumps({'buildings': len(defined_buildings()), 'placements': len(rows), 'levels': sum(int(r['level']) for r in rows), 'by_building': dict(sorted(counts.items()))}, ensure_ascii=False, indent=2))


def load_config():
    with CONFIG.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate row IDs')
    defined = defined_buildings()
    for row in rows:
        if row['building'] not in defined:
            raise ValueError(f"Unknown building in {row['id']}: {row['building']}")
        if row['enabled'] not in {'yes', 'no'}:
            raise ValueError(f"Invalid enabled in {row['id']}")
        if row['enabled'] == 'yes':
            if not row['state'].startswith('STATE_') or not row['region_owner']:
                raise ValueError(f"Missing state/owner in {row['id']}")
            if int(row['level']) <= 0:
                raise ValueError(f"Invalid level in {row['id']}")
            if row['ownership'] not in {'country', 'building', 'company'}:
                raise ValueError(f"Invalid ownership in {row['id']}")
    return rows


def ensure_placeholders():
    rows = load_config()
    present = {row['building'] for row in rows}
    next_id = max((int(row['id'][1:]) for row in rows), default=0) + 1
    added = 0
    for name in sorted(defined_buildings() - present):
        row = dict.fromkeys(FIELDS, '')
        row.update({'id': f'B{next_id:04}', 'enabled': 'no', 'building': name,
                    'level': '0', 'reserves': '1',
                    'notes': '开局无建筑；填写州、地区持有者、所有权和等级后再启用'})
        rows.append(row)
        next_id += 1
        added += 1
    if added:
        with CONFIG.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    print(f'Added {added} zero-start building templates')


def render(rows):
    grouped = {}
    for row in rows:
        if row['enabled'] != 'yes':
            continue
        grouped.setdefault(row['state'], {}).setdefault(row['region_owner'], []).append(row)
    out = ['# Generated from config/building_start_config.csv. Edit the CSV, then run:',
           '# python tools/building_history_config.py generate',
           'BUILDINGS = {']
    for state, regions in grouped.items():
        out.append(f'\ts:{state} = {{')
        for owner, placements in regions.items():
            out.append(f'\t\tregion_state:{owner} = {{')
            for row in placements:
                out += [f'\t\t\tcreate_building = {{',
                        f'\t\t\t\tbuilding = "{row["building"]}"']
                if row['production_methods']:
                    methods = ' '.join(f'"{x}"' for x in row['production_methods'].split(';') if x)
                    out.append(f'\t\t\t\tactivate_production_methods = {{ {methods} }}')
                out += ['\t\t\t\tadd_ownership = {',
                        f'\t\t\t\t\t{row["ownership"]} = {{']
                if row['owner_building']:
                    out.append(f'\t\t\t\t\t\ttype = "{row["owner_building"]}"')
                out += [f'\t\t\t\t\t\tcountry = "{row["owner_country"]}"',
                        f'\t\t\t\t\t\tlevels = {int(row["level"])}']
                if row['owner_region']:
                    out.append(f'\t\t\t\t\t\tregion = "{row["owner_region"]}"')
                out += ['\t\t\t\t\t}', '\t\t\t\t}',
                        f'\t\t\t\treserves = {row["reserves"]}',
                        '\t\t\t}']
            out.append('\t\t}')
        out.append('\t}')
    out += ['}', '']
    return '\n'.join(out)


def canonical(row):
    return tuple(str(row[k]) for k in (
        'state', 'region_owner', 'building', 'level', 'ownership',
        'owner_country', 'owner_building', 'owner_region', 'reserves', 'production_methods',
    ))


def find_mod_spans(path, defined):
    s = path.read_text(encoding='utf-8-sig')
    spans = []
    for root in parse_items(s)[0]:
        if root[0] != 'BUILDINGS':
            continue
        for state in root[1]:
            if not state[0].startswith('s:') or not isinstance(state[1], list):
                continue
            for region in state[1]:
                if not region[0].startswith('region_state:') or not isinstance(region[1], list):
                    continue
                for building in children(region, 'create_building'):
                    if value(building, 'building') not in defined:
                        continue
                    start = s.rfind('\n', 0, building[2]) + 1
                    end = building[3]
                    next_line = s.find('\n', end)
                    if next_line < 0:
                        next_line = len(s)
                    if s[start:building[2]].strip() or s[end:next_line].strip():
                        raise ValueError(f'Inline building block in {path}')
                    end = min(len(s), next_line + 1)
                    spans.append((start, end))
    return s, spans


def generate(migrate=False):
    rows = load_config()
    expected = Counter(canonical(row) for row in rows if row['enabled'] == 'yes')
    originals = {}
    if migrate:
        current, issues = inventory()
        if issues:
            raise ValueError('Cannot migrate records with unsupported fields')
        if Counter(canonical(row) for row in current) != expected:
            raise ValueError('CSV differs from existing history; review before migration')
        defined = defined_buildings()
        for path in sorted((ROOT / 'common/history/buildings').glob('*.txt')):
            if path == OUTPUT:
                continue
            content, spans = find_mod_spans(path, defined)
            if not spans:
                continue
            if any(spans[i][1] > spans[i + 1][0] for i in range(len(spans) - 1)):
                raise ValueError(f'Overlapping blocks in {path}')
            original_bytes = path.read_bytes()
            for start, end in reversed(spans):
                content = content[:start] + content[end:]
            originals[path] = original_bytes
            with path.open('w', encoding='utf-8', newline='\n') as f:
                f.write(content)
    old_output = OUTPUT.read_bytes() if OUTPUT.exists() else None
    try:
        with OUTPUT.open('w', encoding='utf-8', newline='\n') as f:
            f.write(render(rows))
        actual, issues = inventory()
        if issues or Counter(canonical(row) for row in actual) != expected:
            raise ValueError(f'Generated history mismatch: {issues}')
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        if old_output is None:
            OUTPUT.unlink(missing_ok=True)
        else:
            OUTPUT.write_bytes(old_output)
        raise
    print(f'Generated {len(expected)} building placements / {sum(int(r["level"]) for r in rows if r["enabled"] == "yes")} levels')


def write_snapshot(target):
    rows = load_config()
    loc = {}
    game = Path(r'D:\Steam\steamapps\common\Victoria 3\game')
    paths = list((game / 'localization/simp_chinese').rglob('*.yml')) if game.exists() else []
    paths += list((ROOT / 'localization').rglob('*simp_chinese*.yml'))
    pattern = re.compile(r'^\s*([\w.-]+):\d*\s+"((?:[^"\\]|\\.)*)"')
    for path in paths:
        for line in path.read_text(encoding='utf-8-sig', errors='ignore').splitlines():
            m = pattern.match(line)
            if m:
                loc[m.group(1)] = m.group(2)
    annotated = []
    for row in rows:
        item = dict(row)
        item['building_name'] = loc.get(row['building'], row['building'])
        item['state_name'] = loc.get(row['state'], row['state'])
        item['review_note'] = '所有权国家与地区不同，待核对' if row['owner_country'] and row['owner_country'] != 'c:' + row['region_owner'] else ''
        annotated.append(item)
    catalog = []
    for name in sorted(defined_buildings()):
        count = sum(r['building'] == name and r['enabled'] == 'yes' for r in rows)
        levels = sum(int(r['level']) for r in rows if r['building'] == name and r['enabled'] == 'yes')
        path = next(p for p in (ROOT / 'common/buildings').glob('*.txt') if re.search(r'(?m)^' + re.escape(name) + r'\s*=\s*\{', p.read_text(encoding='utf-8-sig')))
        content = path.read_text(encoding='utf-8-sig')
        definition = next(item for item in parse_items(content)[0] if item[0] == name)
        disabled = value(definition, 'buildable') == 'no'
        catalog.append({'building': name, 'building_name': loc.get(name, name),
                        'instances': count, 'levels': levels, 'buildable_no': disabled})
    payload = {'placements': annotated, 'catalog': catalog,
               'totals': {'building_types': len(catalog), 'placements': sum(r['enabled'] == 'yes' for r in rows),
                          'levels': sum(int(r['level']) for r in rows if r['enabled'] == 'yes')}}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote workbook snapshot: {len(annotated)} placements, {len(catalog)} building types')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['export', 'check', 'migrate', 'generate', 'snapshot', 'ensure-placeholders'])
    parser.add_argument('--json-out', type=Path)
    args = parser.parse_args()
    if args.command == 'export':
        export()
    elif args.command == 'check':
        rows = load_config()
        print(f'Valid configuration: {sum(x["enabled"] == "yes" for x in rows)} active placements, {sum(int(x["level"]) for x in rows if x["enabled"] == "yes")} active levels, {sum(x["enabled"] == "no" for x in rows)} templates')
    elif args.command == 'ensure-placeholders':
        ensure_placeholders()
    elif args.command == 'snapshot':
        if args.json_out is None:
            parser.error('snapshot requires --json-out')
        write_snapshot(args.json_out)
    else:
        generate(migrate=args.command == 'migrate')


if __name__ == '__main__':
    main()
