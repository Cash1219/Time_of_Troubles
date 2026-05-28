import re, pathlib
files=[
r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt',
r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\game.txt',
r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\musical_instrument.txt',
r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\publisher_press.txt',
r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\kissaten.txt',
]
pat_block=re.compile(r'(?ms)^(\s*pm_[A-Za-z0-9_]+\s*=\s*\{)(.*?)(^\})')
pat_level=re.compile(r'(?ms)(level_scaled\s*=\s*\{)(.*?)(\n\s*\})')
pat_emp=re.compile(r'(building_employment_[A-Za-z_]+_add\s*=\s*)(-?\d+)(\s*)')

for fp in files:
    p=pathlib.Path(fp)
    t=p.read_text(encoding='utf-8-sig')
    def repl_block(mb):
        head,body,tail=mb.group(1),mb.group(2),mb.group(3)
        def repl_level(ml):
            lhead,lbody,ltail=ml.group(1),ml.group(2),ml.group(3)
            em=list(pat_emp.finditer(lbody))
            if not em:
                return ml.group(0)
            vals=[int(e.group(2)) for e in em]
            total=sum(vals)
            if total==5000:
                return ml.group(0)
            # keep sign pattern; if mixed signs, skip (likely delta pm)
            signs=set(1 if v>0 else -1 if v<0 else 0 for v in vals)
            if len([s for s in signs if s!=0])>1:
                return ml.group(0)
            # if all negative, normalize to -5000
            target=5000
            if all(v<=0 for v in vals):
                target=-5000
            # proportional redistribute
            if total==0:
                # equal distribution
                n=len(vals); base=target//n
                new=[base]*n; new[-1]+=target-sum(new)
            else:
                raw=[v/total*target for v in vals]
                new=[int(round(x/10.0)*10) for x in raw]
                diff=target-sum(new)
                new[-1]+=diff
            # rebuild lbody with sequential replacements
            out=[]; last=0
            for i,e in enumerate(em):
                out.append(lbody[last:e.start()])
                out.append(e.group(1)+str(new[i])+e.group(3))
                last=e.end()
            out.append(lbody[last:])
            return lhead+''.join(out)+ltail
        body2=pat_level.sub(repl_level,body)
        return head+body2+tail
    t2=pat_block.sub(repl_block,t)
    p.write_text(t2,encoding='utf-8-sig')
print('done')
