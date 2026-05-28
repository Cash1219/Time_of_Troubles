import re
from pathlib import Path
root=Path(r"D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT")
pm_dir=root/'common'/'production_methods'
van_goods=Path(r"D:/Steam/steamapps/common/Victoria 3/game/common/goods/00_goods.txt")

def blocks(t):
 import re
 b={};i=0
 p=re.compile(r'(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{')
 while True:
  m=p.search(t,i)
  if not m: break
  k=m.group(1);s=m.end()-1;d=0;j=s
  while j<len(t):
   if t[j]=='{': d+=1
   elif t[j]=='}':
    d-=1
    if d==0: b[k]=t[s+1:j]; i=j+1; break
   j+=1
  else: break
 return b
costs=set()
for k,v in blocks(van_goods.read_text(encoding='utf-8-sig',errors='ignore')).items():
 if re.search(r'(?m)^\s*cost\s*=\s*',v): costs.add(k)
for f in (root/'common'/'goods').glob('*.txt'):
 for k,v in blocks(f.read_text(encoding='utf-8-sig',errors='ignore')).items():
  if re.search(r'(?m)^\s*cost\s*=\s*',v): costs.add(k)
unknown=set()
for f in pm_dir.glob('*.txt'):
 t=f.read_text(encoding='utf-8-sig',errors='ignore')
 for m in re.finditer(r'(?m)^\s*(?!#)goods_(?:input|output)_([A-Za-z0-9_]+)_add\s*=\s*([+-]?[0-9]+(?:\.[0-9]+)?)',t):
  g=m.group(1)
  if g not in costs: unknown.add(g)
print('\n'.join(sorted(unknown)))
