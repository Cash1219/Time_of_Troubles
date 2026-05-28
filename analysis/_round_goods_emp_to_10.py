import re,pathlib
p=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt')
t=p.read_text(encoding='utf-8-sig')

main_prefixes=('pm_goods_doll_','pm_goods_jewelry_','pm_goods_print_','pm_goods_garage_')
sub_prefixes=('pm_goods_ip_','pm_goods_selling_')

pm_iter=list(re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t))
out=[]; idx=0
for m in pm_iter:
    name=m.group(1)
    start=m.start()
    i=m.end()-1;d=0;j=i
    while j<len(t):
        if t[j]=='{': d+=1
        elif t[j]=='}':
            d-=1
            if d==0:
                end=j+1; break
        j+=1
    block=t[start:end]
    out.append(t[idx:start]); idx=end

    target=None
    if name.startswith(main_prefixes) and not name.endswith('_null'):
        target=1000
    elif name.startswith(sub_prefixes) and not name.endswith('_null'):
        target=500
    if target is None:
        out.append(block); continue

    lm=re.search(r'(?ms)(level_scaled\s*=\s*\{)(.*?)(\n\s*\})',block)
    if not lm:
        out.append(block); continue
    body=lm.group(2)
    em=list(re.finditer(r'(building_employment_[a-z_]+_add\s*=\s*)(-?\d+)(\s*)',body))
    if not em:
        out.append(block); continue
    vals=[int(e.group(2)) for e in em]
    s=sum(vals)
    if s==0:
        out.append(block); continue
    # scale then round to nearest 10
    raw=[v*target/s for v in vals]
    new=[int(round(x/10.0)*10) for x in raw]
    diff=target-sum(new)
    new[-1]+=diff
    # enforce multiples of 10 by shifting diff across last two if needed
    if new[-1] % 10 != 0 and len(new) >= 2:
        rem=new[-1] % 10
        adjust=10-rem if rem>=5 else -rem
        new[-1]+=adjust
        new[-2]-=adjust
    # rebuild
    b=[]; last=0
    for k,e in enumerate(em):
        b.append(body[last:e.start()]); b.append(e.group(1)+str(new[k])+e.group(3)); last=e.end()
    b.append(body[last:])
    new_body=''.join(b)
    block2=block[:lm.start(2)] + new_body + block[lm.end(2):]
    out.append(block2)

out.append(t[idx:])
p.write_text(''.join(out),encoding='utf-8-sig')
print('done')
