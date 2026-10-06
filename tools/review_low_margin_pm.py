"""Review PMs below 30% base-price goods gross margin in full-building context."""

from collections import defaultdict
from itertools import product
from math import ceil
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
audit = runpy.run_path(str(ROOT / "tools/audit_pm_economy.py"))
rows = audit["rows"]
prices = audit["prices"]
pms = audit["pms"]
clean = audit["clean"]
fmt = audit["fmt"]
by_building = audit["by_building"]
OUT = ROOT / "analysis" / "low_margin_improvements.md"

input_mult = {}
output_mult = {}
for pm, (body, _) in pms.items():
    code = clean(body)
    input_mult[pm] = sum(float(v) for v in re.findall(
        r"\bbuilding_goods_input_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", code
    ))
    mults = defaultdict(float)
    for good, amount in re.findall(
        r"\bgoods_output_([\w]+)_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", code
    ):
        mults[good] += float(amount)
    for amount in re.findall(
        r"\bbuilding_goods_output_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", code
    ):
        mults["*"] += float(amount)
    output_mult[pm] = mults


def totals(selected):
    raw_input = sum(row["input"] for row in selected)
    total_input = raw_input * (1 + sum(input_mult[row["pm"]] for row in selected))
    quantities = defaultdict(float)
    multipliers = defaultdict(float)
    for row in selected:
        for (direction, good), quantity in row["goods"].items():
            if direction == "output":
                quantities[good] += quantity
        for good, amount in output_mult[row["pm"]].items():
            multipliers[good] += amount
    total_output = sum(
        quantity * prices[good] * (1 + multipliers["*"] + multipliers[good])
        for good, quantity in quantities.items()
    )
    return total_input, total_output


stats = defaultdict(lambda: [0, 0, float("inf"), float("-inf")])
building_stats = {}
for building, items in by_building.items():
    groups = defaultdict(list)
    for row in items:
        groups[row["group"]].append(row)
    all_count = bad_count = 0
    for selected in product(*groups.values()):
        if building == "building_kissaten" and not any(
            row["group"] in {
                "pmg_kissaten_coffee", "pmg_kissaten_tea", "pmg_kissaten_sweet", "pmg_kissaten_food"
            } and not row["pm"].endswith("_null") for row in selected
        ):
            continue
        cost, revenue = totals(selected)
        if revenue <= 0:
            continue
        margin = 100 * (revenue - cost) / revenue
        all_count += 1
        bad_count += margin < 30
        for row in selected:
            state = stats[(building, row["pm"])]
            state[0] += 1
            state[1] += margin < 30
            state[2] = min(state[2], margin)
            state[3] = max(state[3], margin)
    building_stats[building] = (bad_count, all_count)

low = [row for row in rows if row["margin"] is not None and row["margin"] < 30]
commercial_low = [row for row in low if row["building"] not in {
    "building_band_headquarter", "building_club"
}]
lines = [
    "# 毛利率低于 30% 的生产方式：改进清单",
    "",
    f"共 **{len(low)} 项**，其中 **{len(commercial_low)} 项**属于可自营建筑，另 15 项属于 `no_ownership` 的乐队总部和社团。口径固定为 `（商品产出基准价－商品投入基准价）÷商品产出基准价`；30% 的最低产出价为 `投入价÷0.7`。",
    "",
    "## 判断方法",
    "",
    "- 明细表的“补足产值”和“仅增产参考”表示该 PM *单项*达到 30% 毛利所需的最小改动，不是整栋建筑的最终修改建议。仅增产参考把差额加到该 PM 产值最大的现有产出商品，按整数数量取整。若保持产出不变，也可减少投入 `当前投入－0.7×当前产出`。",
    "- “完整组合低毛利数”枚举这栋建筑各 PMG 所有理论选项，并计入代码里的建筑投入倍率和指定商品的产出倍率；不筛科技、法律、AI 选择或无就业状态，不含工资与市场价。因此它用来识别联动风险，不能当作玩家遭遇概率。",
    "- 即使单项毛利不足，整栋建筑仍可能高于 30%；相反，单项全部达标时，昂贵的辅助 PM 也可能使整栋建筑低于 30%。",
    "",
    "## 优先处理建议",
    "",
    "1. **咖啡厅**：当前开局标准咖啡＋普通女仆＋基本桌椅约 37.1%；完整组合 21/7,500 低于 30%，主要是少量菜单搭配高价设备。仍须在游戏内复测 AI 选档和市场价。",
    "2. **酒馆**：已给收费接待档增加体验产出，降低厨房持续消耗；81 种完整组合均达到 30%。下一步优先看谷子工坊的 IP/销售组及娱乐传媒社的发行/自动化组。",
    "3. **游戏工坊 IP 运营**：单项投入 1,300、产出 1,400，毛利 7.1%，还把游戏产出乘以 0.9；选它的 64 种理论组合全部低于 30%。如保留投入及游戏减产，`experience` 至少先从 35 提到 47，才让该 PM 自身过 30%，然后再核对完整组合。也可降低服务/电话投入并减轻游戏减产。",
    "4. **舞台**：更新运营与规模产出后，400 种理论组合中只有 2 种为 29.9%，其余落在 30%～70%。豪华舞台规模档单项毛利为 35.0%；剩余边界组合涉及大型舞台、最高档场贩与杂志宣传。",
    "5. **乐队总部与社团**：这两栋建筑均为 `ownership_type = no_ownership`，乐队 11 项、社团 4 项低毛利不宜强制达到商业建筑标准。乐队总部所有有产出的组合商品毛利都低于 30%，符合补贴型设施的可能设计；若希望它们自负盈亏，需另设经营产出。",
    "6. **水族馆、动物园、游乐园等场馆**：多数偏差只差一小档产出，且同建筑多组会互相抵消。优先微调完整组合持续低毛利的档位。",
    "",
    "## 各建筑完整组合情况",
    "",
    "| 建筑 | 毛利低于30%的理论组合 | 有正产出的理论组合 | 占比 |",
    "|---|---:|---:|---:|",
]
for building, (bad, count) in building_stats.items():
    if bad:
        lines.append(f"| `{building}` | {bad:,} | {count:,} | {bad/count:.1%} |")

lines += ["", f"## {len(low)} low-margin PMs", ""]
for building in dict.fromkeys(row["building"] for row in low):
    lines += [
        f"### `{building}`",
        "",
        "| PM | 投入 | 产出 | 毛利率 | 单项补足产值 | 仅增产参考 | 完整组合低毛利数 |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in (r for r in low if r["building"] == building):
        state = stats[(building, row["pm"])]
        shortfall = max(0, row["input"] / 0.7 - row["output"])
        output_goods = [
            (good, quantity) for (direction, good), quantity in row["goods"].items()
            if direction == "output" and quantity > 0
        ]
        good, quantity = max(output_goods, key=lambda item: item[1] * prices[item[0]])
        extra = ceil(shortfall / prices[good] - 1e-9)
        lines.append(
            f"| `{row['pm']}` | {fmt(row['input'])} | {fmt(row['output'])} | "
            f"{row['margin']:.1f}% | +{fmt(shortfall)} | `{good}` +{extra}（{fmt(quantity)}→{fmt(quantity+extra)}） | {state[1]:,}/{state[0]:,} |"
        )
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}: {len(low)} low-margin items")
