import re,pathlib
p=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt')
t=p.read_text(encoding='utf-8-sig')
main_prefixes=('pm_goods_doll_','pm_goods_jewelry_','pm_goods_print_','pm_goods_garage_')

def adj_block(name,body):
    if not name.startswith(main_prefixes):
        return body
    if name.endswith('_null'):
        return body
    m=re.search(r'(?ms)(level_scaled\s*=\s*\{)(.*?)(\n\s*\})',body)
    if not m:
        return body
    sec=m.group(2)
    em=list(re.finditer(r'(building_employment_[a-z_]+_add\s*=\s*)(-?\d+)(\s*)',sec))
    if not em:
        return body
    vals=[int(e.group(2)) for e in em]
    s=sum(vals)
    if s==1000:
        return body
    # proportional to 1000
    new=[round(v*1000/s) for v in vals]
    diff=1000-sum(new)
    new[-1]+=diff
    out=[]; last=0
    for i,e in enumerate(em):
        out.append(sec[last:e.start()])
        out.append(e.group(1)+str(int(new[i]))+e.group(3))
        last=e.end()
    out.append(sec[last:])
    newsec=''.join(out)
    return body[:m.start(2)] + newsec + body[m.end(2):]

out=[]
idx=0
for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t):
    name=m.group(1)
    start=m.start()
    i=m.end()-1;d=0;j=i
    while j<len(t):
        c=t[j]
        if c=='{':d+=1
        elif c=='}':
            d-=1
            if d==0:
                end=j+1; break
        j+=1
    out.append(t[idx:start])
    block=t[start:end]
    head=f"{name} = {{"
    head_pos=block.find('{')
    body=block[head_pos+1:-1]
    body2=adj_block(name,body)
    out.append(block[:head_pos+1]+body2+'}')
    idx=end
out.append(t[idx:])
p.write_text(''.join(out),encoding='utf-8-sig')
print('done')
