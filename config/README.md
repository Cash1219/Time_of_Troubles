# 模组建筑开局配置

`building_start_config.csv` 是模组自定义建筑**开局放置**的唯一配置源。每行是一条建筑记录，填州、地区持有者、建筑、等级、所有权和启用 PM。当前有 58 条启用记录、合计 126 级；另有 13 条 `enabled=no` 的零开局模板，所以 27 种建筑都出现在配置表中。

原来的放置记录已从各区域历史文件迁至由此表生成的 `common/history/buildings/tot_configured_mod_buildings.txt`。**以后请修改 CSV，再运行：**

```powershell
python tools/building_history_config.py check
python tools/building_history_config.py generate
```

`generate` 会重写专用历史文件，并再次解析所有建筑历史，逐条核对州、地区持有者、建筑、等级、所有权、储备与启用 PM；不匹配时会恢复原文件并报错。不要直接修改生成文件，因为下一次运行会覆盖它。

## 字段

| 列 | 含义 |
|---|---|
| `id` | 稳定行号；新增记录时使用未占用的新编号 |
| `enabled` | `yes` 生成开局建筑；`no` 保留为模板，不生成 |
| `state` | `STATE_...` 州 ID |
| `region_owner` | 该州在历史文件中的 `region_state:TAG` |
| `building` | `common/buildings` 中定义的建筑 ID |
| `level` | 开局等级，启用行须大于 0 |
| `ownership` | `country`、`building` 或 `company` |
| `owner_country` | 所有权国家，格式如 `c:GBDP`；可与地区持有者不同 |
| `owner_building` | `ownership=building` 时的金融区类型，或 `ownership=company` 时的公司类型 |
| `owner_region` | 所有权主体所在州；无则留空 |
| `reserves` | 建筑历史中的储备值 |
| `production_methods` | PM ID 用分号隔开；留空则使用建筑默认 PM |
| `source_file`, `source_line` | 迁移前来源，供核对；生成器不使用这两列 |
| `notes` | 人工备注，生成器不使用 |

`building_catalog.csv` 汇总全部 27 种建筑的开局处数与等级。`outputs/01a0fcb6-a3d0-7ee2-8c95-222977a33847/building_start_config.xlsx` 是先前导出的审核副本，可能滞后于当前 CSV；**游戏配置以 CSV 为准**。

两条既有记录的 `owner_country` 与 `region_owner` 不同，保留了原历史写法，并在 Excel 审核副本中标记待核对。四座魔法矿井当前没有开局放置，且建筑定义仍为 `buildable = no`；将来启用矿井时，还要同步检查建筑定义及地图资源上限。
