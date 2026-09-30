# 幻想乡利益集团、角色立场与退出共同体

研究日期：2026-09-29。本文件是设计与接口调查，不启用任何游戏改动。

## 建议

第一版保留原版八类集团的底层键，在幻想乡国家内改名称、集团意识形态、人口吸引与特质；角色使用另设的幻想乡角色意识形态。其他国家保留现有行为。

文化表示人群身份，利益集团表示组织与利益，角色意识形态表示个人的法律立场。不要要求一种族只能支持一个集团，也不要把维护共同体等同于忠于博丽。

| 底层键 | 第一版名称建议 | 组织基础 |
|---|---|---|
| ig_landowners | 传统权贵 | 地产、家族与既有特权 |
| ig_devout | 信仰共同体 | 神社、寺院、信徒与宗教服务 |
| ig_intelligentsia | 术法学社 | 学者、术法研究者、文教与行政人员 |
| ig_industrialists | 工艺经营者 | 工厂经营者、技术经营与资本 |
| ig_armed_forces | 守备组织 | 军人、警备及有组织的武装 |
| ig_rural_folk | 乡土住民 | 农牧业、乡村与土地使用者 |
| ig_petty_bourgeoisie | 商贩行会 | 商店、手工业经营与地方服务 |
| ig_trade_unions | 生产劳动者 | 雇佣劳动者与劳动组织 |

这套名称只是讨论稿。改变吸引规则时仍需保留职业、财富、识字率等经济因素，再加入文化倾向；否则工业发展不会产生相应的政治变化。

当前模组已经用 `REPLACE:ig_*` 覆盖八类集团，文件位于 `common/interest_groups/zzzz_tot_*.txt`。应在现有覆盖中增加幻想乡限定分支，而不是再制造另一份相互竞争的覆盖。

原版法律直接使用 `interest_group_ig_landowners_pol_str_mult`、`interest_group_ig_devout_pol_str_mult`，以及 `ig:ig_landowners` 等引用。全新键并非不可行，但必须同步迁移引用、启用条件、角色生成、集团特质、政治权重与有关界面/事件，兼容维护量明显增加。

## 角色安排

以下是模组设计建议，不是原作给定的政治立场：

- 灵梦：信仰共同体；结界秩序与势力自治。维护共同规则，不自动支持神权统治或强迫所有成员服从博丽。
- 神奈子：信仰共同体；技术开发与信仰经营。不能简单继承原版宗教集团的全部保守立场。
- 荷取：工艺经营者；技术开发。帕秋莉、爱丽丝、永琳可侧重术法学社，但各自法律偏好分别讨论。
- 蕾米莉亚：传统权贵；家族统治。咲夜可侧重守备组织，不能仅因为同属红魔馆就赋予相同立场。
- 慧音：术法学社；聚落保护与文教。村民支持者仍可分属乡土住民、商贩行会、生产劳动者。

先按法律组确定少量共享角色立场，再为真正存在分歧的角色增加差异。没有明确偏好的法律先不表态，不将所有角色统一填为原版温和派。

现有东方资产不等于已生成开局角色：多数资产角色尚未恢复开局创建。`common/history/characters/tot_gensokyo_nz.txt` 中纯狐与赫卡提亚目前均以 `ig_landowners` 临时占位，没有显式指定意识形态，需要重排。

## 已核实的退出接口

| 接口 | 本机证据 | 适用范围 |
|---|---|---|
| AI 退出分数阈值 | 原版 `common/defines/00_ai.txt`：`LEAVE_POWER_BLOC_SCORE_THRESHOLD = -100`，注释明确分数取自 `invite_to_power_bloc` 接受评分 | 改 define 会影响全世界，建议不改 |
| 加入接受度 | 原版 `common/diplomatic_actions/28_invite_to_power_bloc.txt` 在 `scope:actor.power_bloc` 内读取 `modifier:power_bloc_invite_acceptance_add` | 修正属于集团，不能直接塞入普通国家/IG 特质假定生效 |
| 退出资格 | 原版 `common/power_bloc_identities/00_power_bloc_identities.txt` 使用 `can_leave` | 自定义身份可以设置退出门槛；玩家和 AI 都受资格判定影响 |
| 成员年限 | 导出 `triggers.log` 的 `tenure_in_current_power_bloc_years`，国家作用域 | 整年计数 |
| IG 状态 | 导出 `triggers.log` 的 `any_interest_group`、`ig_approval`、`ig_clout`、`has_ideology` | 可由退出规则或事件读取 |
| 脚本标记修正 | 本模组 `country_tot_character_growth_cost_mult_add` 已声明 `script_only = yes`，由效果读取数值 | 可用同一模式制作条约支持标记，但标记不会自行改变引擎行为 |

在本机原版修正类型中未发现专门的 AI 退集团概率/权重修正。不应编造 `country_ai_leave_power_bloc_mult` 之类接口。

## 两种实现

### 软偏好

自定义集团身份中可配置：

```paradox
power_bloc_modifier = {
    power_bloc_customs_union_bool = yes
    power_bloc_invite_acceptance_add = 300
}
```

300 是待测试的设计值，不是退阵概率减少 300% 或保证永不退出。修正提高集团整体的加入接受度，因此也可能影响外部国家的入盟意愿。若只希望作用于现有成员、并按每个成员的 IG 状态加分，可在 `invite_to_power_bloc` 的 `accept_score` 中增加幻想乡身份 + 已在同集团的限定分支；这会覆盖原版外交动作，需要随版本维护。

### 硬门槛与 IG 联动

推荐先通过自定义身份的 `can_leave` 实现严格退出资格，避免为了这一步覆盖邀请外交动作。利益集团可以提供一个脚本标记，退出规则读取标记。

下面是三个文件中的对应片段，不是可直接作为完整模组加载的文件；本轮没有创建这些运行时定义或进行游戏验证。

修正类型片段，放在 `common/modifier_type_definitions/`：

```paradox
country_tot_gensokyo_charter_support_add = {
    script_only = yes
    decimals = 0
    color = good
    game_data = { ai_value = 0 }
}
```

IG 特质片段，放在 `common/interest_group_traits/`，并通过集团初始化的 `set_ig_trait` 指派：

```paradox
ig_trait_tot_gensokyo_charter_support = {
    icon = "gfx/interface/icons/ig_trait_icons/propagandists.dds"
    min_approval = happy
    modifier = {
        country_tot_gensokyo_charter_support_add = 1
    }
}
```

自定义幻想乡集团身份内的退出判定片段：

```paradox
can_leave = {
    tenure_in_current_power_bloc_years >= 5
    has_variable = tot_gensokyo_exit_authorized
    NOT = {
        modifier:country_tot_gensokyo_charter_support_add > 0
    }
}
```

含义：至少加入五年、事件批准退出、且当前没有生效的条约支持特质。IG 特质按满意度与集团力量生效/缩放，读取正值即可，不应假定数值恒为 1。不是靠修正名称自动锁定退出，而是 `can_leave` 显式读取它。

该写法展示可行的连接方式；若满意度变化不应立即封锁或解锁，应改为事件持续记录支持/反对，资格只检查事件批准变量。可以要求退出请求持续两年或共同体严重失灵，再发放限时许可；这些时间、程序与变量必须另写事件/日志逻辑，本片段没有实现。

不建议把维持共同体完全交给一个种族、一个集团或某位统治者的特质。更稳妥的正式版是固定章程 + 多集团条约支持 + 持续性退出程序。内部战争本身不直接批准退出。

## 限制与测试

- 退出资格与强制参战、禁止内战是不同接口。仍需排除防御合作等禁战原则，也不能为保住集团把成员重新变为受保护国。
- 成员主动退出与主持国踢人是不同机制；上述代码不保证封住踢人。
- 集团领袖退出/解散、战争强制移除、革命和主持国灭亡均需单独验证。成员的设定身份可另用变量记录，不能把引擎集团成员关系当作唯一身份来源。
- 第一轮游戏测试应检查满意/不满/边缘化 IG 的标记值、玩家退出按钮、AI 多年观测、内战、主持国踢人和市场稳定。

本次仅补充研究稿；当前博丽主持、受保护国关系等运行时设置没有被本稿更改。
