"""Install the approved rabbit goods and matching animal-garden building icon."""
import argparse
import json
import shutil
from PIL import Image
from install_religion_building_icons import ROOT, OUT, update, update_texticon


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('building_source')
    args=parser.parse_args()
    building=OUT/'building_animal_garden_rabbit.png'
    shutil.copy2(args.building_source,building)
    specs=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    installed=json.loads((OUT/'installed.json').read_text(encoding='utf-8'))
    tasks=[('ornamental_animals',OUT/'ornamental_animals_rabbit.png','gfx/interface/icons/goods_icons/ornamental_animals_rabbit.dds','ornamental_animals_rabbit_generation.json','_rabbit'),('building_tot_animal_breeding_center',building,'gfx/interface/icons/building_icons/building_tot_animal_breeding_center_framed_rabbit.dds','rabbit_building_generation.json','_framed_rabbit')]
    for key,source,texture,record,suffix in tasks:
        image=Image.open(source).convert('RGBA')
        assert image.width==image.height and image.getchannel('A').getextrema()==(0,255)
        icon=image.resize((256,256),Image.Resampling.LANCZOS)
        icon.save(OUT/'icons_256'/(key+'.png'))
        icon.save(ROOT/texture)
        assert Image.open(ROOT/texture).convert('RGBA').tobytes()==icon.tobytes()
        if key=='ornamental_animals':
            update(ROOT/'common/goods/tot_ornamental_animals.txt',key,'texture',texture)
            update_texticon(ROOT/'gui/tot_goods_texticons.gui',key,texture)
        else:
            update(ROOT/'common/buildings/tot_animal_breeding.txt',key,'icon',texture)
        record_path=OUT/record
        generation=json.loads(record_path.read_text(encoding='utf-8'))
        generation.update({'status':'installed','texture':texture,'size':[256,256]})
        record_path.write_text(json.dumps(generation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for spec in specs:
            if spec['key']==key:
                spec.update({'source':source.relative_to(OUT).as_posix(),'texture_suffix':suffix,'prompt':generation['prompt']})
                if key=='ornamental_animals':
                    spec['subject']='单只白兔头像，透明背景。'
                    spec['full_bleed']=True
                else: spec['subject']='动物培育园，完整铜金边框，右下角单只白兔。'
        for entry in installed:
            if entry['key']==key: entry['texture']=texture
    (OUT/'manifest.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'installed.json').write_text(json.dumps(installed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    preview=Image.new('RGBA',(1280,256),(38,42,48,255))
    keys=['building_botanical_garden','building_izakaya','building_tot_pet_shop','building_tot_animal_breeding_center','building_religious_center']
    for i,key in enumerate(keys): preview.alpha_composite(Image.open(OUT/'icons_256'/(key+'.png')).convert('RGBA'),(256*i,0))
    preview.convert('RGB').save(OUT/'framed_buildings_preview.png')
    preview.convert('RGB').save(OUT/'building_preview.png')
    print('PASS: rabbit goods/texticon/building references installed; 256px DDS pixel roundtrip verified.')


if __name__=='__main__': main()
