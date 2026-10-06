"""Export one row per PM relevant to the mod, without building combinations."""

from collections import defaultdict
from pathlib import Path
import contextlib
import io
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "all_single_pm_economy.md"

with contextlib.redirect_stdout(io.StringIO()):
    audit = runpy.run_path(str(ROOT / "tools" / "audit_pm_economy.py"))

definitions = audit["definitions"]("common/production_methods", "")
prices = audit["prices"]
used_by = defaultdict(set)
for item in audit["rows"]:
    used_by[item["pm"]].add(item["building"])


def chinese_names():
    """Load vanilla labels, then let mod labels and replacements override them."""
    labels = {}
    vanilla = audit["VANILLA"]
    roots = (
        vanilla / "localization",
        ROOT / "localization" / "simp_chinese",
        ROOT / "localization" / "replace" / "simp_chinese",
    )
    entry = re.compile(r'^\s*([\w.-]+):\s*(?:\d+\s*)?"((?:\\.|[^"\\])*)"')
    for folder in roots:
        for path in sorted(folder.rglob("*_l_simp_chinese.yml")):
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                match = entry.match(line)
                if match:
                    labels[match.group(1)] = match.group(2).replace(r'\"', '"')
    return labels


labels = chinese_names()

names = {
    name for name, (_, path) in definitions.items() if audit["in_mod"](path)
} | set(used_by)


def fmt(value):
    return f"{value:,.2f}".rstrip("0").rstrip(".") if value != int(value) else f"{value:,.0f}"


def single_pm_values(name):
    body, _ = definitions[name]
    scaled = audit["inner"](
        audit["inner"](audit["clean"](body), "building_modifiers"),
        "workforce_scaled",
    )
    totals = defaultdict(float)
    for direction, good, quantity in re.findall(
        r"\bgoods_(input|output)_([\w]+)_add\s*=\s*([-+]?\d+(?:\.\d+)?)",
        scaled,
    ):
        if good not in prices:
            raise ValueError(f"Missing base price for {name}: {good}")
        totals[direction] += float(quantity) * prices[good]
    return totals["input"], totals["output"]


rows = []
for name in names:
    cost, revenue = single_pm_values(name)
    margin = (revenue - cost) / revenue * 100 if revenue > 0 else None
    body, path = definitions[name]
    rows.append({
        "pm": name,
        "pm_zh": labels.get(name),
        "buildings": sorted(used_by[name]),
        "source": "模组" if audit["in_mod"](path) else "原版复用",
        "input": cost,
        "output": revenue,
        "margin": margin,
    })

rows.sort(key=lambda row: (not row["buildings"], row["buildings"][0] if row["buildings"] else "", row["pm"]))

# The new independent parse must agree with the existing per-building PM audit.
for item in audit["rows"]:
    cost, revenue = single_pm_values(item["pm"])
    assert abs(cost - item["input"]) < 1e-8, item["pm"]
    assert abs(revenue - item["output"]) < 1e-8, item["pm"]

lines = [
    "# 全部单项 PM 的商品投入、产出和毛利率",
    "",
    f"共 **{len(rows)} 个独立 PM**：{sum(r['source'] == '模组' for r in rows)} 个模组定义、"
    f"{sum(r['source'] == '原版复用' for r in rows)} 个被模组建筑复用的原版 PM；"
    f"其中 {sum(not r['buildings'] for r in rows)} 个模组 PM 当前未被建筑引用。",
    "",
    "每行只计算该 PM 在 `workforce_scaled` 中直接添加的商品数量 × 商品基础价。"
    "毛利率＝（产出总价－投入总价）÷产出总价。无正产出的 PM 毛利率记为“—”。"
    "建筑整体投入折扣、产出倍率、吞吐量、工资和市场价均未计入，因为它们需要完整建筑组合才能核算。",
    "",
    "| 建筑中文名 | 建筑 ID | PM 中文名 | PM ID | 来源 | 投入总价 | 产出总价 | 毛利率 |",
    "|---|---|---|---|---|---:|---:|---:|",
]
for row in rows:
    buildings = "、".join(f"`{name}`" for name in row["buildings"]) or "—"
    building_names = "、".join(
        labels.get(name) or labels.get("pm_default_" + name) or "缺中文翻译"
        for name in row["buildings"]
    ) or "未引用"
    pm_name = row["pm_zh"] or "缺中文翻译"
    margin = f"{row['margin']:.1f}%" if row["margin"] is not None else "—"
    lines.append(
        f"| {building_names} | {buildings} | {pm_name} | `{row['pm']}` | {row['source']} | "
        f"{fmt(row['input'])} | {fmt(row['output'])} | {margin} |"
    )

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {OUT}: {len(rows)} unique PMs")
