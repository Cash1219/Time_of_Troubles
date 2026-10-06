# 咖啡厅 PM 与共性科技补充审核（旧讨论稿）

> 2026-10-05：咖啡厅现有菜单结构保留，进阶 PM 已按原版科技树设置科技门槛；实际配置以 [`common/production_methods/kissaten.txt`](../../common/production_methods/kissaten.txt) 为准。下表中的“机械工具→机械化工坊→轮班工作”方案未采用，亦未新增共用科技。

> 讨论稿，尚未修改任何 PM 科技门槛或新增科技。主清单中的电气化乐器已改为保留旧版；游戏线、谷子线的拟定门槛暂作备选。

> 更新：下方“机械工具 → 机械化工坊 → 轮班工作”的菜单映射已被否决，保留仅供追溯。咖啡厅应参照原版食品厂，把菜单扩充、烘焙工艺、设备与服务分开设计；具体方案待审核。

## 咖啡厅的 26 个在用 PM

咖啡厅建筑本身要求原版 `manufacturies`。当前咖啡 PMG 已移除“无”档，故共有 26 个在用 PM。四组菜单的高档 PM 包含低档菜单，投入与产出一并增加；下表按经营规模而非菜式发明年代设置科技。`—` 表示无额外 PM 科技门槛。科技仅为审核建议，尚未写入 PM 定义。

| PMG | 顺序 | PM | 建议的单一科技 | 依据 |
|---|---:|---|---|---|
| 咖啡菜单 | 1 | 标准咖啡 `pm_kissaten_coffee_coffee` | — | 建筑已有 `manufacturies` 门槛，产出 25 |
| 咖啡菜单 | 2 | 摩卡咖啡 `pm_kissaten_coffee_mocha` | **机械工具** `mechanical_tools` | 扩大完整菜单，产出 50 |
| 咖啡菜单 | 3 | 拿铁咖啡 `pm_kissaten_coffee_latte` | **机械化工坊** `mechanized_workshops` | 标准化制备与更大规模，产出 70 |
| 饮料菜单 | 1 | 无 `pm_kissaten_tea_null` | — | 不提供此菜单 |
| 饮料菜单 | 2 | 牛奶 `pm_kissaten_tea_milk` | — | 基础菜单，产出 25 |
| 饮料菜单 | 3 | 可可 `pm_kissaten_tea_cocoa` | **机械工具** `mechanical_tools` | 扩大完整菜单，产出 40；当前没有可可原料 |
| 饮料菜单 | 4 | 红茶 `pm_kissaten_tea_black_tea` | **机械化工坊** `mechanized_workshops` | 更大规模，产出 55 |
| 甜点菜单 | 1 | 无 `pm_kissaten_sweet_null` | — | 不提供此菜单 |
| 甜点菜单 | 2 | 饼干 `pm_kissaten_sweet_biscuit` | — | 基础烘焙，产出 25 |
| 甜点菜单 | 3 | 可丽饼 `pm_kissaten_sweet_pancake` | **机械工具** `mechanical_tools` | 扩大完整菜单，产出 45 |
| 甜点菜单 | 4 | 蛋糕 `pm_kissaten_sweet_cake` | **机械化工坊** `mechanized_workshops` | 标准化制备，产出 60 |
| 甜点菜单 | 5 | 苹果派 `pm_kissaten_sweet_pie` | **轮班工作** `shift_work` | 更长营业时间与更大菜单，产出 70 |
| 主食菜单 | 1 | 无 `pm_kissaten_food_null` | — | 不提供此菜单 |
| 主食菜单 | 2 | 三明治 `pm_kissaten_food_sandwich` | — | 基础轻食，产出 30 |
| 主食菜单 | 3 | 意大利面 `pm_kissaten_food_pasta` | **机械工具** `mechanical_tools` | 扩大完整菜单，产出 40 |
| 主食菜单 | 4 | 蛋包饭 `pm_kissaten_food_omuraisu` | **机械化工坊** `mechanized_workshops` | 标准化制备，产出 55 |
| 主食菜单 | 5 | 章鱼烧 `pm_kissaten_food_takoyaki` | **轮班工作** `shift_work` | 更长营业时间与更大菜单，产出 65 |
| 服务水准 | 1 | 普通营业 `pm_kissaten_server_null` | — | 基础经营 |
| 服务水准 | 2 | 普通女仆 `pm_kissaten_server_waitress` | — | 初级接待 |
| 服务水准 | 3 | 女仆营业 `pm_kissaten_server_maid` | 拟议的**专业接待业** | 可与酒馆、舞台共用科技 |
| 服务水准 | 4 | 主题公演 `pm_kissaten_server_fuwafuwa` | 拟议的**组织化休闲娱乐** | 科技需继承“专业接待业” |
| 工具设备 | 1 | 无 `pm_kissaten_tool_null` | — | 不加设备 |
| 工具设备 | 2 | 基本桌椅 `pm_kissaten_tool_table` | 待定 | 现有 -5% 投入增益应晚期开，但其 PMG 位置靠前 |
| 工具设备 | 3 | 餐具套装 `pm_kissaten_tool_porcelain` | 待定 | 须与桌椅和锅炉形成同一科技链 |
| 工具设备 | 4 | 水管锅炉 `pm_kissaten_tool_watertube_boiler` | **水管锅炉** `watertube_boiler` | 原版 E2 |
| 工具设备 | 5 | 冷藏设备 `pm_kissaten_tool_flash_freezing` | **电容器** `electrical_capacitors` | 原版 E4；PM 当前投入电力和发动机 |

菜单科技链为 `manufacturies`（建筑门槛）→ `mechanical_tools` → `mechanized_workshops` → `shift_work`。原版 `mechanized_workshops` 有 `mechanical_tools` 前置，`shift_work` 有 `mechanized_workshops` 前置；一组内的上档不会先于下档解锁。这里的科技控制的是完整菜单经营规模，而非单道菜的发明时间。设备组仍须先处理桌椅的百分比增益与组内排序冲突，不能硬填不相干的科技。

## 值得共用的新科技候选

| 优先级 | 候选科技 | 类别与前置建议 | 可以覆盖的建筑与 PM | 价值与限制 |
|---|---|---|---|---|
| 1 | **成套电器** `tot_appliance_integration` | 生产 E4；前置原版 `electrical_capacitors`、`mechanical_tools` | 咖啡厅高档冷藏、酒馆电冷厨；游戏街机和电动谷子若决定重排，也可沿此线走 | 原版电容器已经覆盖一般电动设备；新科技仅负责将元件集成到商用、民用终端设备。若覆盖面不够，可取消新节点；电气化乐器保留旧设定 |
| 2 | **专业接待业** `tot_professional_hospitality` | 社会 E3；前置原版 `modern_sewerage`、`corporate_charters` | 咖啡厅女仆营业、酒馆包间/宴席、舞台接待 | 表示卫生、标准化服务与商业运营的结合；不适合拿来解锁具体菜式 |
| 3 | **组织化休闲娱乐** `tot_organized_leisure` | 社会 E4；拟前置“专业接待业”与原版 `camera` | 咖啡厅主题公演、舞台活动、游乐场、水族馆和动物园的演出档 | 给跨建筑的表演运营一个共同节点，具体 PM 仍待审核 |

这三个共用科技的**概念已得到确认**，拟定时代与前置见[科技树草图](shared_tech_and_magic_architecture.md)。科技定义允许多个前置科技；**每个 PM 仍只要求一个科技**。超前设备另用实际投入魔法矿物的魔导 PM 解释，不把早期魔法和晚期电力硬写在同一个 PM 里。上述均未落地；游戏与谷子是否需要再加电子媒介科技，应在你确定这两条生产线的时代跨度后决定。

## 当前应保留的分歧

- **电气化乐器**继续使用旧版 `electrical_capacitors`，不纳入这次改动。它与前档的 `mechanical_tools` 在原版树上不是祖先关系，因此乐器 PMG 的严格科技前置仍有一个既有例外；若要同时满足两条要求，需要日后重新讨论前档或新增桥接科技。
- **游戏线、谷子线**暂不实施主清单的备选映射。成套电器若保留，可作为常规终端设备的一档；魔导提前版需另有矿物投入。最高档是否还需要“电子媒介”之类新科技，须先确定 PM 名称、时代和投入商品。
