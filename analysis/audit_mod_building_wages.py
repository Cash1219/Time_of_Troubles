"""Add reference-wage employment estimates to the current mod building audit.

This is a static PM-definition audit, not a simulation of market prices, hiring,
ownership dividends, throughput, laws, or changing annual base wages.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
VANILLA = Path(r"D:\Steam\steamapps\common\Victoria 3\game")
SOURCE = ROOT / "analysis/current_all_mod_buildings.md"
OUTPUT = ROOT / "analysis/mod_building_workforce_wages.md"


def blocks(folder: Path, prefix: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(folder.glob("*.txt")):
        source = path.read_text(encoding="utf-8-sig", errors="ignore")
        for match in re.finditer(rf"(?m)^({re.escape(prefix)}[A-Za-z0-9_]+)\s*=\s*\{{", source):
            name = match.group(1)
            opening = match.end() - 1
            depth = 0
            for index in range(opening, len(source)):
                if source[index] == "{":
                    depth += 1
                elif source[index] == "}":
                    depth -= 1
                    if depth == 0:
                        result[name] = source[opening + 1:index]
                        break
    return result


def combined_blocks(folder: str, prefix: str) -> dict[str, str]:
    result = blocks(VANILLA / folder, prefix)
    result.update(blocks(ROOT / folder, prefix))
    return result


def members(body: str, key: str, prefix: str) -> list[str]:
    match = re.search(rf"\b{key}\s*=\s*\{{([^}}]*)\}}", body, re.S)
    return re.findall(rf"\b{prefix}[A-Za-z0-9_]+\b", match.group(1)) if match else []


def employment(body: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for kind, amount in re.findall(r"\bbuilding_employment_([a-z0-9_]+)_add\s*=\s*(-?\d+)", body):
        result[kind] = result.get(kind, 0) + int(amount)
    return result


def price_pair(cell: str) -> tuple[float, float] | None:
    match = re.fullmatch(r"([\d,.]+)→([\d,.]+)", cell.strip())
    return (float(match.group(1).replace(",", "")),
            float(match.group(2).replace(",", ""))) if match else None


def fmt(value: float | None) -> str:
    return "—" if value is None else f"{value:,.1f}".rstrip("0").rstrip(".")


def main() -> None:
    pms = combined_blocks("common/production_methods", "pm_")
    groups = combined_blocks("common/production_method_groups", "pmg_")
    buildings = combined_blocks("common/buildings", "building_")
    pop_types = combined_blocks("common/pop_types", "")
    wage_weights: dict[str, float] = {}
    for name, body in pop_types.items():
        weight = re.search(r"\bwage_weight\s*=\s*([\d.]+)", body)
        paid = re.search(r"\bpaid_private_wage\s*=\s*(yes|no)", body)
        if weight and paid and paid.group(1) == "yes":
            wage_weights[name] = float(weight.group(1))

    def selection_for(building: str, advanced: bool) -> list[str] | None:
        if building not in buildings:
            return None
        selected = []
        for group in members(buildings[building], "production_method_groups", "pmg_"):
            if group not in groups:
                continue
            options = members(groups[group], "production_methods", "pm_")
            if not options:
                continue
            if advanced:
                chosen = options[-1]
            else:
                chosen = next((pm for pm in options if re.search(r"\bis_default\s*=\s*yes", pms.get(pm, ""))), options[0])
            selected.append(chosen)
        return selected

    def staff_for(selected: list[str] | None) -> dict[str, int] | None:
        if selected is None:
            return None
        result: dict[str, int] = {}
        for chosen in selected:
            for kind, amount in employment(pms.get(chosen, "")).items():
                result[kind] = result.get(kind, 0) + amount
        return result

    def throughput_for(selected: list[str] | None) -> float:
        if selected is None:
            return 0.0
        total = 0.0
        for chosen in selected:
            total += sum(float(value) for value in re.findall(
                r"\bbuilding_throughput_add\s*=\s*([-+]?\d+(?:\.\d+)?)", pms.get(chosen, "")
            ))
        return total

    def weekly_wage(staff: dict[str, int] | None) -> float | None:
        if staff is None:
            return None
        return sum(amount * wage_weights.get(kind, 0.0) for kind, amount in staff.items()) / 52

    lines = [
        "# 模组建筑：参考工资下的人力与净商品收益",
        "",
        "以劳工年工资 1、每年 52 周为基准；其他职业乘原版 `wage_weight`。未付私人企业工资的职业不计工资。",
        "商品投入/产出沿用《全部模组建筑：当前基准价商品收支复核》。默认档和全高档按原表规则选 PM。",
        "部分建筑第一档是无生产 PM；其默认人数为 0 只说明该组合未开工，不能据此判断正常生产时的编制。",
        "人均年产值＝（产出商品总价－投入商品总价）×PM 直接吞吐量倍率×52÷员工数；扣工资后差额也计入 PM 直接吞吐量。",
        "这是假设满就业、商品按基础价、无州修正、规模经济或市场价格变化的静态比较，不代表实际游戏利润。",
        "若劳工实际年工资为 B，则表中周工资乘 B；其他职业工资也按原版倍率随 B 变化。无所有权和事件建筑的财政含义须另看。",
        "",
        "| 建筑 | 可建 | 默认人数 | 默认周工资 | 默认扣工资后差额 | 默认人均年产值 | 全高档人数 | 全高档周工资 | 全高档扣工资后差额 | 全高档人均年产值 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    count = 0
    for line in SOURCE.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("| ") or "(`building_" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        match = re.search(r"\((`building_[a-z0-9_]+`)\)", cells[0])
        if not match:
            continue
        building = match.group(1).strip("`")
        default_selection = selection_for(building, False)
        advanced_selection = selection_for(building, True)
        default_staff = staff_for(default_selection)
        advanced_staff = staff_for(advanced_selection)
        default_wage = weekly_wage(default_staff)
        advanced_wage = weekly_wage(advanced_staff)
        default_values = price_pair(cells[3])
        advanced_values = price_pair(cells[5])
        default_gross = (default_values[1] - default_values[0]) * (1 + throughput_for(default_selection)) if default_values else None
        advanced_gross = (advanced_values[1] - advanced_values[0]) * (1 + throughput_for(advanced_selection)) if advanced_values else None
        default_net = default_gross - default_wage if default_gross is not None and default_wage is not None else None
        advanced_net = advanced_gross - advanced_wage if advanced_gross is not None and advanced_wage is not None else None
        default_workers = sum(default_staff.values()) if default_staff is not None else None
        advanced_workers = sum(advanced_staff.values()) if advanced_staff is not None else None
        default_annual = default_gross * 52 / default_workers if default_gross is not None and default_workers and default_workers > 0 else None
        advanced_annual = advanced_gross * 52 / advanced_workers if advanced_gross is not None and advanced_workers and advanced_workers > 0 else None
        lines.append("| " + " | ".join([
            cells[0], cells[1],
            fmt(default_workers), fmt(default_wage), fmt(default_net), fmt(default_annual),
            fmt(advanced_workers), fmt(advanced_wage), fmt(advanced_net), fmt(advanced_annual),
        ]) + " |")
        count += 1
    lines.extend([
        "", f"共列出 {count} 栋建筑。没有对应定义或商品价格的单元格以「—」表示。", "",
        "## 原版自动化参照（每级、基础价）", "",
        "| 原版生产方式 | 新增商品投入/周 | 少用劳工 | 每省 1000 人的商品成本 |", "|---|---:|---:|---:|",
        "| 纺织厂机械织机 | 工具 5＝200 | 1,500 | 133.3 |",
        "| 食品厂自动化烘焙 | 工具 10＝400 | 2,500 | 160 |",
        "| 家具厂流水线 | 工具 5＋石油 5＋电力 5＝550 | 3,000 | 183.3 |",
        "| 纺织厂自动动力织机 | 工具 5＋电力 10＝500 | 2,500 | 200 |",
        "| 矿井铁路运输 | 运输 5＝150 | 1,000 | 150 |",
        "", "谷子工坊销售线：展会摊位 150/500＝每千人 300；专卖店铺 150/1500＝100；连锁店铺 150/3000＝50。",
        "这组比例衡量的是商品换劳动力，不要求新增商品成本由省下的工资立即抵消。",
        "在劳工年工资 1 时，连锁店铺相对小众定制省下的周工资为 3000/52＝57.7，新增商品投入为 150；仅看本建筑账面会少 92.3/周，同时释放 3000 人。",
        "劳工年工资达到 150×52/3000＝2.6 时，若商品价格不变，连锁档相对无销售投入档才在本建筑内直接回本。",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {count} buildings to {OUTPUT}")


if __name__ == "__main__":
    main()
