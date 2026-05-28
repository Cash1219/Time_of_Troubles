import re,pathlib
mod=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt').read_text(encoding='utf-8-sig')
van=pathlib.Path(r'D:\Steam\steamapps\common\Victoria 3\game\common\production_methods\01_industry.txt').read_text(encoding='utf-8-sig')
price={
'fabric':30,'clothes':30,'iron':40,'glass':40,'tools':40,'paper':30,'dye':35,'fine_art':150,'wood':20,'engines':60,'electricity':30,
'services':30,'transportation':30,'omocha':60,
'lead':35,'coal':30,'explosives':50,'oil':40,'ceramics':40
}

def blocks(text,prefix='pm_'):
 d={}
 for m in re.finditer(r'(?ms)^\s*('+prefix+r'[A-Za-z0-9_]+)\s*=\s*\{',text):
  n=m.group(1); i=m.end()-1; dep=0; j=i
  while j<len(text):
   c=text[j]
   if c=='{': dep+=1
   elif c=='}':
    dep-=1
    if dep==0:
      d[n]=text[i+1:j]; break
   j+=1
 return d

def calc(b):
 ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
 outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
 iv=sum(price.get(g,0)*float(v) for g,v in ins)
 ov=sum(price.get(g,0)*float(v) for g,v in outs)
 net=ov-iv
 roi=(net/iv*100) if iv else None
 return iv,ov,net,roi,ins,outs

mb=blocks(mod)
vb=blocks(van)

goods_pms=[k for k in mb if k.startswith('pm_goods_') and not any(x in k for x in ['_null'])]
main_goods=[k for k in goods_pms if any(k.startswith(p) for p in ['pm_goods_doll_','pm_goods_jewelry_','pm_goods_print_','pm_goods_garage_'])]
ops_goods=[k for k in goods_pms if any(k.startswith(p) for p in ['pm_goods_ip_','pm_goods_selling_'])]

# vanilla glassworks related PM names
glass_pms=[k for k in vb if ('glass' in k or 'crystal' in k) and k.startswith('pm_')]
# keep likely production line PMs
glass_pms=[k for k in glass_pms if any(x in k for x in ['glassworks','glass','crystal'])]

def summary(name,pms,src):
 vals=[]
 for p in pms:
  iv,ov,net,roi,_,_=calc(src[p])
  if roi is None: continue
  vals.append((p,iv,ov,net,roi))
 print(name, 'count',len(vals))
 if not vals:
  return
 rois=[x[4] for x in vals]
 nets=[x[3] for x in vals]
 print(' roi_min',round(min(rois),2),'roi_max',round(max(rois),2),'roi_avg',round(sum(rois)/len(rois),2))
 print(' net_min',round(min(nets),2),'net_max',round(max(nets),2),'net_avg',round(sum(nets)/len(nets),2))
 for p,iv,ov,net,roi in sorted(vals,key=lambda x:x[4]):
  print(f'  {p}\tin={iv:.0f}\tout={ov:.0f}\tnet={net:.0f}\troi={roi:.2f}%')

summary('GOODS_MAIN',main_goods,mb)
summary('GOODS_OPS',ops_goods,mb)
summary('VANILLA_GLASSLIKE',glass_pms,vb)
