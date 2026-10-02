"""Small province transfers to smooth the Australian political map.

Run with --apply after reviewing the province map. All transfers stay within
their existing state region and leave state resources and hubs untouched.
"""

import json
import re
import sys

import west_coast_draft as map_tools


# Province: (current owner, new owner). Reviewed on the province raster.
TRANSFERS = {
    'x086D7B': ('EITR', 'HITO'),
    'xB15C6D': ('MFSR', 'YKYM'),
    'xC7A584': ('MFSR', 'YKYM'),
    'x30D9E5': ('MYRN', 'HITO'),
    'xE6C282': ('SHRM', 'MYRN'),
    'x880696': ('RDMK', 'EITR'),
    'xC60700': ('RDMK', 'MIST'),
    'xCF6050': ('MFSR', 'YKYM'),
    'x8904F0': ('MRYA', 'YKYM'),
    'x9EF9EC': ('MKAI', 'UKDO'),
    'x8243B6': ('UKDO', 'RNGN'),
    'x6CACF6': ('YKMF', 'BYKR'),
    'x220D4E': ('YKMF', 'HIGN'),
}


def edit_ownership(text, state, province, old_tag, new_tag):
    start, end = map_tools.block(text, 's:' + state)
    section = text[start:end]

    def owner_block(tag):
        for match in re.finditer(r'\bcreate_state\s*=\s*\{', section):
            opening = section.index('{', match.start())
            closing = map_tools.close(section, opening)
            body = section[match.start():closing]
            if re.search(r'\bcountry\s*=\s*c:' + tag + r'\b', body):
                return match.start(), closing
        raise ValueError((state, tag))

    old_start, old_end = owner_block(old_tag)
    old = section[old_start:old_end]
    match = re.search(r'\bowned_provinces\s*=\s*\{([^}]*)\}', old)
    assert match and len(re.findall(r'\b' + province + r'\b', match[1])) == 1
    replacement = re.sub(r'(?<!\w)' + province + r'(?!\w)', '', match[1])
    old = old[:match.start(1)] + replacement + old[match.end(1):]
    section = section[:old_start] + old + section[old_end:]

    new_start, new_end = owner_block(new_tag)
    new = section[new_start:new_end]
    match = re.search(r'\bowned_provinces\s*=\s*\{([^}]*)\}', new)
    assert match and province not in match[1]
    body = match[1]
    indent = re.search(r'(?m)^(\s*)x[0-9a-fA-F]{6}', body)
    assert indent
    body += '\n' + indent[1] + province + '\n'
    new = new[:match.start(1)] + body + new[match.end(1):]
    section = section[:new_start] + new + section[new_end:]
    return text[:start] + section + text[end:]


def revised(text):
    before = map_tools.ownership(text)
    after = {p: list(value) for p, value in before.items()}
    for province, (old_tag, new_tag) in TRANSFERS.items():
        assert before[province][1] == old_tag, (province, before[province])
        state = before[province][0]
        assert any(before[neighbor] == [state, new_tag]
                   for neighbor in CONTEXT['adj'][province]), province
        after[province][1] = new_tag
        text = edit_ownership(text, state, province, old_tag, new_tag)
    assert map_tools.ownership(text) == after
    for state, tag in {(before[p][0], t) for p, pair in TRANSFERS.items() for t in pair}:
        prior = [p for p, value in before.items() if value == [state, tag] and p in CONTEXT['adj']]
        final = [p for p, value in after.items() if value == [state, tag] and p in CONTEXT['adj']]
        assert len(map_tools.components(final, CONTEXT['adj'])) <= len(
            map_tools.components(prior, CONTEXT['adj'])), (state, tag)
    return text, after


CONTEXT = json.loads((map_tools.OUT / 'west_coast_context.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    original = map_tools.HISTORY.read_bytes()
    text, owners = revised(original.decode('utf-8-sig'))
    if '--apply' in sys.argv:
        newline = '\r\n' if b'\r\n' in original else '\n'
        encoded = text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8')
        map_tools.HISTORY.write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b'') + encoded)
    print(json.dumps({'transfers': len(TRANSFERS), 'owners': len(owners)}, indent=2))
