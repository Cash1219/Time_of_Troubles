"""Check cafe margins after reducing inputs and requiring one coffee PM."""

from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import runpy


ROOT = Path(__file__).resolve().parents[1]
audit = runpy.run_path(str(ROOT / "tools/audit_pm_economy.py"))
rows = [row for row in audit["rows"] if row["building"] == "building_kissaten"]
groups = defaultdict(list)
for row in rows:
    groups[row["group"]].append(row)

assert "pm_kissaten_coffee_null" not in [row["pm"] for row in groups["pmg_kissaten_coffee"]]
assert all(row["pm"] != "pm_kissaten_coffee_null" for row in rows)
menu_groups = {"pmg_kissaten_coffee", "pmg_kissaten_tea", "pmg_kissaten_sweet", "pmg_kissaten_food"}
menus = [row for row in rows if row["group"] in menu_groups and row["output"] > 0]
assert len(menus) == 15
assert all(30 <= row["margin"] <= 70 for row in menus)

discount = {}
for pm, (body, _) in audit["pms"].items():
    discount[pm] = sum(float(value) for value in re.findall(
        r"\bbuilding_goods_input_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", audit["clean"](body)
    ))


def margin(selected):
    output = sum(row["output"] for row in selected)
    inputs = sum(row["input"] for row in selected)
    inputs *= 1 + sum(discount[row["pm"]] for row in selected)
    return 100 * (output - inputs) / output if output else None


by_pm = {row["pm"]: row for row in rows}
benchmark = (
    "pm_kissaten_tea_null", "pm_kissaten_sweet_null", "pm_kissaten_food_null",
    "pm_kissaten_server_waitress", "pm_kissaten_tool_table",
)
for coffee in groups["pmg_kissaten_coffee"]:
    selected = [coffee] + [by_pm[pm] for pm in benchmark]
    value = margin(selected)
    assert 30 <= value <= 70
    print(f"{coffee['pm']}: one-menu cafe with waitress and table = {value:.1f}%")

total = below = within = above = 0
by_tool = defaultdict(lambda: [0, 0])
for selected in product(*groups.values()):
    value = margin(selected)
    if value is None:
        continue
    total += 1
    below += value < 30
    within += 30 <= value <= 70
    above += value > 70
    tool = next(row["pm"] for row in selected if row["group"] == "pmg_kissaten_tool")
    by_tool[tool][0] += value < 30
    by_tool[tool][1] += 1

print(f"All theoretical combinations: {total}; below 30%: {below}; 30-70%: {within}; above 70%: {above}")
for tool, (bad, count) in by_tool.items():
    print(f"  {tool}: {bad}/{count} below 30%")
print(f"Menu PM margins: {min(row['margin'] for row in menus):.1f}% to {max(row['margin'] for row in menus):.1f}%")
