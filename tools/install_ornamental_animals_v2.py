"""Convert the simplified animal goods icon and update its two references."""
import argparse
import json
import shutil
from PIL import Image
from install_religion_building_icons import ROOT, OUT, update, update_texticon


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source')
    args=parser.parse_args()
    source=OUT/'ornamental_animals_v2.png'
    shutil.copy2(args.source,source)
    original=Image.open(source).convert('RGBA')
    assert original.getchannel('A').getextrema()==(0,255)
    cropped=original.crop(original.getchannel('A').getbbox())
    side=round(max(cropped.size)*1.08)
    canvas=Image.new('RGBA',(side,side))
    canvas.paste(cropped,((side-cropped.width)//2,(side-cropped.height)//2))
    icon=canvas.resize((256,256),Image.Resampling.LANCZOS)
    icon.save(OUT/'icons_256/ornamental_animals.png')
    texture='gfx/interface/icons/goods_icons/ornamental_animals_v2.dds'
    icon.save(ROOT/texture)
    check=Image.open(ROOT/texture).convert('RGBA')
    assert check.size==(256,256) and check.tobytes()==icon.tobytes()
    update(ROOT/'common/goods/tot_ornamental_animals.txt','ornamental_animals','texture',texture)
    update_texticon(ROOT/'gui/tot_goods_texticons.gui','ornamental_animals',texture)
    generation_path=OUT/'ornamental_animals_v2_generation.json'
    generation=json.loads(generation_path.read_text(encoding='utf-8'))
    generation.update({'status':'installed','texture':texture,'size':[256,256]})
    generation_path.write_text(json.dumps(generation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    specs=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    for spec in specs:
        if spec['key']=='ornamental_animals':
            spec.update({'source':'ornamental_animals_v2.png','texture_suffix':'_v2','prompt':generation['prompt']})
    (OUT/'manifest.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    installed_path=OUT/'installed.json'
    entries=json.loads(installed_path.read_text(encoding='utf-8'))
    for entry in entries:
        if entry['key']=='ornamental_animals': entry['texture']=texture
    installed_path.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    preview=Image.new('RGBA',(96,96),(43,48,58,255))
    preview.alpha_composite(icon.resize((64,64),Image.Resampling.LANCZOS),(16,16))
    preview.convert('RGB').save(OUT/'ornamental_animals_v2_preview64.png')
    print('PASS: 256px RGBA DDS roundtrip, goods and texticon connected: '+texture)


if __name__=='__main__': main()
