"""Apply the population/arable prototype without changing borders or industries.

Defaults to a validated dry run. --apply backs up every changed runtime file.
Existing culture/religion cohorts are retained; obsolete owners are reassigned
within their existing state using the explicit population plan, not map pixels.
"""
import collections
import datetime
import hashlib
import json
import re
import sys

from west_coast_draft import ROOT, GAME, NAMES, close, ownership

ALLOCATIONS = {
    'STATE_NEW_SOUTH_WALES': {'HITO': 3000000, 'HAKR': 600000, 'YKYM': 550000,
                              'MFSR': 250000, 'EITR': 50000, 'YSSK': 150000},
    'STATE_VICTORIA': {'HITO': 600000, 'HAKR': 100000, 'EITR': 700000, 'KZNH': 500000},
    'STATE_QUEENSLAND': {'YKYM': 1650000, 'MFSR': 450000, 'MRYA': 1000000, 'CHRD': 1000},
    'STATE_SOUTH_AUSTRALIA': {'RDMK': 1200000, 'MIST': 300000, 'MYRN': 500000, 'SHRM': 400000},
    'STATE_WESTERN_AUSTRALIA': {'BYKR': 1300000, 'KYTO': 500000, 'UKDO': 450000,
                                 'RNGN': 700000, 'HIGN': 450000, 'YKMF': 350000, 'MKAI': 120000},
    'STATE_NORTHERN_TERRITORY': {'MKAI': 1180000},
    'STATE_TASMANIA': {'MTOU': 350000},
    'STATE_NORTH_ISLAND': {'TENG': 400000},
    'STATE_SOUTH_ISLAND': {'TENG': 400000},
    'STATE_FIJI': {'TENG': 100000},
    'STATE_VANUATU': {'TENG': 100000},
    'STATE_CHIREIDEN_CAPITAL': {'CHRD': 400000},
    'STATE_CHIREIDEN_OASIS': {'CHRD': 300000},
    'STATE_CHIREIDEN_NORTH_OASIS': {'CHRD': 150000},
    'STATE_CHIREIDEN_GATE': {'CHRD': 249000},
    'STATE_CHIREIDEN_WEST_GATE': {'CHRD': 100000},
    'STATE_CHIREIDEN_CAVERN_ZONE': {'CHRD': 10000},
}
ARABLE = dict(zip(ALLOCATIONS, [300, 120, 150, 120, 200, 65, 20, 25, 25, 7, 6, 20, 15, 8, 13, 5, 1]))
STATE_NAMES = dict(zip(ALLOCATIONS, ['新南威尔士', '维多利亚', '昆士兰', '南澳大利亚',
    '西澳大利亚', '北领地', '塔斯马尼亚', '新西兰北岛', '新西兰南岛', '斐济', '瓦努阿图',
    '地灵殿本部', '爱丽丝泉绿洲', '北部绿洲', '地灵殿东侧入口', '地灵殿西侧出口', '地穴地带']))


def spans(text, pattern):
    # Replacing comments with spaces retains offsets into the original source.
    masked = re.sub(r'#[^\n]*', lambda m: ' ' * len(m[0]), text)
    for m in re.finditer(pattern, masked):
        start = masked.index('{', m.start())
        end = close(masked, start)
        yield m, text[start + 1:end - 1], end


def pop_entries(files):
    result = []
    for path, text in files.items():
        for sm, state_body, _ in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
            if sm[1] not in ALLOCATIONS:
                continue
            for tm, owner_body, _ in spans(state_body, r'region_state:(\w+)\s*=\s*\{'):
                for _, pop, _ in spans(owner_body, r'create_pop\s*=\s*\{'):
                    pop = re.sub(r'#[^\n]*', '', pop)
                    fields = dict(re.findall(r'(\w+)\s*=\s*(\w+)', pop))
                    assert set(fields) <= {'culture', 'religion', 'size'}, (path, fields)
                    result.append((sm[1], tm[1], fields['culture'], fields.get('religion'), int(fields['size'])))
    return result


def split_size(size, weights):
    total = sum(weights.values())
    parts = {tag: size * weight // total for tag, weight in weights.items()}
    order = sorted(weights, key=lambda tag: (-(size * weights[tag] % total), tag))
    for tag in order[:size - sum(parts.values())]:
        parts[tag] += 1
    return parts


def render_state(state, cohorts):
    lines = ['s:{} = {{'.format(state)]
    for tag, target in ALLOCATIONS[state].items():
        lines.append('\t\tregion_state:{} = {{'.format(tag))
        existing = cohorts[state, tag]
        added = target - sum(existing.values())
        assert added >= 0, (state, tag, target, sum(existing.values()))
        combined = existing.copy()
        combined['japanese', 'shinto'] += added
        for (culture, religion), size in sorted(combined.items(), key=lambda item: (item[0][0], item[0][1] or '')):
            if not size:
                continue
            fields = 'culture = {}'.format(culture)
            if religion:
                fields += ' religion = {}'.format(religion)
            lines.append('\t\t\tcreate_pop = {{ {} size = {} }}'.format(fields, size))
        lines.append('\t\t}')
    lines.append('\t}')
    return '\n'.join(lines)


def normalize_region(text):
    text = re.sub(r'\barable_land\s*=\s*\d+', 'arable_land = CAPACITY', text)
    text = text.replace('building_subsistence_pastures', 'building_subsistence_pasture')
    text = text.replace('building_subsistence_farms', 'building_subsistence_farm')
    return text.strip()


def main():
    owners = ownership((ROOT / 'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    actual_pairs = {(state, tag) for state, tag in owners.values() if state in ALLOCATIONS}
    expected_pairs = {(state, tag) for state, tags in ALLOCATIONS.items() for tag in tags}
    assert actual_pairs == expected_pairs, (actual_pairs ^ expected_pairs)
    pop_files = {p: p.read_text(encoding='utf-8-sig') for p in (ROOT / 'common/history/pops').glob('*.txt')}
    original_entries = pop_entries(pop_files)
    cohorts = collections.defaultdict(collections.Counter)
    original_profiles = collections.Counter()
    for state, tag, culture, religion, size in original_entries:
        original_profiles[state, culture, religion] += size
        recipients = {tag: size} if tag in ALLOCATIONS[state] else split_size(size, ALLOCATIONS[state])
        for recipient, count in recipients.items():
            cohorts[state, recipient][culture, religion] += count
    changed = {}
    seen = set()
    for path, text in pop_files.items():
        replacements = []
        for m, body, end in spans(text, r's:(STATE_\w+)\s*=\s*\{'):
            state = m[1]
            if state not in ALLOCATIONS:
                continue
            assert state not in seen, ('Duplicate state population definition', state)
            seen.add(state)
            replacements.append((m.start(), end, render_state(state, cohorts)))
        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        if replacements:
            changed[path] = text
    missing = set(ALLOCATIONS) - seen
    main_pop = ROOT / 'common/history/pops/13_australasia.txt'
    text = changed.get(main_pop, pop_files[main_pop])
    m, _, end = next(spans(text, r'\bPOPS\s*=\s*\{'))
    new_blocks = ''.join('\n\t' + render_state(state, cohorts) + '\n' for state in ALLOCATIONS if state in missing)
    changed[main_pop] = text[:end - 1] + new_blocks + text[end - 1:]

    region_path = ROOT / 'map_data/state_regions/tot_13_australasia_chireiden.txt'
    region_text = region_path.read_text(encoding='utf-8-sig')
    before_regions = {}
    for directory in [GAME / 'map_data/state_regions', ROOT / 'map_data/state_regions']:
        for path in sorted(directory.glob('*.txt')):
            text = path.read_text(encoding='utf-8-sig')
            for m, _, end in spans(text, r'(?m)^[ \t]*(STATE_\w+)\s*=\s*\{'):
                if m[1] in ARABLE:
                    before_regions[m[1]] = text[m.start():end]
    assert set(before_regions) == set(ARABLE)
    old_arable = sum(int(re.search(r'\barable_land\s*=\s*(\d+)', body)[1]) for body in before_regions.values())
    original_region_states = {m[1] for m, _, _ in spans(region_text, r'(?m)^[ \t]*(STATE_\w+)\s*=\s*\{')}
    for state, capacity in ARABLE.items():
        body = before_regions[state]
        replacement = re.sub(r'\barable_land\s*=\s*\d+', 'arable_land = {}'.format(capacity), body)
        replacement = replacement.replace('building_subsistence_pastures', 'building_subsistence_pasture')
        replacement = replacement.replace('building_subsistence_farms', 'building_subsistence_farm')
        assert normalize_region(body) == normalize_region(replacement), state
        if state in original_region_states:
            match = next((m, end) for m, _, end in spans(region_text, r'(?m)^[ \t]*(STATE_\w+)\s*=\s*\{') if m[1] == state)
            m, end = match
            region_text = region_text[:m.start()] + replacement + region_text[end:]
        else:
            region_text += '\n\n' + replacement + '\n'
    changed[region_path] = region_text

    new_entries = pop_entries({**pop_files, **changed})
    totals = collections.Counter()
    profiles = collections.Counter()
    for state, tag, culture, religion, size in new_entries:
        assert (state, tag) in actual_pairs
        totals[state, tag] += size
        profiles[state, culture, religion] += size
    assert dict(totals) == {(state, tag): size for state, tags in ALLOCATIONS.items() for tag, size in tags.items()}
    for profile, size in original_profiles.items():
        assert profiles[profile] >= size, ('Lost existing population', profile)
    country_totals = collections.Counter()
    for (state, tag), size in totals.items():
        country_totals[tag] += size
    assert sum(country_totals.values()) == 19610000
    assert len(country_totals) == 22 and sum(ARABLE.values()) == 1100
    for path, text in changed.items():
        masked = re.sub(r'#[^\n]*', '', text)
        assert masked.count('{') == masked.count('}'), path
        assert close(masked, masked.index('{')) <= len(masked)
    print(json.dumps(dict(population=sum(country_totals.values()), countries=len(country_totals),
                         cavern=totals['STATE_CHIREIDEN_CAVERN_ZONE', 'CHRD'],
                         arable_before=old_arable, arable_after=sum(ARABLE.values()),
                         runtime_files=[str(p.relative_to(ROOT)) for p in changed]), ensure_ascii=False))
    if '--apply' not in sys.argv:
        print('Validated dry run; no runtime files written.')
        return
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = ROOT / 'docs/backups' / ('population_arable_' + stamp)
    checksums = {}
    for path in changed:
        target = backup / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_bytes()
        target.write_bytes(raw)
        checksums[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    for path, text in changed.items():
        # Preserve the source's BOM and Windows newline convention.
        bom = path.read_bytes().startswith(b'\xef\xbb\xbf')
        raw = text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
        path.write_bytes((b'\xef\xbb\xbf' if bom else b'') + raw)
    written_entries = pop_entries({p: p.read_text(encoding='utf-8-sig') for p in pop_files})
    assert collections.Counter(written_entries) == collections.Counter(new_entries)
    report = dict(status='applied; static validation passed; in-game new-save validation pending',
        total_population=19610000, cavern_population=10000, total_arable_land=1100,
        previous_arable_land=old_arable, backup=str(backup), original_sha256=checksums,
        state_populations=ALLOCATIONS, arable_land=ARABLE, country_populations=dict(country_totals),
        policy='No building, industry, mineral, border or migration changes. Existing culture/religion cohorts retained. New population uses Japanese/Shinto as a testing placeholder.')
    out = ROOT / 'docs/drafts'
    (out / 'gensokyo_population_arable_applied_v1.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = ['# 幻想乡人口与耕地：第一版实装', '',
            '开局人口合计 **1,961万人**，22个国家；可耕地合计 **1,100**，原值296。', '',
            '地灵殿共121万人，其中地穴1万人；本部40万、爱丽丝泉30万、北部绿洲15万、东入口24.9万、西出口10万、昆士兰小据点0.1万。', '',
            '保留既有居民的文化与宗教；失效的原版国家人口归属改到现有国家。新增人口暂用大和／神道，作为测试占位。斐济与瓦努阿图各10万，新西兰两岛各40万，以保留群岛现有居民。', '',
            '只修改人口与可耕地容量，并修正地下州自给建筑名称的拼写。未改产业、开局建筑、矿藏、边界、农区位置、迁移政策及建设限制。', '',
            '## 国家人口', '', '| 国家 | 人口 |', '|---|---:|']
    for tag, size in sorted(country_totals.items(), key=lambda item: -item[1]):
        rows.append('| {}（{}） | {:,} |'.format('冰之领地' if tag == 'MIST' else NAMES[tag], tag, size))
    rows += ['', '## 州容量', '', '| 州 | 开局人口 | 可耕地 |', '|---|---:|---:|']
    for state in ALLOCATIONS:
        rows.append('| {} | {:,} | {} |'.format(STATE_NAMES[state], sum(ALLOCATIONS[state].values()), ARABLE[state]))
    rows += ['', '## 测试说明', '',
        '本版是人口与农业容量的测试基线，不代表经济已经平衡。共享州会按照省份及优质耕地权重分配容量，因此花田、冰之领地等小国的实际耕地较少，需结合后续产业解决就业，不能只用全国耕地总数判断。', '',
        '按基础25%劳动力比例，1,961万人约有490.25万劳动力；一个通常雇佣5,000人的满编建筑等级，相当于约2万人口的劳动力。实际就业取决于生产方式、法律与居民结构。', '',
        '地穴只有1万人、1单位可耕地，不设置常规建筑禁令。低人口不是永久人口上限；迁移和低人力特色能源建筑仍需后续讨论。', '',
        '修改需要新开局；已完成人口总数、归属、现有文化保留、州定义及文件结构检查，尚未在游戏内验证。', '',
        '备份：`{}`'.format(backup), '']
    (out / 'gensokyo_population_arable_applied_v1.md').write_text('\n'.join(rows), encoding='utf-8')
    print('Applied with backup:', backup)


if __name__ == '__main__':
    main()
