import re
from pathlib import Path
p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig', errors='ignore')
text=text.replace('\r\r\n','\n').replace('\r\n','\n').replace('\r','\n')
# Collapse any 2+ blank lines to exactly one blank line
text=re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+','\n\n',text)
# Trim leading/trailing blank lines
text=text.strip('\n')+'\n'
# Write CRLF
p.write_text(text.replace('\n','\r\n'), encoding='utf-8-sig')
print('collapsed blank lines')
