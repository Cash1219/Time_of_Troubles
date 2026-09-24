# 北美幻想乡迁移前基线

本文件记录将幻想乡迁往美国和加拿大以前的可回退基线。它与同次 Git 提交共同构成迁移前备份；后续重划领土、人口、建筑或角色时，应保留本文件列出的标签、历史文件和角色配置，直到逐项完成迁移或明确废止。

## 已恢复的日本

日本已恢复为原有的 `JAP` 单一国家分布。此前草拟的博丽、红魔、人里、妖怪山与守矢五国，以及对应本地化和人口、领土改动均已移除。保留 `JAP` 现有的东方角色；这次恢复不删除角色。

## 美国和加拿大的现有势力

下列是开局时在美国、加拿大州区拥有省份的标签。一个州区可由数个标签分别拥有省份，因此重复出现的州区并不表示冲突。

| 标签 | 名称 | 现有州区 |
| --- | --- | --- |
| `TGCC` | 环塔商会 | 阿拉斯加、不列颠哥伦比亚 |
| `ATB` | 原有标签 | 阿拉斯加、育空 |
| `SGXY` | 圣葛罗莉安娜女子学院 | 育空、西北地区、努纳武特、不列颠哥伦比亚、阿尔伯塔、萨斯喀彻温、马尼托巴 |
| `IRC` | 原有标签 | 阿尔伯塔、萨斯喀彻温、马尼托巴 |
| `BLF` | 原有标签 | 阿尔伯塔 |
| `BCXY` | 法属加拿大 | 安大略、魁北克、新不伦瑞克 |
| `NAVL` | 新阿瓦隆 | 纽芬兰、新不伦瑞克 |
| `USA` | 美国 | 标签和国家历史存在，但目前未持有北美州区省份 |
| `CAN` | 加拿大 | 原版标签，当前未持有北美州区省份 |
| `WULN` | 武陵 | 华盛顿、俄勒冈、爱达荷 |
| `VAIV` | 四号谷地 | 内华达、加利福尼亚 |
| `UTE` | 原有标签 | 犹他、科罗拉多 |
| `LKT` | 原有标签 | 怀俄明、蒙大拿、北达科他、南达科他、爱荷华、明尼苏达 |
| `PWN` | 原有标签 | 内布拉斯加、堪萨斯 |
| `SLOF` | 圣洛夫基金会 | 威斯康星、印第安纳、密歇根、俄亥俄、肯塔基、伊利诺伊 |
| `LOU` | 露易丝安娜 | 路易斯安那、阿肯色、密苏里、密西西比 |
| `USAF` | 美利坚联盟国 | 田纳西、阿拉巴马、佛罗里达、佐治亚、北卡罗来纳、南卡罗来纳 |
| `HHWO` | Hello Happy World | 弗吉尼亚、哥伦比亚特区、西弗吉尼亚、马里兰、特拉华、新泽西、宾夕法尼亚 |
| `NRHD` | 新罗德岛 | 纽约、康涅狄格、罗得岛、马萨诸塞、佛蒙特、新罕布什尔、缅因 |
| `SBRT` | 原有标签 | 俄克拉何马、得克萨斯、亚利桑那、新墨西哥 |

墨西哥与中美洲也已被模组势力占据：`AKXS` 持有墨西哥主要州区，`YUZ1` 持有危地马拉至巴拿马一带。它们不属于本次美国和加拿大的迁移范围，但北美重划若向南扩展，应另行备份。

## 已配置的模组角色

目前只有四组美国或加拿大势力拥有模组专属历史角色文件。其余北美标签仍可能使用原版角色或在其他系统生成角色，不能据此认定为“没有角色”。

| 国家 | 文件 | 角色与开局职务 |
| --- | --- | --- |
| `LOU` 露易丝安娜 | `common/history/characters/lou - lou.txt` | 安丽埃塔·德·托里斯汀（君主）；露易丝·瓦利埃尔（继承人）；蒙莫朗西、谢斯塔、夏洛特、丘鲁克、小鸟游六花、丹生谷森夏、凸守早苗、五月七日茴香（利益集团领袖）；七宫智音（鼓动者） |
| `NAVL` 新阿瓦隆 | `common/history/characters/navl - new avalon.txt` | 阿尔托莉雅·潘德拉贡（君主）；莫德雷德（继承人、将领）；肯尼斯、言峰绮礼、梅林、贝狄威尔、远坂时臣（利益集团领袖、将领）；远坂凛、露维亚、卫宫士郎、Archer、韦伯（利益集团领袖，其中 Archer 亦为将领） |
| `USAF` 美利坚联盟国 | `common/history/characters/usaf - saunders.txt` | 凯·桑德斯（君主、军队领袖）；直美·桑德斯、艾丽莎·桑德斯（将领） |
| `SLOF` 圣洛夫基金会 | `common/history/characters/tus - tuscany.txt` | 维尔汀、十四行诗、星锑、阿莱夫、卡卡尼亚、维拉、玛丽安娜、图图石子（利益集团领袖）；红弩箭、J（将领）；淑女格蕾丝、37（海军将领）；巴卡罗拉、APPLe、X、新巴别（普通角色） |

`SLOF` 的角色文件名仍为 `tus - tuscany.txt`，但文件内容已明确绑定 `c:SLOF`。迁移时应保留或顺手改名，避免按文件名误判归属。

## 迁移幻想乡时必须改写的设定大纲内容

设定大纲第十四版将幻想乡明确放在日本历史链中，不能只改地图说明。建议保留“日本是源头”，把“北美是幻想乡外显大陆或重建地”作为新设定层。

1. **蓝晶与古大和优势**：大纲称日本是高纯度蓝晶的重要产地，并以此解释古大和的技术优势。应保留为日本的史前根源；北美的幻想乡可改为结界汇聚、彗星碎片坠落或空间乱流造成的次生高浓度地区。
2. **阴阳寮与亚人平权**：阴阳寮设于古大和，幻想乡崛起也直接影响大和人的身体结构与法术体系。该段适合保留在日本，新增“北美分寮、结界观测站或流亡共同体”，使北美国家承接其制度与技术。
3. **幻想乡崛起与幻想神道**：现文写为大和亚人组成的法师组织和信仰。应改成先在日本形成的宗教与政治传统，后由结界事件带到北美并发展为多国共同的地方秩序；这样博丽、守矢、人里、妖怪山等势力仍保有日式来源。
4. **日本开局定位**：大纲后段仍有藤原崛起、日本贵族议会和锁国令。若 `JAP` 不再等同幻想乡，需改其国家名、军队名、角色政治职务与本地化，使其成为日本本土政权；同时把幻想乡角色和特殊内容迁给北美的新标签。
5. **北美既有殖民叙事**：罗德岛发现美洲、新罗德岛、四号谷地、武陵城、加拿大殖民地、HHW 的美洲殖民均已写入编年史。幻想乡若直接占据这些土地，必须补一段时间顺序：结界/空间乱流何时形成，谁被吸纳、迁出或转为附庸，避免与既有“罗德岛首先建立据点”的叙事冲突。
6. **政治关系与人口**：日本的 `JAP` 当前拥有州区、人口、建筑、军队和利益集团领袖脚本。迁移时必须成套调整 `common/history/states/00_states.txt`、`common/history/pops/11_east_asia.txt`、`common/history/buildings/11_east_asia.txt`、日本角色文件，以及新北美州区对应的人口和建筑历史；只改变国家定义会留下错误的所有权和开局资源。

## 迁移时需要保留的代码入口

- `common/country_definitions/tot_countries.txt`
- `common/history/states/00_states.txt`
- `common/history/pops/05_north_america.txt` 与 `common/history/pops/11_east_asia.txt`
- `common/history/buildings/05_north_america.txt` 与 `common/history/buildings/11_east_asia.txt`
- `common/history/countries/usa - usa.txt`、`common/history/countries/bcxy - bcxy.txt`、`common/history/countries/hhwo - hhwo.txt`、`common/history/countries/sbrt - sbrt.txt`、`common/history/countries/sgxy - sgxy.txt`、`common/history/countries/usaf - confederacy.txt`
- `common/history/characters/jap - japan.txt` 与 `common/history/characters/jap - touhou_2.txt`
- `common/history/characters/lou - lou.txt`、`common/history/characters/navl - new avalon.txt`、`common/history/characters/usaf - saunders.txt`、`common/history/characters/tus - tuscany.txt`
- `localization/replace/simp_chinese/common/core/tot_countries_l_simp_chinese.yml`
- `localization/replace/simp_chinese/common/military/tot_military_formations_l_simp_chinese.yml`
