import re,glob,pathlib
root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT')

def read(p): return pathlib.Path(p).read_text(encoding='utf-8-sig')
# pm blocks
pm={}
for f in glob.glob(str(root/'common'/'production_methods'/'*.txt')):
 t=read(f)
 for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t):
  n=m.group(1);i=m.end()-1;d=0;j=i
  while j<len(t):
   if t[j]=='{':d+=1
   elif t[j]=='}':
    d-=1
    if d==0: b=t[i+1:j]; break
   j+=1
  vals=re.findall(r'building_employment_[A-Za-z_]+_add\s*=\s*([-0-9\.]+)',b)
  pm[n]=sum(float(v) for v in vals)
# pmg->pms
pmg={}
for f in glob.glob(str(root/'common'/'production_method_groups'/'*.txt')):
 t=read(f)
 for m in re.finditer(r'(?ms)^\s*(pmg_[A-Za-z0-9_]+)\s*=\s*\{',t):
  n=m.group(1);i=m.end()-1;d=0;j=i
  while j<len(t):
   if t[j]=='{':d+=1
   elif t[j]=='}':
    d-=1
    if d==0: b=t[i+1:j]; break
   j+=1
  mm=re.search(r'production_methods\s*=\s*\{(.*?)\}',b,re.S)
  if mm:
   p=[x for x in re.findall(r'\b(pm_[A-Za-z0-9_]+)\b',mm.group(1))]
   pmg[n]=p
# buildings
bt=read(root/'common'/'buildings'/'tot_industry.txt')
for bname in ['building_kissaten','building_musical_instrument','building_publisher','building_entertainment_press','building_game','building_goods']:
 m=re.search(rf'(?ms){bname}\s*=\s*\{{(.*?)\n\}}',bt)
 body=m.group(1)
 mm=re.search(r'production_method_groups\s*=\s*\{(.*?)\}',body,re.S)
 gs=[x for x in re.findall(r'\b(pmg_[A-Za-z0-9_]+)\b',mm.group(1))]
 low=0; high=0
 for g in gs:
  plist=pmg.get(g,[])
  if not plist: continue
  # low: first non-null if exists else first
  lowpm=None
  for p in plist:
   if '_null' not in p and '_none' not in p and 'disabled' not in p:
    lowpm=p;break
  if lowpm is None: lowpm=plist[0]
  # high: last
  highpm=plist[-1]
  low += pm.get(lowpm,0)
  high += pm.get(highpm,0)
 print(bname,'low',int(low),'high',int(high),'pmgs',len(gs))
