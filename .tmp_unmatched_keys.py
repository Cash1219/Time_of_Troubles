import re
from pathlib import Path
from collections import defaultdict
root=Path(r"D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT")
van=Path(r"D:/Steam/steamapps/common/Victoria 3/game")

def iterf(d):
    for p in d.rglob('*'):
        if p.is_file(): yield p

def blocks(t):
    b={};i=0;pat=re.compile(r'(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{');n=len(t)
    while True:
      m=pat.search(t,i)
      if not m: break
      k=m.group(1);s=m.end()-1;d=0;j=s
      while j<n:
        if t[j]=='{': d+=1
        elif t[j]=='}':
          d-=1
          if d==0: b[k]=t[s+1:j]; i=j+1; break
        j+=1
      else: break
    return b

def load(d):
    o={}
    for f in iterf(d): o.update(blocks(f.read_text(encoding='utf-8-sig',errors='ignore')))
    return o
pm_v=load(van/'common'/'production_methods'); pm_m=load(root/'common'/'production_methods')
pmg=load(van/'common'/'production_method_groups'); pmg.update(load(root/'common'/'production_method_groups'))
bld=load(van/'common'/'buildings'); bld.update(load(root/'common'/'buildings'))
new=[k for k in pm_m if k not in pm_v]
pm_to_pmg=defaultdict(set)
for g,body in pmg.items():
 m=re.search(r'(?ms)production_methods\s*=\s*\{(.*?)\}',body)
 if not m: continue
 for ln in m.group(1).splitlines():
  s=ln.strip()
  if not s or s.startswith('#'): continue
  s=s.split('#',1)[0].strip()
  if re.match(r'^[A-Za-z0-9_]+$',s): pm_to_pmg[s].add(g)
pmg_to_bld=defaultdict(set)
for b,body in bld.items():
 m=re.search(r'(?ms)production_method_groups\s*=\s*\{(.*?)\}',body)
 if not m: continue
 for ln in m.group(1).splitlines():
  s=ln.strip();
  if not s or s.startswith('#'): continue
  s=s.split('#',1)[0].strip()
  if re.match(r'^[A-Za-z0-9_]+$',s): pmg_to_bld[s].add(b)

un=[]
for pm in sorted(new):
 gs=pm_to_pmg.get(pm)
 if not gs:
  un.append((pm,'NO_PMG',''))
 else:
  for g in gs:
   if not pmg_to_bld.get(g): un.append((pm,g,'NO_BUILDING'))
print('unmatched_count',len(un))
for x in un: print(x)
