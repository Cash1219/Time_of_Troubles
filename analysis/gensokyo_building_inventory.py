"""Count all explicit startup building levels in the current Gensokyo countries.

Ownership levels fund the created building; they are not additional standalone
financial districts/manor houses. Engine-generated buildings are not counted.
"""
import collections
import json
import re
from eastern_industry_prototype import ROOT, OUT, clean, blocks
from west_coast_draft import ownership, NAMES

NAMES = dict(NAMES, JNKF='纯狐阵营', HCTI='赫卡提亚地狱', MIST='冰之领地')
NAMES.pop('WAS',None)
CATEGORY_NAMES = ['农牧','采矿林渔','制造业','公共及基建','特色建筑','军事']


def category(kind):
    if kind in ['building_barrack','building_naval_base']:return '军事'
    if kind in ['building_botanical_garden','building_religious_center','building_izakaya','building_tot_kappa_power','building_tot_chireiden_fusion']:return '特色建筑'
    if kind.endswith(('_farm','_plantation','_ranch','_vineyard')):return '农牧'
    if kind.endswith(('_mine','_field')) or kind in ['building_logging_camp','building_fishing_wharf','building_whaling_station']:return '采矿林渔'
    if kind in ['building_government_administration','building_university','building_construction_sector','building_port','building_railway']:return '公共及基建'
    return '制造业'


def main():
    owners = ownership((ROOT/'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    pairs = {tuple(v) for v in owners.values()}
    tags = {tag for state,tag in pairs if tag in NAMES}
    inventory = {tag:dict(name=NAMES[tag],levels=0,records=0,by_building=collections.Counter(),by_category=collections.Counter()) for tag in tags}
    entries = []
    for path in sorted((ROOT/'common/history/buildings').glob('*.txt')):
        for sm,sb in blocks(clean(path.read_text(encoding='utf-8-sig')),r's:(STATE_\w+)\s*=\s*\{'):
            for tm,tb in blocks(sb,r'region_state:(\w+)\s*=\s*\{'):
                if tm[1] not in tags:continue
                assert (sm[1],tm[1]) in pairs,(path.name,sm[1],tm[1])
                for _,bb in blocks(tb,r'create_building\s*=\s*\{'):
                    kind = re.search(r'\bbuilding\s*=\s*"?(building_\w+)',bb)[1]
                    funded = sum(int(n) for _,ob in blocks(bb,r'add_ownership\s*=\s*\{') for n in re.findall(r'\blevels\s*=\s*(\d+)',ob))
                    if not funded:
                        level = re.search(r'\blevel\s*=\s*(\d+)',bb)
                        assert level,(path.name,tm[1],kind,'No explicit levels')
                        funded = int(level[1])
                    row=dict(country=tm[1],state=sm[1],building=kind,levels=funded,category=category(kind),source=str(path.relative_to(ROOT)))
                    entries.append(row)
                    item=inventory[tm[1]]
                    item['levels']+=funded;item['records']+=1
                    item['by_building'][kind]+=funded;item['by_category'][category(kind)]+=funded
    totals=collections.Counter()
    for item in inventory.values():totals.update(item['by_category'])
    report=dict(country_count=len(tags),total_levels=sum(item['levels'] for item in inventory.values()),creation_records=len(entries),by_category=totals,
        countries=inventory,entries=entries,scope='Explicit create_building history only. Excludes engine-generated urban centers, subsistence, ownership buildings, conscription centers and event-created buildings; not a runtime save measurement.')
    (OUT/'gensokyo_all_buildings_current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 幻想乡全部开局建筑配置统计','',
        '统计当前模组历史配置中的全部幻想乡国家。数量按**建筑等级**计算；同一种建筑在不同国家地区的创建记录分别统计，不把等级当成独立工厂数量。',
        '',f"共**{report['country_count']}国、{report['total_levels']}级、{report['creation_records']}条建筑创建记录**。",
        '', '自动生成的城市中心、自给农场、金融区/庄园、征兵中心，以及事件后续创建的建筑未计入。所有权里的等级是已有建筑的持有份额，不重复计成另一批金融区/庄园建筑。这是配置统计，实际游戏内全部建筑需要读开局存档确认。',
        '', '| 国家 | 农牧 | 采矿林渔 | 制造业 | 公共及基建 | 特色 | 军事 | 总等级 |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for tag,item in sorted(inventory.items(),key=lambda pair:(-pair[1]['levels'],pair[0])):
        lines.append('| '+item['name']+' | '+' | '.join(str(item['by_category'].get(cat,0)) for cat in CATEGORY_NAMES)+' | '+str(item['levels'])+' |')
    lines += ['| **总计** | '+' | '.join(str(totals.get(cat,0)) for cat in CATEGORY_NAMES)+' | **'+str(report['total_levels'])+'** |','',
        '公共及基建包括行政、大学、建设部门、港口、铁路。特色包括植物园、宗教设施、居酒屋和两种特色电站。天界没有显式开局建筑配置，表中为0，不代表没有人口或游戏自动生成的建筑。',
        '', '## 各国建筑明细','']
    for tag,item in sorted(inventory.items(),key=lambda pair:(-pair[1]['levels'],pair[0])):
        lines += ['### '+item['name']+'（'+tag+'）','',
            '| 建筑代码 | 总等级 |','|---|---:|']
        lines += ['| '+kind+' | '+str(n)+' |' for kind,n in sorted(item['by_building'].items())]
        lines.append('')
    (OUT/'gensokyo_all_buildings_current.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['country_count','total_levels','creation_records','by_category']},ensure_ascii=False))


if __name__ == '__main__':main()
