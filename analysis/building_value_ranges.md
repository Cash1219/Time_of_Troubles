# Base-price goods value ranges for all buildings

Effective vanilla and mod definitions: 144 buildings (114 vanilla, 30 mod).

Each figure is per building level at full employment and base goods prices. One PM is selected from each PM group. The six extrema in a row may come from six different selections. Goods-input and goods-output multipliers in selected PMs are applied to the entire building. Wages, market prices, throughput, ownership and legal/technology availability are excluded. Explicitly unbuildable buildings remain in scope.

## All buildings

| Measure | Input | Output | Goods surplus | Building | PM selection |
|---|---:|---:|---:|---|---|
| minimum input | 0 | 0 | 0 | `building_angkor_wat` | `pm_default_building_angkor_wat` |
| maximum input | 12,250 | 19,800 | 7,550 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_porcelain` |
| minimum output | 0 | 0 | 0 | `building_angkor_wat` | `pm_default_building_angkor_wat` |
| maximum output | 12,050 | 19,800 | 7,750 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_table` |
| minimum surplus | 7,900 | 0 | -7,900 | `building_construction_sector` | `pm_arc_welded_buildings` |
| maximum surplus | 12,050 | 19,800 | 7,750 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_table` |

## Vanilla buildings

| Measure | Input | Output | Goods surplus | Building | PM selection |
|---|---:|---:|---:|---|---|
| minimum input | 0 | 0 | 0 | `building_angkor_wat` | `pm_default_building_angkor_wat` |
| maximum input | 7,900 | 0 | -7,900 | `building_construction_sector` | `pm_arc_welded_buildings` |
| minimum output | 0 | 0 | 0 | `building_angkor_wat` | `pm_default_building_angkor_wat` |
| maximum output | 5,000 | 7,500 | 2,500 | `building_explosives_factory` | `pm_brine_electrolysis` |
| minimum surplus | 7,900 | 0 | -7,900 | `building_construction_sector` | `pm_arc_welded_buildings` |
| maximum surplus | 1,300 | 5,000 | 3,700 | `building_sulfur_mine` | `pm_diesel_pump_building_sulfur_mine`; `pm_dynamite_building_sulfur_mine`; `pm_no_steam_automation`; `pm_road_carts` |

## Mod buildings

| Measure | Input | Output | Goods surplus | Building | PM selection |
|---|---:|---:|---:|---|---|
| minimum input | 0 | 1,600 | 1,600 | `building_barn` | `pm_wooden_barn`; `pm_market_barn`; `pm_shopkeeper_barn` |
| maximum input | 12,250 | 19,800 | 7,550 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_porcelain` |
| minimum output | 300 | 0 | -300 | `building_band_headquarter` | `pm_band_food_none`; `pm_band_entertainment_none`; `pm_band_equipment_none` |
| maximum output | 12,050 | 19,800 | 7,750 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_table` |
| minimum surplus | 4,380 | 1,920 | -2,460 | `building_band_headquarter` | `pm_band_food_lavish`; `pm_band_entertainment_active`; `pm_band_equipment_professional` |
| maximum surplus | 12,050 | 19,800 | 7,750 | `building_kissaten` | `pm_kissaten_coffee_latte`; `pm_kissaten_tea_mixed_juice`; `pm_kissaten_sweet_fruit_parfait`; `pm_kissaten_food_seafood_doria`; `pm_kissaten_server_fuwafuwa`; `pm_kissaten_tool_table` |

## Smallest positive values

| Scope | Measure | Input | Output | Goods surplus | Building | PM selection |
|---|---|---:|---:|---:|---|---|
| All | Input > 0 | 30 | 2,100 | 2,070 | `building_sugar_plantation` | `default_building_sugar_plantation`; `vacuum_pan_sugar`; `slave_exploitation_sugar`; `pm_road_carts` |
| All | Output > 0 | 0 | 74.9 | 74.9 | `building_subsistence_orchard` | `default_building_subsistence_orchard`; `pm_home_workshops_no_building_subsistence_orchard`; `pm_serfdom_no` |
| Vanilla | Input > 0 | 30 | 2,100 | 2,070 | `building_sugar_plantation` | `default_building_sugar_plantation`; `vacuum_pan_sugar`; `slave_exploitation_sugar`; `pm_road_carts` |
| Vanilla | Output > 0 | 0 | 74.9 | 74.9 | `building_subsistence_orchard` | `default_building_subsistence_orchard`; `pm_home_workshops_no_building_subsistence_orchard`; `pm_serfdom_no` |
| Mod | Input > 0 | 40 | 480 | 440 | `building_livestock_ranch` | `pm_open_air_stockyards`; `pm_simple_ranch`; `pm_standard_fences`; `pm_unrefrigerated`; `pm_tot_dairy_traditional` |
| Mod | Output > 0 | 450 | 160 | -290 | `building_band_headquarter` | `pm_band_food_none`; `pm_band_entertainment_daily`; `pm_band_equipment_none` |


## Every building

| Building | Source | Group | Buildable | Combinations | Input min | Input max | Output min | Output max | Surplus min | Surplus max |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `building_amusement_park` | mod | `bg_entertainment` | yes | 16 | 1,850 | 3,950 | 2,800 | 8,000 | 950 | 4,050 |
| `building_angkor_wat` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_aquarium` | mod | `bg_entertainment` | yes | 48 | 1,350 | 7,000 | 2,500 | 9,600 | 200 | 3,550 |
| `building_argebam` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_arms_industry` | vanilla | `bg_military_industry` | unspecified | 12 | 800 | 3,150 | 1,800 | 6,000 | 450 | 3,400 |
| `building_army_logistics_center` | vanilla | `bg_army_logistics_center` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_art_academy` | vanilla | `bg_arts` | unspecified | 24 | 300 | 1,000 | 1,000 | 2,000 | 700 | 1,000 |
| `building_artillery_foundry` | vanilla | `bg_military_industry` | unspecified | 12 | 1,000 | 3,750 | 1,750 | 6,300 | 200 | 3,100 |
| `building_automotive_industry` | vanilla | `bg_heavy_industry` | unspecified | 16 | 1,000 | 2,440 | 2,400 | 5,000 | 360 | 3,600 |
| `building_banana_plantation` | vanilla | `bg_plantations` | unspecified | 12 | 0 | 450 | 900 | 1,650 | 750 | 1,350 |
| `building_band_headquarter` | mod | `bg_entertainment` | yes | 125 | 300 | 4,500 | 0 | 2,040 | -2,460 | -290 |
| `building_barn` | mod | `bg_private_infrastructure` | no | 27 | 0 | 0 | 1,600 | 4,000 | 1,600 | 4,000 |
| `building_barrack` | vanilla | `bg_army` | unspecified | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_big_ben` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_blue_crystal_mine` | mod | `bg_mining` | no | 48 | 200 | 1,880 | 1,200 | 5,400 | 670 | 4,100 |
| `building_botanical_garden` | mod | `bg_entertainment` | yes | 16 | 200 | 2,400 | 1,000 | 5,550 | 800 | 3,150 |
| `building_capitol_hill` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_central_park` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_chemical_plant` | vanilla | `bg_heavy_industry` | unspecified | 3 | 1,900 | 4,000 | 2,700 | 6,000 | 800 | 2,000 |
| `building_chichen_itza` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_club` | mod | `bg_entertainment` | yes | 12 | 300 | 900 | 200 | 1,200 | -550 | 400 |
| `building_coal_mine` | vanilla | `bg_mining` | unspecified | 48 | 200 | 1,510 | 660 | 3,450 | 250 | 2,150 |
| `building_coffee_plantation` | vanilla | `bg_plantations` | unspecified | 36 | 0 | 770 | 1,250 | 3,000 | 1,100 | 2,380 |
| `building_company_headquarter` | vanilla | `bg_company_headquarter` | no | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_company_regional_headquarter` | vanilla | `bg_company_regional_headquarter` | no | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_conscription_center` | vanilla | `bg_conscription` | no | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_construction_sector` | vanilla | `bg_construction` | unspecified | 4 | 2,000 | 7,900 | 0 | 0 | -7,900 | -2,000 |
| `building_cotton_plantation` | vanilla | `bg_plantations` | unspecified | 12 | 0 | 450 | 900 | 2,000 | 750 | 1,700 |
| `building_cristo_redentor` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_dye_plantation` | vanilla | `bg_plantations` | unspecified | 12 | 0 | 450 | 1,200 | 2,400 | 1,050 | 2,100 |
| `building_easter_island_heads` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_eiffel_tower` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_electrics_industry` | vanilla | `bg_heavy_industry` | unspecified | 2 | 2,800 | 4,300 | 4,200 | 6,000 | 1,400 | 1,700 |
| `building_entertainment_press` | mod | `bg_entertainment` | unspecified | 12 | 1,500 | 3,900 | 2,400 | 5,700 | 450 | 2,250 |
| `building_estacion_de_madrid_atocha` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_explosives_factory` | vanilla | `bg_heavy_industry` | unspecified | 4 | 1,600 | 5,000 | 2,500 | 7,500 | 900 | 2,500 |
| `building_eye_of_sahara` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_financial_district` | vanilla | `bg_financial_districts` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_fishing_wharf` | vanilla | `bg_fishing` | unspecified | 12 | 0 | 1,220 | 500 | 2,000 | 80 | 1,200 |
| `building_food_industry` | vanilla | `bg_light_industry` | unspecified | 90 | 800 | 5,250 | 1,350 | 7,500 | 150 | 2,650 |
| `building_forbidden_city` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_furniture_manufactory` | vanilla | `bg_light_industry` | unspecified | 36 | 800 | 3,050 | 1,350 | 4,950 | 0 | 2,450 |
| `building_game` | mod | `bg_entertainment` | unspecified | 192 | 600 | 7,800 | 600 | 11,300 | -900 | 4,400 |
| `building_giza_necropolis` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_glassworks` | vanilla | `bg_light_industry` | unspecified | 24 | 600 | 2,800 | 1,200 | 5,300 | 200 | 2,900 |
| `building_gold_field` | vanilla | `bg_gold_fields` | no | 1 | 0 | 0 | 1,000 | 1,000 | 1,000 | 1,000 |
| `building_gold_mine` | vanilla | `bg_mining` | unspecified | 48 | 200 | 1,880 | 800 | 4,000 | 270 | 2,700 |
| `building_goods` | mod | `bg_entertainment` | unspecified | 1,024 | 2,800 | 8,850 | 4,200 | 13,200 | 1,250 | 4,500 |
| `building_government_administration` | vanilla | `bg_bureaucracy` | unspecified | 16 | 0 | 950 | 0 | 0 | -950 | 0 |
| `building_gran_teatro_de_la_habana` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 300 | 0 | 1,000 | 0 | 700 |
| `building_hagia_sophia` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_halloween_castledracula` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_iron_mine` | vanilla | `bg_mining` | unspecified | 48 | 200 | 1,880 | 800 | 3,600 | 270 | 2,300 |
| `building_izakaya` | mod | `bg_light_industry` | unspecified | 81 | 1,500 | 5,082.5 | 2,400 | 8,400 | 900 | 4,080 |
| `building_kaiserforum_1` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_kaiserforum_2` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_kaiserforum_3` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_kaiserforum_4` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_keystone_mine` | mod | `bg_mining` | no | 48 | 200 | 1,880 | 1,300 | 5,850 | 770 | 4,550 |
| `building_khaju_bridge` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_kiel_canal` | vanilla | `bg_canals` | unspecified | 1 | 850 | 850 | 0 | 0 | -850 | -850 |
| `building_kissaten` | mod | `bg_light_industry` | unspecified | 6,000 | 1,050 | 12,250 | 1,500 | 19,800 | 250 | 7,750 |
| `building_lead_mine` | vanilla | `bg_mining` | unspecified | 48 | 200 | 1,880 | 800 | 3,600 | 270 | 2,300 |
| `building_livestock_ranch` | mod | `bg_ranching` | unspecified | 432 | 40 | 960 | 480 | 2,100 | 310 | 1,270 |
| `building_logging_camp` | vanilla | `bg_logging` | unspecified | 81 | 0 | 1,010 | 500 | 2,000 | 40 | 1,450 |
| `building_machu_picchu` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_maize_farm` | vanilla | `bg_staple_crops` | unspecified | 40 | 0 | 590 | 400 | 1,280 | 260 | 830 |
| `building_manila_cathedral_monument` | vanilla | `bg_monuments` | yes | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_manila_cathedral_original` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_manila_cathedral_ruins` | vanilla | `bg_monuments_hidden` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_manor_house` | vanilla | `bg_manor_houses` | no | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_martandsuntemple` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_millet_farm` | vanilla | `bg_staple_crops` | unspecified | 40 | 0 | 590 | 400 | 1,280 | 260 | 830 |
| `building_mosque_of_djenne` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_motor_industry` | vanilla | `bg_heavy_industry` | unspecified | 12 | 1,500 | 5,050 | 2,400 | 7,200 | 350 | 2,700 |
| `building_munition_plant` | vanilla | `bg_military_industry` | unspecified | 6 | 1,800 | 3,750 | 2,500 | 4,500 | 150 | 1,300 |
| `building_musical_instrument` | mod | `bg_light_industry` | unspecified | 16 | 800 | 3,150 | 1,800 | 5,100 | 450 | 2,500 |
| `building_naval_administration` | vanilla | `bg_naval_administration` | unspecified | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_naval_fortification` | vanilla | `bg_naval_fortification` | unspecified | 3 | 500 | 1,400 | 0 | 0 | -1,400 | -500 |
| `building_naval_logistics_center` | vanilla | `bg_naval_logistics_center` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_observatorygreenwich` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_oil_rig` | vanilla | `bg_oil_extraction` | unspecified | 6 | 600 | 900 | 2,400 | 4,000 | 1,500 | 3,400 |
| `building_opium_plantation` | vanilla | `bg_plantations` | unspecified | 4 | 0 | 450 | 1,000 | 2,000 | 850 | 1,700 |
| `building_originium_mine` | mod | `bg_mining` | no | 48 | 200 | 1,880 | 1,500 | 6,750 | 970 | 5,450 |
| `building_panama_canal` | vanilla | `bg_canals` | unspecified | 1 | 850 | 850 | 0 | 0 | -850 | -850 |
| `building_paper_mill` | vanilla | `bg_light_industry` | unspecified | 9 | 600 | 2,000 | 1,200 | 3,000 | 100 | 1,500 |
| `building_pena_convent` | vanilla | `bg_monuments_hidden` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_pena_palace` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_petra` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_port` | vanilla | `bg_private_infrastructure` | unspecified | 4 | 0 | 750 | 0 | 1,500 | 0 | 750 |
| `building_power_bloc_statue` | vanilla | `bg_monuments` | unspecified | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_power_plant` | vanilla | `bg_power` | unspecified | 3 | 490 | 1,600 | 750 | 2,400 | 260 | 800 |
| `building_publisher` | mod | `bg_light_industry` | unspecified | 12 | 1,045 | 3,900 | 2,000 | 9,200 | 955 | 5,300 |
| `building_railway` | vanilla | `bg_private_infrastructure` | unspecified | 21 | 360 | 930 | 600 | 1,950 | 240 | 1,020 |
| `building_religious_center` | mod | `bg_entertainment` | yes | 9 | 600 | 2,850 | 1,000 | 4,200 | 400 | 1,350 |
| `building_rice_farm` | vanilla | `bg_staple_crops` | unspecified | 30 | 0 | 1,120 | 700 | 2,110 | 480 | 1,210 |
| `building_rubber_plantation` | vanilla | `bg_rubber` | unspecified | 12 | 0 | 450 | 800 | 2,600 | 650 | 2,300 |
| `building_rye_farm` | vanilla | `bg_staple_crops` | unspecified | 80 | 0 | 590 | 400 | 1,300 | 260 | 850 |
| `building_sagrada_familia_cathedral_1` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_sagrada_familia_cathedral_2` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_sagrada_familia_cathedral_3` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_saint_basils_cathedral` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_sakura_stone_mine` | mod | `bg_mining` | no | 48 | 200 | 1,880 | 1,400 | 6,300 | 870 | 5,000 |
| `building_shipyard` | vanilla | `bg_ship_construction` | unspecified | 4 | 1,200 | 3,000 | 2,400 | 5,600 | 1,200 | 2,600 |
| `building_silk_plantation` | vanilla | `bg_plantations` | unspecified | 4 | 0 | 450 | 600 | 1,600 | 450 | 1,300 |
| `building_skyscraper` | vanilla | `bg_skyscraper` | unspecified | 4 | 750 | 750 | 0 | 0 | -750 | -750 |
| `building_stage` | mod | `bg_entertainment` | yes | 400 | 600 | 6,350 | 1,500 | 9,200 | -400 | 4,150 |
| `building_statue_of_liberty` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_steel_mill` | vanilla | `bg_heavy_industry` | unspecified | 12 | 2,500 | 6,300 | 3,250 | 7,500 | 250 | 1,700 |
| `building_subsistence_farm` | vanilla | `bg_subsistence_agriculture` | no | 10 | 0 | 0 | 75 | 87.5 | 75 | 87.5 |
| `building_subsistence_fishing_village` | vanilla | `bg_subsistence_agriculture` | no | 10 | 0 | 0 | 75 | 87.5 | 75 | 87.5 |
| `building_subsistence_orchard` | vanilla | `bg_subsistence_agriculture` | no | 10 | 0 | 0 | 74.9 | 87.4 | 74.9 | 87.4 |
| `building_subsistence_pasture` | vanilla | `bg_subsistence_ranching` | no | 10 | 0 | 0 | 74.9 | 87.4 | 74.9 | 87.4 |
| `building_subsistence_rice_farm` | vanilla | `bg_subsistence_agriculture` | no | 10 | 0 | 0 | 140 | 165 | 140 | 165 |
| `building_suez_canal` | vanilla | `bg_canals` | unspecified | 1 | 850 | 850 | 0 | 0 | -850 | -850 |
| `building_sugar_plantation` | vanilla | `bg_plantations` | unspecified | 48 | 0 | 630 | 750 | 3,600 | 600 | 3,120 |
| `building_sulfur_mine` | vanilla | `bg_mining` | unspecified | 48 | 200 | 1,880 | 1,000 | 5,000 | 470 | 3,700 |
| `building_synthetics_plant` | vanilla | `bg_heavy_industry` | unspecified | 2 | 1,900 | 2,100 | 3,200 | 4,000 | 1,300 | 1,900 |
| `building_taj_mahal` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tea_plantation` | vanilla | `bg_plantations` | unspecified | 12 | 0 | 390 | 1,000 | 2,750 | 850 | 2,510 |
| `building_temple_of_poseidon` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_textile_mill` | vanilla | `bg_light_industry` | unspecified | 36 | 800 | 4,300 | 1,350 | 6,300 | 50 | 2,500 |
| `building_tobacco_plantation` | vanilla | `bg_plantations` | unspecified | 48 | 0 | 670 | 1,200 | 2,800 | 1,050 | 2,360 |
| `building_tooling_workshop` | vanilla | `bg_light_industry` | unspecified | 16 | 600 | 2,450 | 1,200 | 4,400 | 50 | 2,500 |
| `building_tot_animal_breeding_center` | mod | `bg_light_industry` | yes | 12 | 600 | 2,500 | 1,500 | 5,400 | 200 | 3,600 |
| `building_tot_chireiden_fusion` | mod | `bg_power` | no | 1 | 250 | 250 | 750 | 750 | 500 | 500 |
| `building_tot_golden_hall_construction_site` | mod | `bg_monuments` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tot_golden_hall_large_contract` | mod | `bg_monuments` | yes | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tot_golden_hall_monument` | mod | `bg_monuments` | yes | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tot_golden_hall_naming_contract` | mod | `bg_monuments` | yes | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tot_golden_hall_small_contract` | mod | `bg_monuments` | yes | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_tot_kappa_power` | mod | `bg_power` | no | 1 | 400 | 400 | 750 | 750 | 350 | 350 |
| `building_tot_pet_shop` | mod | `bg_entertainment` | yes | 12 | 800 | 2,700 | 1,800 | 5,600 | 350 | 3,550 |
| `building_trade_center` | vanilla | `bg_trade` | unspecified | 8 | 150 | 300 | 0 | 0 | -300 | -150 |
| `building_university` | vanilla | `bg_technology` | unspecified | 12 | 150 | 450 | 0 | 0 | -450 | -150 |
| `building_urban_center` | vanilla | `bg_service` | no | 108 | 0 | 400 | 510 | 1,440 | 510 | 1,040 |
| `building_vatican_city` | vanilla | `bg_monuments` | no | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_victoria_terminus` | vanilla | `bg_monuments` | unspecified | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_vineyard` | vanilla | `bg_agriculture` | unspecified | 4 | 0 | 450 | 1,000 | 2,000 | 850 | 1,700 |
| `building_wat_arun` | vanilla | `bg_monuments_hidden` | no | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_whaling_station` | vanilla | `bg_whaling` | unspecified | 12 | 0 | 1,370 | 550 | 2,200 | 130 | 1,250 |
| `building_wheat_farm` | vanilla | `bg_staple_crops` | unspecified | 75 | 0 | 590 | 400 | 1,280 | 260 | 830 |
| `building_white_house` | vanilla | `bg_monuments` | no | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `building_zoo` | mod | `bg_entertainment` | yes | 48 | 1,400 | 6,100 | 2,500 | 8,900 | 150 | 3,750 |

## How to read the table

`Surplus = output value - input value`. It is a goods-only difference, not net building profit. For a building's maximum surplus, subtracting its minimum input from its maximum output is usually wrong because those extremes can use different PM selections.
