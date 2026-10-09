"""Reuse the actual vanilla building frame, as explicitly requested by the user."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from install_religion_building_icons import ROOT, OUT, update

DEST = ROOT / 'artwork/icon_candidates/frame_and_secondary_pm_20261010'
VANILLA = Path('D:/Steam/steamapps/common/Victoria 3/game/gfx/interface/icons/building_icons/food_industry.dds')
TARGETS = [
    ('building_botanical_garden', 'common/buildings/tot_botanical_garden.txt'),
    ('building_izakaya', 'common/buildings/tot_izakaya.txt'),
    ('building_tot_pet_shop', 'common/buildings/tot_pet_shop.txt'),
    ('building_tot_animal_breeding_center', 'common/buildings/tot_animal_breeding.txt'),
    ('building_religious_center', 'common/buildings/tot_religious_center.txt'),
]

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    vanilla = Image.open(VANILLA).convert('RGBA')
    assert vanilla.size == (256, 256)
    interior = Image.new('L', vanilla.size, 0)
    ImageDraw.Draw(interior).rounded_rectangle((8, 8, 247, 247), radius=16, fill=255)
    # Keep the source frame, its edge shading and alpha pixels verbatim.
    frame = vanilla.copy()
    frame.paste((0, 0, 0, 0), (0, 0), interior)
    frame.save(DEST / 'vanilla_frame.png')
    manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    installed = json.loads((OUT / 'installed.json').read_text(encoding='utf-8'))
    previews = []
    provenance = []
    for key, definition in TARGETS:
        prior = DEST / (key + '_before_frame.png')
        if not prior.exists():
            Image.open(OUT / 'icons_256' / (key + '.png')).save(prior)
        scene = Image.open(prior).convert('RGBA')
        # Remove the old generated perimeter before fitting the original frame.
        scene = scene.crop((12, 12, 244, 244)).resize((256, 256), Image.Resampling.LANCZOS)
        result = frame.copy()
        result.paste(scene, (0, 0), interior)
        # Outside the interior aperture, every RGBA pixel equals vanilla.
        check = Image.new('RGBA', vanilla.size)
        check.paste(result, (0, 0), Image.eval(interior, lambda v: 255-v))
        expected = Image.new('RGBA', vanilla.size)
        expected.paste(vanilla, (0, 0), Image.eval(interior, lambda v: 255-v))
        assert check.tobytes() == expected.tobytes()
        png = DEST / (key + '_vanilla_frame.png')
        texture = 'gfx/interface/icons/building_icons/' + key + '_vanilla_frame.dds'
        result.save(png)
        result.save(ROOT / texture)
        assert Image.open(ROOT / texture).convert('RGBA').tobytes() == result.tobytes()
        result.save(OUT / 'icons_256' / (key + '.png'))
        update(ROOT / definition, key, 'icon', texture)
        old_paths = [entry['texture'] for entry in installed if entry['key'] == key]
        for gui in (ROOT / 'gui').glob('*.gui'):
            data = gui.read_text(encoding='utf-8-sig')
            updated = data
            for old in old_paths:
                updated = updated.replace('"'+old+'"', '"'+texture+'"')
            if updated != data:
                gui.write_text(updated, encoding='utf-8-sig')
        for spec in manifest:
            if spec['key'] == key:
                spec['source'] = '../frame_and_secondary_pm_20261010/' + png.name
                spec['texture_suffix'] = '_vanilla_frame'
                spec['frame_method'] = 'original vanilla food_industry DDS perimeter pixels'
        for entry in installed:
            if entry['key'] == key:
                entry['texture'] = texture
        provenance.append({'key': key, 'texture': texture, 'frame_source': str(VANILLA), 'prior': str(prior)})
        previews.append(result)
    preview = Image.new('RGBA', (1536, 256), (38, 42, 48, 255))
    preview.alpha_composite(vanilla, (0, 0))
    for i, item in enumerate(previews):
        preview.alpha_composite(item, ((i+1)*256, 0))
    preview.convert('RGB').save(DEST / 'building_frame_comparison.png')
    current = preview.crop((256, 0, 1536, 256)).convert('RGB')
    for name in ['building_preview.png', 'framed_buildings_preview.png']:
        current.save(OUT / name)
    (DEST / 'frame_installation.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'installed.json').write_text(json.dumps(installed, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('PASS: 5 building frames use identical original perimeter pixels; DDS roundtrip verified.')

if __name__ == '__main__':
    main()
