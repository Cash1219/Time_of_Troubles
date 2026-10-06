"""Compare cafe menu, service, and kitchen combinations at base prices."""

import contextlib
import itertools
import re
import runpy
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
with contextlib.redirect_stdout(StringIO()):
    audit = runpy.run_path(str(ROOT / "tools/audit_current_pm.py"))
blocks, vals, clean = (audit[key] for key in ("blocks", "vals", "clean"))
rows = {row["pm"]: row for row in audit["rows"]}

groups = {}
for group, body, _ in blocks(ROOT / "common/production_method_groups/kissaten.txt"):
    if group.startswith("pmg_kissaten_"):
        groups[group] = vals(body, "production_methods")

employment = {}
throughput = {}
for name, body, _ in blocks(ROOT / "common/production_methods/kissaten.txt"):
    body = clean(body)
    employment[name] = {
        kind: int(amount)
        for kind, amount in re.findall(r"\bbuilding_employment_([a-z_]+)_add\s*=\s*(-?\d+)", body)
    }
    match = re.search(r"\bbuilding_throughput_add\s*=\s*([-+]?\d+(?:\.\d+)?)", body)
    throughput[name] = float(match.group(1)) if match else 0.0

group_ids = list(groups)
menu_groups = group_ids[:4]
assert len(menu_groups) == 4 and group_ids[-2:] == ["pmg_kissaten_server", "pmg_kissaten_tool"]

results = []
for selected in itertools.product(*(groups[group] for group in group_ids)):
    menu_count = sum(not pm.endswith("_null") for pm in selected[:4])
    if not menu_count:
        continue
    revenue = sum(rows[pm]["outputs_value"] for pm in selected)
    raw_inputs = sum(rows[pm]["inputs_value"] for pm in selected)
    staff = {}
    for pm in selected:
        for kind, amount in employment[pm].items():
            staff[kind] = staff.get(kind, 0) + amount
    assert all(count >= 0 for count in staff.values()), (selected, staff)
    workers = sum(staff.values())
    wage_weights = {"laborers": 1, "machinists": 1.5, "shopkeepers": 3,
                    "clerks": 1.5, "academics": 4, "engineers": 3}
    weekly_wage = sum(count * wage_weights[kind] for kind, count in staff.items()) / 52
    scale = 1 + sum(throughput[pm] for pm in selected)
    margin = 100 * (revenue - raw_inputs) / revenue
    net = (revenue - raw_inputs) * scale - weekly_wage
    results.append((menu_count, selected[-1], selected[-2], margin, selected,
                    revenue, raw_inputs, workers, weekly_wage, net))

print(f"All selections: {len(results)} with at least one menu")
for menu_count in range(1, 5):
    subset = [x for x in results if x[0] == menu_count]
    low = min(subset, key=lambda x: x[3])
    high = max(subset, key=lambda x: x[3])
    print(f"{menu_count} menu(s): {len(subset)} choices, margin {low[3]:.1f}% to {high[3]:.1f}%, "
          f"workers {min(x[7] for x in subset)} to {max(x[7] for x in subset)}")

for tool in groups["pmg_kissaten_tool"]:
    subset = [x for x in results if x[1] == tool]
    low = min(subset, key=lambda x: x[3])
    print(f"{tool}: input {rows[tool]['inputs_value']:.0f}, "
          f"workers {min(x[7] for x in subset)} to {max(x[7] for x in subset)}, "
          f"worst margin {low[3]:.1f}%")

opening = (
    "pm_kissaten_coffee_coffee", "pm_kissaten_tea_null", "pm_kissaten_sweet_null",
    "pm_kissaten_food_null", "pm_kissaten_server_waitress", "pm_kissaten_tool_table",
)
matches = [x for x in results if x[4] == opening]
assert len(matches) == 1
open_row = matches[0]
print(f"Opening cafe selection: output {open_row[5]:.0f}, input {open_row[6]:.0f}, "
      f"workers {open_row[7]}, wage {open_row[8]:.1f}, net {open_row[9]:.1f}")
all_high = tuple(groups[group][-1] for group in group_ids)
high_row = next(x for x in results if x[4] == all_high)
print(f"All-high selection: output {high_row[5]:.0f}, input {high_row[6]:.0f}, "
      f"workers {high_row[7]}, wage {high_row[8]:.1f}, net including throughput {high_row[9]:.1f}")
