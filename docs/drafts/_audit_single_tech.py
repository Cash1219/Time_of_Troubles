import re
from pathlib import Path

M=Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT')
V=Path(r'D:\Steam\steamapps\common\Victoria 3\game')
def blocks(p):
    lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines(); out=[]; i=0
    while i<len(lines):
        m=re.match(r'^([\w-]+)\s*=\s*\{',lines[i])
        if not m: i+=1; continue
        s=i; d=0
        while i<len(lines):
            code=lines[i].split('#',1)[0]; d+=code.count('{')-code.count('}'); i+=1
            if d==0: break
        out.append((m.group(1),'\n'.join(lines[s:i]),p))
    return out
def vals(body,key):
    m=re.search(r'\b'+key+r'\s*=\s*\{([^{}]*)\}',body,re.S)
    return re.findall(r'[\w-]+',re.sub(r'#.*','',m.group(1))) if m else []
T={}
for base in (V, M):
    for p in sorted((base/'common/technology/technologies').glob('*.txt')):
        for name,body,_ in blocks(p):
            era=re.search(r'\bera\s*=\s*era_(\d)',body)
            if era:
                T[name]=(int(era.group(1)),vals(body,'unlocking_technologies'))
def ancestors(t):
    seen=set(); stack=[t]
    while stack:
        q=stack.pop()
        if q in seen or q not in T: continue
        seen.add(q); stack.extend(T[q][1])
    return seen
P={}
for p in sorted((M/'common/production_methods').glob('*.txt')):
    for name,body,path in blocks(p):
        if name.startswith('pm_'): P[name]=(vals(body,'unlocking_technologies'),path)
G=[]
for p in sorted((M/'common/production_method_groups').glob('*.txt')):
    for name,body,path in blocks(p):
        if name.startswith('pmg_'): G.append((name,[x for x in vals(body,'production_methods') if x.startswith('pm_')]))
if __name__ == '__main__':
    for group,names in G:
        mod=[x for x in names if x in P]
        multi=[(x,P[x][0]) for x in mod if len(P[x][0])>1]
        breaks=[]
        for a,b in zip(mod,mod[1:]):
            aa=P[a][0]; bb=P[b][0]
            if aa and bb and not all(t in ancestors(bb[0]) for t in aa): breaks.append((a,b,aa,bb))
            if aa and not bb: breaks.append((a,b,aa,bb))
        if multi or breaks:
            print('\n'+group)
            for x in mod: print(' ',x,','.join(P[x][0]) or '-')
            if multi: print(' MULTI',len(multi))
            if breaks: print(' BREAKS',breaks)
