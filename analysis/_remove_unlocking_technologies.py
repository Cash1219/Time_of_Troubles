from pathlib import Path
import re

root=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods")
changed=[]

for p in root.glob('*.txt'):
    text=p.read_text(encoding='utf-8-sig',errors='ignore')
    t=text.replace('\r\n','\n').replace('\r','\n')
    lines=t.split('\n')
    out=[]
    i=0
    modified=False
    while i < len(lines):
        ln=lines[i]
        stripped=ln.lstrip()
        if ('unlocking_technologies' in ln) and (not stripped.startswith('#')):
            idx=ln.find('unlocking_technologies')
            pre=ln[:idx].rstrip()
            block_part=ln[idx:]
            depth=block_part.count('{')-block_part.count('}')
            if pre:
                out.append(pre)
            i += 1
            while i < len(lines) and depth > 0:
                depth += lines[i].count('{')-lines[i].count('}')
                i += 1
            modified=True
            continue
        out.append(ln)
        i += 1

    if modified:
        # collapse 3+ blank lines to max 2
        collapsed=[]
        b=0
        for ln in out:
            if ln.strip()=="":
                b += 1
                if b <= 2:
                    collapsed.append("")
            else:
                b=0
                collapsed.append(ln.rstrip())
        new='\n'.join(collapsed).rstrip('\n')+'\n'
        p.write_text(new.replace('\n','\r\n'), encoding='utf-8-sig')
        changed.append(str(p))

print('changed_files',len(changed))
for c in changed:
    print(c)
