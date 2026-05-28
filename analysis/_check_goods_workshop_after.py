import re, pathlib
p=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt')
t=p.read_text(encoding='utf-8-sig')
price={'wood':20,'fabric':30,'clothes':30,'tools':40,'iron':40,'glass':40,'paper':30,'dye':35,'fine_art':150,'engines':60,'electricity':30,'services':30,'transportation':30,'omocha':60}
for m in re.finditer(r'(?ms)^\s*(pm_goods_[A-Za-z0-9_]+)\s*=\s*\{',t):
    n=m.group(1); i=m.end()-1; d=0; j=i
    while j<len(t):
        if t[j]=='{': d+=1
        elif t[j]=='}':
            d-=1
            if d==0:
                b=t[i+1:j]; break
        j+=1
    ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',b)
    outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',b)
    if not ins and not outs: continue
    iv=sum(price.get(g,0)*float(v) for g,v in ins)
    ov=sum(price.get(g,0)*float(v) for g,v in outs)
    net=ov-iv
    roi=(net/iv*100) if iv else None
    print(f"{n}\tin={iv:.0f}\tout={ov:.0f}\tnet={net:.0f}\troi={'-' if roi is None else round(roi,2)}")
