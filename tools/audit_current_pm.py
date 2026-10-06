"""Export a read-only, base-price audit of the mod's current PM definitions."""

import csv
import re
import runpy
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VANILLA = Path(r"D:\Steam\steamapps\common\Victoria 3\game")
AUDIT = runpy.run_path(str(ROOT / "docs/drafts/_audit_single_tech.py"))
blocks, vals, ancestors = (AUDIT[key] for key in ("blocks", "vals", "ancestors"))


def subblock(body: str, key: str) -> str:
    match = re.search(r"\b" + re.escape(key) + r"\s*=\s*\{", body)
    if not match:
        return ""
    start = match.end()
    depth = 1
    for index in range(start, len(body)):
        if body[index] == "{":
            depth += 1
        elif body[index] == "}":
            depth -= 1
            if depth == 0:
                return body[start:index]
    raise ValueError(f"Unclosed {key} block")


def clean(body: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in body.splitlines())


prices = {}
for base in (VANILLA, ROOT):
    for path in sorted((base / "common/goods").glob("*.txt")):
        for name, body, _ in blocks(path):
            match = re.search(r"\bcost\s*=\s*([0-9.]+)", clean(body))
            if match:
                prices[name] = float(match.group(1))

pms = {}
for path in sorted((ROOT / "common/production_methods").glob("*.txt")):
    for name, body, _ in blocks(path):
        if not name.startswith("pm_"):
            continue
        build = subblock(clean(body), "building_modifiers")
        scale = subblock(build, "workforce_scaled")
        modifiers = {}
        for kind, good, amount in re.findall(
            r"goods_(input|output)_([\w]+)_add\s*=\s*([-+]?[0-9.]+)", scale
        ):
            modifiers[(kind, good)] = modifiers.get((kind, good), 0.0) + float(amount)
        pms[name] = {
            "tech": vals(body, "unlocking_technologies"),
            "modifiers": modifiers,
            "file": str(path.relative_to(ROOT)),
        }

group_buildings = defaultdict(list)
for path in sorted((ROOT / "common/buildings").glob("*.txt")):
    for building, body, _ in blocks(path):
        if building.startswith("building_"):
            for group in vals(body, "production_method_groups"):
                group_buildings[group].append(building)

names_zh = {}
review_path = ROOT / "docs/drafts/building_pm_tech_review.md"
if review_path.exists():
    for line in review_path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"\|\s*\d+\s*\|\s*(.+?)（`(pm_[\w]+)`）", line)
        if match:
            names_zh[match.group(2)] = match.group(1)

rows = []
for path in sorted((ROOT / "common/production_method_groups").glob("*.txt")):
    for group, body, _ in blocks(path):
        if not group.startswith("pmg_"):
            continue
        group_pms = [x for x in vals(body, "production_methods") if x.startswith("pm_")]
        previous = None
        for position, pm in enumerate(group_pms, 1):
            if pm not in pms:
                continue
            item = pms[pm]
            costs = 0.0
            revenue = 0.0
            missing = set()
            output_goods = defaultdict(float)
            for (kind, good), amount in item["modifiers"].items():
                price = prices.get(good)
                if price is None:
                    missing.add(good)
                    continue
                if kind == "input":
                    costs += amount * price
                else:
                    revenue += amount * price
                    output_goods[good] += amount
            tech = item["tech"]
            previous_tech = pms[previous]["tech"] if previous in pms else []
            tech_break = bool(previous_tech) and (
                not tech or previous_tech[0] not in ancestors(tech[0])
            )
            same_tech_as_previous = bool(previous_tech and tech and previous_tech[0] == tech[0])
            output_falls = False
            gross_output_falls = False
            if previous in pms:
                prior_outputs = pms[previous]["output_goods"]
                # Only compare goods produced by both adjacent PMs. Product swaps are flagged separately.
                common = set(output_goods) & set(prior_outputs)
                output_falls = any(output_goods[g] < prior_outputs[g] for g in common)
                gross_output_falls = revenue < pms[previous]["revenue"]
            item["output_goods"] = output_goods
            item["revenue"] = revenue
            rows.append({
                "building": ";".join(group_buildings[group]),
                "group": group,
                "position": position,
                "pm": pm,
                "chinese": names_zh.get(pm, ""),
                "tech": ";".join(tech),
                "inputs_value": round(costs, 2),
                "outputs_value": round(revenue, 2),
                "base_price_standalone_goods_margin_percent": round((revenue - costs) / revenue * 100, 1) if revenue > 0 and not missing else "",
                "goods_inputs": ";".join(f"{g}:{v:g}" for (k, g), v in item["modifiers"].items() if k == "input"),
                "goods_outputs": ";".join(f"{g}:{v:g}" for (k, g), v in item["modifiers"].items() if k == "output"),
                "missing_prices": ";".join(sorted(missing)),
                "tech_break_from_previous": "yes" if tech_break else "",
                "same_tech_as_previous": "yes" if same_tech_as_previous else "",
                "same_good_output_falls": "yes" if output_falls else "",
                "gross_output_falls": "yes" if gross_output_falls else "",
                "source": item["file"],
            })
            previous = pm

output = ROOT / "docs/drafts/current_pm_audit.csv"
with output.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print(f"Exported {len(rows)} PM entries in {len(set(r['group'] for r in rows))} groups")
print(f"Missing prices: {sorted(set(g for r in rows for g in r['missing_prices'].split(';') if g))}")
print(f"Tech breaks: {sum(r['tech_break_from_previous'] == 'yes' for r in rows)}")
print(f"Same-tech adjacent PMs: {sum(r['same_tech_as_previous'] == 'yes' for r in rows)}")
print(f"Same-good output decreases: {sum(r['same_good_output_falls'] == 'yes' for r in rows)}")
print(f"Gross output value decreases: {sum(r['gross_output_falls'] == 'yes' for r in rows)}")
for row in rows:
    if row["gross_output_falls"] == "yes":
        print(" FALL", row["building"], row["group"], row["pm"], row["outputs_value"])
for label, subset in (
    ("below_30", [r for r in rows if isinstance(r['base_price_standalone_goods_margin_percent'], float) and r['base_price_standalone_goods_margin_percent'] < 30]),
    ("above_70", [r for r in rows if isinstance(r['base_price_standalone_goods_margin_percent'], float) and r['base_price_standalone_goods_margin_percent'] > 70]),
):
    print(f"{label}: {len(subset)}")
    for row in subset[:20]:
        print(" ", row["building"], row["pm"], row["base_price_standalone_goods_margin_percent"])
