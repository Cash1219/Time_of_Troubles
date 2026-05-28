import re,glob,os,pathlib
root=pathlib.Path(r'D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT')
for fp in glob.glob(str(root/'common'/'production_methods'/'*.txt')):
    t=pathlib.Path(fp).read_text(encoding='utf-8-sig')
    for m in re.finditer(r'(?ms)^\s*(pm_[A-Za-z0-9_]+)\s*=\s*\{',t):
        name=m.group(1); i=m.end()-1; d=0; j=i
        while j<len(t):
            if t[j]=='{': d+=1
            elif t[j]=='}':
                d-=1
                if d==0:
                    b=t[i+1:j]; break
            j+=1
        emps=re.findall(r'building_employment_[A-Za-z_]+_add\s*=\s*([-0-9\.]+)',b)
        if not emps: continue
        total=sum(float(x) for x in emps)
        if abs(total) < 2000 or abs(total) > 6500:
            print(f"{os.path.basename(fp)}\t{name}\t{int(total)}")
