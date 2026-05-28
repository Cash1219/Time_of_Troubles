import re, pathlib
p=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt')
t=p.read_text(encoding='utf-8-sig')
price={
 'wood':20,'fabric':30,'clothes':30,'luxury_clothes':60,'tools':40,'iron':40,'steel':50,'coal':30,
 'engines':60,'electricity':30,'paper':30,'services':30,'transportation':30,'porcelain':70,'sugar':30,
 'luxury_drinks':60,'coffee':50,'tea':40,'grain':20,'fish':30,'meat':40,'fruit':30,'wine':50,'liquor':40,
 'telephones':60,'instruments':60,'publications':50,'entertainment_publications':65,'furniture':30,'glass':40,
 'rubber':50,'dye':35,'gold':80,'lead':35,'oil':40,'omocha':60,'fine_art':150
}
for m in re.finditer(r'(?ms)^\s*(pm_goods_[A-Za-z0-9_]+)\s*=\s*\{',t):
    name=m.group(1); i=m.end()-1; d=0; j=i
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
    print(f"{name}\tin={iv:.0f}\tout={ov:.0f}\tnet={net:.0f}\troi={'-' if roi is None else round(roi,2)}")
