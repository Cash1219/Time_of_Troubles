"""Refine Eientei's coast and western edge to match the marked outline.

Run --preview, --apply, or --check. Province geometry is unchanged.
"""

import datetime
import json
import sys
from pathlib import Path

import east_four_way_revision as east
import lake_coast_revision as lake
import west_coast_draft as west


ROOT = west.ROOT
OUT = west.OUT
REL = east.REL
MANIFEST = OUT / 'eientei_outline_revision.json'
PREVIEW = OUT / 'eientei_outline_revision_preview.png'

# Fill the village-owned gap above and along Eientei's eastern shore.
TO_EIENTEI = ('xB9104E', 'x2BD326', 'x68E6E2',
              'x5CAC91', 'xB6943C', 'xE86E1F')
# Return the two western protrusions to the village. The southwest coastal
# point follows its adjoining Ice Domain rather than leaving Eientei a tail.
TO_VILLAGE = ('x9AFA6A', 'x8C4823')
TO_ICE = ('x2FC68B',)


def target(before):
    after = {province: value[:] for province, value in before.items()}
    for group, old, new in ((TO_EIENTEI, 'HITO', 'EITR'),
                            (TO_VILLAGE, 'EITR', 'HITO'),
                            (TO_ICE, 'EITR', 'MIST')):
        assert len(group) == len(set(group))
        for province in group:
            assert before[province][1] == old, (province, before[province])
            after[province][1] = new
    audit(before, after)
    return after


def audit(before, after):
    assert set(before) == set(after)
    assert all(before[p][0] == after[p][0] for p in before)
    for tag in ('HITO', 'EITR', 'HAKR', 'YSSK', 'MIST'):
        provinces = [p for p in east.CTX['adj'] if after[p][1] == tag]
        groups = west.components(provinces, east.CTX['adj'])
        assert len(groups) == 1, (tag, [len(g) for g in groups])
    assert all(after[p][1] == 'EITR' for p in TO_EIENTEI)
    assert {after[p][0] for p in TO_EIENTEI} == {
        'STATE_NEW_SOUTH_WALES', 'STATE_VICTORIA'}
    return {tag: sum(v[1] == tag for v in after.values())
            for tag in ('HITO', 'EITR', 'HAKR', 'YSSK', 'MIST')}


def apply():
    assert not MANIFEST.exists(), 'Already applied; use --check.'
    original = (ROOT / REL).read_bytes()
    before = west.ownership(original.decode('utf-8-sig'))
    after = target(before)
    updated = east.history_text(original.decode('utf-8-sig'), after).replace('\r\n', '\n').encode('utf-8')
    if original.startswith(b'\xef\xbb\xbf'):
        updated = b'\xef\xbb\xbf' + updated
    backup = ROOT / 'docs/backups' / ('eientei_outline_before_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    path = backup / REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(original)
    (ROOT / REL).write_bytes(updated)
    report = {'backup': str(backup),
              'hashes': {REL: {'before': east.digest(original), 'after': east.digest(updated)}},
              'province_changes': {p: [before[p], after[p]] for p in before if before[p] != after[p]},
              'countries': audit(before, after)}
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    east.preview(after, PREVIEW)


def check():
    report = json.loads(MANIFEST.read_text(encoding='utf-8'))
    original = (Path(report['backup']) / REL).read_bytes()
    current = (ROOT / REL).read_bytes()
    assert east.digest(original) == report['hashes'][REL]['before']
    assert east.digest(current) == report['hashes'][REL]['after']
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
        east.preview(target(lake.current()), PREVIEW)
    else:
        check()
