"""Convert generated transparent icons to DDS and connect their game references."""
from pathlib import Path
import argparse
import json
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artwork/icon_candidates/religion_buildings_20261009'


def update(path, key, field, value):
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig')
    pattern = r'(^' + re.escape(key) + r'\s*=\s*\{.*?\b' + field + r'\s*=\s*")[^"]+(")'
    changed, count = re.subn(pattern, lambda m: m[1] + value + m[2], text, count=1, flags=re.M | re.S)
    assert count == 1, (path, key, field)
    if changed != text:
        path.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + changed.encode('utf-8'))


def update_texticon(path, key, texture):
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig')
    pattern = r'(\bicon\s*=\s*' + re.escape(key) + r'\s+iconsize\s*=\s*\{\s*texture\s*=\s*")[^"]+(")'
    changed, count = re.subn(pattern, lambda m: m[1] + texture + m[2], text)
    assert count == 1, (path, key)
    path.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + changed.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    specs = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    ready = [s for s in specs if (OUT / s.get('source', 'sources/' + s['key'] + '.png')).is_file()]
    if args.install:
        assert len(ready) == len(specs), 'All requested icons must be ready before installation'
    (OUT / 'icons_256').mkdir(exist_ok=True)
    installed = []
    for spec in ready:
        key, kind = spec['key'], spec['kind']
        original = Image.open(OUT / spec.get('source', 'sources/' + key + '.png')).convert('RGBA')
        if kind == 'building' and spec.get('full_bleed'):
            assert original.width == original.height, key
            icon = original.resize((256, 256), Image.Resampling.LANCZOS)
        else:
            alpha_min, alpha_max = original.getchannel('A').getextrema()
            assert alpha_min == 0 and alpha_max >= 250, key
            image = original.crop(original.getchannel('A').getbbox())
            side = round(max(image.size) * 1.08)
            canvas = Image.new('RGBA', (side, side))
            canvas.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
            icon = canvas.resize((256, 256), Image.Resampling.LANCZOS)
        icon.save(OUT / 'icons_256' / (key + '.png'))
        if not args.install:
            continue
        directory = {'pm': 'production_method_icons', 'goods': 'goods_icons', 'building': 'building_icons'}[kind]
        texture = 'gfx/interface/icons/' + directory + '/' + key + spec.get('texture_suffix', '') + '.dds'
        if (ROOT / texture).exists():
            assert Image.open(ROOT / texture).convert('RGBA').tobytes() == icon.tobytes(), 'Refuse to overwrite a different existing asset: ' + texture
        icon.save(ROOT / texture)
        assert Image.open(ROOT / texture).convert('RGBA').tobytes() == icon.tobytes(), key
        if kind == 'pm':
            update(ROOT / 'common/production_methods/tot_religious_center.txt', key, 'texture', texture)
        elif kind == 'goods':
            filename = 'tot_ornamental_animals.txt' if key == 'ornamental_animals' else 'tot_goods.txt'
            update(ROOT / 'common/goods' / filename, key, 'texture', texture)
            filename = 'tot_goods_texticons.gui' if key == 'ornamental_animals' else 'tot_texticons.gui'
            update_texticon(ROOT / 'gui' / filename, key, texture)
        else:
            filenames = {
                'building_religious_center': 'tot_religious_center.txt',
                'building_botanical_garden': 'tot_botanical_garden.txt',
                'building_izakaya': 'tot_izakaya.txt',
                'building_tot_animal_breeding_center': 'tot_animal_breeding.txt',
                'building_tot_pet_shop': 'tot_pet_shop.txt',
            }
            update(ROOT / 'common/buildings' / filenames[key], key, 'icon', texture)
        installed.append({'key': key, 'texture': texture})
    if args.install:
        groups = {'pmg_religious_center_assembly': 'pm_religious_center_daily_assembly',
                  'pmg_religious_center_rites': 'pm_religious_center_common_rites',
                  'pmg_religious_center_facilities': 'pm_religious_center_traditional_facilities'}
        for group, pm in groups.items():
            update(ROOT / 'common/production_method_groups/tot_religious_center.txt', group, 'texture',
                   'gfx/interface/icons/production_method_icons/' + pm + '.dds')
        (OUT / 'installed.json').write_text(json.dumps(installed, ensure_ascii=False, indent=2), encoding='utf-8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    for kind in ['pm', 'goods', 'building']:
        rows = [s for s in ready if s['kind'] == kind]
        if not rows:
            continue
        sheet = Image.new('RGB', (900, ((len(rows) + 4) // 5) * 210), (43, 48, 58))
        draw = ImageDraw.Draw(sheet)
        for i, spec in enumerate(rows):
            image = Image.open(OUT / 'icons_256' / (spec['key'] + '.png'))
            image.thumbnail((156, 156))
            x, y = (i % 5) * 180, (i // 5) * 210
            sheet.paste(image, (x + 12, y + 10), image)
            draw.text((x + 12, y + 177), spec['name'], font=font, fill='white')
        sheet.save(OUT / (kind + '_preview.png'))
    print('Ready: {} / {}; installed: {}'.format(len(ready), len(specs), args.install))


if __name__ == '__main__':
    main()
