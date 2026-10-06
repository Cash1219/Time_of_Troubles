"""Compare cafe goods margins across relevant Git revisions at base prices."""

import itertools
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VANILLA_GOODS = Path(r"D:\Steam\steamapps\common\Victoria 3\game\common\goods\00_goods.txt")
REVISIONS = (
    ("bb986ed", "2026-05-24 before menu cut"),
    ("7e2886b", "2026-05-28 after menu cut"),
    ("3dd0246", "2026-06-25 service output conversion"),
    ("80f5090", "2026-08-28 ordinary service removed"),
    ("2cc4a1b", "2026-09-04 equipment employment"),
    ("HEAD", "committed HEAD before candidate edits"),
    ("WORKTREE", "working-tree candidate"),
)


def clean(value):
    return "\n".join(line.split("#", 1)[0] for line in value.splitlines())


def blocks(source):
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^([\w-]+)\s*=\s*\{", lines[index])
        if not match:
            index += 1
            continue
        start = index
        depth = 0
        while index < len(lines):
            code = lines[index].split("#", 1)[0]
            depth += code.count("{") - code.count("}")
            index += 1
            if depth == 0:
                break
        yield match.group(1), "\n".join(lines[start:index])


def inner(body, key):
    match = re.search(r"\b" + re.escape(key) + r"\s*=\s*\{", body)
    if not match:
        return ""
    depth = 1
    for index in range(match.end(), len(body)):
        depth += (body[index] == "{") - (body[index] == "}")
        if depth == 0:
            return body[match.end():index]
    raise ValueError(key)


def snapshot(revision, path):
    if revision == "WORKTREE":
        return (ROOT / path).read_text(encoding="utf-8-sig", errors="replace")
    return subprocess.check_output(
        ["git", "show", revision + ":" + path], cwd=str(ROOT)
    ).decode("utf-8-sig", errors="replace")


def values(body, key):
    return re.findall(r"[\w-]+", inner(clean(body), key))


def prices_at(revision):
    prices = {}
    for source in (VANILLA_GOODS.read_text(encoding="utf-8-sig", errors="replace"),
                   snapshot(revision, "common/goods/tot_goods.txt")):
        for name, body in blocks(source):
            match = re.search(r"\bcost\s*=\s*(\d+(?:\.\d+)?)", clean(body))
            if match:
                prices[name] = float(match.group(1))
    return prices


def revisions_data(revision):
    prices = prices_at(revision)
    pms = {}
    for name, body in blocks(snapshot(revision, "common/production_methods/kissaten.txt")):
        if not name.startswith("pm_kissaten_"):
            continue
        code = clean(body)
        scaled = inner(inner(code, "building_modifiers"), "workforce_scaled")
        quantities = defaultdict(float)
        for direction, good, quantity in re.findall(
            r"\bgoods_(input|output)_([\w]+)_add\s*=\s*([-+]?\d+(?:\.\d+)?)",
            scaled,
        ):
            if good not in prices:
                raise ValueError("No price for " + good + " at " + revision)
            quantities[(direction, good)] += float(quantity)
        cost = sum(q * prices[good] for (direction, good), q in quantities.items() if direction == "input")
        revenue = sum(q * prices[good] for (direction, good), q in quantities.items() if direction == "output")
        multiplier = sum(float(value) for value in re.findall(
            r"\bbuilding_goods_input_mult\s*=\s*([-+]?\d+(?:\.\d+)?)", code
        ))
        pms[name] = (cost, revenue, multiplier, quantities)
    groups = {}
    for name, body in blocks(snapshot(revision, "common/production_method_groups/kissaten.txt")):
        if name.startswith("pmg_kissaten_"):
            groups[name] = values(body, "production_methods")
    return pms, groups


def totals(pms, selected):
    cost = sum(pms[pm][0] for pm in selected)
    revenue = sum(pms[pm][1] for pm in selected)
    cost *= 1 + sum(pms[pm][2] for pm in selected)
    return cost, revenue, 100 * (revenue - cost) / revenue if revenue else None


opening = (
    "pm_kissaten_coffee_coffee", "pm_kissaten_tea_null", "pm_kissaten_sweet_null",
    "pm_kissaten_food_null", "pm_kissaten_server_waitress", "pm_kissaten_tool_table",
)
print("revision,menu_cost,menu_revenue,opening_cost,opening_revenue,opening_margin,below30,within30to70,above70,total")
for revision, label in REVISIONS:
    pms, groups = revisions_data(revision)
    group_lists = list(groups.values())
    count = low = in_band = high = 0
    for selected in itertools.product(*group_lists):
        if all(pm.endswith("_null") for pm in selected[:4]):
            continue
        _, _, margin = totals(pms, selected)
        if margin is None:
            continue
        count += 1
        low += margin < 30
        in_band += 30 <= margin <= 70
        high += margin > 70
    cost, revenue, margin = totals(pms, opening)
    menu_cost, menu_revenue = pms["pm_kissaten_coffee_coffee"][:2]
    print(f"{revision} {label},{menu_cost:.0f},{menu_revenue:.0f},{cost:.0f},{revenue:.0f},{margin:.1f}%,{low},{in_band},{high},{count}")

# Isolate the old menu-output schedule while retaining every other current PM.
old_pms, _ = revisions_data("bb986ed")
current_pms, current_groups = revisions_data("HEAD")
for pm in current_pms:
    if pm.startswith(("pm_kissaten_coffee_", "pm_kissaten_tea_", "pm_kissaten_sweet_", "pm_kissaten_food_")):
        old_revenue = old_pms[pm][1]
        current_cost, _, multiplier, quantities = current_pms[pm]
        current_pms[pm] = (current_cost, old_revenue, multiplier, quantities)
low = in_band = high = 0
for selected in itertools.product(*current_groups.values()):
    if all(pm.endswith("_null") for pm in selected[:4]):
        continue
    _, _, margin = totals(current_pms, selected)
    low += margin < 30
    in_band += 30 <= margin <= 70
    high += margin > 70
cost, revenue, margin = totals(current_pms, opening)
print(f"COUNTERFACTUAL old menu output plus current other PMs: opening {cost:.0f}/{revenue:.0f}/{margin:.1f}%; combinations {low} low, {in_band} in band, {high} high")
