import re, pathlib
base=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods')

# target per PM (sum of level_scaled employment in that PM)
# tuned for "all active groups ~= 5000" per building
rules=[
    (base/'goods.txt', [
        (r'^pm_goods_(doll|jewelry|print|garage)_', 900),
        (r'^pm_goods_ip_', 700),
        (r'^pm_goods_selling_', 700),
    ]),
    (base/'game.txt', [
        (r'^pm_game_traditional_', 1600),
        (r'^pm_game_modern_', 1600),
        (r'^pm_game_business_', 1800),
    ]),
    (base/'publisher_press.txt', [
        (r'^pm_publisher_main_', 3000),
        (r'^pm_publisher_business_', 1600),
        (r'^pm_ent_press_main_', 3000),
        (r'^pm_ent_press_distribution_', 1600),
    ]),
    (base/'musical_instrument.txt', [
        (r'^pm_musical_instrument_main_', 5000),
    ]),
    (base/'kissaten.txt', [
        (r'^pm_kissaten_(coffee|tea|sweet|food)_', 800),
        (r'^pm_kissaten_server_', 800),
        # tool line is delta, keep as-is
    ]),
]

pm_pat=re.compile(r'(?ms)^(\s*)(pm_[A-Za-z0-9_]+)\s*=\s*\{(.*?)^\1\}', re.M)
level_pat=re.compile(r'(?ms)(level_scaled\s*=\s*\{)(.*?)(\n\s*\})')
emp_pat=re.compile(r'(building_employment_[A-Za-z_]+_add\s*=\s*)(-?\d+)(\s*)')

def scale_level(body,target):
    m=level_pat.search(body)
    if not m: return body
    lbody=m.group(2)
    em=list(emp_pat.finditer(lbody))
    if not em: return body
    vals=[int(e.group(2)) for e in em]
    s=sum(vals)
    if s==0: return body
    # preserve signs and relative structure
    raw=[v/s*target for v in vals]
    new=[int(round(x/10.0)*10) for x in raw]
    diff=target-sum(new)
    new[-1]+=diff
    out=[]; last=0
    for i,e in enumerate(em):
        out.append(lbody[last:e.start()])
        out.append(e.group(1)+str(new[i])+e.group(3))
        last=e.end()
    out.append(lbody[last:])
    new_lbody=''.join(out)
    return body[:m.start(2)] + new_lbody + body[m.end(2):]

for fp,rls in rules:
    t=fp.read_text(encoding='utf-8-sig')
    def repl(m):
        ind,name,body=m.group(1),m.group(2),m.group(3)
        target=None
        for pat,val in rls:
            if re.match(pat,name):
                target=val; break
        if target is None:
            return m.group(0)
        body2=scale_level(body,target)
        return f"{ind}{name} = {{{body2}{ind}}}"
    t2=pm_pat.sub(repl,t)
    fp.write_text(t2,encoding='utf-8-sig')
print('ok')
