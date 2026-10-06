# 毛利率低于 30% 的生产方式：改进清单

共 **47 项**，其中 **32 项**属于可自营建筑，另 15 项属于 `no_ownership` 的乐队总部和社团。口径固定为 `（商品产出基准价－商品投入基准价）÷商品产出基准价`；30% 的最低产出价为 `投入价÷0.7`。

## 判断方法

- 明细表的“补足产值”和“仅增产参考”表示该 PM *单项*达到 30% 毛利所需的最小改动，不是整栋建筑的最终修改建议。仅增产参考把差额加到该 PM 产值最大的现有产出商品，按整数数量取整。若保持产出不变，也可减少投入 `当前投入－0.7×当前产出`。
- “完整组合低毛利数”枚举这栋建筑各 PMG 所有理论选项，并计入代码里的建筑投入倍率和指定商品的产出倍率；不筛科技、法律、AI 选择或无就业状态，不含工资与市场价。因此它用来识别联动风险，不能当作玩家遭遇概率。
- 即使单项毛利不足，整栋建筑仍可能高于 30%；相反，单项全部达标时，昂贵的辅助 PM 也可能使整栋建筑低于 30%。

## 优先处理建议

1. **咖啡厅**：当前开局标准咖啡＋普通女仆＋基本桌椅约 37.1%；完整组合 21/7,500 低于 30%，主要是少量菜单搭配高价设备。仍须在游戏内复测 AI 选档和市场价。
2. **酒馆**：已给收费接待档增加体验产出，降低厨房持续消耗；81 种完整组合均达到 30%。下一步优先看谷子工坊的 IP/销售组及娱乐传媒社的发行/自动化组。
3. **游戏工坊 IP 运营**：单项投入 1,300、产出 1,400，毛利 7.1%，还把游戏产出乘以 0.9；选它的 64 种理论组合全部低于 30%。如保留投入及游戏减产，`experience` 至少先从 35 提到 47，才让该 PM 自身过 30%，然后再核对完整组合。也可降低服务/电话投入并减轻游戏减产。
4. **舞台**：更新运营与规模产出后，400 种理论组合中只有 2 种为 29.9%，其余落在 30%～70%。豪华舞台规模档单项毛利为 35.0%；剩余边界组合涉及大型舞台、最高档场贩与杂志宣传。
5. **乐队总部与社团**：这两栋建筑均为 `ownership_type = no_ownership`，乐队 11 项、社团 4 项低毛利不宜强制达到商业建筑标准。乐队总部所有有产出的组合商品毛利都低于 30%，符合补贴型设施的可能设计；若希望它们自负盈亏，需另设经营产出。
6. **水族馆、动物园、游乐园等场馆**：多数偏差只差一小档产出，且同建筑多组会互相抵消。优先微调完整组合持续低毛利的档位。

## 各建筑完整组合情况

| 建筑 | 毛利低于30%的理论组合 | 有正产出的理论组合 | 占比 |
|---|---:|---:|---:|
| `building_amusement_park` | 13 | 64 | 20.3% |
| `building_aquarium` | 88 | 256 | 34.4% |
| `building_band_headquarter` | 123 | 123 | 100.0% |
| `building_botanical_garden` | 5 | 16 | 31.2% |
| `building_club` | 10 | 12 | 83.3% |
| `building_entertainment_press` | 46 | 60 | 76.7% |
| `building_game` | 67 | 192 | 34.9% |
| `building_kissaten` | 14 | 6,000 | 0.2% |
| `building_musical_instrument` | 7 | 16 | 43.8% |
| `building_publisher` | 6 | 14 | 42.9% |
| `building_stage` | 2 | 400 | 0.5% |
| `building_zoo` | 122 | 256 | 47.7% |

## 47 low-margin PMs

### `building_amusement_park`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_amusement_ride_coaster` | 1,000 | 1,400 | 28.6% | +28.6 | `experience` +1（35→36） | 7/16 |
| `pm_amusement_shop_stall` | 600 | 800 | 25.0% | +57.1 | `experience` +2（20→22） | 5/16 |
| `pm_amusement_shop_souvenir` | 900 | 1,200 | 25.0% | +85.7 | `experience` +3（30→33） | 7/16 |

### `building_aquarium`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_aquarium_ground_tunnel` | 900 | 1,200 | 25.0% | +85.7 | `exhibition` +2（20→22） | 40/64 |
| `pm_aquarium_type_reef` | 850 | 1,200 | 29.2% | +14.3 | `animal_performance` +1（20→21） | 24/64 |
| `pm_aquarium_program_concert` | 450 | 600 | 25.0% | +42.9 | `animal_performance` +1（10→11） | 28/64 |
| `pm_aquarium_program_theater` | 1,300 | 1,800 | 27.8% | +57.1 | `animal_performance` +1（30→31） | 28/64 |
| `pm_aquarium_program_research` | 1,150 | 1,500 | 23.3% | +142.9 | `exhibition` +3（25→28） | 40/64 |
| `pm_aquarium_program_documentary` | 1,150 | 1,500 | 23.3% | +142.9 | `exhibition` +3（25→28） | 40/64 |

### `building_band_headquarter`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_band_food_basic` | 250 | 200 | -25.0% | +157.1 | `experience` +4（5→9） | 25/25 |
| `pm_band_food_regular` | 550 | 400 | -37.5% | +385.7 | `experience` +10（10→20） | 25/25 |
| `pm_band_food_generous` | 880 | 520 | -69.2% | +737.1 | `experience` +19（13→32） | 25/25 |
| `pm_band_food_lavish` | 1,000 | 600 | -66.7% | +828.6 | `experience` +21（15→36） | 25/25 |
| `pm_band_entertainment_daily` | 150 | 160 | 6.2% | +54.3 | `experience` +2（4→6） | 25/25 |
| `pm_band_entertainment_routine` | 700 | 400 | -75.0% | +600.0 | `experience` +15（10→25） | 25/25 |
| `pm_band_entertainment_active` | 1,430 | 520 | -175.0% | +1,522.9 | `experience` +39（13→52） | 25/25 |
| `pm_band_entertainment_immersive` | 1,550 | 640 | -142.2% | +1,574.3 | `experience` +40（16→56） | 25/25 |
| `pm_band_equipment_enhanced` | 1,350 | 400 | -237.5% | +1,528.6 | `performance` +16（4→20） | 25/25 |
| `pm_band_equipment_maintained` | 1,710 | 600 | -185.0% | +1,842.9 | `performance` +19（6→25） | 25/25 |
| `pm_band_equipment_professional` | 1,950 | 800 | -143.8% | +1,985.7 | `performance` +20（8→28） | 25/25 |

### `building_botanical_garden`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_botanical_garden_nursery` | 550 | 750 | 26.7% | +35.7 | `ornamental_plants` +1（15→16） | 4/4 |

### `building_club`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_club_activity_community` | 450 | 600 | 25.0% | +42.9 | `experience` +2（15→17） | 4/4 |
| `pm_club_activity_network` | 300 | 200 | -50.0% | +228.6 | `experience` +6（5→11） | 4/4 |
| `pm_club_operation_advised` | 150 | 200 | 25.0% | +14.3 | `experience` +1（5→6） | 2/3 |
| `pm_club_operation_certified` | 450 | 400 | -12.5% | +242.9 | `experience` +7（10→17） | 3/3 |

### `building_entertainment_press`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_ent_press_distribution_local` | 500 | 600 | 16.7% | +114.3 | `entertainment_publications` +2（10→12） | 16/20 |

### `building_game`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_game_operation_base` | 450 | 600 | 25.0% | +42.9 | `experience` +2（15→17） | 1/64 |
| `pm_game_operation_ip` | 1,300 | 1,400 | 7.1% | +457.1 | `experience` +12（35→47） | 64/64 |

### `building_izakaya`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_izakaya_iron_stoves_icehouse` | 550 | 400 | -37.5% | +385.7 | `experience` +10（10→20） | 0/27 |
| `pm_izakaya_electric_cold_kitchen` | 600 | 600 | 0.0% | +257.1 | `experience` +7（15→22） | 0/27 |

### `building_publisher`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_publisher_main_general_wood` | 1,100 | 1,500 | 26.7% | +71.4 | `publications` +2（30→32） | 1/3 |
| `pm_publisher_main_general_electric` | 3,300 | 4,500 | 26.7% | +214.3 | `publications` +5（90→95） | 2/3 |
| `pm_publisher_professional_journal` | 600 | 750 | 20.0% | +107.1 | `publications` +3（15→18） | 5/5 |

### `building_stage`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_stage_merchandising_basic` | 450 | 600 | 25.0% | +42.9 | `experience` +2（15→17） | 0/80 |
| `pm_stage_merchandising_standard` | 750 | 1,000 | 25.0% | +71.4 | `experience` +2（25→27） | 0/80 |
| `pm_stage_merchandising_full` | 1,500 | 1,800 | 16.7% | +342.9 | `experience` +9（45→54） | 0/80 |
| `pm_stage_merchandising_premium` | 2,250 | 2,800 | 19.6% | +414.3 | `experience` +11（70→81） | 2/80 |
| `pm_stage_media_flyers` | 450 | 600 | 25.0% | +42.9 | `experience` +2（15→17） | 0/80 |
| `pm_stage_media_magazines` | 1,100 | 1,400 | 21.4% | +171.4 | `experience` +5（35→40） | 2/80 |
| `pm_stage_media_radio` | 1,550 | 2,200 | 29.5% | +14.3 | `experience` +1（55→56） | 0/80 |
| `pm_stage_media_ip_collab` | 2,300 | 3,200 | 28.1% | +85.7 | `experience` +3（80→83） | 0/80 |

### `building_zoo`

| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |
|---|---:|---:|---:|---:|---|---:|
| `pm_zoo_type_small` | 650 | 900 | 27.8% | +28.6 | `exhibition` +1（15→16） | 32/64 |
| `pm_zoo_type_predator` | 650 | 900 | 27.8% | +28.6 | `exhibition` +1（15→16） | 32/64 |
| `pm_zoo_interaction_feeding` | 450 | 600 | 25.0% | +42.9 | `animal_performance` +1（10→11） | 32/64 |
| `pm_zoo_interaction_show` | 900 | 1,200 | 25.0% | +85.7 | `animal_performance` +2（20→22） | 32/64 |
| `pm_zoo_education_conservation` | 1,150 | 1,500 | 23.3% | +142.9 | `exhibition` +3（25→28） | 61/64 |
| `pm_zoo_education_documentary` | 1,150 | 1,500 | 23.3% | +142.9 | `exhibition` +3（25→28） | 61/64 |
