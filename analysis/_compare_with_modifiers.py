import re,pathlib
mod_root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT')
van_root=pathlib.Path(r'D:\Steam\steamapps\common\Victoria 3\game')

price={
'coffee':50,'sugar':30,'tea':50,'grain':20,'fruit':30,'meat':30,'fish':20,
'luxury_drinks':60,'luxury_foods':60,'services':30,
'clothes':30,'luxury_clothes':60,'musical_instruments':60,
'furniture':30,'tools':40,'porcelain':70,'iron':40,'coal':30,'engines':60,'electricity':30,
'groceries':30,'oil':40,'glass':40
}

def parse_blocks(text):
 d={}
 for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',text):
  n=m.group(1);i=m.end()-1;dep=0;j=i
  while j<len(text):
   c=text[j]
   if c=='{':dep+=1
   elif c=='}':
    dep-=1
    if dep==0:
      d[n]=text[i+1:j];break
   j+=1
 return d

def calc(pick,blocks):
 iv=ov=0.0
 throughput=0.0
 in_mult=0.0
 out_mult=0.0
 for n in pick:
  b=blocks[n]
  ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
  outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
  iv+=sum(price.get(g,0)*float(v) for g,v in ins)
  ov+=sum(price.get(g,0)*float(v) for g,v in outs)
  for x in re.findall(r'building_throughput_add\s*=\s*(-?[0-9\.]+)',b):
    throughput += float(x)
  for x in re.findall(r'building_goods_input_mult\s*=\s*(-?[0-9\.]+)',b):
    in_mult += float(x)
  for x in re.findall(r'building_goods_output_mult\s*=\s*(-?[0-9\.]+)',b):
    out_mult += float(x)
 # base
 net=ov-iv
 roi=net/iv*100 if iv else 0
 # with modifiers (simplified multiplicative):
 in_eff = iv * (1+throughput) * (1+in_mult)
 out_eff = ov * (1+throughput) * (1+out_mult)
 net_eff = out_eff - in_eff
 roi_eff = net_eff/in_eff*100 if in_eff else 0
 return {
  'in':iv,'out':ov,'net':net,'roi':roi,
  'throughput':throughput,'in_mult':in_mult,'out_mult':out_mult,
  'in_eff':in_eff,'out_eff':out_eff,'net_eff':net_eff,'roi_eff':roi_eff
 }

kt=(mod_root/'common/production_methods/kissaten.txt').read_text(encoding='utf-8-sig')
kb=parse_blocks(kt)
k_low=['pm_kissaten_coffee_coffee','pm_kissaten_tea_milk','pm_kissaten_sweet_biscuit','pm_kissaten_food_sandwich','pm_kissaten_server_waitress','pm_kissaten_tool_table']
k_high=['pm_kissaten_coffee_latte','pm_kissaten_tea_black_tea','pm_kissaten_sweet_pie','pm_kissaten_food_takoyaki','pm_kissaten_server_fuwafuwa','pm_kissaten_tool_flash_freezing']

vt=(van_root/'common/production_methods/01_industry.txt').read_text(encoding='utf-8-sig')
vb=parse_blocks(vt)
v_low=[x for x in ['pm_bakery','pm_disabled_canning','pm_manual_dough_processing'] if x in vb]
v_high=[x for x in ['pm_baking_powder','pm_vacuum_canning','pm_automated_bakery'] if x in vb]

res=[
 ('KISSATEN_LOW',k_low,calc(k_low,kb)),
 ('KISSATEN_HIGH',k_high,calc(k_high,kb)),
 ('FOOD_INDUSTRY_LOW',v_low,calc(v_low,vb)),
 ('FOOD_INDUSTRY_HIGH',v_high,calc(v_high,vb)),
]
for name,pick,r in res:
 print(name)
 print(' pick=',','.join(pick))
 print(f" base in={r['in']:.0f} out={r['out']:.0f} net={r['net']:.0f} roi={r['roi']:.2f}%")
 print(f" mods throughput={r['throughput']:+.2f} in_mult={r['in_mult']:+.2f} out_mult={r['out_mult']:+.2f}")
 print(f" eff  in={r['in_eff']:.0f} out={r['out_eff']:.0f} net={r['net_eff']:.0f} roi={r['roi_eff']:.2f}%")
 print()
