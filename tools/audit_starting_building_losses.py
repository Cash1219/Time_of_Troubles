"""Read-only comparison of all local vanilla and effective mod opening buildings."""
from pathlib import Path
from collections import Counter, defaultdict
import json
import re
from building_history_config import parse_items, children, value

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('D:/Steam/steamapps/common/Victoria 3/game')
OUT = ROOT / 'analysis/starting_building_review_20261009'


def files(folder, mod=False):
    result = {p.name: p for p in (BASE / folder).glob('*.txt')}
    if mod:
        result.update({p.name: p for p in (ROOT / folder).glob('*.txt')})
    return sorted(result.values(), key=lambda p: p.name)


def parsed(path):
    return parse_items(path.read_text(encoding='utf-8-sig'))[0]


def labels():
    result = {}
    for directory in [BASE/'localization/simp_chinese', ROOT/'localization/simp_chinese', ROOT/'localization/replace/simp_chinese']:
        for p in sorted(directory.rglob('*.yml')):
            result.update(re.findall(r'^\s*([\w]+):\d*\s+"([^"\n]*)"', p.read_text(encoding='utf-8-sig', errors='replace'), re.M))
    return result


def owners(mod=False):
    result = defaultdict(dict)
    for p in files('common/history/states', mod):
        for root in parsed(p):
            if root[0] != 'STATES':
                continue
            for state in root[1]:
                if not state[0].startswith('s:'):
                    continue
                for block in children(state, 'create_state'):
                    country = value(block, 'country').removeprefix('c:')
                    provinces = children(block, 'owned_provinces')
                    ids = [x[0].strip('"').upper() for x in provinces[0][1]] if provinces else []
                    result[state[0][2:]].setdefault(country, []).extend(ids)
    return dict(result)


def buildings(mod=False):
    result, warnings = [], []
    def state_nodes(items, conditions=()):
        for item in items:
            if item[0].startswith('s:'):
                yield item, conditions
            elif item[0] in {'if','else_if','else'}:
                limits = children(item,'limit')
                condition = repr(limits[0][1]) if limits else 'else'
                yield from state_nodes(item[1], conditions+(condition,))
            else:
                warnings.append({'unhandled_key':item[0]})
    for p in files('common/history/buildings', mod):
        text = p.read_text(encoding='utf-8-sig')
        for root in parse_items(text)[0]:
            if root[0] != 'BUILDINGS':
                warnings.append({'file':str(p), 'root':root[0]})
                continue
            for state,conditions in state_nodes(root[1]):
                for region in state[1]:
                    if not region[0].startswith('region_state:'):
                        warnings.append({'file':str(p), 'region_key':region[0]})
                        continue
                    for b in children(region, 'create_building'):
                        ownership = []
                        for own in children(b, 'add_ownership'):
                            for part in own[1]:
                                ownership.append({'kind':part[0], 'levels':int(value(part,'levels','0')), 'country':value(part,'country'), 'type':value(part,'type'), 'region':value(part,'region')})
                        levels = sum(x['levels'] for x in ownership)
                        explicit = value(b, 'level', value(b, 'levels'))
                        if explicit:
                            warnings.append({'file':str(p), 'building':value(b,'building'), 'explicit_level':explicit})
                            levels = int(explicit)
                        if not ownership and not explicit:
                            levels = 1
                            warnings.append({'file':str(p), 'building':value(b,'building'), 'default_level_assumed':1})
                        pms = children(b, 'activate_production_methods')
                        result.append({'state':state[0][2:], 'owner':region[0].split(':',1)[1], 'building':value(b,'building'), 'levels':levels, 'conditions':conditions, 'ownership':ownership, 'pms':[x[0].strip('"') for x in pms[0][1]] if pms else [], 'file':str(p), 'line':text.count('\n',0,b[2])+1})
    return result, warnings


def definitions(folder, mod=False):
    result = {}
    for p in files(folder,mod):
        for n in parsed(p):
            result[n[0]] = n
    return result


def population_mismatches(state_owners):
    issues=[]
    for p in files('common/history/pops', True):
        text=p.read_text(encoding='utf-8-sig')
        for root in parse_items(text)[0]:
            if root[0]!='POPS': continue
            for state in root[1]:
                if not state[0].startswith('s:'): continue
                for region in state[1]:
                    if not region[0].startswith('region_state:'): continue
                    owner=region[0].split(':',1)[1]
                    if owner in state_owners.get(state[0][2:],{}): continue
                    issues.append({'state':state[0][2:],'owner':owner,'population':sum(int(value(pop,'size','0')) for pop in children(region,'create_pop')),'file':str(p),'line':text.count('\n',0,region[2])+1})
    return issues


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = labels()
    name = lambda key: names.get(key,key).replace('|','／')
    original, ow = buildings()
    current, cw = buildings(True)
    vo, mo = owners(), owners(True)
    vb, mb = definitions('common/buildings'), definitions('common/buildings',True)
    groups = definitions('common/building_groups',True)
    def category(b):
        group = value(mb.get(b,vb.get(b,('',[],0,0))), 'building_group')
        ancestry = set()
        while group and group not in ancestry:
            ancestry.add(group)
            group = value(groups.get(group,('',[],0,0)), 'parent_group')
        if 'bg_military' in ancestry: return '军队'
        if b == 'building_construction_sector': return '建设'
        if b in {'building_government_administration','building_university'}: return '行政教育'
        if b in {'building_trade_center','building_urban_center','building_manor_house','building_financial_district'}: return '贸易城镇产权'
        if b in {'building_railway','building_port'}: return '交通'
        if b not in vb: return '模组新增'
        if ancestry & {'bg_manufacturing','bg_agriculture','bg_plantations','bg_ranching','bg_resource','bg_mining','bg_logging','bg_fishing','bg_whaling','bg_arts'}: return '生产'
        return '其他'
    a,b = defaultdict(Counter),defaultdict(Counter)
    source = defaultdict(list)
    for records,table in [(original,a),(current,b)]:
        for r in records:
            table[r['state']][r['building']] += r['levels']
            source[(r['state'],r['building'])].append(r)
    states = sorted(set(vo)|set(mo)|set(a)|set(b))
    rows,details = [],[]
    for s in states:
        losses = Counter({k:max(a[s][k]-b[s][k],0) for k in a[s]})
        gains = Counter({k:max(b[s][k]-a[s][k],0) for k in b[s] if k in vb})
        custom = sum(v for k,v in b[s].items() if k not in vb)
        old = sum(a[s].values())
        now = sum(v for k,v in b[s].items() if k in vb)
        old_ids = set(x for ids in vo.get(s,{}).values() for x in ids)
        new_ids = set(x for ids in mo.get(s,{}).values() for x in ids)
        row = {'state':s,'name':name(s),'vanilla_owners':list(vo.get(s,{})), 'mod_owners':list(mo.get(s,{})), 'vanilla_levels':old,'mod_vanilla_levels':now,'mod_custom_levels':custom,'removed_levels':sum(losses.values()),'added_vanilla_levels':sum(gains.values()),'net_vanilla_delta':now-old,'production_removed':sum(v for k,v in losses.items() if category(k)=='生产'), 'lost_by_type':{k:v for k,v in losses.items() if v}, 'gained_by_type':{k:v for k,v in gains.items() if v},'province_ids_removed':len(old_ids-new_ids),'province_ids_added':len(new_ids-old_ids)}
        rows.append(row)
        for k in sorted(set(a[s])|set(b[s])):
            details.append({'state':s,'state_name':name(s),'building':k,'building_name':name(k),'category':category(k),'vanilla':a[s][k],'mod':b[s][k],'delta':b[s][k]-a[s][k],'current_owners':list(mo.get(s,{})), 'records':source[(s,k)]})
    country = defaultdict(lambda:{'vanilla_same_tag':Counter(),'current':Counter(),'territory_baseline':Counter(),'split_states':[]})
    for r in original: country[r['owner']]['vanilla_same_tag'][category(r['building'])] += r['levels']
    for r in current: country[r['owner']]['current'][category(r['building'])] += r['levels']
    for s in states:
        parts = mo.get(s,{})
        total = sum(len(ids) for ids in parts.values())
        for owner,ids in parts.items():
            fraction = len(set(ids))/sum(len(set(v)) for v in parts.values()) if total else 0
            if len(parts)>1: country[owner]['split_states'].append(s)
            for k,v in a[s].items(): country[owner]['territory_baseline'][category(k)] += v*fraction
    countries = []
    for tag,c in country.items():
        base = sum(c['territory_baseline'].values())
        current_v = sum(v for k,v in c['current'].items() if k!='模组新增')
        countries.append({'tag':tag,'name':name(tag),'current_vanilla':current_v,'current_custom':c['current']['模组新增'],'territory_baseline_estimate':round(base,3),'territory_delta_estimate':round(current_v-base,3),'original_same_tag':sum(c['vanilla_same_tag'].values()),'categories':{k:dict(v) if isinstance(v,Counter) else v for k,v in c.items()}})
    issues = [r for r in current if r['owner'] not in mo.get(r['state'],{})]
    pop_issues = population_mismatches(mo)
    province_owner = {}
    duplicate_provinces = []
    for s,parts in mo.items():
        for tag,ids in parts.items():
            for pid in ids:
                if pid in province_owner: duplicate_provinces.append([pid,province_owner[pid],[s,tag]])
                province_owner[pid]=[s,tag]
    global_province_old = {pid:[s,t] for s,parts in vo.items() for t,ids in parts.items() for pid in ids}
    seen_vanilla, vanilla_duplicates = {}, []
    for s,parts in vo.items():
        for tag,ids in parts.items():
            for pid in ids:
                if pid in seen_vanilla: vanilla_duplicates.append([pid,seen_vanilla[pid],[s,tag]])
                seen_vanilla[pid]=[s,tag]
    province_changes = [{'province':pid,'vanilla':global_province_old.get(pid),'mod':province_owner.get(pid)} for pid in sorted(set(global_province_old)|set(province_owner)) if global_province_old.get(pid)!=province_owner.get(pid)]
    summary = {'state_count':len(states),'vanilla_state_count':len(vo),'mod_state_count':len(mo),'original_records':len(original),'mod_records':len(current),'vanilla_levels':sum(r['levels'] for r in original),'mod_vanilla_levels':sum(r['levels'] for r in current if r['building'] in vb),'mod_custom_levels':sum(r['levels'] for r in current if r['building'] not in vb),'removed_levels':sum(r['removed_levels'] for r in rows),'added_vanilla_levels':sum(r['added_vanilla_levels'] for r in rows),'states_with_any_loss':sum(r['removed_levels']>0 for r in rows),'states_net_lower':sum(r['net_vanilla_delta']<0 for r in rows),'province_count_vanilla':len(global_province_old),'province_count_mod':len(province_owner),'province_changes':len(province_changes),'building_owner_mismatches':len(issues),'mismatched_building_levels':sum(r['levels'] for r in issues),'duplicate_province_assignments':len(duplicate_provinces),'conflicting_province_assignments':sum(old!=new for _,old,new in duplicate_provinces),'conditional_monument_levels_vanilla':sum(r['levels'] for r in original if r['conditions']),'conditional_monument_levels_mod':sum(r['levels'] for r in current if r['conditions'])}
    summary.update({'vanilla_duplicate_province_assignments':len(vanilla_duplicates),'vanilla_conflicting_province_assignments':sum(old!=new for _,old,new in vanilla_duplicates),'new_conflicting_province_ids':sorted({pid for pid,old,new in duplicate_provinces if old!=new}-{pid for pid,old,new in vanilla_duplicates if old!=new})})
    summary.update({'population_region_mismatches':len(pop_issues),'mismatched_population':sum(r['population'] for r in pop_issues)})
    data = {'summary':summary,'states':rows,'building_details':details,'countries':countries,'province_changes':province_changes,'owner_mismatches':issues,'population_mismatches':pop_issues,'duplicate_province_assignments':duplicate_provinces,'vanilla_duplicate_province_assignments':vanilla_duplicates,'parse_warnings':{'vanilla':ow,'mod':cw}}
    (OUT/'full_audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['# 开局建筑全量对照（2026-10-09）','','比较本机原版与当前模组的1836开局历史。所有同名历史文件以模组覆盖，新增文件追加。按州和建筑类型比较，跨国转移不算删除；等级来自add_ownership内各份额levels之和。未改建筑历史。','','## 范围与口径','','- 游戏没有给这些建筑逐小省份定位，不能判定某个省份具体有多少厂；逐省检查归属，逐州检查建筑。','- 原版建筑与模组新增建筑分开，新增体验建筑不能视为补回工具厂、农场等。','- 下表“削减”逐建筑类型累加；新增其他建筑不抵销该项。净减则比较原版建筑总等级。','- 包含两项DLC条件地标（国会山、中央公园），双方均各1级；未启用对应DLC时双方各扣2，差额不变。产权建筑、城镇中心、自给建筑、驻军等引擎动态生成项目不是本表的静态开局建筑。军队栏是历史中明确放置的军事建筑，并非全体军队单位数。','- 文件记录总等级包括归属失配条目，不代表全部成功生成；41条失配见owner_mismatches.md，必须先核对这些潜在损失，再判断补偿。','- 国家当前领土基准：单一归属州直接采用全州原版等级；分割州按当前省份数量比例估算，非历史实际分配，也非人口/GDP比例。地图变动州需结合地形重划审核。','- 未计算工资、生产方式效率、人口、法律、附属国上缴、市场规模及1848年的存档建设；建筑等级差不能直接换算财政收入。','','## 全局','', '```json', json.dumps(summary,ensure_ascii=False,indent=2),'```','','## 英法：拆分与本地削减分别看','','|国家|原版同标签等级（含其殖民地）|当前原版建筑等级|当前领土原版基准（分割州估算）|领土差额|模组新增等级|','|---|---:|---:|---:|---:|---:|']
    for r in countries:
        if r['tag'] in {'GBR','FRA'}: lines.append(f"|{r['name']} ({r['tag']})|{r['original_same_tag']}|{r['current_vanilla']}|{r['territory_baseline_estimate']}|{r['territory_delta_estimate']}|{r['current_custom']}|")
    lines += ['','## 有任一原版建筑削减的全部州','','|州|当前国家|原版等级|现存原版等级|净差额|逐类型削减|其中生产削减|模组新增|削减明细|','|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in sorted(rows,key=lambda r:(-r['removed_levels'],r['state'])):
        if not r['removed_levels']: continue
        loss = '；'.join(f'{name(k)} -{v}' for k,v in r['lost_by_type'].items())
        tags = '、'.join(f'{name(t)} ({t})' for t in r['mod_owners'])
        lines.append(f"|{r['name']} ({r['state']})|{tags}|{r['vanilla_levels']}|{r['mod_vanilla_levels']}|{r['net_vanilla_delta']:+}|{r['removed_levels']}|{r['production_removed']}|{r['mod_custom_levels']}|{loss}|")
    lines += ['','## 当前领土原版建筑低于基准的国家','','分割州估算可能影响边界国家排名。不能据此直接按差额发补贴；先恢复明确缺失的生产建筑，再核对建设、行政和军队负担。','','|国家|原版领土基准|现存原版等级|差额|生产现存／基准|军队现存／基准|建设现存／基准|行政教育现存／基准|','|---|---:|---:|---:|---|---|---|---|']
    for r in sorted(countries,key=lambda r:r['territory_delta_estimate']):
        if r['territory_delta_estimate']>=-0.001: continue
        c=r['categories']
        fmt=lambda k:f"{c['current'].get(k,0)}／{c['territory_baseline'].get(k,0):.1f}"
        lines.append(f"|{r['name']} ({r['tag']})|{r['territory_baseline_estimate']:.1f}|{r['current_vanilla']}|{r['territory_delta_estimate']:.1f}|{fmt('生产')}|{fmt('军队')}|{fmt('建设')}|{fmt('行政教育')}|")
    lines += ['','## 数据校验','',f'建筑所属国家与州归属不一致：{len(issues)}条；重复省份归属：{len(duplicate_provinces)}条。完整来源、生产方式、产权份额以及所有未削减州在full_audit.json内。']
    lines=[f'- 当前建筑地区归属失配{len(issues)}条，涉及{sum(r["levels"] for r in issues)}级，详见owner_mismatches.md。文件配置等级不等于游戏内已成功加载等级。' if line.startswith('- 文件记录总等级') else line for line in lines]
    (OUT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    all_lines=['# 全部州与全部建筑类型对照','','|州|当前国家|原版总等级|现存原版等级|模组新增|净差额|','|---|---|---:|---:|---:|---:|']
    for r in rows: all_lines.append(f"|{r['name']} ({r['state']})|{','.join(r['mod_owners'])}|{r['vanilla_levels']}|{r['mod_vanilla_levels']}|{r['mod_custom_levels']}|{r['net_vanilla_delta']:+}|")
    all_lines += ['','## 逐建筑类型','','|州|建筑|分类|原版等级|模组等级|差额|','|---|---|---|---:|---:|---:|']
    for r in details: all_lines.append(f"|{r['state_name']} ({r['state']})|{r['building_name']} ({r['building']})|{r['category']}|{r['vanilla']}|{r['mod']}|{r['delta']:+}|")
    (OUT/'all_states_and_buildings.md').write_text('\n'.join(all_lines)+'\n',encoding='utf-8')
    invalid_lines=['# 建筑州归属失配清单','','这些条目引用的region_state国家不在对应州的create_state归属内。不是普通的海外产权：region_state是建筑所在地，add_ownership才是产权。引擎是否忽略、报错或采用其他处理需要游戏日志/开局实测确认；静态统计不能把它们视为已成功落地。','','|州|实际州主|错误地区国家|建筑|等级|来源|','|---|---|---|---|---:|---|']
    for r in issues:
        owners_text='、'.join(f'{name(t)} ({t})' for t in mo.get(r['state'],{}))
        invalid_lines.append(f"|{name(r['state'])} ({r['state']})|{owners_text}|{name(r['owner'])} ({r['owner']})|{name(r['building'])}|{r['levels']}|{Path(r['file']).relative_to(ROOT).as_posix()}:{r['line']}|")
    (OUT/'owner_mismatches.md').write_text('\n'.join(invalid_lines)+'\n',encoding='utf-8')
    pop_lines=['# 人口历史地区归属失配','','只校验人口初始化中的region_state与州主是否匹配，不把脚本size当作游戏中已成功生成的人口；未计算迁移、人口增长或人口倍率。','','|州|实际州主|错误地区国家|人口size合计|来源|','|---|---|---|---:|---|']
    for r in pop_issues:
        pop_lines.append(f"|{name(r['state'])} ({r['state']})|{','.join(mo.get(r['state'],{}))}|{r['owner']}|{r['population']:,}|{Path(r['file']).relative_to(ROOT).as_posix()}:{r['line']}|")
    (OUT/'population_mismatches.md').write_text('\n'.join(pop_lines)+'\n',encoding='utf-8')
    assert summary['mod_vanilla_levels']-summary['vanilla_levels']==summary['added_vanilla_levels']-summary['removed_levels']
    assert sum(r['vanilla'] for r in details)==summary['vanilla_levels']
    assert sum(r['mod'] for r in details)==summary['mod_vanilla_levels']+summary['mod_custom_levels']
    anomalies=['# 省份归属异常','',f'原版重复记录{len(vanilla_duplicates)}条，其中归属冲突{sum(old!=new for _,old,new in vanilla_duplicates)}条；模组重复记录{len(duplicate_provinces)}条，其中归属冲突{sum(old!=new for _,old,new in duplicate_provinces)}条。新增冲突省份ID见full_audit.json，不能把原版自带冲突归因于模组。','', '同一州同一国家内的重复省份ID与跨国家／跨州冲突分开看。前者是列表重复，不能当成额外领土；后者需要确定实际归属。','','|省份ID|第一次州／国家|再次州／国家|类型|','|---|---|---|---|']
    for pid,old,new in duplicate_provinces:
        anomalies.append(f"|{pid}|{' / '.join(old)}|{' / '.join(new)}|{'列表重复' if old==new else '归属冲突'}|")
    anomalies+=['','原版有、模组归属表没有的省份ID：'+', '.join(sorted(set(global_province_old)-set(province_owner))), '', '模组新增归属省份ID：'+', '.join(sorted(set(province_owner)-set(global_province_old)))]
    (OUT/'province_anomalies.md').write_text('\n'.join(anomalies)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('Top losses:',json.dumps([(r['state'],r['removed_levels'],r['mod_owners']) for r in sorted(rows,key=lambda r:-r['removed_levels'])[:12]],ensure_ascii=False))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=OUT)
    OUT=parser.parse_args().output_dir
    main()
