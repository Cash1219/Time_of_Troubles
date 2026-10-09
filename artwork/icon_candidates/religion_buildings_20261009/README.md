# 宗教中心与缺失建筑、商品图标

生成工具：内置 image_gen；每个资产单独生成，使用真实透明背景。完整提示词见 manifest.json。

## 本批范围

- 宗教中心启用的7个PM：日常礼仪、公开讲习、宗教庆典、普通仪式、简易设施、印刷工具、现代化教堂。
- 缺少专用建筑图的5个普通建筑：宗教中心、私家庭院、酒馆、动物培育园、宠物店。
- 缺少合适专用商品图的3种商品：信仰、观赏植物、观赏动物。

观赏动物此前引用magic_animals.dds，实际是魔法书图案。本批为它单独制作图像，不覆盖旧魔法书资源。牛奶虽然借用PM路径，但图像确实是奶壶，因此保留。魔矿内容暂时搁置，其借用图标列为后续事项；本批不覆盖已经有专用图标的旧建筑。

信仰商品初版“双手＋吊坠”经用户审核后替换为博丽灵梦的御币。新透明原图位于sources/faith_gohei.png，商品及texticon均使用faith_gohei.dds。完整生成提示词与原始保存位置见faith_gohei_generation.json；初版原图保留。

宗教中心建筑随后按用户要求重做为日式神社，右下角采用同一御币的图案。原图为sources/building_religious_center_shrine.png，安装纹理为building_religious_center_shrine.dds。画面无边框、铺满方形画布；完整提示词见religious_shrine_generation.json。建筑图仅表达日漫风格，不修改宗教、PM或商品机制。

最终采用用户认可的通用幻想木石会堂，去除鸟居、注连绳及其他具体宗教建筑标志，右下角保留御币。当前安装纹理为building_religious_center_generic_hall.dds，完整原图为religious_center_generic_preview.png，提示词见generic_hall_preview_generation.json。此前神社与教堂图均作为历史候选留存，已不由宗教中心引用。

## 视觉规则

参考原版食品厂、艺术学院、种植园及模组咖啡厅、谷子工坊的构图。建筑采用完整方形场景，商品或服务的象征主体置于右下角。按用户2026-10-09纠正，建筑图片自身需要完整细铜金色圆角边框；场景铺满框内，不另加缩小主体的透明边距，框外圆角透明。PM与商品采用无边框、透明背景、单一物件组合。使用自然材质、正常比例、克制线条，避免Q版。

此前无框版遵循了用户当时的判断，现已被带框版替代。原始带框生成PNG留存于sources，无框候选仍在sources_frameless。当前使用sources_framed_v2中的图，安装纹理为_framed_v2.dds。转换时建筑直接缩放至256×256，不套用PM的透明留白流程。

## 当前带框版本

最新商品与动物培育园右下角均已按用户确认改为单只白兔。商品及texticon使用ornamental_animals_rabbit.dds，建筑使用building_tot_animal_breeding_center_framed_rabbit.dds；建筑主体、养育设施和边框保留。对应原图为ornamental_animals_rabbit.png与building_animal_garden_rabbit.png，完整提示词分别见ornamental_animals_rabbit_generation.json与rabbit_building_generation.json。以下猫鸟方案为此前候选，旧图保留。

私家庭院、酒馆、宠物店恢复此前原始带框图。宗教中心保持已认可的通用木石会堂及右下角御币，使用内置imagegen补边框。动物培育园使用内置imagegen重绘，改为紧凑养育屋、鸟舍、小围栏与兔子，右下角猫和鸟的商品标识不再占据大半画面。

完整生成提示词与输入图角色见framed_redesign_generation.json，安装检查见framed_buildings_installed.json，合成预览为framed_buildings_preview.png。DDS均为256×256 RGBA，透明仅用于框外圆角，已回读核对像素和游戏引用。旧版本保留。

## 文件与安装

- sources：完整生成PNG，保留原始透明通道。
- icons_256：等比缩放、保留透明通道的256×256 PNG。
- generated_paths.json：生成工具原始保存位置。
- installed.json：安装完成后记录游戏使用的DDS路径。
- *_preview.png：按类别制作的缩小预览。
- tools/install_religion_building_icons.py：使用项目既有RGBA DDS格式，更新PM、PMG、建筑、商品及对应texticon引用。

本批只调整图像引用，不改投入、产出、员工、科技或需求。被禁用的三个特色宗教仪式不在本批范围。
