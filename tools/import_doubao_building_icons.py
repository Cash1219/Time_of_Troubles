"""Preserve source art, remove connected white backgrounds, and install DDS icons.

Run with the bundled Python and scipy dependency directory. Default is preview only;
--install copies approved results and updates the PM / PMG texture references.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import sys

sys.path.insert(0, r'C:/Users/Administrator/.codex/cache/icon-cutout-deps')
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artwork/imports/doubao_four_buildings_20261009'

GARDEN = [
    'pm_botanical_garden_nursery', 'pm_botanical_garden_fine_flowerbeds',
    'pm_botanical_garden_glasshouse_flowers', 'pm_botanical_garden_rare_greenhouse',
    'pm_botanical_garden_courtyard_fruit_trees', 'pm_botanical_garden_grafted_fruit_trees',
    'pm_botanical_garden_greenhouse_fruit_trees',
]
TAVERN = [
    'pm_izakaya_hearth_drinks', 'pm_izakaya_izakaya_banquet', 'pm_izakaya_city_cocktails',
    'pm_izakaya_travelers_stew', 'pm_izakaya_izakaya_delicacies', 'pm_izakaya_hearth_banquet',
    'pm_izakaya_communal_tables', 'pm_izakaya_counter_longtables', 'pm_izakaya_patron_rooms',
    'pm_izakaya_brick_stoves', 'pm_izakaya_iron_stoves_icehouse', 'pm_izakaya_electric_cold_kitchen',
]
BREED = [
    'pm_tot_animal_breeding_standard', 'pm_tot_animal_breeding_scientific',
    'pm_tot_animal_breeding_training', 'pm_tot_animal_breeding_modern',
    'pm_tot_animal_feeding_manual', 'pm_tot_animal_feeding_mechanized', 'pm_tot_animal_feeding_electric',
]
PET = [
    'pm_tot_pet_services_traditional', 'pm_tot_pet_services_companion', 'pm_tot_pet_services_care',
    'pm_tot_pet_services_comprehensive', 'pm_tot_pet_operation_small',
    'pm_tot_pet_operation_professional', 'pm_tot_pet_operation_centralized',
]
GROUPS = {
    'pmg_botanical_garden_cultivation': GARDEN[0], 'pmg_botanical_garden_fruit_trees': GARDEN[4],
    'pmg_izakaya_drinks': TAVERN[0], 'pmg_izakaya_food': TAVERN[3],
    'pmg_izakaya_hospitality': TAVERN[6], 'pmg_izakaya_kitchen': TAVERN[9],
    'pmg_tot_animal_breeding': BREED[0], 'pmg_tot_animal_feeding_equipment': BREED[4],
    'pmg_tot_pet_services': PET[0], 'pmg_tot_pet_operation': PET[4],
}

# Enclosed background components identified in visual QA of these exact originals.
# White animal fur, paper, glass reflections and medical cases are deliberately kept.
ENCLOSED_BACKGROUND = {
    '10_training.png': {10, 379, 381, 388, 393, 423, 469, 534},
    '08_hearth_drinks.png': {9, 87},
    '11_travelers_stew.png': {21, 22, 368, 369, 567},
    '14_communal_tables.png': {2, 15, 23, 742},
    '12_delicacies.png': {654},
    '14_electric.png': {94, 962},
    '07_centralized.png': {44, 69},
    '01_traditional.png': {
        2, 19, 20, 37, 40, 42, 44, 46, 47, 49, 50, 57, 69, 76, 79, 85,
        99, 105, 116, 118, 128, 153, 154, 155, 156, 157, 158, 159, 160, 161,
        164, 165, 184, 188, 197, 201, 203, 205, 206, 208, 218, 219, 221,
        226, 227, 228, 232, 486, 1507, 1648, 1650, 1651, 1662, 1815,
        1851, 1856, 1858, 1861, 1862, 1864, 1865, 1869, 1888, 1893, 1914,
        1924, 1943, 1950, 1969,
    },
}

def cutout(source):
    image = Image.open(source).convert('RGBA')
    rgba = np.asarray(image).copy()
    rgb = rgba[:, :, :3].astype(np.float32)
    low, high = rgb.min(axis=2), rgb.max(axis=2)
    white = (low >= 236) & ((high - low) <= 18)
    regions, count = ndimage.label(white)
    border = np.unique(np.concatenate((regions[0], regions[-1], regions[:, 0], regions[:, -1])))
    border = border[border != 0]
    background = np.isin(regions, border)
    selected = ENCLOSED_BACKGROUND.get(source.name, set())
    if selected:
        background |= np.isin(regions, list(selected))
    # Only a narrow edge is softened. Closed white foreground areas remain opaque.
    distance = ndimage.distance_transform_edt(~background)
    alpha = np.clip(distance / 1.5, 0, 1)
    # Floating pale smoke / shadow fragments are not opaque white objects.
    foreground_regions, _ = ndimage.label(alpha > 0)
    foreground_areas = np.bincount(foreground_regions.ravel())
    for label, slices in enumerate(ndimage.find_objects(foreground_regions), 1):
        if slices is None or not 40 <= foreground_areas[label] <= 40000:
            continue
        piece = foreground_regions[slices] == label
        piece_low = low[slices][piece]
        piece_span = (high-low)[slices][piece]
        if np.mean(piece_low) > 218 and np.mean(piece_span) < 16 and np.mean(piece_low < 180) < .01:
            local_alpha = alpha[slices]
            local_alpha[piece] *= np.clip((255-piece_low)/70, 0, 1)
    rgba[:, :, 3] = np.rint(alpha * 255).astype(np.uint8)
    # Unblend a white matte at partial-alpha edge pixels.
    edge = (alpha > 0) & (alpha < 1)
    rgb[edge] = np.clip((rgb[edge] - 255 * (1-alpha[edge, None])) / alpha[edge, None], 0, 255)
    rgba[:, :, :3] = np.rint(rgb).astype(np.uint8)
    rgba[alpha == 0, :3] = 0
    result = Image.fromarray(rgba, 'RGBA')
    bbox = result.getchannel('A').getbbox()
    if not bbox:
        raise ValueError('Empty cutout: ' + str(source))
    crop = result.crop(bbox)
    side = max(crop.size)
    canvas = Image.new('RGBA', (side + int(side * .10),) * 2)
    canvas.paste(crop, ((canvas.width-crop.width)//2, (canvas.height-crop.height)//2))
    return result, canvas.resize((256, 256), Image.Resampling.LANCZOS), bbox

def replace_texture(path, key, texture):
    bom = path.read_bytes().startswith(b'\xef\xbb\xbf')
    raw = path.read_text(encoding='utf-8-sig')
    # Texture is the first property in all of these project definitions.
    pattern = r'(^' + re.escape(key) + r'\s*=\s*\{\s*\n\s*texture\s*=\s*")[^"]+(")'
    updated, n = re.subn(pattern, lambda m: m[1]+texture+m[2], raw, flags=re.M)
    if n != 1:
        raise ValueError('Expected one texture: ' + key)
    if updated != raw:
        with path.open('w', encoding='utf-8-sig' if bom else 'utf-8', newline='') as stream:
            stream.write(updated)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', action='store_true')
    args = ap.parse_args()
    records = []
    for folder, pm_ids in [('garden_izakaya', GARDEN+TAVERN), ('breed_png', BREED), ('pet_png', PET)]:
        sources = sorted((OUT / 'originals' / folder).glob('*.png'))
        assert len(sources) == len(pm_ids), folder
        for source, pm in zip(sources, pm_ids):
            full, icon, bbox = cutout(source)
            for child in ('transparent', 'icons_256', 'dds'):
                (OUT / child).mkdir(parents=True, exist_ok=True)
            full.save(OUT / 'transparent' / (pm+'.png'))
            icon.save(OUT / 'icons_256' / (pm+'.png'))
            # Existing project PM DDS icons use uncompressed 32-bit RGBA without mipmaps.
            icon.save(OUT / 'dds' / (pm+'.dds'))
            decoded = Image.open(OUT / 'dds' / (pm+'.dds')).convert('RGBA')
            assert decoded.size == (256, 256)
            assert np.array_equal(np.asarray(decoded), np.asarray(icon)), pm
            assert decoded.getchannel('A').getextrema() == (0, 255), pm
            records.append(dict(pm=pm, source=str(source.relative_to(ROOT)), bbox=list(bbox),
                                texture='gfx/interface/icons/production_method_icons/'+pm+'.dds'))
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
    for start, end, name in [(0, 7, 'garden'), (7, 19, 'tavern'), (19, 26, 'breed'), (26, 33, 'pet')]:
        rows = records[start:end]
        sheet = Image.new('RGB', (1000, ((len(rows)+4)//5)*240), (42,48,60))
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(rows):
            icon = Image.open(OUT / 'icons_256' / (row['pm']+'.png'))
            icon.thumbnail((185, 185))
            x, y = (i%5)*200, (i//5)*240
            sheet.paste(icon, (x+7, y), icon)
            draw.text((x+4, y+192), Path(row['source']).name[:26], font=font, fill='white')
            draw.text((x+4, y+212), row['pm'].replace('pm_botanical_garden_', '').replace('pm_tot_', '').replace('pm_izakaya_', '')[:27], font=font, fill='white')
        sheet.save(OUT / (name+'_cutout_review.png'))
    if args.install:
        for row in records:
            target = ROOT / row['texture']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(OUT / 'dds' / (row['pm']+'.dds'), target)
            paths = list((ROOT / 'common/production_methods').glob('*.txt'))
            matches = [p for p in paths if re.search(r'^'+re.escape(row['pm'])+r'\s*=\s*\{', p.read_text(encoding='utf-8-sig'), re.M)]
            assert len(matches) == 1, row['pm']
            replace_texture(matches[0], row['pm'], row['texture'])
        for group, pm in GROUPS.items():
            paths = list((ROOT / 'common/production_method_groups').glob('*.txt'))
            matches = [p for p in paths if re.search(r'^'+re.escape(group)+r'\s*=\s*\{', p.read_text(encoding='utf-8-sig'), re.M)]
            assert len(matches) == 1, group
            replace_texture(matches[0], group, 'gfx/interface/icons/production_method_icons/'+pm+'.dds')
    (OUT / 'manifest.json').write_text(json.dumps(dict(installed=args.install, format='uncompressed RGBA 32-bit, 256x256, no mipmaps', icons=records), ensure_ascii=False, indent=2), encoding='utf-8')
    print('Processed {} icons; installed={}'.format(len(records), args.install))

if __name__ == '__main__':
    main()
