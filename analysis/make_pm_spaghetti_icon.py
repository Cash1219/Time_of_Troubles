from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path
import struct, math

src = Path(r'Y:/v3mod/素材/意大利面.png')
mod_root = Path(r'D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/mod/ToT')
out_dir = mod_root / 'gfx/interface/icons/production_method_icons'
out_dir.mkdir(parents=True, exist_ok=True)
preview_dir = mod_root / 'analysis/icon_previews'
preview_dir.mkdir(parents=True, exist_ok=True)

img = Image.open(src).convert('RGBA')
w, h = img.size
side = min(w, h)
left = (w - side) // 2
upper = max(0, (h - side) // 2 - int(side * 0.015))
img = img.crop((left, upper, left + side, upper + side))

work = img.resize((416, 416), Image.Resampling.LANCZOS)
base = work.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SMOOTH_MORE)
base = ImageEnhance.Color(base).enhance(0.68)
base = ImageEnhance.Contrast(base).enhance(0.95)
base = ImageEnhance.Brightness(base).enhance(0.88)

r, g, b, a = base.split()
r = ImageEnhance.Brightness(r).enhance(1.08)
g = ImageEnhance.Brightness(g).enhance(0.97)
b = ImageEnhance.Brightness(b).enhance(0.76)
base = Image.merge('RGBA', (r, g, b, a))

# Add a soft painted paper tint and vignette, closer to vanilla production icons.
overlay = Image.new('RGBA', (416, 416), (92, 62, 28, 0))
base = Image.alpha_composite(base, overlay)
noise = Image.effect_noise((416, 416), 15).convert('L')
noise_rgba = Image.merge('RGBA', (noise, noise, noise, Image.new('L', (416, 416), 26)))
base = Image.alpha_composite(base, noise_rgba)

mask = Image.new('L', (416,416), 0)
for y in range(416):
    for x in range(416):
        dx = (x - 207.5) / 207.5
        dy = (y - 207.5) / 207.5
        d = min(1.0, math.sqrt(dx*dx + dy*dy))
        val = int(max(0, (d - 0.56) / 0.44) * 120)
        mask.putpixel((x,y), val)
vig = Image.new('RGBA', (416,416), (36, 27, 18, 255))
base = Image.composite(vig, base, mask)
base = base.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120, threshold=5))

for size in (208, 104):
    icon = base.resize((size, size), Image.Resampling.LANCZOS)
    icon.save(preview_dir / f'pm_spaghetti_vic3_{size}.png')

def write_dds_from_template(template_path, out_path, image, size, mip_count):
    header = bytearray(Path(template_path).read_bytes()[:128])
    struct.pack_into('<I', header, 12, size)
    struct.pack_into('<I', header, 16, size)
    struct.pack_into('<I', header, 20, size * 4)
    struct.pack_into('<I', header, 28, mip_count)
    payload = bytearray()
    cur = image.resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    for idx in range(mip_count):
        payload.extend(cur.tobytes('raw', 'BGRA'))
        if idx != mip_count - 1:
            cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.Resampling.LANCZOS)
    Path(out_path).write_bytes(bytes(header) + bytes(payload))

vanilla = Path(r'D:/Steam/steamapps/common/Victoria 3/game/gfx/interface/icons/production_method_icons')
write_dds_from_template(vanilla / 'bakeries.dds', out_dir / 'pm_spaghetti_vic3.dds', base, 104, 7)
write_dds_from_template(vanilla / 'aeroplanes.dds', out_dir / 'pm_spaghetti_vic3_208.dds', base, 208, 8)

print(preview_dir / 'pm_spaghetti_vic3_104.png')
print(preview_dir / 'pm_spaghetti_vic3_208.png')
print(out_dir / 'pm_spaghetti_vic3.dds')
print(out_dir / 'pm_spaghetti_vic3_208.dds')
