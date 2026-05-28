from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageDraw
from pathlib import Path
import struct, math, random

src = Path(r'Y:/v3mod/素材/意大利面.png')
mod_root = Path(r'D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT')
out_dir = mod_root / 'gfx/interface/icons/production_method_icons'
out_dir.mkdir(parents=True, exist_ok=True)
preview_dir = mod_root / 'analysis/icon_previews'
preview_dir.mkdir(parents=True, exist_ok=True)

img = Image.open(src).convert('RGBA')

# crop to remove watermark and keep plate centered
w, h = img.size
crop = img.crop((120, 40, w-170, h-190))
side = min(crop.width, crop.height)
crop = crop.crop(((crop.width-side)//2, (crop.height-side)//2, (crop.width+side)//2, (crop.height+side)//2))

# Work at large resolution then downsample
work = crop.resize((832, 832), Image.Resampling.LANCZOS)

# Build painterly base: flatten detail + directional brush-like blur mix
flat = work.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.1))
edge = work.filter(ImageFilter.FIND_EDGES).convert('L')
edge = ImageOps.invert(edge).filter(ImageFilter.GaussianBlur(0.8))
edge = ImageEnhance.Contrast(edge).enhance(1.8)
flat = Image.composite(flat, work, edge)

# Tone map toward Victoria-like subdued warm palette
flat = ImageEnhance.Color(flat).enhance(0.46)
flat = ImageEnhance.Contrast(flat).enhance(1.08)
flat = ImageEnhance.Brightness(flat).enhance(0.78)

r, g, b, a = flat.split()
r = ImageEnhance.Brightness(r).enhance(1.10)
g = ImageEnhance.Brightness(g).enhance(0.93)
b = ImageEnhance.Brightness(b).enhance(0.70)
base = Image.merge('RGBA', (r, g, b, a))

# subtle sepia glaze
sepia = Image.new('RGBA', base.size, (114, 84, 46, 70))
base = Image.alpha_composite(base, sepia)

# Add canvas grain
rnd = random.Random(7)
noise = Image.new('L', base.size)
np = noise.load()
for y in range(base.height):
    for x in range(base.width):
        np[x,y] = int(120 + rnd.randint(-24,24))
noise = noise.filter(ImageFilter.GaussianBlur(0.4))
tex = Image.merge('RGBA', (noise, noise, noise, Image.new('L', base.size, 34)))
base = Image.alpha_composite(base, tex)

# paint-like dodge highlights on plate center for depth
hl = Image.new('RGBA', base.size, (0,0,0,0))
dr = ImageDraw.Draw(hl)
for rad, alpha in [(320,28),(255,22),(190,16)]:
    dr.ellipse((416-rad,416-rad,416+rad,416+rad), fill=(255,240,210,alpha))
base = Image.alpha_composite(base, hl)

# vignette
mask = Image.new('L', base.size, 0)
mp = mask.load()
cx = cy = base.width/2
for y in range(base.height):
    for x in range(base.width):
        dx=(x-cx)/(base.width/2)
        dy=(y-cy)/(base.height/2)
        d=min(1.0, (dx*dx+dy*dy)**0.5)
        t=max(0.0,(d-0.52)/0.48)
        mp[x,y]=int(180*t*t)
shade = Image.new('RGBA', base.size, (34,24,16,255))
base = Image.composite(shade, base, mask)

# final local contrast and sharpen for icon readability
base = ImageEnhance.Contrast(base).enhance(1.09)
base = base.filter(ImageFilter.UnsharpMask(radius=1.8, percent=145, threshold=4))

for size in (208,104):
    icon = base.resize((size,size), Image.Resampling.LANCZOS)
    icon.save(preview_dir / f'pm_spaghetti_vic3_v2_{size}.png')

# Write DDS A8R8G8B8 using vanilla headers
vanilla = Path(r'D:/Steam/steamapps/common/Victoria 3/game/gfx/interface/icons/production_method_icons')

def write_dds(template, outp, image, size, mips):
    head = bytearray(template.read_bytes()[:128])
    struct.pack_into('<I', head, 12, size)
    struct.pack_into('<I', head, 16, size)
    struct.pack_into('<I', head, 20, size*4)
    struct.pack_into('<I', head, 28, mips)
    payload = bytearray()
    cur = image.resize((size,size), Image.Resampling.LANCZOS).convert('RGBA')
    for i in range(mips):
        payload.extend(cur.tobytes('raw','BGRA'))
        if i < mips-1:
            cur = cur.resize((max(1,cur.width//2), max(1,cur.height//2)), Image.Resampling.LANCZOS)
    outp.write_bytes(bytes(head)+bytes(payload))

write_dds(vanilla/'bakeries.dds', out_dir/'pm_spaghetti_vic3_v2.dds', base, 104, 7)
write_dds(vanilla/'aeroplanes.dds', out_dir/'pm_spaghetti_vic3_v2_208.dds', base, 208, 8)

print(preview_dir / 'pm_spaghetti_vic3_v2_104.png')
print(preview_dir / 'pm_spaghetti_vic3_v2_208.png')
print(out_dir / 'pm_spaghetti_vic3_v2.dds')
print(out_dir / 'pm_spaghetti_vic3_v2_208.dds')
