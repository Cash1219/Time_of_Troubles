import re
from pathlib import Path
p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
text=p.read_text(encoding='utf-8-sig',errors='ignore')
text=text.replace('\r\r\n','\n').replace('\r\n','\n').replace('\r','\n')

for key in [
    'pm_goods_doll_null',
    'pm_goods_jewelry_null',
    'pm_goods_print_null',
    'pm_goods_garage_null',
    'pm_goods_ip_null',
    'pm_goods_selling_null',
]:
    pattern=rf'({key}\s*=\s*\{{[^}}]*?texture\s*=\s*")([^"]+)(")'
    text,new_n=re.subn(pattern, rf'\1gfx/interface/icons/production_method_icons/pm_goods_goods_null.dds\3', text, count=1, flags=re.S)

# write with clean LF first then convert to CRLF bytes explicitly
out=text.replace('\n','\r\n').encode('utf-8-sig')
p.write_bytes(out)
print('updated null pm textures')
