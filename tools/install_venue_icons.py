"""Convert directly transparent generated PNGs to PM DDS and create small previews."""
from pathlib import Path
import json
import re
import argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artwork/icon_candidates/venue_simple_20261009'

def update(path, key, texture):
    bom = path.read_bytes().startswith(b'\xef\xbb\xbf')
    raw = path.read_text(encoding='utf-8-sig')
    pattern = r'(^'+re.escape(key)+r'\s*=\s*\{\s*\n\s*texture\s*=\s*")[^"]+(")'
    new, count = re.subn(pattern, lambda m:m[1]+texture+m[2], raw, flags=re.M)
    assert count == 1, key
    if raw != new:
        with path.open('w',encoding='utf-8-sig' if bom else 'utf-8',newline='') as stream:
            stream.write(new)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--install',action='store_true');args=ap.parse_args()
    specs=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    ready=[s for s in specs if (OUT/'sources'/(s['pm']+'.png')).is_file()]
    if args.install:
        assert len(ready)==30,'Require all 30 icons before installation'
    (OUT/'icons_256').mkdir(parents=True,exist_ok=True)
    for s in ready:
        image=Image.open(OUT/'sources'/(s['pm']+'.png')).convert('RGBA')
        assert image.getchannel('A').getextrema()==(0,255),s['pm']
        box=image.getchannel('A').getbbox();image=image.crop(box)
        size=max(image.size);side=round(size*1.12)
        canvas=Image.new('RGBA',(side,side));canvas.paste(image,((side-image.width)//2,(side-image.height)//2))
        icon=canvas.resize((256,256),Image.Resampling.LANCZOS)
        icon.save(OUT/'icons_256'/(s['pm']+'.png'))
        if args.install:
            texture='gfx/interface/icons/production_method_icons/'+s['pm']+'.dds'
            icon.save(ROOT/texture)
            decoded=Image.open(ROOT/texture).convert('RGBA')
            assert np.array_equal(np.asarray(icon),np.asarray(decoded)),s['pm']
            update(ROOT/'common/production_methods/tot_venue.txt',s['pm'],texture)
    for venue,prefix in [('zoo','pm_zoo_'),('amusement','pm_amusement_'),('aquarium','pm_aquarium_')]:
        rows=[s for s in ready if s['pm'].startswith(prefix)]
        if not rows:continue
        sheet=Image.new('RGB',(960,((len(rows)+5)//6)*150),(40,46,57));draw=ImageDraw.Draw(sheet)
        font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
        for i,s in enumerate(rows):
            image=Image.open(OUT/'icons_256'/(s['pm']+'.png')).resize((104,104))
            x=(i%6)*160;y=(i//6)*150;sheet.paste(image,(x+28,y+5),image)
            draw.text((x+7,y+116),s['name'],font=font,fill='white')
        sheet.save(OUT/(venue+'_preview.png'))
    if args.install:
        groups={
            'pmg_zoo_animal_type':'pm_zoo_type_small',
            'pmg_zoo_interaction':'pm_zoo_interaction_basic',
            'pmg_zoo_feeding_equipment':'pm_zoo_feeding_manual',
            'pmg_amusement_ride':'pm_amusement_ride_carousel',
            'pmg_amusement_shop':'pm_amusement_shop_stall',
            'pmg_aquarium_animal_type':'pm_aquarium_type_freshwater',
            'pmg_aquarium_interaction':'pm_aquarium_program_feeding',
            'pmg_aquarium_circulation':'pm_aquarium_circulation_manual',
        }
        for key,pm in groups.items():
            update(ROOT/'common/production_method_groups/tot_venue.txt',key,'gfx/interface/icons/production_method_icons/'+pm+'.dds')
    print('Ready {} / 30; installed {}'.format(len(ready),args.install))

if __name__=='__main__':main()
