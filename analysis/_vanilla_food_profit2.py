import re, pathlib
p=pathlib.Path(r'D:\Steam\steamapps\common\Victoria 3\game\common\production_methods\01_industry.txt')
t=p.read_text(encoding='utf-8-sig')
price={'grain':20,'sugar':30,'fish':20,'meat':30,'iron':40,'oil':40,'glass':40,'groceries':30,'liquor':30}
names=['pm_bakery','pm_sweeteners','pm_baking_powder','pm_cannery','pm_cannery_fish','pm_vacuum_canning','pm_vacuum_canning_principle_3','pm_pot_stills','pm_patent_stills']

def block(name):
 m=re.search(rf'(?m)^\s*{name}\s*=\s*\{{',t)
 if not m:return ''
 i=m.end()-1;d=0;j=i
 while j<len(t):
  c=t[j]
  if c=='{':d+=1
  elif c=='}':
   d-=1
   if d==0:return t[i+1:j]
  j+=1
 return ''

for n in names:
 b=block(n)
 ins=re.findall(r'goods_input_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
 outs=re.findall(r'goods_output_([A-Za-z0-9_]+)_add\s*=\s*(-?[0-9\.]+)',b)
 iv=sum(price.get(g,0)*float(v) for g,v in ins)
 ov=sum(price.get(g,0)*float(v) for g,v in outs)
 net=ov-iv
 roi=(net/iv*100 if iv else 0)
 cm=re.search(r'#\s*profit\s*=\s*([^\n]+)',b)
 c=cm.group(1).strip() if cm else ''
 print(f'{n}\tin={iv:.0f}\tout={ov:.0f}\tnet={net:.0f}\troi={roi:.1f}%\tcomment={c}')
