import base64
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

sys.path.insert(0, r"C:\Users\Administrator\PycharmProjects\image")
from gpt import client


source_path = Path(r"C:\Users\ADMINI~1\AppData\Local\Temp\codex-clipboard-0c9660b0-c478-44d3-bc0f-b9cd997c7c1e.png")
output_path = Path(
    r"D:\Users\Administrator\Documents\Paradox Interactive\Victoria 3\mod\ToT\gfx\interface\icons\goods_icons\prestige_goods\tot_company_otonokisaka_kyuudoubu_prestige_good.png"
)

prompt = r"""
Use case: background-extraction
Asset type: transparent-background grand-strategy game prestige-good icon
Input image: Image 1 is the edit target.

Extract only the ornate magical bow and its arrow from Image 1. The bow is the
large white, gold, pink and blue bow on the right side, with the arrow extending
diagonally toward the upper left. Reconstruct and complete the missing upper
part of the bow where the source image is cropped by the top edge. Keep the bow
and arrow as one coherent object, centered and fully visible, with a clean readable
silhouette and polished anime game-icon rendering. Preserve the decorative gold
trim, pink jewel accents, blue details, and a small number of elegant floating
heart motifs around the bow and arrow.

The final image must have a genuinely transparent background. Remove the girl,
her hands, body, clothing, hair, all other people, all scenery, sky, clouds,
platforms, lights, sparkles, and unrelated objects. Do not include a character,
face, arm, hand, torso, building, landscape, text, logo, watermark, border, or UI.
Do not leave fragments of the original background attached to the bow. Do not
invent a second bow or a second arrow. Keep the composition icon-like, with the
complete bow and arrow filling most of a square canvas and a few hearts remaining
as isolated decorative accents.
"""

with source_path.open("rb") as image_file:
    try:
        result = client.images.edit(
            model="gpt-image-2",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
            background="transparent",
        )
    except Exception as first_error:
        image_file.seek(0)
        result = client.images.edit(
            model="gpt-image-2",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
        )
        print("透明背景参数未被接口接受，已使用提示词生成并保留返回结果：", first_error)

if not result.data or not result.data[0].b64_json:
    raise RuntimeError("图像接口没有返回 b64_json 图片数据")

image = Image.open(BytesIO(base64.b64decode(result.data[0].b64_json)))
if image.mode != "RGBA":
    image = image.convert("RGBA")
output_path.parent.mkdir(parents=True, exist_ok=True)
image.save(output_path, format="PNG", optimize=True)
print(output_path)
print(image.size, image.mode)
