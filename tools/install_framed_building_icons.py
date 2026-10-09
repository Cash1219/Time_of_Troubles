"""Install approved framed building sources as 256px RGBA DDS assets."""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image
from install_religion_building_icons import ROOT, OUT, update


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--animal-source',required=True,type=Path)
    parser.add_argument('--religion-source',required=True,type=Path)
    args=parser.parse_args()
    specs=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    sources={
        'building_botanical_garden':OUT/'sources/building_botanical_garden.png',
        'building_izakaya':OUT/'sources/building_izakaya.png',
        'building_tot_pet_shop':OUT/'sources/building_tot_pet_shop.png',
        'building_tot_animal_breeding_center':args.animal_source,
        'building_religious_center':args.religion_source,
    }
    filenames={
        'building_botanical_garden':'tot_botanical_garden.txt',
        'building_izakaya':'tot_izakaya.txt',
        'building_tot_pet_shop':'tot_pet_shop.txt',
        'building_tot_animal_breeding_center':'tot_animal_breeding.txt',
        'building_religious_center':'tot_religious_center.txt',
    }
    target=OUT/'sources_framed_v2'
    target.mkdir(exist_ok=True)
    report=[]
    for key,source in sources.items():
        destination=target/(key+'.png')
        if source.resolve()!=destination.resolve(): shutil.copy2(source,destination)
        original=Image.open(destination).convert('RGBA')
        assert original.width==original.height,(key,original.size)
        icon=original.resize((256,256),Image.Resampling.LANCZOS)
        png=OUT/'icons_256'/(key+'.png')
        icon.save(png)
        texture='gfx/interface/icons/building_icons/'+key+'_framed_v2.dds'
        dds=ROOT/texture
        # New suffix preserves all previous candidates; subsequent runs must match.
        if dds.exists(): assert Image.open(dds).convert('RGBA').tobytes()==icon.tobytes(),texture
        icon.save(dds)
        check=Image.open(dds).convert('RGBA')
        assert check.size==(256,256) and check.tobytes()==icon.tobytes(),key
        update(ROOT/'common/buildings'/filenames[key],key,'icon',texture)
        for spec in specs:
            if spec['key']==key:
                spec.update({'source':destination.relative_to(OUT).as_posix(),'texture_suffix':'_framed_v2','full_bleed':True,'frame_required':True})
        report.append({'key':key,'source':str(destination),'png':str(png),'texture':texture,'size':check.size,'alpha_extrema':check.getchannel('A').getextrema()})
    generation_path=OUT/'framed_redesign_generation.json'
    if generation_path.exists():
        generation=json.loads(generation_path.read_text(encoding='utf-8'))
        for spec in specs:
            entry={'building_tot_animal_breeding_center':'animal_breeding','building_religious_center':'religious_center'}.get(spec['key'])
            if entry: spec['prompt']=generation[entry]['prompt']
    (OUT/'manifest.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'framed_buildings_installed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    installed_path=OUT/'installed.json'
    if installed_path.exists():
        installed=json.loads(installed_path.read_text(encoding='utf-8'))
        textures={r['key']:r['texture'] for r in report}
        for entry in installed:
            if entry['key'] in textures: entry['texture']=textures[entry['key']]
        installed_path.write_text(json.dumps(installed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Preview assembly only; generated artwork is not edited with this script.
    preview=Image.new('RGBA',(256*5,256),(38,42,48,255))
    for i,key in enumerate(sources):
        icon=Image.open(OUT/'icons_256'/(key+'.png')).convert('RGBA')
        preview.alpha_composite(icon,(256*i,0))
    preview.convert('RGB').save(OUT/'framed_buildings_preview.png')
    preview.convert('RGB').save(OUT/'building_preview.png')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
