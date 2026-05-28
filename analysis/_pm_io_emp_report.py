import re, pathlib
root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods')
files=['goods.txt','game.txt','musical_instrument.txt','publisher_press.txt','kissaten.txt']
for fn in files:
    t=(root/fn).read_text(encoding='utf-8-sig')
    print(f'## {fn}')
    for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t):
        n=m.group(1); i=m.end()-1; d=0; j=i
        while j<len(t):
            if t[j]=='{': d+=1
            elif t[j]=='}':
                d-=1
                if d==0: b=t[i+1:j]; break
            j+=1
        ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',b)
        outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',b)
        emps=re.findall(r'building_employment_([A-Za-z_]+)_add\s*=\s*(-?\d+)',b)
        if not ins and not outs and not emps:
            continue
        emp_total=sum(int(v) for _,v in emps)
        ins_s='; '.join([f'{g}*{v}' for g,v in ins]) if ins else '-'
        outs_s='; '.join([f'{g}*{v}' for g,v in outs]) if outs else '-'
        emp_s='; '.join([f'{k}:{v}' for k,v in emps]) if emps else '-'
        print(f'{n}\n  in: {ins_s}\n  out: {outs_s}\n  emp: {emp_s} | total={emp_total}')
    print()
