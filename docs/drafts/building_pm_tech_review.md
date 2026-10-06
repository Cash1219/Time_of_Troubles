# 模组建筑 PM 科技门槛逐项审核稿

> 审核稿：以下“拟定”均未写入 PM 文件。当前栏是已恢复的旧版科技设定。

> 讨论状态：电气化乐器保留旧版科技；游戏线和谷子线的拟定值只是备选，等待决定是否用新科技重排。咖啡厅配方与接待方式另见[咖啡厅与共性科技补充审核](cafe_and_shared_tech_review.md)。

> 建筑覆盖：本清单包含全部 27 个建筑定义，其中四座特殊矿井与黄金殿建设工地当前 `buildable = no`。四种魔法矿物尚无下游 PM 投入，另见[四矿接入草案](four_mineral_integration_review.md)。

> 科技方向：魔矿内容暂缓，不纳入本轮 PM 修改。专业接待业、组织化休闲娱乐和收窄后的“成套电器”仍只是共用科技候选；游戏与谷子科技候选也未定案。现有数值另见[当前 PM 基准价审核](current_pm_balance_20261004.md)。

## 审核规则

- 每个 PM 至多一个科技门槛；“无”表示开局或建筑解锁后可用。基础档和并列风格档可以无科技。
- 同组升级档若有科技，后档科技必须在原版前置树中继承前档科技；时代数字相同也可有前置顺序。
- 商品需求是另一层限制：例如电力、广播、电话商品可能晚于 PM 科技才有供应。这里逐项审核科技门槛，不改变投入产出。
- 拟定优先使用原版科技，没有提议新科技。名称后括号中保留代码 ID 便于核对。

## 建筑逐项清单

### 乐队总部（`building_band_headquarter`）

#### 饮食维护（`pmg_band_food_support`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_band_food_none`） | 无 | 无 | 保留原设定 |
| 2 | 少量点心（`pm_band_food_basic`） | 无 | 无 | 保留原设定 |
| 3 | 固定下午茶（`pm_band_food_regular`） | 无 | 无 | 保留原设定 |
| 4 | 定期聚餐（`pm_band_food_generous`） | 无 | 无 | 保留原设定 |
| 5 | 高规格庆功宴（`pm_band_food_lavish`） | 无 | 无 | 保留原设定 |

#### 娱乐维护（`pmg_band_entertainment_support`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_band_entertainment_none`） | 无 | 无 | 保留原设定 |
| 2 | 简单聚会（`pm_band_entertainment_daily`） | 无 | 无 | 保留原设定 |
| 3 | 娱乐设备（`pm_band_entertainment_routine`） | 无 | 无 | 保留原设定 |
| 4 | 定期合宿（`pm_band_entertainment_active`） | 无 | 无 | 保留原设定 |
| 5 | 常驻外地合宿（`pm_band_entertainment_immersive`） | 无 | 无 | 保留原设定 |

#### 设备维护（`pmg_band_equipment_support`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_band_equipment_none`） | 无 | 无 | 保留原设定 |
| 2 | 普通乐器（`pm_band_equipment_standard`） | 无 | 无 | 保留原设定 |
| 3 | 配件齐全（`pm_band_equipment_enhanced`） | 无 | 无 | 保留原设定 |
| 4 | 定期保养（`pm_band_equipment_maintained`） | 无 | 无 | 保留原设定 |
| 5 | 收藏级器材套组（`pm_band_equipment_professional`） | 无 | 无 | 保留原设定 |

### 私家庭园（`building_botanical_garden`）

#### 花卉培育（`pmg_botanical_garden_cultivation`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 庭园苗圃（`pm_botanical_garden_nursery`） | 无 | 无 | 保留原设定 |
| 2 | 精细花圃（`pm_botanical_garden_fine_flowerbeds`） | 集约农业（`intensive_agriculture`，E2） | 集约农业（`intensive_agriculture`，E2） | 保留原设定 |
| 3 | 玻璃花房（`pm_botanical_garden_glasshouse_flowers`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | **改良化肥（`improved_fertilizer`，E3）** | 改良肥料与温室花卉；承接精耕 |
| 4 | 珍稀温室植物（`pm_botanical_garden_rare_greenhouse`） | 发电（`electrical_generation`，E3） | **固氮（`nitrogen_fixation`，E4）** | 高投入稀有温室；固氮承接改良肥料，电力另由商品需求限制 |

#### 庭园果树（`pmg_botanical_garden_fruit_trees`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无果树（`pm_botanical_garden_fruit_trees_none`） | 无 | 无 | 保留原设定 |
| 2 | 庭院果树（`pm_botanical_garden_courtyard_fruit_trees`） | 无 | 无 | 保留原设定 |
| 3 | 嫁接果树（`pm_botanical_garden_grafted_fruit_trees`） | 集约农业（`intensive_agriculture`，E2） | 集约农业（`intensive_agriculture`，E2） | 保留原设定 |
| 4 | 温室果树（`pm_botanical_garden_greenhouse_fruit_trees`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | **改良化肥（`improved_fertilizer`，E3）** | 改良栽培；承接嫁接果树的精耕 |

### 社团（`building_club`）

#### 活动重心（`pmg_club_activity`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 日常活动（`pm_club_activity_community`） | 无 | 无 | 保留原设定 |
| 2 | 对外交流（`pm_club_activity_exchange`） | 无 | 无 | 保留原设定 |
| 3 | 组织网络（`pm_club_activity_network`） | 无 | 无 | 保留原设定 |

#### 运营方式（`pmg_club_operation`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 成员自治运营（`pm_club_operation_member_run`） | 无 | 无 | 保留原设定 |
| 2 | 顾问配属运营（`pm_club_operation_advised`） | 无 | 无 | 保留原设定 |
| 3 | 认证项目运营（`pm_club_operation_certified`） | 无 | 无 | 保留原设定 |
| 4 | 统合运营（`pm_club_operation_integrated`） | 无 | 无 | 保留原设定 |

### 河童精密发电站（`building_tot_kappa_power`）

#### 河童发电技术（`pmg_tot_kappa_power`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 河童精密发电（`pm_tot_kappa_precision_generation`） | 发电（`electrical_generation`，E3） | 发电（`electrical_generation`，E3） | 保留原设定 |

### 地灵殿核聚变设施（`building_tot_chireiden_fusion`）

#### 地底核聚变技术（`pmg_tot_chireiden_fusion`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 八咫乌核聚变（`pm_tot_chireiden_fusion_generation`） | 发电（`electrical_generation`，E3） | 发电（`electrical_generation`，E3） | 保留原设定 |

### 金色大厅基础修缮合同（`building_tot_golden_hall_small_contract`）

#### pmg_base_building_tot_golden_hall_small_contract（`pmg_base_building_tot_golden_hall_small_contract`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 基础修缮（`pm_default_building_tot_golden_hall_small_contract`） | 无 | 无 | 保留原设定 |

### 金色大厅舞台扩建合同（`building_tot_golden_hall_large_contract`）

#### pmg_base_building_tot_golden_hall_large_contract（`pmg_base_building_tot_golden_hall_large_contract`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 舞台扩建（`pm_default_building_tot_golden_hall_large_contract`） | 无 | 无 | 保留原设定 |

### 金色大厅冠名重建合同（`building_tot_golden_hall_naming_contract`）

#### pmg_base_building_tot_golden_hall_naming_contract（`pmg_base_building_tot_golden_hall_naming_contract`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 冠名重建（`pm_default_building_tot_golden_hall_naming_contract`） | 无 | 无 | 保留原设定 |

### 维也纳金色大厅施工现场（`building_tot_golden_hall_construction_site`）

#### pmg_base_building_tot_golden_hall_construction_site（`pmg_base_building_tot_golden_hall_construction_site`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 施工现场（`pm_default_building_tot_golden_hall_construction_site`） | 无 | 无 | 保留原设定 |

### 粮仓（`building_barn`）

#### 粮仓设施（`pmg_base_building_barn`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 木框架粮仓（`pm_wooden_barn`） | 无 | 无 | 保留原设定 |
| 2 | 铁框架粮仓（`pm_iron_barn`） | 无 | 无 | 保留原设定 |
| 3 | 钢框架粮仓（`pm_stell_barn`） | 无 | 无 | 保留原设定 |

#### 主要作用（`pmg_distribution_building_barn`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 调控粮价（`pm_market_barn`） | 无 | 无 | 保留原设定 |
| 2 | 救济赈灾（`pm_relief_barn`） | 无 | 无 | 保留原设定 |
| 3 | 运输粮道（`pm_transport_barn`） | 无 | 无 | 保留原设定 |

#### 管理人员（`pmg_manage_building_barn`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 委托私人（`pm_shopkeeper_barn`） | 无 | 无 | 保留原设定 |
| 2 | 庄园和教堂（`pm_noble_barn`） | 无 | 无 | 保留原设定 |
| 3 | 官方监粮官（`pm_bureaucrat_barn`） | 无 | 无 | 保留原设定 |

### 咖啡厅（`building_kissaten`）

#### 咖啡菜单（`pmg_kissaten_coffee`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_kissaten_coffee_null`） | 无 | 无 | 保留原设定 |
| 2 | 标准咖啡（`pm_kissaten_coffee_coffee`） | 无 | 无 | 保留原设定 |
| 3 | 摩卡咖啡（`pm_kissaten_coffee_mocha`） | 无 | 无 | 保留原设定 |
| 4 | 拿铁咖啡（`pm_kissaten_coffee_latte`） | 无 | 无 | 保留原设定 |

#### 饮料菜单（`pmg_kissaten_tea`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_kissaten_tea_null`） | 无 | 无 | 保留原设定 |
| 2 | 牛奶（`pm_kissaten_tea_milk`） | 无 | 无 | 保留原设定 |
| 3 | 可可（`pm_kissaten_tea_cocoa`） | 无 | 无 | 保留原设定 |
| 4 | 红茶（`pm_kissaten_tea_black_tea`） | 无 | 无 | 保留原设定 |

#### 甜点菜单（`pmg_kissaten_sweet`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_kissaten_sweet_null`） | 无 | 无 | 保留原设定 |
| 2 | 饼干（`pm_kissaten_sweet_biscuit`） | 无 | 无 | 保留原设定 |
| 3 | 可丽饼（`pm_kissaten_sweet_pancake`） | 无 | 无 | 保留原设定 |
| 4 | 蛋糕（`pm_kissaten_sweet_cake`） | 无 | 无 | 保留原设定 |
| 5 | 苹果派（`pm_kissaten_sweet_pie`） | 无 | 无 | 保留原设定 |

#### 主食菜单（`pmg_kissaten_food`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_kissaten_food_null`） | 无 | 无 | 保留原设定 |
| 2 | 三明治（`pm_kissaten_food_sandwich`） | 无 | 无 | 保留原设定 |
| 3 | 意大利面（`pm_kissaten_food_pasta`） | 无 | 无 | 保留原设定 |
| 4 | 蛋包饭（`pm_kissaten_food_omuraisu`） | 无 | 无 | 保留原设定 |
| 5 | 章鱼烧（`pm_kissaten_food_takoyaki`） | 无 | 无 | 保留原设定 |

#### 服务水准（`pmg_kissaten_server`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 普通营业（`pm_kissaten_server_null`） | 无 | 无 | 保留原设定 |
| 2 | 普通女仆（`pm_kissaten_server_waitress`） | 无 | 无 | 保留原设定 |
| 3 | 女仆营业（`pm_kissaten_server_maid`） | 无 | 无 | 保留原设定 |
| 4 | 主题公演（`pm_kissaten_server_fuwafuwa`） | 无 | 无 | 保留原设定 |

#### 工具设备（`pmg_kissaten_tool`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_kissaten_tool_null`） | 无 | 无 | 保留原设定 |
| 2 | 基本桌椅（`pm_kissaten_tool_table`） | 无 | 无 | 保留原设定 |
| 3 | 餐具套装（`pm_kissaten_tool_porcelain`） | 无 | 无 | 保留原设定 |
| 4 | 水管锅炉（`pm_kissaten_tool_watertube_boiler`） | 无 | **水管锅炉（`watertube_boiler`，E2）** | 设备名直接对应水管锅炉 |
| 5 | 冷藏设备（`pm_kissaten_tool_flash_freezing`） | 无 | **发电（`electrical_generation`，E3）** | 冷藏设备耗电；发电科技承接水管锅炉 |

### 乐器工坊（`building_musical_instrument`）

#### 乐器生产（`pmg_building_musical_instrument_main`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_musical_instrument_main_null`） | 无 | 无 | 保留原设定 |
| 2 | 手工制作（`pm_musical_instrument_main_wood`） | 无 | 无 | 保留原设定 |
| 3 | 冶金工艺（`pm_musical_instrument_main_iron`） | 车床（`lathe`，E1） | 车床（`lathe`，E1） | 保留原设定 |
| 4 | 机械加工（`pm_musical_instrument_main_steel`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 5 | 电气化乐器（`pm_musical_instrument_main_electric`） | 电容器（`electrical_capacitors`，E4） | 电容器（`electrical_capacitors`，E4） | 保留原设定 |

#### 自动化（`pmg_automation_building_tooling_workshop`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工装配（`pm_automation_disabled`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 水管锅炉（`pm_watertube_boiler_building_tooling_workshop`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 原版 PM，模组复用 |
| 3 | 旋转阀发动机（`pm_rotary_valve_engine_building_tooling_workshop`） | 旋转阀发动机（`rotary_valve_engine`，E3） | 旋转阀发动机（`rotary_valve_engine`，E3） | 原版 PM，模组复用 |
| 4 | 流水线（`pm_assembly_lines_building_tooling_workshop`） | 传送带（`conveyors`，E4） | 传送带（`conveyors`，E4） | 原版 PM，模组复用 |

### 综合出版社（`building_publisher`）

#### 编辑流程（`pmg_publisher_main`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_publisher_main_null`） | 无 | 无 | 保留原设定 |
| 2 | 手工编辑（`pm_publisher_main_general_wood`） | 无 | 无 | 保留原设定 |
| 3 | 分工编辑（`pm_publisher_main_general_iron`） | 现实主义（`realism`，E2） | **机械工具（`mechanical_tools`，E2）** | 机械化印刷与编辑设备 |
| 4 | 标准化编辑部（`pm_publisher_main_general_steel`） | 哲学实用主义（`philosophical_pragmatism`，E3） | **轮班工作（`shift_work`，E3）** | 标准化分工；轮班制承接机械工具 |
| 5 | 媒体编审体系（`pm_publisher_main_general_electric`） | 政治煽动（`political_agitation`，E4） | **电话（`telephone`，E4）** | 电话编审网络；承接轮班制 |

#### 内容方向（`pmg_publisher_business`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 综合出版（`pm_publisher_comprehensive_publishing`） | 无 | 无 | 保留原设定 |
| 2 | 专业期刊（`pm_publisher_professional_journal`） | 无 | 无 | 保留原设定 |
| 3 | 大众杂志（`pm_publisher_mass_magazine`） | 无 | **相机（`camera`，E3）** | 插图与广告杂志；摄影技术 |

### 娱乐出版社（`building_entertainment_press`）

#### 娱乐刊物（`pmg_ent_press_main`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_ent_press_main_null`） | 无 | 无 | 保留原设定 |
| 2 | 漫画工作室时代（`pm_ent_press_main_manga`） | 无 | 无 | 保留原设定 |
| 3 | 动画工业化时代（`pm_ent_press_main_serial`） | 相机（`camera`，E3） | 相机（`camera`，E3） | 保留原设定 |
| 4 | 轻小说改编时代（`pm_ent_press_main_novel`） | 电影（`film`，E4） | 电影（`film`，E4） | 保留原设定 |
| 5 | IP化运营时代（`pm_ent_press_main_multimedia`） | 大众宣传（`mass_propaganda`，E5） | 大众宣传（`mass_propaganda`，E5） | 保留原设定 |

#### 发行渠道（`pmg_ent_press_distribution`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 本地发行（`pm_ent_press_distribution_local`） | 无 | 无 | 保留原设定 |
| 2 | 全国发行（`pm_ent_press_distribution_national`） | 无 | 无 | 保留原设定 |
| 3 | 海外发行（`pm_ent_press_distribution_export`） | 无 | 无 | 保留原设定 |

#### 娱乐传媒自动化（`pmg_automation_building_entertainment_press`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工装订（`pm_tot_ent_press_automation_disabled`） | 无 | 无 | 保留原设定 |
| 2 | 水管锅炉自动化（`pm_tot_ent_press_automation_watertube`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 保留原设定 |
| 3 | 旋转阀引擎自动化（`pm_tot_ent_press_automation_rotary`） | 旋转阀发动机（`rotary_valve_engine`，E3） | 旋转阀发动机（`rotary_valve_engine`，E3） | 保留原设定 |
| 4 | 流水线自动化（`pm_tot_ent_press_automation_assembly`） | 传送带（`conveyors`，E4） | 传送带（`conveyors`，E4） | 保留原设定 |

### 游戏工坊（`building_game`）

#### 桌游开发（`pmg_game_traditional_dev`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无生产方式（`pm_game_traditional_null`） | 无 | 无 | 保留原设定 |
| 2 | 古典棋牌（`pm_game_traditional_tabletop`） | 无 | 无 | 保留原设定 |
| 3 | 近代兵棋（`pm_game_traditional_mechanical`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 4 | 现代桌游（`pm_game_traditional_craft`） | 机械化工坊（`mechanized_workshops`，E2） | 机械化工坊（`mechanized_workshops`，E2） | 保留原设定 |

#### 机械开发（`pmg_game_modern_dev`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无生产方式（`pm_game_modern_null`） | 无 | 无 | 保留原设定 |
| 2 | 弹簧玩具（`pm_game_modern_pinball`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 3 | 机电街机（`pm_game_modern_arcade`） | 发电（`electrical_generation`，E3） | **电话（`telephone`，E4）** | 机电设备；电话科技继承机械工具与发电 |
| 4 | 现代街机（`pm_game_modern_video`） | 电容器（`electrical_capacitors`，E4） | **无线电（`radio`，E4）** | 电子传播技术；广播承接电话 |

#### 电子开发（`pmg_game_business`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无生产方式（`pm_game_business_null`） | 无 | 无 | 保留原设定 |
| 2 | 卡带时代（`pm_game_cartridge_era`） | 发电（`electrical_generation`，E3） | 发电（`electrical_generation`，E3） | 保留原设定 |
| 3 | 光盘时代（`pm_game_disc_era`） | 电容器（`electrical_capacitors`，E4） | **电话（`telephone`，E4）** | 电子媒介；电话科技承接发电 |
| 4 | 移动时代（`pm_game_mobile_era`） | 无线电（`radio`，E4） | 无线电（`radio`，E4） | 保留原设定 |

#### 运营模式（`pmg_game_operation`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 仅本体（`pm_game_operation_base`） | 无 | 无 | 保留原设定 |
| 2 | 补充包（`pm_game_operation_expansion`） | 相机（`camera`，E3） | 相机（`camera`，E3） | 保留原设定 |
| 3 | IP运营（`pm_game_operation_ip`） | 电影（`film`，E4） | 电影（`film`，E4） | 保留原设定 |

### 谷子工坊（`building_goods`）

#### 毛绒产品（`pmg_goods_doll`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_doll_null`） | 无 | 无 | 保留原设定 |
| 2 | 手工玩偶（`pm_goods_doll_doll`） | 无 | 无 | 保留原设定 |
| 3 | 定制玩偶（`pm_goods_doll_custom`） | 车床（`lathe`，E1） | 车床（`lathe`，E1） | 保留原设定 |
| 4 | 抱枕（`pm_goods_doll_pillow`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 5 | 等身抱枕（`pm_goods_doll_iron`） | 机械化工坊（`mechanized_workshops`，E2） | 机械化工坊（`mechanized_workshops`，E2） | 保留原设定 |

#### 小饰品（`pmg_goods_jewelry`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_jewelry_null`） | 无 | 无 | 保留原设定 |
| 2 | 徽章（`pm_goods_jewelry_badge`） | 无 | 无 | 保留原设定 |
| 3 | 挂件（`pm_goods_jewelry_pendant`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 4 | 立牌（`pm_goods_jewelry_stand`） | 机械化工坊（`mechanized_workshops`，E2） | 机械化工坊（`mechanized_workshops`，E2） | 保留原设定 |
| 5 | 手办（`pm_goods_jewelry_premium`） | 橡胶塑炼（`rubber_mastication`，E3） | **传送带（`conveyors`，E4）** | 批量装配手办；橡胶并非该档核心工艺 |

#### 模型（`pmg_goods_garage`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_garage_null`） | 无 | 无 | 保留原设定 |
| 2 | 木制玩具（`pm_goods_garage_lego`） | 无 | 无 | 保留原设定 |
| 3 | 军用模型（`pm_goods_garage_military_model`） | 机械化工坊（`mechanized_workshops`，E2） | 机械化工坊（`mechanized_workshops`，E2） | 保留原设定 |
| 4 | 高达（`pm_goods_garage_gundam`） | 橡胶塑炼（`rubber_mastication`，E3） | **轮班工作（`shift_work`，E3）** | 标准化批量模型；承接机械化车间 |
| 5 | 电动玩具（`pm_goods_garage_motor`） | 电容器（`electrical_capacitors`，E4） | **电话（`telephone`，E4）** | 电气零部件；电话科技继承轮班制与发电 |

#### 印刷品（`pmg_goods_print`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_print_null`） | 无 | 无 | 保留原设定 |
| 2 | 色纸（`pm_goods_print_seal`） | 无 | 无 | 保留原设定 |
| 3 | 卡牌（`pm_goods_print_card`） | 机械工具（`mechanical_tools`，E2） | **车床（`lathe`，E1）** | 早期机械印制，作为漂白纸张前的工业档 |
| 4 | 海报（`pm_goods_print_post`） | 化学漂白（`chemical_bleaching`，E2） | 化学漂白（`chemical_bleaching`，E2） | 保留原设定 |
| 5 | 挂画（`pm_goods_print_art`） | 轮班工作（`shift_work`，E3） | **苯胺（`aniline`，E3）** | 合成染料和彩色印刷；承接化学漂白 |

#### ip管理（`pmg_goods_ip`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_ip_null`） | 无 | 无 | 保留原设定 |
| 2 | 本国优先（`pm_goods_ip_home`） | 无 | 无 | 保留原设定 |
| 3 | 热门优先（`pm_goods_ip_hot`） | 无 | 无 | 保留原设定 |
| 4 | 随机上架（`pm_goods_ip_random`） | 无 | 无 | 保留原设定 |

#### 销售方式（`pmg_goods_selling`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无（`pm_goods_selling_null`） | 无 | 无 | 保留原设定 |
| 2 | 抽奖模式（`pm_goods_selling_lotto`） | 无 | 无 | 保留原设定 |
| 3 | 大量贩售（`pm_goods_selling_large`） | 无 | 无 | 保留原设定 |
| 4 | 饥饿营销（`pm_goods_selling_hunger_marketing`） | 无 | 无 | 保留原设定 |

### 酒馆（`building_izakaya`）

#### 酒水菜单（`pmg_izakaya_drinks`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 炉边温酒（`pm_izakaya_hearth_drinks`） | 无 | 无 | 保留原设定 |
| 2 | 清酒与果酒（`pm_izakaya_izakaya_banquet`） | 无 | 无 | 保留原设定 |
| 3 | 招牌调酒（`pm_izakaya_city_cocktails`） | 分馏（`fractional_distillation`，E2） | 分馏（`fractional_distillation`，E2） | 保留原设定 |

#### 料理菜单（`pmg_izakaya_food`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 旅店炖菜（`pm_izakaya_travelers_stew`） | 无 | 无 | 保留原设定 |
| 2 | 居酒屋小菜（`pm_izakaya_izakaya_delicacies`） | 无 | 无 | 保留原设定 |
| 3 | 海陆拼盘（`pm_izakaya_hearth_banquet`） | 城镇规划（`urban_planning`，E1） | **现代排水系统（`modern_sewerage`，E2）** | 城市卫生支撑大型餐饮 |

#### 店面风格（`pmg_izakaya_hospitality`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 炉边拼桌（`pm_izakaya_communal_tables`） | 无 | 无 | 保留原设定 |
| 2 | 居酒屋柜台（`pm_izakaya_counter_longtables`） | 无 | 无 | 保留原设定 |
| 3 | 贵宾包间（`pm_izakaya_patron_rooms`） | 城镇规划（`urban_planning`，E1） | **公司章程（`corporate_charters`，E2）** | 商务包间与企业经营 |

#### 厨房设备（`pmg_izakaya_kitchen`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 砖砌灶台（`pm_izakaya_brick_stoves`） | 无 | 无 | 保留原设定 |
| 2 | 铸铁炉灶与冰窖（`pm_izakaya_iron_stoves_icehouse`） | 大气式蒸汽机（`atmospheric_engine`，E2） | **机械工具（`mechanical_tools`，E2）** | 机械厨房设备；承接基础灶台 |
| 3 | 电气冷藏厨房（`pm_izakaya_electric_cold_kitchen`） | 发电（`electrical_generation`，E3） | **电话（`telephone`，E4）** | 电冷厨；电话科技继承机械工具与发电 |

### 蓝晶矿井（`building_blue_crystal_mine`）

#### 矿井设备（`pmg_mining_equipment_building_blue_crystal_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 镐和铲（`pm_picks_and_shovels_building_blue_crystal_mine`） | 无 | 无 | 保留原设定 |
| 2 | 大气蒸汽机泵（`pm_atmospheric_engine_pump_building_blue_crystal_mine`） | 大气式蒸汽机（`atmospheric_engine`，E2） | 大气式蒸汽机（`atmospheric_engine`，E2） | 保留原设定 |
| 3 | 冷凝蒸汽机泵（`pm_condensing_engine_pump_building_blue_crystal_mine`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 保留原设定 |
| 4 | 柴油泵（`pm_diesel_pump_building_blue_crystal_mine`） | 压缩点火（`compression_ignition`，E5） | 压缩点火（`compression_ignition`，E5） | 保留原设定 |

#### 爆破技术（`pmg_explosives_building_blue_crystal_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工钻孔（`pm_no_explosives`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 硝化甘油（`pm_nitroglycerin_building_blue_crystal_mine`） | 硝化甘油（`nitroglycerin`，E2） | 硝化甘油（`nitroglycerin`，E2） | 保留原设定 |
| 3 | 炸药（`pm_dynamite_building_blue_crystal_mine`） | 黄色炸药（`dynamite`，E3） | 黄色炸药（`dynamite`，E3） | 保留原设定 |

#### 自动化（`pmg_steam_automation_building_blue_crystal_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手动曲柄起重机（`pm_no_steam_automation`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 辅助蒸汽机（`pm_steam_donkey_mine`） | 辅助蒸汽机（`steam_donkey`，E3） | 辅助蒸汽机（`steam_donkey`，E3） | 原版 PM，模组复用 |

#### 运输（`pmg_train_automation_building_blue_crystal_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手推车（`pm_road_carts`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | $pm_rail_transport$（`pm_rail_transport_mine`） | 铁路（`railways`，E2） | 铁路（`railways`，E2） | 原版 PM，模组复用 |

### 樱石矿井（`building_sakura_stone_mine`）

#### 矿井设备（`pmg_mining_equipment_building_sakura_stone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 镐和铲（`pm_picks_and_shovels_building_sakura_stone_mine`） | 无 | 无 | 保留原设定 |
| 2 | 大气蒸汽机泵（`pm_atmospheric_engine_pump_building_sakura_stone_mine`） | 大气式蒸汽机（`atmospheric_engine`，E2） | 大气式蒸汽机（`atmospheric_engine`，E2） | 保留原设定 |
| 3 | 冷凝蒸汽机泵（`pm_condensing_engine_pump_building_sakura_stone_mine`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 保留原设定 |
| 4 | 柴油泵（`pm_diesel_pump_building_sakura_stone_mine`） | 压缩点火（`compression_ignition`，E5） | 压缩点火（`compression_ignition`，E5） | 保留原设定 |

#### 爆破技术（`pmg_explosives_building_sakura_stone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工钻孔（`pm_no_explosives`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 硝化甘油（`pm_nitroglycerin_building_sakura_stone_mine`） | 硝化甘油（`nitroglycerin`，E2） | 硝化甘油（`nitroglycerin`，E2） | 保留原设定 |
| 3 | 炸药（`pm_dynamite_building_sakura_stone_mine`） | 黄色炸药（`dynamite`，E3） | 黄色炸药（`dynamite`，E3） | 保留原设定 |

#### 自动化（`pmg_steam_automation_building_sakura_stone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手动曲柄起重机（`pm_no_steam_automation`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 辅助蒸汽机（`pm_steam_donkey_mine`） | 辅助蒸汽机（`steam_donkey`，E3） | 辅助蒸汽机（`steam_donkey`，E3） | 原版 PM，模组复用 |

#### 运输（`pmg_train_automation_building_sakura_stone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手推车（`pm_road_carts`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | $pm_rail_transport$（`pm_rail_transport_mine`） | 铁路（`railways`，E2） | 铁路（`railways`，E2） | 原版 PM，模组复用 |

### 要石矿井（`building_keystone_mine`）

#### 矿井设备（`pmg_mining_equipment_building_keystone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 镐和铲（`pm_picks_and_shovels_building_keystone_mine`） | 无 | 无 | 保留原设定 |
| 2 | 大气蒸汽机泵（`pm_atmospheric_engine_pump_building_keystone_mine`） | 大气式蒸汽机（`atmospheric_engine`，E2） | 大气式蒸汽机（`atmospheric_engine`，E2） | 保留原设定 |
| 3 | 冷凝蒸汽机泵（`pm_condensing_engine_pump_building_keystone_mine`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 保留原设定 |
| 4 | 柴油泵（`pm_diesel_pump_building_keystone_mine`） | 压缩点火（`compression_ignition`，E5） | 压缩点火（`compression_ignition`，E5） | 保留原设定 |

#### 爆破技术（`pmg_explosives_building_keystone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工钻孔（`pm_no_explosives`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 硝化甘油（`pm_nitroglycerin_building_keystone_mine`） | 硝化甘油（`nitroglycerin`，E2） | 硝化甘油（`nitroglycerin`，E2） | 保留原设定 |
| 3 | 炸药（`pm_dynamite_building_keystone_mine`） | 黄色炸药（`dynamite`，E3） | 黄色炸药（`dynamite`，E3） | 保留原设定 |

#### 自动化（`pmg_steam_automation_building_keystone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手动曲柄起重机（`pm_no_steam_automation`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 辅助蒸汽机（`pm_steam_donkey_mine`） | 辅助蒸汽机（`steam_donkey`，E3） | 辅助蒸汽机（`steam_donkey`，E3） | 原版 PM，模组复用 |

#### 运输（`pmg_train_automation_building_keystone_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手推车（`pm_road_carts`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | $pm_rail_transport$（`pm_rail_transport_mine`） | 铁路（`railways`，E2） | 铁路（`railways`，E2） | 原版 PM，模组复用 |

### 源石矿井（`building_originium_mine`）

#### 矿井设备（`pmg_mining_equipment_building_originium_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 镐和铲（`pm_picks_and_shovels_building_originium_mine`） | 无 | 无 | 保留原设定 |
| 2 | 大气蒸汽机泵（`pm_atmospheric_engine_pump_building_originium_mine`） | 大气式蒸汽机（`atmospheric_engine`，E2） | 大气式蒸汽机（`atmospheric_engine`，E2） | 保留原设定 |
| 3 | 冷凝蒸汽机泵（`pm_condensing_engine_pump_building_originium_mine`） | 水管锅炉（`watertube_boiler`，E2） | 水管锅炉（`watertube_boiler`，E2） | 保留原设定 |
| 4 | 柴油泵（`pm_diesel_pump_building_originium_mine`） | 压缩点火（`compression_ignition`，E5） | 压缩点火（`compression_ignition`，E5） | 保留原设定 |

#### 爆破技术（`pmg_explosives_building_originium_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手工钻孔（`pm_no_explosives`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 硝化甘油（`pm_nitroglycerin_building_originium_mine`） | 硝化甘油（`nitroglycerin`，E2） | 硝化甘油（`nitroglycerin`，E2） | 保留原设定 |
| 3 | 炸药（`pm_dynamite_building_originium_mine`） | 黄色炸药（`dynamite`，E3） | 黄色炸药（`dynamite`，E3） | 保留原设定 |

#### 自动化（`pmg_steam_automation_building_originium_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手动曲柄起重机（`pm_no_steam_automation`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | 辅助蒸汽机（`pm_steam_donkey_mine`） | 辅助蒸汽机（`steam_donkey`，E3） | 辅助蒸汽机（`steam_donkey`，E3） | 原版 PM，模组复用 |

#### 运输（`pmg_train_automation_building_originium_mine`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 手推车（`pm_road_carts`） | 无 | 无 | 原版 PM，模组复用 |
| 2 | $pm_rail_transport$（`pm_rail_transport_mine`） | 铁路（`railways`，E2） | 铁路（`railways`，E2） | 原版 PM，模组复用 |

### building_tot_golden_hall_monument（`building_tot_golden_hall_monument`）

#### pmg_base_building_tot_golden_hall_monument（`pmg_base_building_tot_golden_hall_monument`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 金色大厅（`pm_default_building_tot_golden_hall_monument`） | 无 | 无 | 保留原设定 |
| 2 | 威望（`pm_monument_prestige_only`） | 无 | 无 | 原版 PM，模组复用 |
| 3 | 无效果（`pm_monument_no_effects`） | 无 | 无 | 原版 PM，模组复用 |

### 宗教中心（`building_religious_center`）

#### 会堂活动（`pmg_religious_center_assembly`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 日常会堂（`pm_religious_center_daily_assembly`） | 无 | 无 | 保留原设定 |
| 2 | 公开讲习（`pm_religious_center_public_instruction`） | 城镇规划（`urban_planning`，E1） | 城镇规划（`urban_planning`，E1） | 保留原设定 |
| 3 | 全城庆典（`pm_religious_center_city_celebration`） | 现实主义（`realism`，E2） | **现代排水系统（`modern_sewerage`，E2）** | 城市基础设施；承接城市规划 |

#### 特色仪式（`pmg_religious_center_rites`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 普通仪式（`pm_religious_center_common_rites`） | 无 | 无 | 保留原设定 |
| 2 | 圣三一圣礼（`pm_religious_center_trinity_rite`） | 无 | 无 | 保留原设定 |
| 3 | 星歌祈愿（`pm_religious_center_starbeat_rite`） | 无 | 无 | 保留原设定 |
| 4 | 学园誓约（`pm_religious_center_kiseki_rite`） | 无 | 无 | 保留原设定 |

#### 仪式设施（`pmg_religious_center_facilities`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 传统仪轨（`pm_religious_center_traditional_facilities`） | 无 | 无 | 保留原设定 |
| 2 | 印刷仪典（`pm_religious_center_printed_liturgy`） | 机械工具（`mechanical_tools`，E2） | 机械工具（`mechanical_tools`，E2） | 保留原设定 |
| 3 | 电气化会堂（`pm_religious_center_electric_facilities`） | 发电（`electrical_generation`，E3） | **电话（`telephone`，E4）** | 电气设施；电话科技继承机械工具与发电 |

### 舞台（`building_stage`）

#### 舞台运营（`pmg_stage_operation`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 仅票务（`pm_stage_operation_public`） | 无 | 无 | 保留原设定 |
| 2 | 标准服务（`pm_stage_operation_ticketed`） | 无 | 无 | 保留原设定 |
| 3 | 餐饮设施（`pm_stage_operation_hospitality`） | 现代排水系统（`modern_sewerage`，E2） | 现代排水系统（`modern_sewerage`，E2） | 保留原设定 |
| 4 | 豪华大厅（`pm_stage_operation_festival`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 保留原设定 |

#### 舞台规模（`pmg_stage_scale`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 简易舞台（`pm_stage_scale_small`） | 无 | 无 | 保留原设定 |
| 2 | 正式舞台（`pm_stage_scale_compact`） | 无 | 无 | 保留原设定 |
| 3 | 大型舞台（`pm_stage_scale_medium`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 保留原设定 |
| 4 | 豪华舞台（`pm_stage_scale_large`） | 电梯（`elevator`，E4） | 电梯（`elevator`，E4） | 保留原设定 |

#### 场贩配置（`pmg_stage_merchandising`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无场贩（`pm_stage_merchandising_none`） | 无 | 无 | 保留原设定 |
| 2 | 简易场贩（`pm_stage_merchandising_basic`） | 无 | 无 | 保留原设定 |
| 3 | 常设物贩区（`pm_stage_merchandising_standard`） | 公司章程（`corporate_charters`，E2） | 公司章程（`corporate_charters`，E2） | 保留原设定 |
| 4 | 综合物贩区（`pm_stage_merchandising_full`） | 股份公司（`joint_stock_companies`，E2） | 股份公司（`joint_stock_companies`，E2） | 保留原设定 |
| 5 | 限定特典卖场（`pm_stage_merchandising_premium`） | 投资银行（`investment_banks`，E3） | 投资银行（`investment_banks`，E3） | 保留原设定 |

#### 媒体宣传（`pmg_stage_media`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 无宣传（`pm_stage_media_none`） | 无 | 无 | 保留原设定 |
| 2 | 传单宣传（`pm_stage_media_flyers`） | 无 | 无 | 保留原设定 |
| 3 | 纸媒宣传（`pm_stage_media_magazines`） | 现实主义（`realism`，E2） | **机械工具（`mechanical_tools`，E2）** | 机械化期刊印制 |
| 4 | 广播宣传（`pm_stage_media_radio`） | 无线电（`radio`，E4） | **电话（`telephone`，E4）** | 电话传播网络；广播商品本身仍需供应 |
| 5 | 跨媒宣传（`pm_stage_media_ip_collab`） | 大众宣传（`mass_propaganda`，E5） | **无线电（`radio`，E4）** | 广播媒介扩大跨地域联动；承接电话 |

### 游乐场（`building_amusement_park`）

#### 园区场地（`pmg_amusement_ground`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 露天游乐场（`pm_amusement_ground_fair`） | 无 | 无 | 保留原设定 |
| 2 | 景观游乐园（`pm_amusement_ground_garden`） | 无 | 无 | 保留原设定 |
| 3 | 电气主题乐园（`pm_amusement_ground_electric`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | **发电（`electrical_generation`，E3）** | 电气化园区 |
| 4 | 综合主题乐园（`pm_amusement_ground_dream`） | 电梯（`elevator`，E4） | **电容器（`electrical_capacitors`，E4）** | 更复杂的电气游乐设施；承接发电 |

#### 游乐设备（`pmg_amusement_ride`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 旋转木马（`pm_amusement_ride_carousel`） | 无 | 无 | 保留原设定 |
| 2 | 蒸汽过山车（`pm_amusement_ride_coaster`） | 机械工具（`mechanical_tools`，E2） | **大气式蒸汽机（`atmospheric_engine`，E2）** | 蒸汽动力设施；承接基础旋转木马 |
| 3 | 霓虹飞车（`pm_amusement_ride_neon`） | 发电（`electrical_generation`，E3） | 发电（`electrical_generation`，E3） | 保留原设定 |
| 4 | 摩天轮（`pm_amusement_ride_ferris`） | 电梯（`elevator`，E4） | **电容器（`electrical_capacitors`，E4）** | 大型电动游乐设施；承接发电 |

#### 园区商店（`pmg_amusement_shop`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 园区周边摊位（`pm_amusement_shop_stall`） | 无 | 无 | 保留原设定 |
| 2 | 纪念品商店（`pm_amusement_shop_souvenir`） | 公司章程（`corporate_charters`，E2） | 公司章程（`corporate_charters`，E2） | 保留原设定 |
| 3 | 主题商品店（`pm_amusement_shop_limited`） | 股份公司（`joint_stock_companies`，E2） | 股份公司（`joint_stock_companies`，E2） | 保留原设定 |
| 4 | 角色联名商店（`pm_amusement_shop_collab`） | 大众传播（`mass_communication`，E1） | **企业治理（`corporate_management`，E4）** | 跨品牌商业管理；承接股份公司 |

### 水族馆（`building_aquarium`）

#### 展馆场地（`pmg_aquarium_ground`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 玻璃水箱展馆（`pm_aquarium_ground_tank`） | 无 | 无 | 保留原设定 |
| 2 | 海洋生物馆（`pm_aquarium_ground_marine`） | 水晶玻璃（`crystal_glass`，E2） | **现代排水系统（`modern_sewerage`，E2）** | 海水循环和公共卫生设施 |
| 3 | 海底隧道（`pm_aquarium_ground_tunnel`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 保留原设定 |
| 4 | 巨型综合馆（`pm_aquarium_ground_mega`） | 电梯（`elevator`，E4） | 电梯（`elevator`，E4） | 保留原设定 |

#### 动物类型（`pmg_aquarium_animal_type`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 淡水生物（`pm_aquarium_type_freshwater`） | 无 | 无 | 保留原设定 |
| 2 | 海水鱼类（`pm_aquarium_type_marine`） | 现实主义（`realism`，E2） | **大气式蒸汽机（`atmospheric_engine`，E2）** | 海水泵送与温控设备 |
| 3 | 海洋生物展演（`pm_aquarium_type_reef`） | 发电（`electrical_generation`，E3） | 发电（`electrical_generation`，E3） | 保留原设定 |
| 4 | 海洋哺乳动物（`pm_aquarium_type_mammal`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | **电容器（`electrical_capacitors`，E4）** | 更复杂的电气化维生设备；承接发电 |

#### 动物互动（`pmg_aquarium_interaction`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 公开饲养展示（`pm_aquarium_program_feeding`） | 无 | 无 | 保留原设定 |
| 2 | 公开喂食（`pm_aquarium_program_concert`） | 现代排水系统（`modern_sewerage`，E2） | 现代排水系统（`modern_sewerage`，E2） | 保留原设定 |
| 3 | 海洋动物表演（`pm_aquarium_program_show`） | 发电（`electrical_generation`，E3） | **钢框架结构建筑（`steel_frame_buildings`，E3）** | 结构化观演场所；承接城市排水 |
| 4 | 海洋动物剧场（`pm_aquarium_program_theater`） | 大众传播（`mass_communication`，E1） | **电梯（`elevator`，E4）** | 大型多层剧场；承接钢框架 |

#### 科普教育（`pmg_aquarium_education`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 科普导览（`pm_aquarium_program_guide`） | 无 | 无 | 保留原设定 |
| 2 | 夜间科普展（`pm_aquarium_program_night`） | 现实主义（`realism`，E2） | 现实主义（`realism`，E2） | 保留原设定 |
| 3 | 水生生态教育（`pm_aquarium_program_research`） | 发电（`electrical_generation`，E3） | **相机（`camera`，E3）** | 摄影记录；承接写实主义 |
| 4 | 海洋纪录放映（`pm_aquarium_program_documentary`） | 大众传播（`mass_communication`，E1） | **电影（`film`，E4）** | 纪录片；电影承接摄影 |

### 动物园（`building_zoo`）

#### 园区场地（`pmg_zoo_ground`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 小型围场（`pm_zoo_ground_pen`） | 无 | 无 | 保留原设定 |
| 2 | 围场园区（`pm_zoo_ground_park`） | 无 | 无 | 保留原设定 |
| 3 | 大型剧场（`pm_zoo_ground_stadium`） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 钢框架结构建筑（`steel_frame_buildings`，E3） | 保留原设定 |
| 4 | 生态园区（`pm_zoo_ground_eco`） | 电梯（`elevator`，E4） | 电梯（`elevator`，E4） | 保留原设定 |

#### 动物类型（`pmg_zoo_animal_type`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 小型动物（`pm_zoo_type_small`） | 无 | 无 | 保留原设定 |
| 2 | 猛兽（`pm_zoo_type_predator`） | 现实主义（`realism`，E2） | **现代排水系统（`modern_sewerage`，E2）** | 安全卫生的专门兽栏 |
| 3 | 大型动物（`pm_zoo_type_large`） | 公司章程（`corporate_charters`，E2） | **钢框架结构建筑（`steel_frame_buildings`，E3）** | 大型结构兽栏；承接城市卫生 |
| 4 | 明星动物（`pm_zoo_type_star`） | 大众传播（`mass_communication`，E1） | **电梯（`elevator`，E4）** | 大型多层游客设施；承接钢框架 |

#### 动物互动（`pmg_zoo_interaction`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 饲养员喂食（`pm_zoo_interaction_basic`） | 无 | 无 | 保留原设定 |
| 2 | 游客喂食区（`pm_zoo_interaction_feeding`） | 现代排水系统（`modern_sewerage`，E2） | 现代排水系统（`modern_sewerage`，E2） | 保留原设定 |
| 3 | 驯兽表演（`pm_zoo_interaction_show`） | 公司章程（`corporate_charters`，E2） | **钢框架结构建筑（`steel_frame_buildings`，E3）** | 结构化表演场所；承接城市排水 |
| 4 | 动物马戏团（`pm_zoo_interaction_grand`） | 大众传播（`mass_communication`，E1） | **电梯（`elevator`，E4）** | 大型多层演出场所；承接钢框架 |

#### 科普教育（`pmg_zoo_education`）

| 顺序 | PM 中文名 / ID | 当前 | 拟定 | 理由 |
|---:|---|---|---|---|
| 1 | 动物导览（`pm_zoo_education_guide`） | 无 | 无 | 保留原设定 |
| 2 | 自然史教育（`pm_zoo_education_natural_history`） | 现实主义（`realism`，E2） | 现实主义（`realism`，E2） | 保留原设定 |
| 3 | 动物保育研究（`pm_zoo_education_conservation`） | 发电（`electrical_generation`，E3） | **相机（`camera`，E3）** | 摄影记录；承接写实主义 |
| 4 | 动物纪录展（`pm_zoo_education_documentary`） | 大众传播（`mass_communication`，E1） | **电影（`film`，E4）** | 纪录片；电影承接摄影 |

## 前置关系核验

- 模组定义且在 PMG 中使用的 PM：249 项；拟调整：45 项。
- 建筑复用的原版 PM 条目：26 项。
- 拟改组前置链冲突：0 项；电气化乐器保留旧版造成的既有跨分支例外：1 项。

- pmg_building_musical_instrument_main: pm_musical_instrument_main_steel (mechanical_tools) -> pm_musical_instrument_main_electric (electrical_capacitors)
- 缺少简体中文 PM 名称：0 项。
