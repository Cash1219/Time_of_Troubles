# 模组建筑生产方式：基准价投入、产出与收益率

覆盖 **28 栋模组建筑、283 个建筑 × 生产方式选择**。同一个 PM 若供多栋建筑使用，会按建筑重复列出。

## 计算口径

- 商品单价取游戏原版与模组 `common/goods/*.txt` 的 `cost`；模组同名商品覆盖原版。每级建筑满就业时，投入/产出总价为 `workforce_scaled` 的商品数量 × 基准价之和。
- **商品毛利率 =（产出总价 − 投入总价）÷ 产出总价 × 100%**，以此判断 30%～70% 区间，与仓库已有审计的口径一致。另列投入收益率 `（产出总价 − 投入总价）÷ 投入总价` 供参考。
- 这是一项 PM 单独带来的商品流，不是整栋建筑的利润。建筑会同时启用多个 PMG；不含工资、实际就业率、吞吐量、科技/法律效果和市场价格。
- 倍率修正（如 `building_goods_input_mult`、`goods_output_games_mult`）在明细中标记，但未分摊到单项 PM；它们需在整栋建筑组合中计算。零投入、纯成本、无商品流和转产项不适用单项收益率。

## 总览

| 类别 | 数量 |
|---|---:|
| 低于30% | 47 |
| 30%–70% | 128 |
| 高于70% | 21 |
| 无投入/仅产出 | 5 |
| 仅投入/辅助 | 29 |
| 负产出/转产 | 2 |
| 无商品流 | 51 |

可计算毛利率的 196 项中，若改用投入收益率筛选，则低于 30% 有 21 项，区间内 108 项，高于 70% 有 67 项。

## 需要优先核查的地方

以下先列单项数值线索。具体低毛利改进方案见 [低毛利改进清单](low_margin_improvements.md)。只有完整建筑组合与游戏内工资、市场价格核对后，才适合修改 PM 数量。

- `building_amusement_park`：低于下限 3 项；最低 25.0%，高于上限 0 项。
- `building_aquarium`：低于下限 6 项；最低 23.3%，高于上限 0 项。
- `building_band_headquarter`：低于下限 11 项；最低 -237.5%，高于上限 0 项。
- `building_blue_crystal_mine`：低于下限 0 项，高于上限 4 项；最高 83.3%。
- `building_botanical_garden`：低于下限 1 项；最低 26.7%，高于上限 0 项。
- `building_club`：低于下限 4 项；最低 -50.0%，高于上限 0 项。
- `building_entertainment_press`：低于下限 1 项；最低 16.7%，高于上限 0 项。
- `building_game`：低于下限 2 项；最低 7.1%，高于上限 0 项。
- `building_izakaya`：低于下限 2 项；最低 -37.5%，高于上限 0 项。
- `building_keystone_mine`：低于下限 0 项，高于上限 4 项；最高 84.6%。
- `building_livestock_ranch`：低于下限 0 项，高于上限 2 项；最高 82.2%。
- `building_originium_mine`：低于下限 0 项，高于上限 5 项；最高 86.7%。
- `building_publisher`：低于下限 3 项；最低 20.0%，高于上限 0 项。
- `building_sakura_stone_mine`：低于下限 0 项，高于上限 5 项；最高 85.7%。
- `building_stage`：低于下限 8 项；最低 16.7%，高于上限 1 项；最高 80.0%。
- `building_zoo`：低于下限 6 项；最低 23.3%，高于上限 0 项。

**调整量参考**：若投入固定为 I，毛利率 30%～70% 对应的产出范围是 `I÷0.7～I÷0.3`；若只要求至少 30%，产出必须不低于 `I÷0.7`。辅助 PM 不适用。

## 全量明细

### `building_amusement_park`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_amusement_ground` | `pm_amusement_ground_fair` | 600 | 1,000 | 400 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_amusement_ground` | `pm_amusement_ground_garden` | 800 | 1,200 | 400 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_amusement_ground` | `pm_amusement_ground_electric` | 1,250 | 1,800 | 550 | 44.0% | 30.6% | 30%–70% | — |
| `pmg_amusement_ground` | `pm_amusement_ground_dream` | 1,650 | 2,400 | 750 | 45.5% | 31.2% | 30%–70% | — |
| `pmg_amusement_ride` | `pm_amusement_ride_carousel` | 700 | 1,000 | 300 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_amusement_ride` | `pm_amusement_ride_coaster` | 1,000 | 1,400 | 400 | 40.0% | 28.6% | 低于30% | — |
| `pmg_amusement_ride` | `pm_amusement_ride_neon` | 1,600 | 2,400 | 800 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_amusement_ride` | `pm_amusement_ride_ferris` | 2,350 | 3,400 | 1,050 | 44.7% | 30.9% | 30%–70% | — |
| `pmg_amusement_shop` | `pm_amusement_shop_stall` | 600 | 800 | 200 | 33.3% | 25.0% | 低于30% | — |
| `pmg_amusement_shop` | `pm_amusement_shop_souvenir` | 900 | 1,200 | 300 | 33.3% | 25.0% | 低于30% | — |
| `pmg_amusement_shop` | `pm_amusement_shop_limited` | 1,500 | 2,200 | 700 | 46.7% | 31.8% | 30%–70% | — |
| `pmg_amusement_shop` | `pm_amusement_shop_collab` | 2,100 | 3,000 | 900 | 42.9% | 30.0% | 30%–70% | — |

### `building_aquarium`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_aquarium_ground` | `pm_aquarium_ground_tank` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_aquarium_ground` | `pm_aquarium_ground_marine` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_aquarium_ground` | `pm_aquarium_ground_tunnel` | 900 | 1,200 | 300 | 33.3% | 25.0% | 低于30% | — |
| `pmg_aquarium_ground` | `pm_aquarium_ground_mega` | 1,100 | 1,800 | 700 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_aquarium_animal_type` | `pm_aquarium_type_freshwater` | 400 | 600 | 200 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_aquarium_animal_type` | `pm_aquarium_type_marine` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_aquarium_animal_type` | `pm_aquarium_type_reef` | 850 | 1,200 | 350 | 41.2% | 29.2% | 低于30% | — |
| `pmg_aquarium_animal_type` | `pm_aquarium_type_mammal` | 1,050 | 1,500 | 450 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_aquarium_interaction` | `pm_aquarium_program_feeding` | 400 | 600 | 200 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_aquarium_interaction` | `pm_aquarium_program_concert` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_aquarium_interaction` | `pm_aquarium_program_show` | 750 | 1,200 | 450 | 60.0% | 37.5% | 30%–70% | — |
| `pmg_aquarium_interaction` | `pm_aquarium_program_theater` | 1,300 | 1,800 | 500 | 38.5% | 27.8% | 低于30% | — |
| `pmg_aquarium_education` | `pm_aquarium_program_guide` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_aquarium_education` | `pm_aquarium_program_night` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_aquarium_education` | `pm_aquarium_program_research` | 1,150 | 1,500 | 350 | 30.4% | 23.3% | 低于30% | — |
| `pmg_aquarium_education` | `pm_aquarium_program_documentary` | 1,150 | 1,500 | 350 | 30.4% | 23.3% | 低于30% | — |

### `building_band_headquarter`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_band_food_support` | `pm_band_food_none` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_band_food_support` | `pm_band_food_basic` | 250 | 200 | -50 | -20.0% | -25.0% | 低于30% | — |
| `pmg_band_food_support` | `pm_band_food_regular` | 550 | 400 | -150 | -27.3% | -37.5% | 低于30% | — |
| `pmg_band_food_support` | `pm_band_food_generous` | 880 | 520 | -360 | -40.9% | -69.2% | 低于30% | — |
| `pmg_band_food_support` | `pm_band_food_lavish` | 1,000 | 600 | -400 | -40.0% | -66.7% | 低于30% | — |
| `pmg_band_entertainment_support` | `pm_band_entertainment_none` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_band_entertainment_support` | `pm_band_entertainment_daily` | 150 | 160 | 10 | 6.7% | 6.2% | 低于30% | — |
| `pmg_band_entertainment_support` | `pm_band_entertainment_routine` | 700 | 400 | -300 | -42.9% | -75.0% | 低于30% | — |
| `pmg_band_entertainment_support` | `pm_band_entertainment_active` | 1,430 | 520 | -910 | -63.6% | -175.0% | 低于30% | — |
| `pmg_band_entertainment_support` | `pm_band_entertainment_immersive` | 1,550 | 640 | -910 | -58.7% | -142.2% | 低于30% | — |
| `pmg_band_equipment_support` | `pm_band_equipment_none` | 300 | 0 | -300 | — | — | 仅投入/辅助 | — |
| `pmg_band_equipment_support` | `pm_band_equipment_standard` | 750 | 0 | -750 | — | — | 仅投入/辅助 | — |
| `pmg_band_equipment_support` | `pm_band_equipment_enhanced` | 1,350 | 400 | -950 | -70.4% | -237.5% | 低于30% | — |
| `pmg_band_equipment_support` | `pm_band_equipment_maintained` | 1,710 | 600 | -1,110 | -64.9% | -185.0% | 低于30% | — |
| `pmg_band_equipment_support` | `pm_band_equipment_professional` | 1,950 | 800 | -1,150 | -59.0% | -143.8% | 低于30% | — |

### `building_barn`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_barn` | `pm_wooden_barn` | 0 | 1,600 | 1,600 | — | — | 无投入/仅产出 | — |
| `pmg_base_building_barn` | `pm_iron_barn` | 0 | 2,400 | 2,400 | — | — | 无投入/仅产出 | — |
| `pmg_base_building_barn` | `pm_stell_barn` | 0 | 4,000 | 4,000 | — | — | 无投入/仅产出 | — |
| `pmg_distribution_building_barn` | `pm_market_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_distribution_building_barn` | `pm_relief_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_distribution_building_barn` | `pm_transport_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_manage_building_barn` | `pm_shopkeeper_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_manage_building_barn` | `pm_noble_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_manage_building_barn` | `pm_bureaucrat_barn` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_blue_crystal_mine`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_mining_equipment_building_blue_crystal_mine` | `pm_picks_and_shovels_building_blue_crystal_mine` | 200 | 1,200 | 1,000 | 500.0% | 83.3% | 高于70% | — |
| `pmg_mining_equipment_building_blue_crystal_mine` | `pm_atmospheric_engine_pump_building_blue_crystal_mine` | 700 | 2,400 | 1,700 | 242.9% | 70.8% | 高于70% | — |
| `pmg_mining_equipment_building_blue_crystal_mine` | `pm_condensing_engine_pump_building_blue_crystal_mine` | 1,050 | 3,600 | 2,550 | 242.9% | 70.8% | 高于70% | — |
| `pmg_mining_equipment_building_blue_crystal_mine` | `pm_diesel_pump_building_blue_crystal_mine` | 800 | 4,200 | 3,400 | 425.0% | 81.0% | 高于70% | — |
| `pmg_explosives_building_blue_crystal_mine` | `pm_no_explosives` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_explosives_building_blue_crystal_mine` | `pm_nitroglycerin_building_blue_crystal_mine` | 250 | 720 | 470 | 188.0% | 65.3% | 30%–70% | — |
| `pmg_explosives_building_blue_crystal_mine` | `pm_dynamite_building_blue_crystal_mine` | 500 | 1,200 | 700 | 140.0% | 58.3% | 30%–70% | — |
| `pmg_steam_automation_building_blue_crystal_mine` | `pm_no_steam_automation` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_steam_automation_building_blue_crystal_mine` | `pm_steam_donkey_mine` | 180 | 0 | -180 | — | — | 仅投入/辅助 | — |
| `pmg_train_automation_building_blue_crystal_mine` | `pm_road_carts` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_train_automation_building_blue_crystal_mine` | `pm_rail_transport_mine` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |

### `building_botanical_garden`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_botanical_garden_cultivation` | `pm_botanical_garden_nursery` | 550 | 750 | 200 | 36.4% | 26.7% | 低于30% | — |
| `pmg_botanical_garden_cultivation` | `pm_botanical_garden_fine_flowerbeds` | 800 | 1,250 | 450 | 56.2% | 36.0% | 30%–70% | — |
| `pmg_botanical_garden_cultivation` | `pm_botanical_garden_glasshouse_flowers` | 1,150 | 1,750 | 600 | 52.2% | 34.3% | 30%–70% | — |
| `pmg_botanical_garden_cultivation` | `pm_botanical_garden_rare_greenhouse` | 1,700 | 2,500 | 800 | 47.1% | 32.0% | 30%–70% | — |
| `pmg_botanical_garden_fruit_trees` | `pm_botanical_garden_fruit_trees_none` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_botanical_garden_fruit_trees` | `pm_botanical_garden_courtyard_fruit_trees` | 0 | -100 | -100 | — | — | 负产出/转产 | — |
| `pmg_botanical_garden_fruit_trees` | `pm_botanical_garden_grafted_fruit_trees` | 0 | -50 | -50 | — | — | 负产出/转产 | — |
| `pmg_botanical_garden_fruit_trees` | `pm_botanical_garden_greenhouse_fruit_trees` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_club`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_club_activity` | `pm_club_activity_community` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_club_activity` | `pm_club_activity_exchange` | 450 | 800 | 350 | 77.8% | 43.8% | 30%–70% | — |
| `pmg_club_activity` | `pm_club_activity_network` | 300 | 200 | -100 | -33.3% | -50.0% | 低于30% | — |
| `pmg_club_operation` | `pm_club_operation_member_run` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_club_operation` | `pm_club_operation_advised` | 150 | 200 | 50 | 33.3% | 25.0% | 低于30% | — |
| `pmg_club_operation` | `pm_club_operation_certified` | 450 | 400 | -50 | -11.1% | -12.5% | 低于30% | — |
| `pmg_club_operation` | `pm_club_operation_integrated` | 450 | 0 | -450 | — | — | 仅投入/辅助 | — |

### `building_entertainment_press`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_ent_press_main` | `pm_ent_press_main_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_ent_press_main` | `pm_ent_press_main_manga` | 1,350 | 2,100 | 750 | 55.6% | 35.7% | 30%–70% | — |
| `pmg_ent_press_main` | `pm_ent_press_main_serial` | 1,700 | 2,700 | 1,000 | 58.8% | 37.0% | 30%–70% | — |
| `pmg_ent_press_main` | `pm_ent_press_main_novel` | 2,650 | 4,200 | 1,550 | 58.5% | 36.9% | 30%–70% | — |
| `pmg_ent_press_main` | `pm_ent_press_main_multimedia` | 3,300 | 5,100 | 1,800 | 54.5% | 35.3% | 30%–70% | — |
| `pmg_ent_press_distribution` | `pm_ent_press_distribution_local` | 500 | 600 | 100 | 20.0% | 16.7% | 低于30% | — |
| `pmg_ent_press_distribution` | `pm_ent_press_distribution_national` | 750 | 1,200 | 450 | 60.0% | 37.5% | 30%–70% | — |
| `pmg_ent_press_distribution` | `pm_ent_press_distribution_export` | 1,200 | 1,800 | 600 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_automation_building_entertainment_press` | `pm_tot_ent_press_automation_disabled` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_automation_building_entertainment_press` | `pm_tot_ent_press_automation_watertube` | 450 | 0 | -450 | — | — | 仅投入/辅助 | — |
| `pmg_automation_building_entertainment_press` | `pm_tot_ent_press_automation_rotary` | 900 | 0 | -900 | — | — | 仅投入/辅助 | — |
| `pmg_automation_building_entertainment_press` | `pm_tot_ent_press_automation_assembly` | 550 | 0 | -550 | — | — | 仅投入/辅助 | — |

### `building_game`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_game_traditional_dev` | `pm_game_traditional_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_game_traditional_dev` | `pm_game_traditional_tabletop` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_game_traditional_dev` | `pm_game_traditional_mechanical` | 1,100 | 1,800 | 700 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_game_traditional_dev` | `pm_game_traditional_craft` | 1,800 | 2,700 | 900 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_game_modern_dev` | `pm_game_modern_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_game_modern_dev` | `pm_game_modern_pinball` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_game_modern_dev` | `pm_game_modern_arcade` | 1,150 | 1,800 | 650 | 56.5% | 36.1% | 30%–70% | — |
| `pmg_game_modern_dev` | `pm_game_modern_video` | 1,600 | 2,700 | 1,100 | 68.8% | 40.7% | 30%–70% | — |
| `pmg_game_business` | `pm_game_business_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_game_business` | `pm_game_cartridge_era` | 1,300 | 2,100 | 800 | 61.5% | 38.1% | 30%–70% | — |
| `pmg_game_business` | `pm_game_disc_era` | 1,600 | 2,700 | 1,100 | 68.8% | 40.7% | 30%–70% | — |
| `pmg_game_business` | `pm_game_mobile_era` | 3,100 | 4,500 | 1,400 | 45.2% | 31.1% | 30%–70% | — |
| `pmg_game_operation` | `pm_game_operation_base` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_game_operation` | `pm_game_operation_expansion` | 450 | 800 | 350 | 77.8% | 43.8% | 30%–70% | goods_output_games_mult = -0.05 |
| `pmg_game_operation` | `pm_game_operation_ip` | 1,300 | 1,400 | 100 | 7.7% | 7.1% | 低于30% | goods_output_games_mult = -0.10 |

### `building_goods`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_goods_doll` | `pm_goods_doll_doll` | 500 | 900 | 400 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_goods_doll` | `pm_goods_doll_custom` | 1,100 | 1,800 | 700 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_goods_doll` | `pm_goods_doll_pillow` | 1,300 | 2,100 | 800 | 61.5% | 38.1% | 30%–70% | — |
| `pmg_goods_doll` | `pm_goods_doll_iron` | 1,800 | 2,700 | 900 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_goods_jewelry` | `pm_goods_jewelry_badge` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_goods_jewelry` | `pm_goods_jewelry_pendant` | 1,000 | 1,800 | 800 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_goods_jewelry` | `pm_goods_jewelry_stand` | 1,400 | 2,700 | 1,300 | 92.9% | 48.1% | 30%–70% | — |
| `pmg_goods_jewelry` | `pm_goods_jewelry_premium` | 2,400 | 3,900 | 1,500 | 62.5% | 38.5% | 30%–70% | — |
| `pmg_goods_garage` | `pm_goods_garage_lego` | 500 | 900 | 400 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_goods_garage` | `pm_goods_garage_military_model` | 1,000 | 1,500 | 500 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_goods_garage` | `pm_goods_garage_gundam` | 1,500 | 2,400 | 900 | 60.0% | 37.5% | 30%–70% | — |
| `pmg_goods_garage` | `pm_goods_garage_motor` | 1,750 | 2,700 | 950 | 54.3% | 35.2% | 30%–70% | — |
| `pmg_goods_print` | `pm_goods_print_seal` | 1,050 | 1,500 | 450 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_goods_print` | `pm_goods_print_card` | 1,400 | 2,100 | 700 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_goods_print` | `pm_goods_print_post` | 1,950 | 3,000 | 1,050 | 53.8% | 35.0% | 30%–70% | — |
| `pmg_goods_print` | `pm_goods_print_art` | 2,600 | 3,900 | 1,300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_goods_selling` | `pm_goods_selling_custom` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_goods_selling` | `pm_goods_selling_exhibition` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |
| `pmg_goods_selling` | `pm_goods_selling_specialty` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |
| `pmg_goods_selling` | `pm_goods_selling_chain` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |

### `building_izakaya`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_izakaya_drinks` | `pm_izakaya_hearth_drinks` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_izakaya_drinks` | `pm_izakaya_izakaya_banquet` | 1,000 | 1,800 | 800 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_izakaya_drinks` | `pm_izakaya_city_cocktails` | 1,800 | 3,000 | 1,200 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_izakaya_food` | `pm_izakaya_travelers_stew` | 850 | 1,500 | 650 | 76.5% | 43.3% | 30%–70% | — |
| `pmg_izakaya_food` | `pm_izakaya_izakaya_delicacies` | 1,400 | 2,400 | 1,000 | 71.4% | 41.7% | 30%–70% | — |
| `pmg_izakaya_food` | `pm_izakaya_hearth_banquet` | 2,200 | 3,600 | 1,400 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_izakaya_hospitality` | `pm_izakaya_communal_tables` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_izakaya_hospitality` | `pm_izakaya_counter_longtables` | 300 | 600 | 300 | 100.0% | 50.0% | 30%–70% | — |
| `pmg_izakaya_hospitality` | `pm_izakaya_patron_rooms` | 800 | 1,200 | 400 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_izakaya_kitchen` | `pm_izakaya_brick_stoves` | 100 | 0 | -100 | — | — | 仅投入/辅助 | — |
| `pmg_izakaya_kitchen` | `pm_izakaya_iron_stoves_icehouse` | 550 | 400 | -150 | -27.3% | -37.5% | 低于30% | building_goods_input_mult = -0.05 |
| `pmg_izakaya_kitchen` | `pm_izakaya_electric_cold_kitchen` | 600 | 600 | 0 | 0.0% | 0.0% | 低于30% | building_goods_input_mult = -0.20 |

### `building_keystone_mine`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_mining_equipment_building_keystone_mine` | `pm_picks_and_shovels_building_keystone_mine` | 200 | 1,300 | 1,100 | 550.0% | 84.6% | 高于70% | — |
| `pmg_mining_equipment_building_keystone_mine` | `pm_atmospheric_engine_pump_building_keystone_mine` | 700 | 2,600 | 1,900 | 271.4% | 73.1% | 高于70% | — |
| `pmg_mining_equipment_building_keystone_mine` | `pm_condensing_engine_pump_building_keystone_mine` | 1,050 | 3,900 | 2,850 | 271.4% | 73.1% | 高于70% | — |
| `pmg_mining_equipment_building_keystone_mine` | `pm_diesel_pump_building_keystone_mine` | 800 | 4,550 | 3,750 | 468.8% | 82.4% | 高于70% | — |
| `pmg_explosives_building_keystone_mine` | `pm_no_explosives` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_explosives_building_keystone_mine` | `pm_nitroglycerin_building_keystone_mine` | 250 | 780 | 530 | 212.0% | 67.9% | 30%–70% | — |
| `pmg_explosives_building_keystone_mine` | `pm_dynamite_building_keystone_mine` | 500 | 1,300 | 800 | 160.0% | 61.5% | 30%–70% | — |
| `pmg_steam_automation_building_keystone_mine` | `pm_no_steam_automation` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_steam_automation_building_keystone_mine` | `pm_steam_donkey_mine` | 180 | 0 | -180 | — | — | 仅投入/辅助 | — |
| `pmg_train_automation_building_keystone_mine` | `pm_road_carts` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_train_automation_building_keystone_mine` | `pm_rail_transport_mine` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |

### `building_kissaten`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_kissaten_coffee` | `pm_kissaten_coffee_coffee` | 900 | 1,500 | 600 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_kissaten_coffee` | `pm_kissaten_coffee_milk_coffee` | 1,650 | 3,000 | 1,350 | 81.8% | 45.0% | 30%–70% | — |
| `pmg_kissaten_coffee` | `pm_kissaten_coffee_latte` | 2,500 | 4,500 | 2,000 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_kissaten_tea` | `pm_kissaten_tea_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_kissaten_tea` | `pm_kissaten_tea_black_tea` | 650 | 1,200 | 550 | 84.6% | 45.8% | 30%–70% | — |
| `pmg_kissaten_tea` | `pm_kissaten_tea_milk` | 1,150 | 2,100 | 950 | 82.6% | 45.2% | 30%–70% | — |
| `pmg_kissaten_tea` | `pm_kissaten_tea_cream_soda` | 1,700 | 3,000 | 1,300 | 76.5% | 43.3% | 30%–70% | — |
| `pmg_kissaten_tea` | `pm_kissaten_tea_mixed_juice` | 2,350 | 4,200 | 1,850 | 78.7% | 44.0% | 30%–70% | — |
| `pmg_kissaten_sweet` | `pm_kissaten_sweet_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_kissaten_sweet` | `pm_kissaten_sweet_biscuit` | 850 | 1,500 | 650 | 76.5% | 43.3% | 30%–70% | — |
| `pmg_kissaten_sweet` | `pm_kissaten_sweet_pie` | 1,750 | 3,000 | 1,250 | 71.4% | 41.7% | 30%–70% | — |
| `pmg_kissaten_sweet` | `pm_kissaten_sweet_custard_pudding` | 2,150 | 3,900 | 1,750 | 81.4% | 44.9% | 30%–70% | — |
| `pmg_kissaten_sweet` | `pm_kissaten_sweet_fruit_parfait` | 2,700 | 4,800 | 2,100 | 77.8% | 43.8% | 30%–70% | — |
| `pmg_kissaten_food` | `pm_kissaten_food_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_kissaten_food` | `pm_kissaten_food_sandwich` | 1,050 | 1,800 | 750 | 71.4% | 41.7% | 30%–70% | — |
| `pmg_kissaten_food` | `pm_kissaten_food_curry_rice` | 1,650 | 3,000 | 1,350 | 81.8% | 45.0% | 30%–70% | — |
| `pmg_kissaten_food` | `pm_kissaten_food_omuraisu` | 2,450 | 4,500 | 2,050 | 83.7% | 45.6% | 30%–70% | — |
| `pmg_kissaten_food` | `pm_kissaten_food_seafood_doria` | 3,150 | 5,700 | 2,550 | 81.0% | 44.7% | 30%–70% | — |
| `pmg_kissaten_server` | `pm_kissaten_server_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_kissaten_server` | `pm_kissaten_server_waitress` | 150 | 400 | 250 | 166.7% | 62.5% | 30%–70% | — |
| `pmg_kissaten_server` | `pm_kissaten_server_maid` | 600 | 1,000 | 400 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_kissaten_server` | `pm_kissaten_server_fuwafuwa` | 1,200 | 1,800 | 600 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_kissaten_tool` | `pm_kissaten_tool_table` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |
| `pmg_kissaten_tool` | `pm_kissaten_tool_porcelain` | 350 | 0 | -350 | — | — | 仅投入/辅助 | — |
| `pmg_kissaten_tool` | `pm_kissaten_tool_watertube_boiler` | 350 | 0 | -350 | — | — | 仅投入/辅助 | — |
| `pmg_kissaten_tool` | `pm_kissaten_tool_flash_freezing` | 300 | 0 | -300 | — | — | 仅投入/辅助 | — |

### `building_livestock_ranch`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_livestock_ranch` | `pm_open_air_stockyards` | 0 | 300 | 300 | — | — | 无投入/仅产出 | — |
| `pmg_base_building_livestock_ranch` | `pm_butchering_tools` | 80 | 450 | 370 | 462.5% | 82.2% | 高于70% | — |
| `pmg_base_building_livestock_ranch` | `pm_slaughterhouses` | 200 | 750 | 550 | 275.0% | 73.3% | 高于70% | — |
| `pmg_base_building_livestock_ranch` | `pm_mechanized_slaughtering` | 350 | 1,050 | 700 | 200.0% | 66.7% | 30%–70% | — |
| `pmg_sheep_ranch` | `pm_simple_ranch` | 0 | 100 | 100 | — | — | 无投入/仅产出 | — |
| `pmg_sheep_ranch` | `pm_sheep_farms` | 200 | 375 | 175 | 87.5% | 46.7% | 30%–70% | — |
| `pmg_sheep_ranch` | `pm_intensive_grazing_ranch` | 300 | 650 | 350 | 116.7% | 53.8% | 30%–70% | — |
| `pmg_fencing` | `pm_standard_fences` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_fencing` | `pm_barbed_wire_fences` | 40 | 0 | -40 | — | — | 仅投入/辅助 | — |
| `pmg_fencing` | `pm_electric_fencing` | 70 | 0 | -70 | — | — | 仅投入/辅助 | — |
| `pmg_refrigeration_building_livestock_ranch` | `pm_unrefrigerated` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_refrigeration_building_livestock_ranch` | `pm_refrigerated_storage_building_livestock_ranch` | 30 | 0 | -30 | — | — | 仅投入/辅助 | — |
| `pmg_refrigeration_building_livestock_ranch` | `pm_refrigerated_rail_cars_building_livestock_ranch` | 60 | 0 | -60 | — | — | 仅投入/辅助 | — |
| `pmg_tot_dairy_livestock_ranch` | `pm_tot_dairy_traditional` | 40 | 80 | 40 | 100.0% | 50.0% | 30%–70% | — |
| `pmg_tot_dairy_livestock_ranch` | `pm_tot_dairy_mechanized` | 60 | 160 | 100 | 166.7% | 62.5% | 30%–70% | — |
| `pmg_tot_dairy_livestock_ranch` | `pm_tot_dairy_fresh` | 140 | 300 | 160 | 114.3% | 53.3% | 30%–70% | — |
| `pmg_tot_dairy_livestock_ranch` | `pm_tot_dairy_refrigerated` | 180 | 400 | 220 | 122.2% | 55.0% | 30%–70% | — |

### `building_musical_instrument`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_building_musical_instrument_main` | `pm_musical_instrument_main_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_building_musical_instrument_main` | `pm_musical_instrument_main_wood` | 800 | 1,200 | 400 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_building_musical_instrument_main` | `pm_musical_instrument_main_iron` | 1,000 | 1,800 | 800 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_building_musical_instrument_main` | `pm_musical_instrument_main_steel` | 2,000 | 3,600 | 1,600 | 80.0% | 44.4% | 30%–70% | — |
| `pmg_building_musical_instrument_main` | `pm_musical_instrument_main_electric` | 2,600 | 4,800 | 2,200 | 84.6% | 45.8% | 30%–70% | — |
| `pmg_automation_building_tooling_workshop` | `pm_automation_disabled` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_automation_building_tooling_workshop` | `pm_watertube_boiler_building_tooling_workshop` | 300 | 0 | -300 | — | — | 仅投入/辅助 | — |
| `pmg_automation_building_tooling_workshop` | `pm_rotary_valve_engine_building_tooling_workshop` | 450 | 0 | -450 | — | — | 仅投入/辅助 | — |
| `pmg_automation_building_tooling_workshop` | `pm_assembly_lines_building_tooling_workshop` | 550 | 0 | -550 | — | — | 仅投入/辅助 | — |

### `building_originium_mine`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_mining_equipment_building_originium_mine` | `pm_picks_and_shovels_building_originium_mine` | 200 | 1,500 | 1,300 | 650.0% | 86.7% | 高于70% | — |
| `pmg_mining_equipment_building_originium_mine` | `pm_atmospheric_engine_pump_building_originium_mine` | 700 | 3,000 | 2,300 | 328.6% | 76.7% | 高于70% | — |
| `pmg_mining_equipment_building_originium_mine` | `pm_condensing_engine_pump_building_originium_mine` | 1,050 | 4,500 | 3,450 | 328.6% | 76.7% | 高于70% | — |
| `pmg_mining_equipment_building_originium_mine` | `pm_diesel_pump_building_originium_mine` | 800 | 5,250 | 4,450 | 556.2% | 84.8% | 高于70% | — |
| `pmg_explosives_building_originium_mine` | `pm_no_explosives` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_explosives_building_originium_mine` | `pm_nitroglycerin_building_originium_mine` | 250 | 900 | 650 | 260.0% | 72.2% | 高于70% | — |
| `pmg_explosives_building_originium_mine` | `pm_dynamite_building_originium_mine` | 500 | 1,500 | 1,000 | 200.0% | 66.7% | 30%–70% | — |
| `pmg_steam_automation_building_originium_mine` | `pm_no_steam_automation` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_steam_automation_building_originium_mine` | `pm_steam_donkey_mine` | 180 | 0 | -180 | — | — | 仅投入/辅助 | — |
| `pmg_train_automation_building_originium_mine` | `pm_road_carts` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_train_automation_building_originium_mine` | `pm_rail_transport_mine` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |

### `building_publisher`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_publisher_main` | `pm_publisher_main_null` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_publisher_main` | `pm_publisher_main_general_wood` | 1,100 | 1,500 | 400 | 36.4% | 26.7% | 低于30% | — |
| `pmg_publisher_main` | `pm_publisher_main_general_iron` | 1,750 | 2,500 | 750 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_publisher_main` | `pm_publisher_main_general_steel` | 2,250 | 3,250 | 1,000 | 44.4% | 30.8% | 30%–70% | — |
| `pmg_publisher_main` | `pm_publisher_main_general_electric` | 3,300 | 4,500 | 1,200 | 36.4% | 26.7% | 低于30% | — |
| `pmg_publisher_business` | `pm_publisher_comprehensive_publishing` | 0 | 0 | 0 | — | — | 无商品流 | building_goods_input_mult = -0.05 |
| `pmg_publisher_business` | `pm_publisher_professional_journal` | 600 | 750 | 150 | 25.0% | 20.0% | 低于30% | — |
| `pmg_publisher_business` | `pm_publisher_mass_magazine` | 600 | 960 | 360 | 60.0% | 37.5% | 30%–70% | — |

### `building_religious_center`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_religious_center_assembly` | `pm_religious_center_daily_assembly` | 750 | 1,250 | 500 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_religious_center_assembly` | `pm_religious_center_public_instruction` | 1,450 | 2,250 | 800 | 55.2% | 35.6% | 30%–70% | — |
| `pmg_religious_center_assembly` | `pm_religious_center_city_celebration` | 2,300 | 3,750 | 1,450 | 63.0% | 38.7% | 30%–70% | — |
| `pmg_religious_center_rites` | `pm_religious_center_common_rites` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_religious_center_rites` | `pm_religious_center_trinity_rite` | 700 | 1,000 | 300 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_religious_center_rites` | `pm_religious_center_starbeat_rite` | 600 | 1,000 | 400 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_religious_center_rites` | `pm_religious_center_kiseki_rite` | 600 | 1,000 | 400 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_religious_center_facilities` | `pm_religious_center_traditional_facilities` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_religious_center_facilities` | `pm_religious_center_printed_liturgy` | 500 | 750 | 250 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_religious_center_facilities` | `pm_religious_center_electric_facilities` | 950 | 1,500 | 550 | 57.9% | 36.7% | 30%–70% | — |

### `building_sakura_stone_mine`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_mining_equipment_building_sakura_stone_mine` | `pm_picks_and_shovels_building_sakura_stone_mine` | 200 | 1,400 | 1,200 | 600.0% | 85.7% | 高于70% | — |
| `pmg_mining_equipment_building_sakura_stone_mine` | `pm_atmospheric_engine_pump_building_sakura_stone_mine` | 700 | 2,800 | 2,100 | 300.0% | 75.0% | 高于70% | — |
| `pmg_mining_equipment_building_sakura_stone_mine` | `pm_condensing_engine_pump_building_sakura_stone_mine` | 1,050 | 4,200 | 3,150 | 300.0% | 75.0% | 高于70% | — |
| `pmg_mining_equipment_building_sakura_stone_mine` | `pm_diesel_pump_building_sakura_stone_mine` | 800 | 4,900 | 4,100 | 512.5% | 83.7% | 高于70% | — |
| `pmg_explosives_building_sakura_stone_mine` | `pm_no_explosives` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_explosives_building_sakura_stone_mine` | `pm_nitroglycerin_building_sakura_stone_mine` | 250 | 840 | 590 | 236.0% | 70.2% | 高于70% | — |
| `pmg_explosives_building_sakura_stone_mine` | `pm_dynamite_building_sakura_stone_mine` | 500 | 1,400 | 900 | 180.0% | 64.3% | 30%–70% | — |
| `pmg_steam_automation_building_sakura_stone_mine` | `pm_no_steam_automation` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_steam_automation_building_sakura_stone_mine` | `pm_steam_donkey_mine` | 180 | 0 | -180 | — | — | 仅投入/辅助 | — |
| `pmg_train_automation_building_sakura_stone_mine` | `pm_road_carts` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_train_automation_building_sakura_stone_mine` | `pm_rail_transport_mine` | 150 | 0 | -150 | — | — | 仅投入/辅助 | — |

### `building_stage`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_stage_operation` | `pm_stage_operation_public` | 450 | 1,000 | 550 | 122.2% | 55.0% | 30%–70% | — |
| `pmg_stage_operation` | `pm_stage_operation_ticketed` | 750 | 1,500 | 750 | 100.0% | 50.0% | 30%–70% | — |
| `pmg_stage_operation` | `pm_stage_operation_hospitality` | 1,500 | 2,500 | 1,000 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_stage_operation` | `pm_stage_operation_festival` | 2,700 | 4,500 | 1,800 | 66.7% | 40.0% | 30%–70% | — |
| `pmg_stage_scale` | `pm_stage_scale_small` | 200 | 1,000 | 800 | 400.0% | 80.0% | 高于70% | — |
| `pmg_stage_scale` | `pm_stage_scale_compact` | 600 | 1,500 | 900 | 150.0% | 60.0% | 30%–70% | — |
| `pmg_stage_scale` | `pm_stage_scale_medium` | 1,600 | 2,500 | 900 | 56.2% | 36.0% | 30%–70% | — |
| `pmg_stage_scale` | `pm_stage_scale_large` | 3,250 | 5,000 | 1,750 | 53.8% | 35.0% | 30%–70% | — |
| `pmg_stage_merchandising` | `pm_stage_merchandising_none` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_stage_merchandising` | `pm_stage_merchandising_basic` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_stage_merchandising` | `pm_stage_merchandising_standard` | 750 | 1,000 | 250 | 33.3% | 25.0% | 低于30% | — |
| `pmg_stage_merchandising` | `pm_stage_merchandising_full` | 1,500 | 1,800 | 300 | 20.0% | 16.7% | 低于30% | — |
| `pmg_stage_merchandising` | `pm_stage_merchandising_premium` | 2,250 | 2,800 | 550 | 24.4% | 19.6% | 低于30% | — |
| `pmg_stage_media` | `pm_stage_media_none` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_stage_media` | `pm_stage_media_flyers` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_stage_media` | `pm_stage_media_magazines` | 1,100 | 1,400 | 300 | 27.3% | 21.4% | 低于30% | — |
| `pmg_stage_media` | `pm_stage_media_radio` | 1,550 | 2,200 | 650 | 41.9% | 29.5% | 低于30% | — |
| `pmg_stage_media` | `pm_stage_media_ip_collab` | 2,300 | 3,200 | 900 | 39.1% | 28.1% | 低于30% | — |

### `building_tot_chireiden_fusion`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_tot_chireiden_fusion` | `pm_tot_chireiden_fusion_generation` | 250 | 750 | 500 | 200.0% | 66.7% | 30%–70% | — |

### `building_tot_golden_hall_construction_site`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_tot_golden_hall_construction_site` | `pm_default_building_tot_golden_hall_construction_site` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_tot_golden_hall_large_contract`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_tot_golden_hall_large_contract` | `pm_default_building_tot_golden_hall_large_contract` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_tot_golden_hall_monument`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_tot_golden_hall_monument` | `pm_default_building_tot_golden_hall_monument` | 0 | 0 | 0 | — | — | 无商品流 | goods_output_experience_mult = 0.10；goods_output_services_mult = 0.05 |
| `pmg_base_building_tot_golden_hall_monument` | `pm_monument_prestige_only` | 0 | 0 | 0 | — | — | 无商品流 | — |
| `pmg_base_building_tot_golden_hall_monument` | `pm_monument_no_effects` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_tot_golden_hall_naming_contract`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_tot_golden_hall_naming_contract` | `pm_default_building_tot_golden_hall_naming_contract` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_tot_golden_hall_small_contract`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_base_building_tot_golden_hall_small_contract` | `pm_default_building_tot_golden_hall_small_contract` | 0 | 0 | 0 | — | — | 无商品流 | — |

### `building_tot_kappa_power`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_tot_kappa_power` | `pm_tot_kappa_precision_generation` | 400 | 750 | 350 | 87.5% | 46.7% | 30%–70% | — |

### `building_zoo`

| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |
|---|---|---:|---:|---:|---:|---:|---|---|
| `pmg_zoo_ground` | `pm_zoo_ground_pen` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_zoo_ground` | `pm_zoo_ground_park` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_zoo_ground` | `pm_zoo_ground_stadium` | 1,050 | 1,500 | 450 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_zoo_ground` | `pm_zoo_ground_eco` | 1,250 | 1,800 | 550 | 44.0% | 30.6% | 30%–70% | — |
| `pmg_zoo_animal_type` | `pm_zoo_type_small` | 650 | 900 | 250 | 38.5% | 27.8% | 低于30% | — |
| `pmg_zoo_animal_type` | `pm_zoo_type_predator` | 650 | 900 | 250 | 38.5% | 27.8% | 低于30% | — |
| `pmg_zoo_animal_type` | `pm_zoo_type_large` | 600 | 900 | 300 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_zoo_animal_type` | `pm_zoo_type_star` | 1,050 | 1,500 | 450 | 42.9% | 30.0% | 30%–70% | — |
| `pmg_zoo_interaction` | `pm_zoo_interaction_basic` | 400 | 600 | 200 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_zoo_interaction` | `pm_zoo_interaction_feeding` | 450 | 600 | 150 | 33.3% | 25.0% | 低于30% | — |
| `pmg_zoo_interaction` | `pm_zoo_interaction_show` | 900 | 1,200 | 300 | 33.3% | 25.0% | 低于30% | — |
| `pmg_zoo_interaction` | `pm_zoo_interaction_grand` | 1,200 | 1,800 | 600 | 50.0% | 33.3% | 30%–70% | — |
| `pmg_zoo_education` | `pm_zoo_education_guide` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_zoo_education` | `pm_zoo_education_natural_history` | 550 | 900 | 350 | 63.6% | 38.9% | 30%–70% | — |
| `pmg_zoo_education` | `pm_zoo_education_conservation` | 1,150 | 1,500 | 350 | 30.4% | 23.3% | 低于30% | — |
| `pmg_zoo_education` | `pm_zoo_education_documentary` | 1,150 | 1,500 | 350 | 30.4% | 23.3% | 低于30% | — |
