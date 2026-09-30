# 幻想乡共同体：独立势力、共同市场与内部战争

研究日期：2026-09-29。依据本机游戏脚本、随游戏提供的模组说明、游戏导出的 effects/triggers 文档，以及开发日志。
本目录的原型没有启用，不会改变当前开局。

## 结论

推荐把幻想乡做成“结界共同体”：成员是独立国家，共享市场，在共同体内可以战争、结盟、援助和中立。取消博丽对其他国家的受保护国关系。

原版国家集团仍然有一个技术上的领袖国家。`create_power_bloc` 是国家作用域的效果，文档明确说明创建国家就是领袖；没有找到可设置“无领袖”或“多人共同领袖”的公开脚本接口。因此，政治上的平等与底层市场的记账国家需要分开。

推荐分两步：第一步验证独立成员的共同市场和内战；第二步约束集团踢人、原则修改和继任，才把政治权力真正交给共同规则。不能仅把“领袖”文字改成“议会”就宣称完成平等。

## 已经核实的接口

| 问题 | 本机代码中的证据 | 含义 |
|---|---|---|
| 同集团是否天然禁止战争 | `common/scripted_rules/00_scripted_rules.txt` 的 `can_start_diplomatic_plays_against` 仅在集团有 `power_bloc_disallow_war_bool = yes` 时因集团身份阻止战争 | 不需要为普通成员内战先重写全局战争规则 |
| 哪些原则禁止内战 | `principle_defensive_cooperation_1/2/3` 都设置上述布尔修正 | 三个等级都应排除，不能只避开三级 |
| 哪些原则强制参战 | `principle_defensive_cooperation_3` 设置 `country_join_power_bloc_member_in_defensive_plays_bool`；`principle_aggressive_coordination_3` 设置 `country_join_power_bloc_member_in_plays_bool` | 不把这些原则用于允许自行选边的共同体 |
| 共同市场从哪里来 | `power_bloc_customs_union_bool = yes`，原版贸易联盟身份和二级市场统一原则都使用它 | 不依赖受保护国关系也能表达关税同盟 |
| 独立国家如何入集团 | `create_power_bloc` 的重复 `member = c:TAG` 参数，或者国家作用域 `join_power_bloc = c:HOST` | 开局直接登记成员，避免普通外交邀请的威望和优势限制 |
| 普通邀请为什么不适合弱主持国 | `26_join_power_bloc.txt` 的 `possible` 要求申请国威望或等级低于目标，同时需要优势 | 不应拿常规外交邀请代替开局登记 |
| 集团领袖资格 | `can_lead_power_bloc` 原版要求至少 major_power | 幻想乡都是小国，需要局部例外或中立机构方案，不能只换身份后忽略资格 |
| 集团会不会争领袖 | `NPowerBlocs` 有威望 1.2 倍触发、维持 12 月等权力争夺参数 | 固定主持国和轮值主持都不能靠改名保证；没有查到直接轮换领袖的脚本效果 |
| 能否禁止退出 | 身份文件原版使用 `can_leave = { ... }` | 可以对自定义身份给出封闭共同体规则，但必须游戏验证领袖退出、解散和战败边界 |
| 是否有单独的禁止踢人接口 | 文档中未找到身份 `can_kick`；GUI 直接调用 `PowerBloc.Kick` | 暂不能保证只写身份文件就封住踢人；隐藏按钮也不能证明 AI 被限制 |
| 是否有市场首都接口 | `set_market_capital` 支持国家作用域和 state_region 参数 | 它只移动市场首都，不会把市场变成多人共同拥有 |

源码目录均为 `D:/Steam/steamapps/common/Victoria 3/game/`。
导出接口文档为 `D:/Users/Administrator/Documents/Paradox Interactive/Victoria 3/docs/effects.log` 与 `triggers.log`。

## 建议的共同规则

| 事项 | 第一版规则 |
|---|---|
| 主权 | 24 国独立；没有固定宗主、贡税、宗主保卫义务或强制跟随战争 |
| 经济 | 一个共同市场；本地价格、基础设施、港口与本州电力保留原版机制 |
| 内部战争 | 按正常外交博弈发动；第三方可援助、结盟或中立 |
| 普通合作 | 使用同盟、防御协定、援助及允许的投资条约；不自动让全集团加入一场成员战争 |
| 身份归属 | 结界共同体不是因一次争端就消失的军事联盟；成员国家身份另用变量记录，避免战时引擎退出等于失去设定身份 |
| 对外防卫 | 第二阶段增加外敌入侵事件；分别邀请成员响应。必须区分外敌入侵与内部争端 |
| 原则 | 测试版冻结章程，不产生授权点。正式版再用议题、投票、执行事件决定变更 |
| 退出与踢人 | 退出先按封闭结界规则限制；踢人必须继续查引擎和 AI，不能把按钮隐藏当作完整实现 |
| 灭国与割地 | 未先行限制。是否保留每个命名势力，需要单独选择“可灭国”或“有限内部战争”，不能冒充底层集团自带限制 |

不会使用 `power_bloc_leader_can_make_subjects_bool`、强制宗教、强制政体或领袖追加战争目标等集团特权。
第一版不加入强制参战修正，也不使用防御合作原则。

## 市场由谁记账

| 路线 | 得到什么 | 代价与限制 |
|---|---|---|
| 现有国家承担市场事务 | 改动少，能最快测试独立成员和贸易；主持者没有宗主权 | 引擎仍显示一个领袖，且存在踢人、外交和市场控制残余；不能说是彻底无领袖 |
| 中立结界机构作为技术国家 | 现有势力不再占领袖位置，设定上更接近共同规则 | 需要真实可用的国家和领土、市场运输及财政安排；无地国家不宜直接假设能运行；仍要防止引擎权力争夺和市场枢纽被占领 |
| 脚本自建共同体，不使用原版国家集团 | 阵营归属、投票和规则可以完全平等 | 自定义变量不能直接创造一个无国家所有者的原版市场；要另找市场承载，不能假装这一步已经解决 |

第一步可用人里作“市场记账国”的技术试验，因为它是主要生产与消费地区。原型中的 `c:HITO` 仅作例子，不是已经决定让人里成为政治领袖。
如果连技术位置都不想交给现有势力，则应选中立机构路线，而不是重新把博丽包装成领袖。
真正轮值主持没有查到直接脚本接口。不要全局提高威望阈值来锁住主持者，那会影响英国、奥地利等全部原版集团。

## 改哪些文件

1. `common/history/diplomacy/tot_gensokyo_subjects.txt`：撤销 23 条开局 `tot_gensokyo_protectorate` 创建记录。新开局直接不创建，比加载后解除关系更干净；后者可能触发已有脚本的五年休战。
2. `common/history/power_blocs/tot_gensokyo_power_bloc.txt`：替换当前博丽创建的主权帝国；用自定义身份，显式登记 23 个独立成员。
3. `common/power_bloc_identities/tot_gensokyo_charter.txt`：新身份只承载共同市场，没有主权帝国或军事集团特权。
4. `common/power_bloc_principles/tot_gensokyo_charter.txt` 与 `common/power_bloc_principle_groups/tot_gensokyo_charter.txt`：提供初始固定章程。测试版不产生授权点，避免主持者升级出禁战或强制参战原则。
5. `common/scripted_rules/...`：为幻想乡主持资格增加局部例外，并检查弱集团处理。保留其他国家的原版条件；同名规则覆盖需要按当前游戏版本维护，不能整份丢掉原版文件。
6. `common/scripted_triggers/...` 与开局登记：明确幻想乡成员；独立的 `tot_gensokyo_member` 变量可用于事件身份和投票，不拿是否受保护作判定。
7. 后续 `common/scripted_guis`、`common/journal_entries`、事件和必要的 GUI 改动：议题、表决、退出、踢人和战后身份处理。只限制自定义集团，保留其他集团行为。

旧受保护国类型与外交动作可以暂留定义，供历史存档引用；关键是新开局不再建立这些关系。

## 代码骨架

原型文件在 `docs/drafts/gensokyo_charter_prototype/`，不在游戏加载目录里。它展示三个关键部分：

```text
identity_tot_gensokyo_charter = {
    power_bloc_modifier = {
        power_bloc_customs_union_bool = yes
    }
    leader_modifier = {}
    non_leader_modifier = {}
    can_leave = { always = no }
    mandate_progress = { value = 0 }
    cohesion = { value = 70 }
}
```

这个骨架需要配套图标、原则组、主持资格处理与游戏测试。`mandate_progress = 0` 和固定凝聚力是验证阶段配置，不是正式平衡设计。
不要写 `power_bloc_disallow_war_bool = no` 去尝试覆盖别的禁战原则；应直接不提供产生禁战修正的原则。

开局登记的核心写法来自本机效果文档：

```text
c:HITO ?= {
    create_power_bloc = {
        name = GENSOKYO_BARRIER_NETWORK
        identity = identity_tot_gensokyo_charter
        principle = principle_tot_gensokyo_charter_1
        member = c:HAKR
        member = c:CHRD
        # 继续登记其余 21 国
    }
}
```

既有存档的解除关系接口为：

```text
c:HAKR = {
    remove_diplomatic_pact = {
        country = c:CHRD
        type = tot_gensokyo_protectorate
    }
}
```

这不是推荐的新开局实现，也不是完整存档迁移：必须另测解约休战、旧集团清理和身份变更。第一版建议重新开局。

## 必须进游戏验证的边界

- 两个普通成员互相发起博弈，第三成员能分别加入双方或保持中立。
- 成员攻击技术主持国；主持国攻击成员。不能只测两个非领袖国家。
- 开战后集团成员与共同市场是否保留、市场可达性如何变化。脚本入口允许战争，不等于已经证明战争期间市场不会被引擎重组。
- 主持国吞并、解放、革命、威望被超越后，集团与市场是否继续存在。
- 普通国家集团的防御合作禁战、主权帝国和原版领导权争夺仍保持原版行为。
- 24 国是否有足够港口、运输能力和区域利益。取消集团禁战不会自动满足博弈所需利益区，也不会消除休战等正常限制。
- 玩家和 AI 是否仍能单方面踢人、切换章程或退出。不能只检查界面按钮。

第一阶段通过这些测试后，再设计“共同议事”。议题先限定为市场规则、对外防卫、违规惩罚，不把内政和常规成员战争交给某一位领袖裁决。

## 来源

- 本机原版 `common/scripted_rules/00_scripted_rules.txt`、`common/power_bloc_identities/00_power_bloc_identities.txt`、`common/power_bloc_principles/00_power_bloc_principles.txt`。
- 本机 `power_bloc_identities.md`、`power_bloc_principles.md`、`power_bloc_principle_groups.md` 与导出的效果/触发器文档。
- [官方开发日志 #118](https://steamcommunity.com/games/529340/announcements/detail/4185611434351815137)：防御合作原则限制内部战争；战争协同与共同市场属于不同的原则设计。

以上接口存在与入口条件属于源码确认；无领袖、战时市场、踢人与轮值等边界属于明确列出的未验证事项。
