from pathlib import Path
p=Path(r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\common\production_methods\goods.txt")
b=p.read_bytes()
print('raw bytes sample',b[:80])
text=p.read_text(encoding='utf-8-sig',errors='ignore')
print('repr first 200:',repr(text[:200]))
