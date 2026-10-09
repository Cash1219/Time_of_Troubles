# 二次元PM图标候选：2026-10-09

使用内置image_gen制作，未使用豆包。当前为候选，未安装DDS或替换游戏图标。完整原图、透明alpha和100像素预览均保存于本目录。

## 图标

| 用途 | 原图 | 游戏尺寸预览 |
|---|---|---|
| 摩天轮第一版（装饰较多） | ferris_v1.png | ferris_v1_100.png |
| 摩天轮第二版（简化赛璐璐） | ferris_v2.png | ferris_v2_100.png |
| 自营发行 | distribution_local.png | distribution_local_100.png |
| 批发分销 | distribution_national.png | distribution_national_100.png |
| 专业发行 | distribution_export.png | distribution_export_100.png |

## 提示词迭代

摩天轮V1要求单主体、透明背景、6—8个大吊舱、日漫器物插画、100像素可辨认、无场景或文字；实际仍出现较多金属装饰。V2沿用V1构图，定向改为浅色涂装金属、简单赛璐璐、清晰描线，去掉金色花纹、铆钉和碎高光。V2在100像素下更清楚。

三档发行采用同一人物描述：成年Q版出版工作人员、栗色中长发、橙色发饰、蓝围裙及米色衬衫，透明背景，无文字与边框。自行发书表现为抱书及书箱，批量分销表现为推车及书箱，专业协调表现为通信耳机、发货表和书箱。完整英文提示词见 `prompts.json`。

完整摩天轮V2英文编辑提示词：

> Edit target: the attached Ferris wheel icon. Make ONE targeted change: simplify its rendering into a clean Japanese anime cel-shaded game prop icon for a tiny 100-pixel UI. Preserve the same complete wheel, six red/blue gondolas, three-quarter composition and transparent background. Replace shiny ornate gold/brass framework with light ivory painted metal and subdued blue-grey shadows. Remove ornamental sun on hub, small rivets, golden trim, excessive internal bars and fussy reflective lines. Use clear thick dark brown-blue outlines and only two or three shading tones per surface; gondolas should be broad readable red and blue shapes with a simple window. Keep coherent wheel and support-leg geometry. Anime scene prop, not photorealism or 3D rendering. Clean continuous antialiased cutout edges with no colored speckling, no glow, no stray pixels. Fit entire subject inside image with 8 percent transparent margin, no cropping. No added people, text, badges, scenery, floor or shadows outside subject. True alpha transparency.

## QA

五张图均为1254×1254 RGBA，alpha范围0—255。100像素预览经过重采样，仅供小尺寸检视，不修改主体内容。第二版摩天轮可辨认圆轮及红蓝吊舱；发行三档能区分抱书、推车和耳机调度。人物图的小封面细节缩小时不再可读，后续迭代可继续减少附属物数量。

这轮只试四种缺失PM的风格，20处PMG图标引用仍待处理，不应认为全部缺失图标已经修好。
