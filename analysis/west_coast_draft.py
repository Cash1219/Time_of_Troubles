"""Province-based west coast draft; --apply writes the reviewed ownership manifest."""
import collections
import json
import re
import sys
import datetime
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/Steam/steamapps/common/Victoria 3/game')
OUT = ROOT / 'docs/drafts'
HISTORY = ROOT / 'common/history/states/00_states.txt'
PROV = re.compile(r'\bx[0-9a-fA-F]{6}\b')

def close(text, start):
    depth = 0
    clean = re.sub(r'#[^\n]*', lambda m: ' ' * len(m[0]), text)
    for i in range(start, len(clean)):
        if clean[i] == '{': depth += 1
        elif clean[i] == '}':
            depth -= 1
            if depth == 0: return i + 1
    raise ValueError('Unbalanced block')

def block(text, key):
    m = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*\{', text)
    if not m: raise ValueError(key)
    return m.start(), close(text, text.index('{', m.start()))

def ownership(text):
    result = {}
    for m in re.finditer(r'(?m)^\s*s:(STATE_\w+)\s*=\s*\{', text):
        body = text[m.start():close(text, text.index('{', m.start()))]
        for c in re.finditer(r'create_state\s*=\s*\{', body):
            part = body[c.start():close(body, body.index('{', c.start()))]
            tag = re.search(r'country\s*=\s*c:(\w+)', part)[1]
            p = re.search(r'owned_provinces\s*=\s*\{([^}]+)', part)
            if p:
                for code in PROV.findall(p[1]):
                    code = code.upper().replace('X', 'x')
                    result[code] = [m[1], tag]
    return result

def make_context():
    owners = ownership(HISTORY.read_text(encoding='utf-8-sig'))
    targets = {p: v for p, v in owners.items() if v[0] in {
        'STATE_WESTERN_AUSTRALIA','STATE_NORTHERN_TERRITORY','STATE_SOUTH_AUSTRALIA',
        'STATE_QUEENSLAND','STATE_NEW_SOUTH_WALES','STATE_VICTORIA','STATE_TASMANIA',
        'STATE_NORTH_ISLAND','STATE_SOUTH_ISLAND'} or v[0].startswith('STATE_CHIREIDEN')}
    rgb = np.asarray(Image.open(GAME / 'map_data/provinces.png').convert('RGB'), dtype=np.uint32)
    arr = (rgb[:,:,0] << 16) | (rgb[:,:,1] << 8) | rgb[:,:,2]
    del rgb
    mask = np.isin(arr, [int(p[1:],16) for p in targets])
    yy,xx = np.where(mask)
    bounds = [max(0,int(xx.min())-15),max(0,int(yy.min())-15),min(arr.shape[1],int(xx.max())+16),min(arr.shape[0],int(yy.max())+16)]
    a = arr[bounds[1]:bounds[3], bounds[0]:bounds[2]]
    coords = {}
    for p in targets:
        y,x = np.where(a == int(p[1:],16))
        if len(x): coords[p] = [float(x.mean()+bounds[0]),float(y.mean()+bounds[1]),len(x)]
    edges = set()
    for u,v in [(a[:,:-1],a[:,1:]),(a[:-1,:],a[1:,:])]:
        different = u != v
        for left,right in np.unique(np.stack([u[different],v[different]],axis=1),axis=0):
            edges.add(tuple(sorted(('x%06X'%left,'x%06X'%right))))
    adj = {p:[] for p in targets}
    for p,q in edges:
        if p in targets and q in targets:
            adj[p].append(q); adj[q].append(p)
    ctx = dict(owners=targets, coords=coords, adj=adj, bounds=bounds)
    (OUT/'west_coast_context.json').write_text(json.dumps(ctx),encoding='utf-8')
    return ctx,a

COLORS = {'WAS':(217,137,145),'BYKR':(205,224,232),'YKMF':(151,107,188),
          'HIGN':(150,78,117),'UKDO':(112,90,149),'RNGN':(194,179,123),
          'KYTO':(159,123,105),'CHRD':(92,193,181),'MKAI':(145,122,170),
          'MRYA':(237,211,98),'YKYM':(127,180,137),'MFSR':(172,144,190),
          'RDMK':(204,91,115),'MIST':(166,202,205),'HITO':(228,212,137),
          'HAKR':(225,130,144),'EITR':(211,188,214),'MYRN':(154,167,192),
          'MTOU':(231,233,235),'KZNH':(226,200,107),'YSSK':(130,114,151),
          'SHRM':(105,157,188),'TENG':(235,219,165)}
NAMES = dict(WAS='西澳大利亚',BYKR='白玉楼',YKMF='八云府',HIGN='彼岸',
             UKDO='后户之国',RNGN='灵长园',KYTO='旧都',CHRD='地灵殿',MKAI='魔界',
             MRYA='守矢',YKYM='妖怪之山',MFSR='魔法森林',RDMK='红魔馆',MIST='雾之湖',
             HITO='人间之里',HAKR='博丽',EITR='永远亭',MYRN='命莲寺',MTOU='月都',
             KZNH='太阳花田',YSSK='夜雀食堂',SHRM='神灵庙',TENG='天界')

def render(ctx,a,owners,name,grid=False):
    b=list(ctx['bounds'])
    if b[0]<6400:
        a=a[:,6400-b[0]:]; b[0]=6400
    rgb = np.full((*a.shape,3),(57,77,87),dtype=np.uint8)
    for p,(_,tag) in owners.items(): rgb[a==int(p[1:],16)] = COLORS.get(tag,(155,155,155))
    edge = np.zeros(a.shape,bool)
    edge[:,1:] |= a[:,1:] != a[:,:-1]; edge[1:,:] |= a[1:,:] != a[:-1,:]
    rgb[edge] = (60,65,65)
    im = Image.fromarray(rgb).resize((a.shape[1]*2,a.shape[0]*2))
    d = ImageDraw.Draw(im); font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
    if grid:
        for x in range((b[0]//50+1)*50,b[2],50):
            px=(x-b[0])*2; d.line((px,0,px,im.height),fill=(120,130,130)); d.text((px+2,10),str(x),font=font,fill='white')
        for y in range((b[1]//50+1)*50,b[3],50):
            py=(y-b[1])*2; d.line((0,py,im.width,py),fill=(120,130,130)); d.text((5,py),str(y),font=font,fill='white')
    for tag in sorted(set(v[1] for v in owners.values())):
        ps=[p for p,v in owners.items() if v[1]==tag and p in ctx['coords']]
        x=sum(ctx['coords'][p][0]*ctx['coords'][p][2] for p in ps)/sum(ctx['coords'][p][2] for p in ps)
        y=sum(ctx['coords'][p][1]*ctx['coords'][p][2] for p in ps)/sum(ctx['coords'][p][2] for p in ps)
        d.text(((x-b[0])*2,(y-b[1])*2),NAMES.get(tag,tag),font=font,fill='black',stroke_width=1,stroke_fill='white')
    im.save(OUT/name)

def components(ps, adj):
    left=set(ps); groups=[]
    while left:
        seed=min(left); todo=[seed]; left.remove(seed); group=[]
        while todo:
            p=todo.pop(); group.append(p)
            for q in adj[p]:
                if q in left: left.remove(q); todo.append(q)
        groups.append(group)
    return sorted(groups,key=len,reverse=True)

def draft(ctx):
    owners={p:list(v) for p,v in ctx['owners'].items()}
    wa={p for p,v in owners.items() if v[0]=='STATE_WESTERN_AUSTRALIA'}
    # Hand-selected map bands in original province-map coordinates. No nearest-capital partition.
    for p in wa:
        state,tag=owners[p]; x,y,_=ctx['coords'][p]
        if tag not in ('WAS','HIGN'): continue
        if x < 6760 and 2750 <= y < 2830: owners[p][1]='YKMF'
        elif y >= 2800: owners[p][1]='BYKR'
        elif y >= 2690: owners[p][1]='HIGN'
    # Mainland provinces must form one connected territory for each moved country.
    mainland=set(components(wa,ctx['adj'])[0])
    for tag in ('BYKR','HIGN','YKMF','WAS'):
        groups=components([p for p in mainland if owners[p][1]==tag],ctx['adj'])
        if len(groups)>1:
            print('REVIEW DISCONNECTED',tag,[(len(g),g) for g in groups[1:]])
    for p in owners:
        if owners[p][0]=='STATE_NORTH_ISLAND': owners[p][1]='SHRM'
        elif owners[p][0]=='STATE_SOUTH_ISLAND': owners[p][1]='TENG'
    (OUT/'west_coast_ownership_v1.json').write_text(json.dumps({p:owners[p][1] for p in sorted(owners) if owners[p]!=ctx['owners'][p]},indent=2),encoding='utf-8')
    rgb=np.asarray(Image.open(GAME/'map_data/provinces.png').convert('RGB').crop(tuple(ctx['bounds'])),dtype=np.uint32)
    pixels=(rgb[:,:,0]<<16)|(rgb[:,:,1]<<8)|rgb[:,:,2]
    render(ctx,pixels,owners,'west_coast_draft_full.png')
    im=Image.open(OUT/'west_coast_draft_full.png'); b=list(ctx['bounds']); b[0]=max(6400,b[0])
    im.crop(((6580-b[0])*2,(2400-b[1])*2,(7140-b[0])*2,(2980-b[1])*2)).save(OUT/'west_coast_draft_detail.png')
    print('Draft WA counts',dict(collections.Counter(owners[p][1] for p in wa)))
    for tag in ('BYKR','YKMF','HIGN'):
        ns={owners[q][1] for p in wa if owners[p][1]==tag for q in ctx['adj'][p] if owners[q][1]!=tag}
        print(tag,'neighbors',sorted(ns))
    return owners

def replace_block(text,key,new):
    s,e=block(text,key)
    return text[:s]+'\n'+new+text[e:]

def region_bodies(text):
    result=[]
    for m in re.finditer(r'region_state:(\w+)\s*=\s*\{',text):
        start=text.index('{',m.start()); end=close(text,start)
        result.append((m[1],text[start+1:end-1]))
    return result

def indent_block(text):
    depth=1; lines=[]
    for line in text.splitlines():
        line=line.strip()
        if not line: continue
        leading=1 if line.startswith('}') else 0
        lines.append('\t'*(depth-leading)+line)
        depth+=line.count('{')-line.count('}')
    assert depth==1
    return '\n'.join(lines)+'\n'

def apply(ctx):
    manifest=json.loads((OUT/'west_coast_ownership_v1.json').read_text(encoding='utf-8'))
    files=['common/history/states/00_states.txt','common/country_definitions/tot_countries.txt',
           'common/history/countries/tot_gensokyo_australasia.txt',
           'localization/replace/simp_chinese/common/core/tot_countries_l_simp_chinese.yml',
           'common/history/pops/13_australasia.txt','common/history/buildings/13_australasia.txt']
    originals={name:(ROOT/name).read_bytes() for name in files}
    texts={name:data.decode('utf-8-sig') for name,data in originals.items()}
    before=ownership(texts[files[0]])
    for p,tag in manifest.items():
        assert before[p]==ctx['owners'][p], 'Draft became stale: '+p
    after={p:list(v) for p,v in before.items()}
    for p,tag in manifest.items(): after[p][1]=tag
    targets=['STATE_WESTERN_AUSTRALIA','STATE_NORTH_ISLAND','STATE_SOUTH_ISLAND']
    wa={p for p,v in after.items() if v[0]==targets[0]}
    mainland=set(components(wa,ctx['adj'])[0])
    for tag in ('BYKR','YKMF','HIGN','WAS'):
        assert len(components([p for p in mainland if after[p][1]==tag],ctx['adj']))==1, tag+' fragmented'
    for tag in ('BYKR','YKMF'):
        assert all(v[0]==targets[0] for v in after.values() if v[1]==tag), 'Old territory remains'
    for state in targets:
        s,e=block(texts[files[0]],'s:'+state); original=texts[files[0]][s:e]
        groups=collections.defaultdict(list)
        for p,(st,tag) in after.items():
            if st==state: groups[tag].append(p)
        content='s:'+state+' = {\n'
        for tag,ps in sorted(groups.items()):
            content+='\tcreate_state = {\n\t\tcountry = c:'+tag+'\n\t\towned_provinces = {\n'
            ps=sorted(ps)
            content+=''.join('\t\t\t'+' '.join(ps[i:i+12])+'\n' for i in range(0,len(ps),12))
            content+='\t\t}\n\t}\n'
        content+='\n'+''.join('\t'+line.strip()+'\n' for line in original.splitlines() if 'add_homeland' in line)
        if state==targets[0]: content+='\tadd_claim = c:WAS\n'
        content+='}\n'
        texts[files[0]]=replace_block(texts[files[0]],'s:'+state,content)
    for tag,capital in [('BYKR',targets[0]),('YKMF',targets[0]),('TENG',targets[2])]:
        s,e=block(texts[files[1]],tag)
        new=re.sub(r'capital\s*=\s*STATE_\w+','capital = '+capital,texts[files[1]][s:e])
        texts[files[1]]=texts[files[1]][:s]+new+texts[files[1]][e:]
    assert not re.search(r'(?m)^SHRM\s*=',texts[files[1]])
    texts[files[1]]+='\nSHRM = { # 神灵庙：新西兰北岛\n\tcolor = { 105 157 188 }\n\tcountry_type = unrecognized\n\ttier = principality\n\treligion = shinto\n\tcultures = { japanese }\n\tcapital = STATE_NORTH_ISLAND\n}\n'
    i=texts[files[2]].rfind('}')
    texts[files[2]]=texts[files[2]][:i]+'\tc:SHRM ?= {\n\t\teffect_starting_technology_tier_2_tech = yes\n\t\teffect_starting_politics_conservative = yes\n\t\tset_tax_level = medium\n\t}\n'+texts[files[2]][i:]
    texts[files[3]]+='\n SHRM: "神灵庙"\n SHRM_ADJ: "神灵庙"\n'
    # Keep the existing population totals and cultures. Rehome the affected region scopes.
    population_totals={}
    for state in targets:
        s,e=block(texts[files[4]],'s:'+state)
        body=re.sub(r'#[^\n]*','',texts[files[4]][s:e])
        pops=[]
        for m in re.finditer(r'create_pop\s*=\s*\{',body):
            start=body.index('{',m.start()); pops.append(body[m.start():close(body,start)])
        counts=collections.Counter(v[1] for v in after.values() if v[0]==state)
        total=sum(counts.values()); tags=sorted(counts)
        bytag=collections.defaultdict(list)
        population_totals[state]=sum(int(re.search(r'\bsize\s*=\s*(\d+)',p)[1]) for p in pops)
        for pop in pops:
            n=int(re.search(r'\bsize\s*=\s*(\d+)',pop)[1]); sizes={t:n*counts[t]//total for t in tags}
            for t in sorted(tags,key=lambda t: (-(n*counts[t]%total),t))[:n-sum(sizes.values())]: sizes[t]+=1
            for t in tags:
                if sizes[t]: bytag[t].append(re.sub(r'\bsize\s*=\s*\d+','size = '+str(sizes[t]),pop))
        new='\ts:'+state+' = {\n'+''.join('\t\tregion_state:'+t+' = {\n'+'\n'.join(bytag[t])+'\n\t\t}\n' for t in tags)+'\t}\n'
        texts[files[4]]=replace_block(texts[files[4]],'s:'+state,indent_block(new))
    # Existing western buildings remain with WAS, which still owns land in this state.
    # NZ keeps its existing buildings; merge scopes and reassign ownership to the successor.
    for state,tag in [(targets[1],'SHRM'),(targets[2],'TENG')]:
        s,e=block(texts[files[5]],'s:'+state)
        content='\n'.join(body for _,body in region_bodies(texts[files[5]][s:e]))
        content=re.sub(r'c:(UNT|NSW|NTO|NTU)\b','c:'+tag,content)
        new='\ts:'+state+' = {\n\t\tregion_state:'+tag+' = {\n'+content+'\n\t\t}\n\t}\n'
        texts[files[5]]=replace_block(texts[files[5]],'s:'+state,indent_block(new))
    assert ownership(texts[files[0]])==after
    for state in targets:
        s,e=block(texts[files[4]],'s:'+state)
        assert sum(map(int,re.findall(r'\bsize\s*=\s*(\d+)',texts[files[4]][s:e])))==population_totals[state]
        valid={v[1] for v in after.values() if v[0]==state}
        assert set(t for t,_ in region_bodies(texts[files[4]][s:e]))<=valid
    # Validate exact province coverage against the active state-region definitions.
    vanilla=(GAME/'map_data/state_regions/13_australasia.txt').read_text(encoding='utf-8-sig')
    regional=(ROOT/'map_data/state_regions/tot_13_australasia_chireiden.txt').read_text(encoding='utf-8-sig')
    for state in targets:
        source=regional if state==targets[0] else vanilla
        s,e=block(source,state)
        defined={p.upper().replace('X','x') for p in PROV.findall(re.search(r'\bprovinces\s*=\s*\{([^}]+)',source[s:e])[1])}
        assert defined=={p for p,v in after.items() if v[0]==state}, 'Province coverage '+state
    for name in files:
        clean=re.sub(r'#[^\n]*','',texts[name])
        assert clean.count('{')==clean.count('}'), name
    backup=ROOT/'docs/backups'/('west_coast_before_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    for name in files:
        dest=backup/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(originals[name])
        original=originals[name]
        text=texts[name].replace('\r\n','\n')
        if b'\r\n' in original: text=text.replace('\n','\r\n')
        (ROOT/name).write_bytes((b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8'))
    report={'backup':str(backup),'changed_provinces':len(manifest),'western_australia_before':281,
            'western_australia_after':sum(v[1]=='WAS' for v in after.values() if v[0]==targets[0]),
            'western_country_counts':dict(collections.Counter(v[1] for v in after.values() if v[0]==targets[0])),
            'population_totals_preserved':population_totals,'mainland_connectivity':'passed',
            'state_province_coverage':'passed','game_launch':'not tested'}
    (OUT/'west_coast_validation_v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply(json.loads((OUT/'west_coast_context.json').read_text(encoding='utf-8')))
        sys.exit(0)
    if '--draft' in sys.argv:
        draft(json.loads((OUT/'west_coast_context.json').read_text(encoding='utf-8')))
        sys.exit(0)
    ctx,a=make_context()
    render(ctx,a,ctx['owners'],'west_coast_before_grid.png',True)
    wa=[p for p,v in ctx['owners'].items() if v[0]=='STATE_WESTERN_AUSTRALIA']
    print('Bounds',ctx['bounds'])
    print('WA owners',dict(collections.Counter(ctx['owners'][p][1] for p in wa)))
    for tag in ('HIGN','UKDO','RNGN','KYTO'):
        ps=[p for p in wa if ctx['owners'][p][1]==tag]
        print(tag,[(round(ctx['coords'][p][0]),round(ctx['coords'][p][1])) for p in ps][::5])
