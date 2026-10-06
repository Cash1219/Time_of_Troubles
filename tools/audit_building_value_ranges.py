"""Enumerate base-price goods value ranges for vanilla and mod buildings."""

from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "building_value_ranges.md"
audit = runpy.run_path(str(ROOT / "tools/audit_pm_economy.py"))
buildings = audit["buildings"]
groups = audit["groups"]
pms = audit["definitions"]("common/production_methods", "")
prices = audit["prices"]
clean = audit["clean"]
inner = audit["inner"]
vals = audit["vals"]


def value_fmt(value):
    return f"{value:,.1f}" if abs(value - round(value)) > 1e-8 else f"{value:,.0f}"


def pm_effect(name):
    if name not in pms:
        raise ValueError("Undefined PM: " + name)
    body, _ = pms[name]
    code = clean(body)
    modifiers = inner(code, "building_modifiers")
    scaled = inner(modifiers, "workforce_scaled")
    amounts = defaultdict(float)
    for direction, good, amount in re.findall(
        r"\bgoods_(input|output)_([\w]+)_add\s*=\s*([-+]?\d+(?:\.\d+)?)", scaled
    ):
        if good not in prices:
            raise ValueError(f"No base price: {good} in {name}")
        amounts[(direction, good)] += float(amount)
    multipliers = defaultdict(float)
    for direction, good, amount in re.findall(
        r"\bgoods_(input|output)_([\w]+)_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", modifiers
    ):
        multipliers[(direction, good)] += float(amount)
    for direction, amount in re.findall(
        r"\bbuilding_goods_(input|output)_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", modifiers
    ):
        multipliers[(direction, "*")] += float(amount)
    return amounts, multipliers


effects = {name: pm_effect(name) for name in pms}


def values_for(selection):
    amounts = defaultdict(float)
    multipliers = defaultdict(float)
    for name in selection:
        goods, mults = effects[name]
        for key, amount in goods.items():
            amounts[key] += amount
        for key, amount in mults.items():
            multipliers[key] += amount
    totals = {}
    for direction in ("input", "output"):
        totals[direction] = sum(
            amount * prices[good] * (
                1 + multipliers[(direction, "*")] + multipliers[(direction, good)]
            )
            for (kind, good), amount in amounts.items() if kind == direction
        )
    return totals["input"], totals["output"], totals["output"] - totals["input"]


rows = []
selections_all = []
for building, (body, path) in sorted(buildings.items()):
    group_names = vals(body, "production_method_groups")
    choices = []
    for group in group_names:
        if group not in groups:
            raise ValueError(f"Undefined group: {building} / {group}")
        options = [pm for pm in vals(groups[group][0], "production_methods") if pm in pms]
        if not options:
            raise ValueError(f"Empty group: {building} / {group}")
        choices.append(options)
    extrema = [None] * 6
    selections = [None] * 6
    count = 0
    source = "mod" if audit["in_mod"](path) else "vanilla"
    for selection in product(*choices):
        count += 1
        cost, revenue, surplus = values_for(selection)
        selections_all.append((building, source, selection, cost, revenue, surplus))
        for index, value in enumerate((cost, revenue, surplus)):
            lo = index * 2
            hi = lo + 1
            if extrema[lo] is None or value < extrema[lo]:
                extrema[lo], selections[lo] = value, selection
            if extrema[hi] is None or value > extrema[hi]:
                extrema[hi], selections[hi] = value, selection
    building_group = re.search(r"\bbuilding_group\s*=\s*([\w-]+)", clean(body))
    buildable = re.search(r"\bbuildable\s*=\s*(yes|no)", clean(body))
    rows.append({
        "building": building,
        "source": source,
        "group": building_group.group(1) if building_group else "",
        "buildable": buildable.group(1) if buildable else "unspecified",
        "combinations": count,
        "extrema": extrema,
        "selections": selections,
    })

assert all(row["extrema"][0] <= row["extrema"][1] for row in rows)
assert all(row["extrema"][2] <= row["extrema"][3] for row in rows)
assert all(row["extrema"][4] <= row["extrema"][5] for row in rows)

labels = ("minimum input", "maximum input", "minimum output", "maximum output", "minimum surplus", "maximum surplus")
def extrema_for(scope):
    result = []
    for index, label in enumerate(labels):
        key = min if index % 2 == 0 else max
        winner = key(scope, key=lambda row: row["extrema"][index])
        result.append((label, winner, index))
    return result


def extrema_table(title, scope):
    result = [
        f"## {title}", "",
        "| Measure | Input | Output | Goods surplus | Building | PM selection |",
        "|---|---:|---:|---:|---|---|",
    ]
    for label, winner, index in extrema_for(scope):
        values = values_for(winner["selections"][index])
        result.append(
            f"| {label} | " + " | ".join(value_fmt(value) for value in values)
            + f" | `{winner['building']}` | "
            + "; ".join("`" + pm + "`" for pm in winner["selections"][index]) + " |"
        )
    result.append("")
    return result


global_extrema = extrema_for(rows)

lines = [
    "# Base-price goods value ranges for all buildings",
    "",
    f"Effective vanilla and mod definitions: {len(rows)} buildings ({sum(r['source']=='vanilla' for r in rows)} vanilla, {sum(r['source']=='mod' for r in rows)} mod).",
    "",
    "Each figure is per building level at full employment and base goods prices. One PM is selected from each PM group. The six extrema in a row may come from six different selections. Goods-input and goods-output multipliers in selected PMs are applied to the entire building. Wages, market prices, throughput, ownership and legal/technology availability are excluded. Explicitly unbuildable buildings remain in scope.",
    "",
]
lines += extrema_table("All buildings", rows)
lines += extrema_table("Vanilla buildings", [row for row in rows if row["source"] == "vanilla"])
lines += extrema_table("Mod buildings", [row for row in rows if row["source"] == "mod"])
lines += [
    "## Smallest positive values",
    "",
    "| Scope | Measure | Input | Output | Goods surplus | Building | PM selection |",
    "|---|---|---:|---:|---:|---|---|",
]
for scope_name, source in (("All", None), ("Vanilla", "vanilla"), ("Mod", "mod")):
    subset = [entry for entry in selections_all if source is None or entry[1] == source]
    for measure, value_index in (("Input > 0", 3), ("Output > 0", 4)):
        winner = min((entry for entry in subset if entry[value_index] > 0), key=lambda entry: entry[value_index])
        building, _, selection, cost, revenue, surplus = winner
        lines.append(
            f"| {scope_name} | {measure} | {value_fmt(cost)} | {value_fmt(revenue)} | {value_fmt(surplus)} | "
            f"`{building}` | " + "; ".join("`" + pm + "`" for pm in selection) + " |"
        )
lines.append("")

lines += [
    "",
    "## Every building",
    "",
    "| Building | Source | Group | Buildable | Combinations | Input min | Input max | Output min | Output max | Surplus min | Surplus max |",
    "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
]
for row in rows:
    lines.append(
        f"| `{row['building']}` | {row['source']} | `{row['group']}` | {row['buildable']} | "
        f"{row['combinations']:,} | " + " | ".join(value_fmt(x) for x in row["extrema"]) + " |"
    )

lines += [
    "",
    "## How to read the table",
    "",
    "`Surplus = output value - input value`. It is a goods-only difference, not net building profit. For a building's maximum surplus, subtracting its minimum input from its maximum output is usually wrong because those extremes can use different PM selections.",
    "",
]
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}: {len(rows)} buildings, {sum(r['combinations'] for r in rows):,} selections")
for label, winner, index in global_extrema:
    print(label, value_fmt(winner["extrema"][index]), winner["building"])
