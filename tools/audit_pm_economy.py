"""Audit goods values of every PM selectable by a mod building.

Run from anywhere with ``python tools/audit_pm_economy.py``. The output is a
Markdown report; no game definitions are changed.
"""

from collections import Counter, defaultdict
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
VANILLA = Path(r"D:\Steam\steamapps\common\Victoria 3\game")
OUT = ROOT / "analysis" / "production_method_economy.md"
parser = runpy.run_path(str(ROOT / "docs/drafts/_audit_single_tech.py"))
blocks, vals = parser["blocks"], parser["vals"]


def clean(value):
    return "\n".join(line.split("#", 1)[0] for line in value.splitlines())


def inner(value, key):
    match = re.search(r"\b" + re.escape(key) + r"\s*=\s*\{", value)
    if not match:
        return ""
    depth = 1
    for index in range(match.end(), len(value)):
        depth += (value[index] == "{") - (value[index] == "}")
        if depth == 0:
            return value[match.end():index]
    raise ValueError(f"Unclosed block: {key}")


def definitions(folder, prefix):
    result = {}
    for base in (VANILLA, ROOT):
        for path in sorted((base / folder).glob("*.txt")):
            for name, body, _ in blocks(path):
                if name.startswith(prefix):
                    result[name] = (body, path)
    return result


def in_mod(path):
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


prices = {}
for name, (body, _) in definitions("common/goods", "").items():
    match = re.search(r"\bcost\s*=\s*(\d+(?:\.\d+)?)", clean(body))
    if match:
        prices[name] = float(match.group(1))

buildings = definitions("common/buildings", "building_")
# Only buildings defined by this mod are in scope. Vanilla definitions are
# consulted for inherited PM groups and PMs only.
mod_buildings = {
    name: (body, path) for name, (body, path) in buildings.items()
    if in_mod(path)
}
groups = definitions("common/production_method_groups", "pmg_")
pms = definitions("common/production_methods", "pm_")


def fmt(number):
    return f"{number:,.1f}" if number != int(number) else f"{number:,.0f}"


def pct(number):
    return f"{number:.1f}%"


rows = []
missing = []
for building, (body, _) in sorted(mod_buildings.items()):
    for group in vals(body, "production_method_groups"):
        if group not in groups:
            missing.append(f"missing PM group: {building} / {group}")
            continue
        for pm in vals(groups[group][0], "production_methods"):
            if pm not in pms:
                missing.append(f"missing PM: {building} / {group} / {pm}")
                continue
            pm_body, pm_path = pms[pm]
            code = clean(pm_body)
            scaled = inner(inner(code, "building_modifiers"), "workforce_scaled")
            goods = defaultdict(float)
            for direction, good, amount in re.findall(
                r"\bgoods_(input|output)_([\w]+)_add\s*=\s*([-+]?\d+(?:\.\d+)?)",
                scaled,
            ):
                goods[(direction, good)] += float(amount)
                if good not in prices:
                    missing.append(f"missing price: {pm} / {good}")
            input_value = sum(qty * prices.get(good, 0) for (direction, good), qty in goods.items() if direction == "input")
            output_value = sum(qty * prices.get(good, 0) for (direction, good), qty in goods.items() if direction == "output")
            mults = re.findall(r"\b(?:building_goods_(?:input|output)_mult|goods_(?:input|output)_[\w]+_mult)\s*=\s*[-+]?\d+(?:\.\d+)?", code)
            if input_value > 0 and output_value > 0:
                roi = (output_value - input_value) / input_value * 100
                margin = (output_value - input_value) / output_value * 100
                band = "低于30%" if margin < 30 else "高于70%" if margin > 70 else "30%–70%"
            elif input_value == 0 and output_value > 0:
                roi, margin, band = None, None, "无投入/仅产出"
            elif input_value > 0 and output_value <= 0:
                roi, margin, band = None, None, "仅投入/辅助"
            elif input_value == 0 and output_value < 0:
                roi, margin, band = None, None, "负产出/转产"
            else:
                roi, margin, band = None, None, "无商品流"
            rows.append({
                "building": building, "group": group, "pm": pm,
                "input": input_value, "output": output_value, "roi": roi, "margin": margin,
                "band": band, "mults": mults,
                "goods": goods, "source": pm_path.relative_to(ROOT) if in_mod(pm_path) else pm_path,
            })

if missing:
    raise SystemExit("\n".join(missing))

counts = Counter(row["band"] for row in rows)
roi_counts = Counter(
    "低于30%" if row["roi"] < 30 else "高于70%" if row["roi"] > 70 else "30%–70%"
    for row in rows if row["roi"] is not None
)
by_building = defaultdict(list)
for row in rows:
    by_building[row["building"]].append(row)

lines = [
    "# 模组建筑生产方式：基准价投入、产出与收益率",
    "",
    f"覆盖 **{len(by_building)} 栋模组建筑、{len(rows)} 个建筑 × 生产方式选择**。同一个 PM 若供多栋建筑使用，会按建筑重复列出。",
    "",
    "## 计算口径",
    "",
    "- 商品单价取游戏原版与模组 `common/goods/*.txt` 的 `cost`；模组同名商品覆盖原版。每级建筑满就业时，投入/产出总价为 `workforce_scaled` 的商品数量 × 基准价之和。",
    "- **商品毛利率 =（产出总价 − 投入总价）÷ 产出总价 × 100%**，以此判断 30%～70% 区间，与仓库已有审计的口径一致。另列投入收益率 `（产出总价 − 投入总价）÷ 投入总价` 供参考。",
    "- 这是一项 PM 单独带来的商品流，不是整栋建筑的利润。建筑会同时启用多个 PMG；不含工资、实际就业率、吞吐量、科技/法律效果和市场价格。",
    "- 倍率修正（如 `building_goods_input_mult`、`goods_output_games_mult`）在明细中标记，但未分摊到单项 PM；它们需在整栋建筑组合中计算。零投入、纯成本、无商品流和转产项不适用单项收益率。",
    "",
    "## 总览",
    "",
    "| 类别 | 数量 |",
    "|---|---:|",
]
for label in ("低于30%", "30%–70%", "高于70%", "无投入/仅产出", "仅投入/辅助", "负产出/转产", "无商品流"):
    lines.append(f"| {label} | {counts[label]} |")
lines += [
    "",
    f"可计算毛利率的 {sum(roi_counts.values())} 项中，若改用投入收益率筛选，则低于 30% 有 {roi_counts['低于30%']} 项，区间内 {roi_counts['30%–70%']} 项，高于 70% 有 {roi_counts['高于70%']} 项。",
    "",
    "## 需要优先核查的地方",
    "",
    "以下先列单项数值线索。具体低毛利改进方案见 [低毛利改进清单](low_margin_improvements.md)。只有完整建筑组合与游戏内工资、市场价格核对后，才适合修改 PM 数量。",
    "",
]

# Show concentrated outliers, while keeping all rows in the detailed tables.
for building, items in by_building.items():
    relevant = [r for r in items if r["margin"] is not None]
    low = [r for r in relevant if r["margin"] < 30]
    high = [r for r in relevant if r["margin"] > 70]
    if low or high:
        low_text = f"{len(low)} 项；最低 {min(r['margin'] for r in low):.1f}%" if low else "0 项"
        high_text = f"{len(high)} 项；最高 {max(r['margin'] for r in high):.1f}%" if high else "0 项"
        lines.append(f"- `{building}`：低于下限 {low_text}，高于上限 {high_text}。")

lines += [
    "",
    "**调整量参考**：若投入固定为 I，毛利率 30%～70% 对应的产出范围是 `I÷0.7～I÷0.3`；若只要求至少 30%，产出必须不低于 `I÷0.7`。辅助 PM 不适用。",
    "",
    "## 全量明细",
    "",
]
for building, items in by_building.items():
    lines += [
        f"### `{building}`",
        "",
        "| 生产方式组 | 生产方式 | 投入总价 | 产出总价 | 商品差额 | 投入收益率 | 商品毛利率 | 毛利率判定 | 倍率修正 |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in items:
        delta = row["output"] - row["input"]
        lines.append(
            f"| `{row['group']}` | `{row['pm']}` | {fmt(row['input'])} | {fmt(row['output'])} | "
            f"{fmt(delta)} | {pct(row['roi']) if row['roi'] is not None else '—'} | "
            f"{pct(row['margin']) if row['margin'] is not None else '—'} | {row['band']} | "
            f"{'；'.join(row['mults']) if row['mults'] else '—'} |"
        )
    lines.append("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT} ({len(rows)} rows across {len(by_building)} buildings)")
print(dict(counts))
