"""Inspect military history overlays that can affect opening economic burdens."""
import json
from collections import Counter, defaultdict
from audit_starting_building_losses import files, owners, OUT
from building_history_config import parse_items, children, value


def read(mod=False):
    result=[]
    active={tag for parts in owners(mod).values() for tag in parts}
    for p in files('common/history/military_formations',mod):
        text=p.read_text(encoding='utf-8-sig').replace('?=', '=')
        for root in parse_items(text)[0]:
            if root[0]!='MILITARY_FORMATIONS': continue
            for country in root[1]:
                tag=country[0].removeprefix('c:')
                if not isinstance(country[1],list): continue
                for form in children(country,'create_military_formation'):
                    units=children(form,'combat_unit')+children(form,'ship')
                    result.append({'country':tag,'active':tag in active,'kind':value(form,'type'),'name':value(form,'name'),'count':sum(int(value(n,'count','0')) for n in units),'file':str(p),'line':text.count('\n',0,form[2])+1,'state_units':[{'state':value(n,'state_region'),'count':int(value(n,'count','0'))} for n in children(form,'combat_unit')]})
    return result


def main():
    vanilla, current=read(),read(True)
    counts=defaultdict(lambda: {'vanilla':Counter(),'mod_file_only':Counter(),'vanilla_retained':Counter(),'effective':Counter()})
    for r in vanilla:
        if r['active']: counts[r['country']]['vanilla'][r['kind']]+=r['count']
    for r in current:
        if not r['active']: continue
        counts[r['country']]['effective'][r['kind']]+=r['count']
        key='vanilla_retained' if 'steamapps' in r['file'] else 'mod_file_only'
        counts[r['country']][key][r['kind']]+=r['count']
    data={'countries':dict(counts),'vanilla_records':vanilla,'effective_records':current}
    (OUT/'military_history_overlay.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 军队历史叠加检查','','原版军事历史文件名与模组00_generated_formations.txt不同。按普通同名覆盖规则，原版文件仍会加载；同一个仍存在的国家可能同时执行两套create_military_formation。此处是脚本指令数量，不是已验证的实际游戏单位数；需要排除外部descriptor中的replace_path，再检查新开局。战斗单位受驻军建筑和所属州影响，不宜直接把相加值当成全部有效军队。','','|国家|原版陆军／舰船|模组文件陆军／舰船|残留原版指令陆军／舰船|合计指令陆军／舰船|','|---|---|---|---|---|']
    for tag,c in sorted(counts.items()):
        if not c['vanilla_retained'] or not c['mod_file_only']: continue
        fmt=lambda k:f"{c[k].get('army',0)}／{c[k].get('fleet',0)}"
        lines.append(f"|{tag}|{fmt('vanilla')}|{fmt('mod_file_only')}|{fmt('vanilla_retained')}|{fmt('effective')}|")
    (OUT/'military_history_overlay.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({tag:counts[tag] for tag in ('GBR','FRA')},ensure_ascii=False,indent=2))


if __name__=='__main__': main()
