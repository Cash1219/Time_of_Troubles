import re,glob,pathlib,os
root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods')
for fp in ['goods.txt','game.txt','musical_instrument.txt','publisher_press.txt','kissaten.txt']:
 t=(root/fp).read_text(encoding='utf-8-sig')
 for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t):
  n=m.group(1);i=m.end()-1;d=0;j=i
  while j<len(t):
   if t[j]=='{': d+=1
   elif t[j]=='}':
    d-=1
    if d==0: b=t[i+1:j]; break
   j+=1
  mm=re.search(r'(?ms)level_scaled\s*=\s*\{(.*?)\n\s*\}',b)
  if not mm: continue
  vals=[int(x) for x in re.findall(r'building_employment_[A-Za-z_]+_add\s*=\s*(-?\d+)',mm.group(1))]
  if not vals: continue
  s=sum(vals)
  if abs(s)!=5000:
   print(fp,n,s)
