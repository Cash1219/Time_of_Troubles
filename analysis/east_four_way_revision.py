"""Move the eastern village borders and Night Sparrow Diner by province.

Run --preview to inspect the map, --apply to install it, or --check to audit it.
Province geometry, state regions, and each country's population/buildings stay intact.
"""

import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import lake_coast_revision as lake
import west_coast_draft as west
from gensokyo_cultures_v1 import replace_blocks
from ridge_sanzu_revision import history_block


ROOT = west.ROOT
OUT = west.OUT
CTX = lake.CTX
REL = 'common/history/states/00_states.txt'
MANIFEST = OUT / 'east_four_way_revision.json'
PREVIEW = OUT / 'east_four_way_revision_preview.png'

# Three provinces at the village's northeast tip.
VILLAGE_TO_HAKUREI = ('x4866D3', 'x027214', 'x740B78')
# Three provinces at its southeast edge, immediately above Eientei.
VILLAGE_TO_EIENTEI = ('xAFEC31', 'xBEA265', 'xC41B96')
# Eientei's northeastern shoreline, chosen to retain a single land component.
EIENTEI_TO_VILLAGE = ('x5CAC91', 'xB6943C', 'xE86E1F')
# A compact eastern district sharing a land border with Hakurei.
VILLAGE_TO_DINER = ('xCBED4E', 'x116050', 'xE02F70', 'xB01F74',
                    'xE4FF76', 'x3AC189', 'x7E0DF6', 'xFB3077')
TAGS = ('HITO', 'HAKR', 'EITR', 'YSSK')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def target(before):
    after = {province: value[:] for province, value in before.items()}
    transfers = [(VILLAGE_TO_HAKUREI, 'HITO', 'HAKR'),
                 (VILLAGE_TO_EIENTEI, 'HITO', 'EITR'),
                 (EIENTEI_TO_VILLAGE, 'EITR', 'HITO'),
                 (VILLAGE_TO_DINER, 'HITO', 'YSSK')]
    for group, old, new in transfers:
        assert len(group) == len(set(group))
        assert len(west.components(group, CTX['adj'])) == 1, group
        for province in group:
            assert before[province][1] == old, (province, before[province], old)
            after[province][1] = new
    old_diner = [province for province, value in before.items() if value[1] == 'YSSK']
    assert len(old_diner) == 8
    assert all(before[p][0] == 'STATE_NEW_SOUTH_WALES' for p in old_diner)
    for province in old_diner:
        after[province][1] = 'HITO'
    audit(before, after)
    return after


def audit(before, after):
    assert set(before) == set(after)
    assert all(before[p][0] == after[p][0] for p in before)
    for tag in TAGS:
        provinces = [p for p in CTX['adj'] if after[p][1] == tag]
        groups = west.components(provinces, CTX['adj'])
        assert len(groups) == 1, (tag, [len(group) for group in groups])
    assert any(after[q][1] == 'HAKR' for p in VILLAGE_TO_DINER
               for q in CTX['adj'][p])
    assert {after[p][0] for p in VILLAGE_TO_DINER} == {'STATE_NEW_SOUTH_WALES'}
    expected = {'HITO': -3, 'HAKR': 3, 'EITR': 0, 'YSSK': 0}
    for tag, delta in expected.items():
        assert sum(v[1] == tag for v in after.values()) - sum(
            v[1] == tag for v in before.values()) == delta, tag
    return {tag: {'provinces': sum(v[1] == tag for v in after.values()),
                  'states': sorted({v[0] for v in after.values() if v[1] == tag})}
            for tag in TAGS}


def history_text(source, after):
    def rewrite(match, body):
        if match[1] not in ('STATE_NEW_SOUTH_WALES', 'STATE_VICTORIA'):
            return body
        block = history_block(match[1], after, body)
        return block[block.index('{') + 1:block.rfind('}')]

    result = replace_blocks(source, r's:(STATE_\w+)\s*=\s*\{',
                            rewrite)
    result = replace_blocks(result, r's:(STATE_\w+)\s*=\s*\{',
                            lambda match, body: re.sub(r'\n{3,}', '\n\n',
                                                       re.sub(r'(?m)^[ \t]+$', '', body))
                            if match[1] in ('STATE_NEW_SOUTH_WALES', 'STATE_VICTORIA')
                            else body)
    assert west.ownership(result) == after
    stripped = re.sub(r'#[^\n]*', '', result)
    assert stripped.count('{') == stripped.count('}')
    return result


def preview(owners, output=PREVIEW):
    bounds = (7350, 2790, 7590, 3030)
    pixels = np.asarray(Image.open(west.GAME / 'map_data/provinces.png').convert('RGB').crop(bounds), dtype=np.uint32)
    codes = (pixels[:, :, 0] << 16) | (pixels[:, :, 1] << 8) | pixels[:, :, 2]
    rgb = np.full((*codes.shape, 3), (53, 65, 70), dtype=np.uint8)
    for province, (state, tag) in owners.items():
        if province in CTX['coords']:
            rgb[codes == int(province[1:], 16)] = west.COLORS.get(tag, (145, 145, 145))
    edges = np.zeros(codes.shape, dtype=bool)
    edges[:, 1:] |= codes[:, 1:] != codes[:, :-1]
    edges[1:, :] |= codes[1:, :] != codes[:-1, :]
    rgb[edges] = (42, 45, 46)
    image = Image.fromarray(rgb).resize((960, 960))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    for tag in TAGS:
        ps = [p for p in CTX['coords'] if owners[p][1] == tag
              and bounds[0] <= CTX['coords'][p][0] < bounds[2]
              and bounds[1] <= CTX['coords'][p][1] < bounds[3]]
        if not ps:
            continue
        weights = [CTX['coords'][p][2] for p in ps]
        x = sum(CTX['coords'][p][0] * a for p, a in zip(ps, weights)) / sum(weights)
        y = sum(CTX['coords'][p][1] * a for p, a in zip(ps, weights)) / sum(weights)
        draw.text(((x - bounds[0]) * 4, (y - bounds[1]) * 4), west.NAMES[tag],
                  font=font, anchor='mm', fill='white', stroke_width=3,
                  stroke_fill='black')
    image.save(output)


def apply():
    assert not MANIFEST.exists(), 'Already applied; use --check.'
    original = (ROOT / REL).read_bytes()
    before = west.ownership(original.decode('utf-8-sig'))
    after = target(before)
    content = history_text(original.decode('utf-8-sig'), after)
    updated = content.replace('\r\n', '\n').encode('utf-8')
    if original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    backup = ROOT / 'docs/backups' / ('east_four_way_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    saved = backup / REL
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(original)
    (ROOT / REL).write_bytes(updated)
    report = {'backup': str(backup), 'hashes': {REL: {'before': digest(original), 'after': digest(updated)}},
              'province_changes': {p: [before[p], after[p]] for p in before if before[p] != after[p]},
              'countries': audit(before, after)}
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    preview(after)


def check():
    report = json.loads(MANIFEST.read_text(encoding='utf-8'))
    original = (Path(report['backup']) / REL).read_bytes()
    later_path = OUT / 'eientei_outline_revision.json'
    later = json.loads(later_path.read_text(encoding='utf-8')) if later_path.exists() else None
    current = (ROOT / REL).read_bytes()
    if later:
        assert digest(current) == later['hashes'][REL]['after']
        current = (Path(later['backup']) / REL).read_bytes()
        assert digest(current) == later['hashes'][REL]['before']
    assert digest(original) == report['hashes'][REL]['before']
    assert digest(current) == report['hashes'][REL]['after']
    before = west.ownership(original.decode('utf-8-sig'))
    after = west.ownership(current.decode('utf-8-sig'))
    assert {p: [before[p], after[p]] for p in before if before[p] != after[p]} == report['province_changes']
    assert target(before) == after
    assert audit(before, after) == report['countries']
    print(json.dumps({'status': 'static validation passed; not game-tested',
                      'changed_provinces': len(report['province_changes']),
                      'countries': report['countries']}, ensure_ascii=False))


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
        check()
    elif '--preview' in sys.argv:
        preview(target(lake.current()))
    else:
        check()
