# 全部模组建筑：当前基准价商品收支复核

覆盖 30 栋在模组中定义的建筑，包括改写的原版畜牧场、停用建筑和事件建筑。

- 每级建筑满就业，按当前商品 `cost` 计算。投入、产出为每周商品总价；毛利率＝（产出－投入）÷产出。
- 每个 PMG 选择一个 PM，枚举全部理论组合；计入建筑商品投入/产出倍率，不计工资、市场价格、就业不足、吞吐量和科技／法律可用性。吞吐量同时放大商品投入与产出，通常不改变商品毛利率。
- 默认档取 `is_default = yes`，没有标记则取 PMG 第一档。若一组有多个默认标记，则暂取第一个并在下方标明。最高档是所有 PMG 最后一档同时启用，不一定是最优组合。
- 多个 PMG 的投入和产出是先合并商品数量，再应用所选 PM 的建筑级商品倍率。输出为零的组合不计算毛利率。
- 乐队总部与社团采用 `no_ownership`，还提供容量、国家修正等非商品收益；负商品毛利是财政补贴规模的线索，不能直接与自营工厂按同一标准比较。金色大厅合同与纪念建筑主要通过事件或修正发挥作用。

## 汇总

| 建筑 | 可建 | 组合数 | 默认投入→产出 | 默认毛利 | 全高档投入→产出 | 全高档毛利 | 毛利范围 | <30% / 30–70% / >70% |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 游乐场 (`building_amusement_park`) | 是 | 16 | 1,850→2,800 | 33.9% | 3,950→8,000 | 50.6% | 33.9%～50.7% | 0 / 16 / 0 |
| 水族馆 (`building_aquarium`) | 是 | 48 | 1,350→2,500 | 46.0% | 7,000→9,600 | 27.1% | 8.0%～51.1% | 19 / 29 / 0 |
| 乐队总部 (`building_band_headquarter`) | 是 | 125 | 300→0 | — | 4,500→2,040 | -120.6% | -462.5%～-78.6% | 123 / 0 / 0（另有 2 组无商品产出） |
| 粮仓 (`building_barn`) | 否 | 27 | 0→1,600 | 100.0% | 0→4,000 | 100.0% | 100.0%～100.0% | 0 / 0 / 27 |
| 蓝晶矿井 (`building_blue_crystal_mine`) | 否 | 48 | 200→1,200 | 83.3% | 1,630→5,400 | 69.8% | 55.8%～83.3% | 0 / 31 / 17 |
| 私家庭园 (`building_botanical_garden`) | 是 | 16 | 200→1,000 | 80.0% | 2,400→5,550 | 56.8% | 53.3%～84.6% | 0 / 11 / 5 |
| 社团 (`building_club`) | 是 | 12 | 450→600 | 25.0% | 750→200 | -275.0% | -275.0%～43.8% | 10 / 2 / 0 |
| 娱乐出版社 (`building_entertainment_press`) | 是 | 12 | 1,500→2,400 | 37.5% | 3,900→5,700 | 31.6% | 18.8%～43.9% | 1 / 11 / 0 |
| 游戏工坊 (`building_game`) | 是 | 192 | 1,150→1,800 | 36.1% | 7,800→11,300 | 31.0% | -64.3%～50.0% | 54 / 138 / 0 |
| 谷子工坊 (`building_goods`) | 是 | 1,024 | 2,800→4,200 | 33.3% | 8,850→13,200 | 33.0% | 28.0%～40.2% | 9 / 1,015 / 0 |
| 酒馆 (`building_izakaya`) | 是 | 81 | 1,500→2,400 | 37.5% | 4,320→8,400 | 48.6% | 33.8%～51.1% | 0 / 81 / 0 |
| 要石矿井 (`building_keystone_mine`) | 否 | 48 | 200→1,300 | 84.6% | 1,630→5,850 | 72.1% | 59.2%～84.6% | 0 / 25 / 23 |
| 咖啡厅 (`building_kissaten`) | 是 | 6,000 | 1,050→1,500 | 30.0% | 12,200→19,800 | 38.4% | 16.7%～44.6% | 14 / 5,986 / 0 |
| 畜牧场 (`building_livestock_ranch`) | 是 | 432 | 40→480 | 91.7% | 960→2,100 | 54.3% | 50.3%～91.7% | 0 / 390 / 42 |
| 乐器工坊 (`building_musical_instrument`) | 是 | 16 | 800→1,800 | 55.6% | 3,150→5,100 | 38.2% | 25.0%～63.0% | 1 / 15 / 0 |
| 源石矿井 (`building_originium_mine`) | 否 | 48 | 200→1,500 | 86.7% | 1,630→6,750 | 75.9% | 64.7%～86.7% | 0 / 11 / 37 |
| 综合出版社 (`building_publisher`) | 是 | 12 | 1,045→2,000 | 47.8% | 3,900→9,200 | 57.6% | 43.3%～62.8% | 0 / 12 / 0 |
| 宗教中心 (`building_religious_center`) | 是 | 9 | 750→1,250 | 40.0% | 3,250→5,250 | 38.1% | 35.0%～40.0% | 0 / 9 / 0 |
| 樱石矿井 (`building_sakura_stone_mine`) | 否 | 48 | 200→1,400 | 85.7% | 1,630→6,300 | 74.1% | 62.1%～85.7% | 0 / 19 / 29 |
| 舞台 (`building_stage`) | 是 | 400 | 650→2,000 | 67.5% | 10,500→15,500 | 32.3% | 29.9%～67.5% | 2 / 398 / 0 |
| 动物培育园 (`building_tot_animal_breeding_center`) | 是 | 12 | 600→1,500 | 60.0% | 2,500→5,400 | 53.7% | 13.3%～66.7% | 1 / 11 / 0 |
| 地灵殿核聚变设施 (`building_tot_chireiden_fusion`) | 否 | 1 | 250→750 | 66.7% | 250→750 | 66.7% | 66.7%～66.7% | 0 / 1 / 0 |
| 维也纳金色大厅施工现场 (`building_tot_golden_hall_construction_site`) | 否 | 1 | 0→0 | — | 0→0 | — | —～— | 0 / 0 / 0（另有 1 组无商品产出） |
| 金色大厅舞台扩建合同 (`building_tot_golden_hall_large_contract`) | 是 | 1 | 0→0 | — | 0→0 | — | —～— | 0 / 0 / 0（另有 1 组无商品产出） |
| 金色大厅 (`building_tot_golden_hall_monument`) | 是 | 3 | 0→0 | — | 0→0 | — | —～— | 0 / 0 / 0（另有 3 组无商品产出） |
| 金色大厅冠名重建合同 (`building_tot_golden_hall_naming_contract`) | 是 | 1 | 0→0 | — | 0→0 | — | —～— | 0 / 0 / 0（另有 1 组无商品产出） |
| 金色大厅基础修缮合同 (`building_tot_golden_hall_small_contract`) | 是 | 1 | 0→0 | — | 0→0 | — | —～— | 0 / 0 / 0（另有 1 组无商品产出） |
| 河童精密发电站 (`building_tot_kappa_power`) | 否 | 1 | 400→750 | 46.7% | 400→750 | 46.7% | 46.7%～46.7% | 0 / 1 / 0 |
| 宠物店 (`building_tot_pet_shop`) | 是 | 12 | 800→1,800 | 55.6% | 2,700→5,600 | 51.8% | 19.4%～63.6% | 1 / 11 / 0 |
| 动物园 (`building_zoo`) | 是 | 48 | 1,400→2,500 | 44.0% | 6,100→8,900 | 31.5% | 6.0%～50.0% | 15 / 33 / 0 |

## 最低毛利组合

以下列出可计算毛利的建筑。停用建筑仍保留，便于将来重新启用时复核。

- **乐队总部**：-462.5%，投入 900，产出 160；`pm_band_food_none`、`pm_band_entertainment_daily`、`pm_band_equipment_standard`。
- **社团**：-275.0%，投入 750，产出 200；`pm_club_activity_network`、`pm_club_operation_integrated`。
- **游戏工坊**：-64.3%，投入 2,300，产出 1,400；`pm_game_traditional_null`、`pm_game_modern_null`、`pm_game_business_null`、`pm_game_operation_ip`。
- **动物园**：6.0%，投入 2,350，产出 2,500；`pm_zoo_type_small`、`pm_zoo_interaction_basic`、`pm_zoo_feeding_electric`。
- **水族馆**：8.0%，投入 2,300，产出 2,500；`pm_aquarium_type_freshwater`、`pm_aquarium_program_feeding`、`pm_aquarium_circulation_electric`。
- **动物培育园**：13.3%，投入 1,300，产出 1,500；`pm_tot_animal_breeding_standard`、`pm_tot_animal_feeding_electric`。
- **咖啡厅**：16.7%，投入 1,250，产出 1,500；`pm_kissaten_coffee_coffee`、`pm_kissaten_tea_null`、`pm_kissaten_sweet_null`、`pm_kissaten_food_null`、`pm_kissaten_server_null`、`pm_kissaten_tool_porcelain`。
- **娱乐出版社**：18.8%，投入 1,950，产出 2,400；`pm_ent_press_main_manga`、`pm_ent_press_distribution_export`。
- **宠物店**：19.4%，投入 1,450，产出 1,800；`pm_tot_pet_services_traditional`、`pm_tot_pet_operation_centralized`。
- **乐器工坊**：25.0%，投入 1,350，产出 1,800；`pm_musical_instrument_main_wood`、`pm_assembly_lines_building_tooling_workshop`。
- **谷子工坊**：28.0%，投入 4,750，产出 6,600；`pm_goods_doll_iron`、`pm_goods_jewelry_badge`、`pm_goods_garage_military_model`、`pm_goods_print_seal`、`pm_goods_selling_chain`。
- **舞台**：29.9%，投入 5,400，产出 7,700；`pm_stage_operation_public`、`pm_stage_scale_medium`、`pm_stage_merchandising_premium`、`pm_stage_media_magazines`。
- **酒馆**：33.8%，投入 1,852.5，产出 2,800；`pm_izakaya_hearth_drinks`、`pm_izakaya_travelers_stew`、`pm_izakaya_communal_tables`、`pm_izakaya_iron_stoves_icehouse`。
- **游乐场**：33.9%，投入 1,850，产出 2,800；`pm_amusement_ride_carousel`、`pm_amusement_shop_stall`。
- **宗教中心**：35.0%，投入 1,950，产出 3,000；`pm_religious_center_public_instruction`、`pm_religious_center_common_rites`、`pm_religious_center_printed_liturgy`。
- **综合出版社**：43.3%，投入 1,700，产出 3,000；`pm_publisher_main_general_wood`、`pm_publisher_professional_journal`。
- **河童精密发电站**：46.7%，投入 400，产出 750；`pm_tot_kappa_precision_generation`。
- **畜牧场**：50.3%，投入 450，产出 905；`pm_butchering_tools`、`pm_sheep_farms`、`pm_electric_fencing`、`pm_refrigerated_rail_cars_building_livestock_ranch`、`pm_tot_dairy_traditional`。
- **私家庭园**：53.3%，投入 1,400，产出 3,000；`pm_botanical_garden_glasshouse_flowers`、`pm_botanical_garden_fruit_trees_none`。
- **蓝晶矿井**：55.8%，投入 530，产出 1,200；`pm_picks_and_shovels_building_blue_crystal_mine`、`pm_no_explosives`、`pm_steam_donkey_mine`、`pm_rail_transport_mine`。
- **要石矿井**：59.2%，投入 530，产出 1,300；`pm_picks_and_shovels_building_keystone_mine`、`pm_no_explosives`、`pm_steam_donkey_mine`、`pm_rail_transport_mine`。
- **樱石矿井**：62.1%，投入 530，产出 1,400；`pm_picks_and_shovels_building_sakura_stone_mine`、`pm_no_explosives`、`pm_steam_donkey_mine`、`pm_rail_transport_mine`。
- **源石矿井**：64.7%，投入 530，产出 1,500；`pm_picks_and_shovels_building_originium_mine`、`pm_no_explosives`、`pm_steam_donkey_mine`、`pm_rail_transport_mine`。
- **地灵殿核聚变设施**：66.7%，投入 250，产出 750；`pm_tot_chireiden_fusion_generation`。
- **粮仓**：100.0%，投入 0，产出 1,600；`pm_wooden_barn`、`pm_market_barn`、`pm_shopkeeper_barn`。

## 无商品产出的建筑

- 维也纳金色大厅施工现场 (`building_tot_golden_hall_construction_site`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。
- 金色大厅舞台扩建合同 (`building_tot_golden_hall_large_contract`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。
- 金色大厅 (`building_tot_golden_hall_monument`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。
- 金色大厅冠名重建合同 (`building_tot_golden_hall_naming_contract`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。
- 金色大厅基础修缮合同 (`building_tot_golden_hall_small_contract`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。

## 同组商品产值下降

按 PM 自身的基准价商品产出比较相邻档；负产出用于转产时也会列出。

- 社团 / `pmg_club_activity`：`pm_club_activity_exchange` 800 → `pm_club_activity_network` 200。
- 社团 / `pmg_club_operation`：`pm_club_operation_certified` 400 → `pm_club_operation_integrated` 0。

## 多重默认标记

- `building_barn` / `pmg_distribution_building_barn`：`pm_market_barn`、`pm_relief_barn`、`pm_transport_barn`
