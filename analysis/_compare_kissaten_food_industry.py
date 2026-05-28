import re,pathlib
mod_root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT')
van_root=pathlib.Path(r'D:\Steam\steamapps\common\Victoria 3\game')

price={
'coffee':50,'sugar':30,'tea':50,'grain':20,'fruit':30,'meat':30,'fish':20,
'luxury_drinks':60,'luxury_foods':60,'clothes':30,'luxury_clothes':60,'musical_instruments':60,
'furniture':30,'tools':40,'porcelain':70,'iron':40,'coal':30,'engines':60,'electricity':30,
'groceries':30,'oil':40
}

def parse_blocks(text,prefix):
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

def io_of(block):
 ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',block)
 outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',block)
 iv=sum(price.get(g,0)*float(v) for g,v in ins)
 ov=sum(price.get(g,0)*float(v) for g,v in outs)
 return ins,outs,iv,ov

# kissaten picks
kt=(mod_root/'common/production_methods/kissaten.txt').read_text(encoding='utf-8-sig')
kb=parse_blocks(kt,'pm_')
low_pick=['pm_kissaten_coffee_coffee','pm_kissaten_tea_milk','pm_kissaten_sweet_biscuit','pm_kissaten_food_sandwich','pm_kissaten_server_waitress','pm_kissaten_tool_table']
high_pick=['pm_kissaten_coffee_latte','pm_kissaten_tea_black_tea','pm_kissaten_sweet_pie','pm_kissaten_food_takoyaki','pm_kissaten_server_fuwafuwa','pm_kissaten_tool_flash_freezing']

def sum_pick(pick,blocks):
 tin=tout=0
 all_ins=[]; all_out=[]
 for p in pick:
  ins,outs,iv,ov=io_of(blocks[p])
  tin+=iv; tout+=ov; all_ins+=ins; all_out+=outs
 return tin,tout,tout-tin,(tout-tin)/tin*100 if tin else 0,all_ins,all_out

k_low=sum_pick(low_pick,kb)
k_high=sum_pick(high_pick,kb)

# vanilla food industries picks
it=(van_root/'common/production_methods/01_industry.txt').read_text(encoding='utf-8-sig')
ib=parse_blocks(it,'pm_')
# likely groups for food industries: primary production, canning, automation
v_low_pick=['pm_bakery','pm_disabled_canning','pm_manual_dough_processing']
v_high_pick=['pm_baking_powder','pm_vacuum_canning','pm_automated_bakery']
# guard for missing blocks
v_low_pick=[x for x in v_low_pick if x in ib]
v_high_pick=[x for x in v_high_pick if x in ib]
v_low=sum_pick(v_low_pick,ib)
v_high=sum_pick(v_high_pick,ib)

def fmt(name,res,pick):
 tin,tout,net,roi,ins,outs=res
 print(name)
 print(' pick=',','.join(pick))
 print(f' in={tin:.0f} out={tout:.0f} net={net:.0f} roi={roi:.2f}%')

fmt('KISSATEN_LOW_FULL',k_low,low_pick)
fmt('KISSATEN_HIGH_FULL',k_high,high_pick)
fmt('VANILLA_FOOD_LOW_FULL',v_low,v_low_pick)
fmt('VANILLA_FOOD_HIGH_FULL',v_high,v_high_pick)
