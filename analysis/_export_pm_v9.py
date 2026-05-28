import os,re,glob
from openpyxl import Workbook
root=r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT"

def read(path):
    try:
        with open(path,'r',encoding='utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path,'r',encoding='utf-8') as f:
            return f.read()

loc={}
for y in glob.glob(os.path.join(root,'localization','simp_chinese','replace','*.yml')):
    txt=read(y)
    for line in txt.splitlines():
        s=line.strip()
        if (not s) or s.startswith('#') or s.startswith('l_simp_chinese:'): continue
        m=re.match(r'([A-Za-z0-9_\.\-]+)\s*:\s*"(.*)"\s*$', s)
        if m: loc[m.group(1)]=m.group(2)

van_goods={'wood':'木材','fabric':'织物','clothes':'服装','luxury_clothes':'奢侈服装','tools':'工具','iron':'铁','steel':'钢铁','coal':'煤炭','engines':'发动机','electricity':'电力','paper':'纸张','services':'服务','transportation':'运输','porcelain':'瓷器','sugar':'食糖','luxury_drinks':'奢侈饮料','coffee':'咖啡','tea':'茶叶','grain':'谷物','fish':'鱼类','meat':'肉类','fruit':'水果','wine':'葡萄酒','liquor':'烈酒','telephones':'电话','instruments':'乐器','publications':'出版物','entertainment_publications':'娱乐出版物','furniture':'家具','glass':'玻璃','rubber':'橡胶','dye':'染料','gold':'黄金','lead':'铅','oil':'石油'}
good_alias={'magictools':'魔法工具','magic_mineral':'魔法矿物','magic_energy':'魔能','magic_steels':'魔钢','omocha':'玩具'}
price={'wood':20,'fabric':30,'clothes':30,'luxury_clothes':60,'tools':40,'iron':40,'steel':50,'coal':30,'engines':60,'electricity':30,'paper':30,'services':30,'transportation':30,'porcelain':70,'sugar':30,'luxury_drinks':60,'coffee':50,'tea':40,'grain':20,'fish':30,'meat':40,'fruit':30,'wine':50,'liquor':40,'telephones':60,'instruments':60,'publications':50,'entertainment_publications':65,'furniture':30,'glass':40,'rubber':50,'dye':35,'gold':80,'lead':35,'oil':40,'magictools':0,'magic_mineral':0,'magic_energy':0,'magic_steels':0,'omocha':0}

def disp(k): return loc.get(k,k)
def gname(g):
    if g in good_alias: return good_alias[g]
    return loc.get('goods_'+g,van_goods.get(g,g))

pm_block={}
for f in glob.glob(os.path.join(root,'common','production_methods','*.txt')):
    txt=re.sub(r'(?m)#.*$','',read(f))
    for m in re.finditer(r'(?ms)^\s*([A-Za-z0-9_]+)\s*=\s*\{',txt):
        k=m.group(1); i=m.end()-1; depth=0; j=i
        while j < len(txt):
            c=txt[j]
            if c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    pm_block[k]=txt[i+1:j]; break
            j+=1

pmg_to_pms={}
for f in glob.glob(os.path.join(root,'common','production_method_groups','*.txt')):
    txt=re.sub(r'(?m)#.*$','',read(f))
    for m in re.finditer(r'(?ms)^\s*([A-Za-z0-9_]+)\s*=\s*\{',txt):
        pmg=m.group(1); i=m.end()-1; depth=0; j=i
        while j < len(txt):
            c=txt[j]
            if c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    body=txt[i+1:j]
                    mm=re.search(r'production_methods\s*=\s*\{(.*?)\}',body,re.S)
                    if mm:
                        pmg_to_pms[pmg]=[x for x in re.findall(r'\b([A-Za-z0-9_]+)\b',mm.group(1)) if x.startswith('pm_')]
                    break
            j+=1

build_rows=[]
for f in glob.glob(os.path.join(root,'common','buildings','*.txt')):
    txt=re.sub(r'(?m)#.*$','',read(f))
    for m in re.finditer(r'(?ms)^\s*(building_[A-Za-z0-9_]+)\s*=\s*\{',txt):
        b=m.group(1); i=m.end()-1; depth=0; j=i
        while j < len(txt):
            c=txt[j]
            if c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    body=txt[i+1:j]
                    mm=re.search(r'production_method_groups\s*=\s*\{(.*?)\}',body,re.S)
                    if mm:
                        pmgs=[x for x in re.findall(r'\b([A-Za-z0-9_]+)\b',mm.group(1)) if x.startswith('pmg_')]
                        if pmgs: build_rows.append((b,pmgs))
                    break
            j+=1

rows=[]
for b,pmgs in build_rows:
    for pmg in pmgs:
        for pm in pmg_to_pms.get(pmg,[]):
            blk=pm_block.get(pm,'')
            if not blk: continue
            ins=[]; outs=[]
            for gm in re.finditer(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',blk):
                g,v=gm.group(1),float(gm.group(2))
                if abs(v)>1e-9: ins.append((g,v))
            for gm in re.finditer(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*([-0-9\.]+)',blk):
                g,v=gm.group(1),float(gm.group(2))
                if abs(v)>1e-9: outs.append((g,v))
            iv=sum(price.get(g,0)*v for g,v in ins); ov=sum(price.get(g,0)*v for g,v in outs)
            net=ov-iv; roi=(net/iv*100 if iv>0 else None)
            mods=[]
            for line in blk.splitlines():
                s=line.strip()
                if not s or s.startswith('#') or s in ('{','}'): continue
                if s.startswith(('goods_input_','goods_output_','unlocking_technologies','building_modifiers','workforce_scaled','level_scaled','unscaled','texture','is_default')): continue
                mm=re.match(r'([A-Za-z0-9_@\$!\[\]\.\:]+)\s*=\s*([-0-9\.]+)',s)
                if mm: mods.append(f"{mm.group(1)}={mm.group(2)}")
            if not (ins or outs or mods):
                continue
            in_txt='；'.join(f"{gname(g)}*{int(v) if v.is_integer() else v}" for g,v in ins)
            out_txt='；'.join(f"{gname(g)}*{int(v) if v.is_integer() else v}" for g,v in outs)
            rows.append([disp(b),disp(pmg),disp(pm),in_txt,round(iv,2),out_txt,round(ov,2),round(net,2),'' if roi is None else round(roi,2),'；'.join(mods)])

wb=Workbook(); ws=wb.active; ws.title='统计(中文修正)'
ws.append(['建筑','生产方式组','生产方式','商品投入（中文）','商品投入总价格','商品产出（中文）','商品产出总价格','商品收益净值','收益率%','生产方式修正（中文）'])
for r in rows: ws.append(r)
for c,w in {'A':18,'B':20,'C':24,'D':42,'E':16,'F':42,'G':16,'H':16,'I':12,'J':52}.items(): ws.column_dimensions[c].width=w
out=os.path.join(root,'analysis','mod_new_pm_cn_grouped_v9_中文修正更新.xlsx'); wb.save(out)
print(out); print('rows',len(rows))
