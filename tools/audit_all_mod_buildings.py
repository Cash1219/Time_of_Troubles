"""Recalculate every mod-defined building from current PMs and base goods prices."""

from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "current_all_mod_buildings.md"
audit = runpy.run_path(str(ROOT / "tools/audit_pm_economy.py"))
buildings = audit["mod_buildings"]
groups = audit["groups"]
pms = audit["pms"]
prices = audit["prices"]
rows = audit["rows"]
vals = audit["vals"]
clean = audit["clean"]
inner = audit["inner"]


def fmt(value):
    return f"{value:,.0f}" if value == round(value) else f"{value:,.1f}"


def pct(value):
    return "—" if value is None else f"{value:.1f}%"


def modifiers(pm):
    body = inner(clean(pms[pm][0]), "building_modifiers")
    result = defaultdict(float)
    for direction, good, value in re.findall(
        r"\bgoods_(input|output)_([\w]+)_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", body
    ):
        result[(direction, good)] += float(value)
    for direction, value in re.findall(
        r"\bbuilding_goods_(input|output)_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", body
    ):
        result[(direction, "*")] += float(value)
    return result


pm_goods = {row["pm"]: row["goods"] for row in rows}
pm_modifiers = {pm: modifiers(pm) for pm in pm_goods}


def values(selection):
    quantities = defaultdict(float)
    multipliers = defaultdict(float)
    for pm in selection:
        for key, value in pm_goods[pm].items():
            quantities[key] += value
        for key, value in pm_modifiers[pm].items():
            multipliers[key] += value
    totals = defaultdict(float)
    for (direction, good), quantity in quantities.items():
        totals[direction] += quantity * prices[good] * (
            1 + multipliers[(direction, "*")] + multipliers[(direction, good)]
        )
    return totals["input"], totals["output"]


names = {"building_tot_golden_hall_monument": "金色大厅"}
localization_paths = [
    audit["VANILLA"] / "localization/simp_chinese/buildings_l_simp_chinese.yml",
    *(ROOT / "localization/replace/simp_chinese").rglob("*.yml"),
]
for path in localization_paths:
    for key, name in re.findall(
        r'^\s*(building_[\w]+):\d*\s+"([^"\n]+)"',
        path.read_text(encoding="utf-8-sig", errors="replace"),
        re.MULTILINE,
    ):
        names[key] = name


results = []
ambiguous_defaults = []
for building, (body, _) in sorted(buildings.items()):
    options = []
    group_names = vals(body, "production_method_groups")
    for group in group_names:
        assert group in groups, (building, group)
        choices = [pm for pm in vals(groups[group][0], "production_methods") if pm in pms]
        assert choices and all(pm in pm_goods for pm in choices), (building, group)
        options.append(choices)
    assert options, building
    default = []
    for group, choices in zip(group_names, options):
        explicit = [pm for pm in choices if re.search(r"\bis_default\s*=\s*yes", clean(pms[pm][0]))]
        if len(explicit) > 1:
            ambiguous_defaults.append((building, group, explicit))
        default.append(explicit[0] if explicit else choices[0])
    highest = [choices[-1] for choices in options]
    count = in_range = low = high = no_output = 0
    min_margin = max_margin = None
    min_selection = max_selection = None
    min_cost = max_cost = min_output = max_output = None
    for selection in product(*options):
        count += 1
        cost, output = values(selection)
        min_cost = cost if min_cost is None else min(min_cost, cost)
        max_cost = cost if max_cost is None else max(max_cost, cost)
        min_output = output if min_output is None else min(min_output, output)
        max_output = output if max_output is None else max(max_output, output)
        if output <= 0:
            no_output += 1
            continue
        margin = 100 * (output - cost) / output
        low += margin < 30
        in_range += 30 <= margin <= 70
        high += margin > 70
        if min_margin is None or margin < min_margin:
            min_margin, min_selection = margin, selection
        if max_margin is None or margin > max_margin:
            max_margin, max_selection = margin, selection
    default_cost, default_output = values(default)
    highest_cost, highest_output = values(highest)
    results.append({
        "key": building,
        "name": names.get(building, building),
        "buildable": re.search(r"\bbuildable\s*=\s*no", clean(body)) is None,
        "groups": group_names,
        "count": count,
        "low": low,
        "in_range": in_range,
        "high": high,
        "no_output": no_output,
        "min_margin": min_margin,
        "max_margin": max_margin,
        "min_selection": min_selection,
        "max_selection": max_selection,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "min_output": min_output,
        "max_output": max_output,
        "default": default,
        "default_cost": default_cost,
        "default_output": default_output,
        "highest": highest,
        "highest_cost": highest_cost,
        "highest_output": highest_output,
    })


lines = [
    "# 全部模组建筑：当前基准价商品收支复核",
    "",
    f"覆盖 {len(results)} 栋在模组中定义的建筑，包括改写的原版畜牧场、停用建筑和事件建筑。",
    "",
    "- 每级建筑满就业，按当前商品 `cost` 计算。投入、产出为每周商品总价；毛利率＝（产出－投入）÷产出。",
    "- 每个 PMG 选择一个 PM，枚举全部理论组合；计入建筑商品投入/产出倍率，不计工资、市场价格、就业不足、吞吐量和科技／法律可用性。吞吐量同时放大商品投入与产出，通常不改变商品毛利率。",
    "- 默认档取 `is_default = yes`，没有标记则取 PMG 第一档。若一组有多个默认标记，则暂取第一个并在下方标明。最高档是所有 PMG 最后一档同时启用，不一定是最优组合。",
    "- 多个 PMG 的投入和产出是先合并商品数量，再应用所选 PM 的建筑级商品倍率。输出为零的组合不计算毛利率。",
    "- 乐队总部与社团采用 `no_ownership`，还提供容量、国家修正等非商品收益；负商品毛利是财政补贴规模的线索，不能直接与自营工厂按同一标准比较。金色大厅合同与纪念建筑主要通过事件或修正发挥作用。",
    "",
    "## 汇总",
    "",
    "| 建筑 | 可建 | 组合数 | 默认投入→产出 | 默认毛利 | 全高档投入→产出 | 全高档毛利 | 毛利范围 | <30% / 30–70% / >70% |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|",
]
for item in results:
    dc, do = item["default_cost"], item["default_output"]
    hc, ho = item["highest_cost"], item["highest_output"]
    dm = 100 * (do - dc) / do if do > 0 else None
    hm = 100 * (ho - hc) / ho if ho > 0 else None
    lines.append(
        f'| {item["name"]} (`{item["key"]}`) | {"是" if item["buildable"] else "否"} | {item["count"]:,} | '
        f'{fmt(dc)}→{fmt(do)} | {pct(dm)} | {fmt(hc)}→{fmt(ho)} | {pct(hm)} | '
        f'{pct(item["min_margin"])}～{pct(item["max_margin"])} | '
        f'{item["low"]:,} / {item["in_range"]:,} / {item["high"]:,}'
        + (f'（另有 {item["no_output"]:,} 组无商品产出）' if item["no_output"] else "") + " |"
    )

lines += ["", "## 最低毛利组合", "", "以下列出可计算毛利的建筑。停用建筑仍保留，便于将来重新启用时复核。", ""]
for item in sorted((r for r in results if r["min_margin"] is not None), key=lambda r: r["min_margin"]):
    selection = item["min_selection"]
    cost, output = values(selection)
    lines.append(
        f'- **{item["name"]}**：{pct(item["min_margin"])}，投入 {fmt(cost)}，产出 {fmt(output)}；'
        + "、".join(f'`{pm}`' for pm in selection) + "。"
    )

lines += ["", "## 无商品产出的建筑", ""]
for item in results:
    if item["no_output"] == item["count"]:
        lines.append(f'- {item["name"]} (`{item["key"]}`)：主要通过修正、事件或建设进度发挥作用，商品毛利不适用。')

lines += ["", "## 同组商品产值下降", "", "按 PM 自身的基准价商品产出比较相邻档；负产出用于转产时也会列出。", ""]
output_drops = []
for item in results:
    for group in item["groups"]:
        choices = [pm for pm in vals(groups[group][0], "production_methods") if pm in pm_goods]
        for earlier, later in zip(choices, choices[1:]):
            earlier_value = sum(qty * prices[good] for (direction, good), qty in pm_goods[earlier].items() if direction == "output")
            later_value = sum(qty * prices[good] for (direction, good), qty in pm_goods[later].items() if direction == "output")
            if later_value < earlier_value:
                output_drops.append((item["name"], group, earlier, later, earlier_value, later_value))
for name, group, earlier, later, earlier_value, later_value in output_drops:
    lines.append(f'- {name} / `{group}`：`{earlier}` {fmt(earlier_value)} → `{later}` {fmt(later_value)}。')
if not output_drops:
    lines.append("- 无。")

lines += ["", "## 多重默认标记", ""]
for building, group, choices in ambiguous_defaults:
    lines.append(f'- `{building}` / `{group}`：' + "、".join(f'`{pm}`' for pm in choices))
if not ambiguous_defaults:
    lines.append("- 无。")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {OUT}: {len(results)} buildings, {sum(r['count'] for r in results):,} combinations")
for item in results:
    print(item["key"], item["count"], pct(item["min_margin"]), pct(item["max_margin"]), item["low"], item["high"])
