from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = Path(r"D:\Steam\steamapps\common\Victoria 3\game")

STATES_PATH = ROOT / "common/history/states/00_states.txt"
COUNTRIES_PATH = ROOT / "common/country_definitions/tot_countries.txt"
COUNTRIES_DIR = ROOT / "common/country_definitions"
VANILLA_COUNTRIES_DIR = GAME_ROOT / "common/country_definitions"
BUILDINGS_DIR = ROOT / "common/history/buildings"
STRATEGIC_DIR = GAME_ROOT / "common/strategic_regions"
OUTPUT_PATH = ROOT / "common/history/military_formations/00_generated_formations.txt"
REPORT_PATH = ROOT / "analysis/military_formations_generation_report.json"

STATE_RE = r"^[ \t]*(?:s:)?(STATE_[A-Z0-9_]+)\s*=\s*\{"
CREATE_STATE_RE = r"^[ \t]*create_state\s*=\s*\{"
REGION_STATE_RE = r"^[ \t]*region_state:([A-Z0-9_]+)\s*=\s*\{"
COUNTRY_BLOCK_RE = r"^([A-Z0-9_]+)\s*=\s*\{"


def matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_quote = False
    escaped = False
    in_comment = False
    i = open_index
    while i < len(text):
        ch = text[i]
        if in_comment:
            if ch in "\r\n":
                in_comment = False
            i += 1
            continue
        if in_quote:
            if ch == "\\" and not escaped:
                escaped = True
            elif ch == '"' and not escaped:
                in_quote = False
            else:
                escaped = False
            i += 1
            continue
        if ch == "#":
            in_comment = True
        elif ch == '"':
            in_quote = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unclosed block at {open_index}")


def find_blocks(text: str, pattern: str):
    for match in re.finditer(pattern, text, flags=re.MULTILINE):
        open_index = text.find("{", match.end() - 1)
        if open_index == -1:
            continue
        close_index = matching_brace(text, open_index)
        yield {
            "name": match.group(1) if match.lastindex else "",
            "start": match.start(),
            "open": open_index,
            "close": close_index,
            "body": text[open_index + 1 : close_index],
        }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def parse_states():
    text = read_text(STATES_PATH)
    owners_by_state: dict[str, list[str]] = {}
    province_count: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    state_count_by_country: dict[str, int] = defaultdict(int)
    states_by_country: dict[str, list[str]] = defaultdict(list)
    for state_block in find_blocks(text, STATE_RE):
        owners = []
        for create_block in find_blocks(state_block["body"], CREATE_STATE_RE):
            m = re.search(r"\bcountry\s*=\s*c:([A-Z0-9_]+)", create_block["body"])
            if not m:
                continue
            tag = m.group(1)
            owners.append(tag)
            provs = re.findall(r"\bx[0-9A-Fa-f]{6}\b", create_block["body"])
            province_count[tag][state_block["name"]] += len(provs)
        if owners:
            dedup = []
            for owner in owners:
                if owner not in dedup:
                    dedup.append(owner)
            owners_by_state[state_block["name"]] = dedup
            for owner in dedup:
                state_count_by_country[owner] += 1
                states_by_country[owner].append(state_block["name"])
    return owners_by_state, province_count, state_count_by_country, states_by_country


def parse_country_blocks_from_dir(folder: Path):
    capitals: dict[str, str] = {}
    for path in sorted(folder.glob("*.txt")):
        text = read_text(path)
        for block in find_blocks(text, COUNTRY_BLOCK_RE):
            cap = re.search(r"\bcapital\s*=\s*(STATE_[A-Z0-9_]+)", block["body"])
            if cap:
                capitals[block["name"]] = cap.group(1)
    return capitals


def parse_capitals():
    capitals = parse_country_blocks_from_dir(VANILLA_COUNTRIES_DIR)
    capitals.update(parse_country_blocks_from_dir(COUNTRIES_DIR))
    return capitals


def parse_strategic_regions():
    strategic_by_state: dict[str, str] = {}
    for path in STRATEGIC_DIR.glob("*.txt"):
        text = read_text(path)
        for block in find_blocks(text, r"^([a-z0-9_]+)\s*=\s*\{"):
            if not block["name"].startswith("region_"):
                continue
            states_match = re.search(r"\bstates\s*=\s*\{([^}]*)\}", block["body"], flags=re.S)
            if not states_match:
                continue
            for state in re.findall(r"\bSTATE_[A-Z0-9_]+\b", states_match.group(1)):
                strategic_by_state[state] = block["name"]
    return strategic_by_state


def parse_buildings():
    barracks_by_country_state: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    ports_by_country_state: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for path in BUILDINGS_DIR.glob("*.txt"):
        text = read_text(path)
        for state_block in find_blocks(text, STATE_RE):
            state = state_block["name"]
            for region_block in find_blocks(state_block["body"], REGION_STATE_RE):
                tag = region_block["name"]
                for create in re.finditer(r'create_building\s*=\s*\{', region_block["body"]):
                    open_index = region_block["body"].find("{", create.end() - 1)
                    close_index = matching_brace(region_block["body"], open_index)
                    body = region_block["body"][open_index + 1 : close_index]
                    building_match = re.search(r'\bbuilding\s*=\s*"([^"]+)"', body)
                    if not building_match:
                        continue
                    building = building_match.group(1)
                    levels = 1
                    lvl = re.search(r"\blevels?\s*=\s*(\d+)", body)
                    if lvl:
                        levels = int(lvl.group(1))
                    if building == "building_barrack":
                        barracks_by_country_state[tag][state] += levels
                    elif building == "building_port":
                        ports_by_country_state[tag][state] += levels
    return barracks_by_country_state, ports_by_country_state


def choose_anchor_states(
    tag: str,
    capitals: dict[str, str],
    states_by_country: dict[str, list[str]],
    province_count: dict[str, dict[str, int]],
    barracks_by_country_state: dict[str, dict[str, int]],
    strategic_by_state: dict[str, str],
):
    owned = list(states_by_country.get(tag, []))
    owned_set = set(owned)
    anchors = []
    capital = capitals.get(tag)
    capital_region = strategic_by_state.get(capital) if capital else None
    dominant_region = None
    if not capital_region:
        region_scores = defaultdict(int)
        for state in owned:
            region = strategic_by_state.get(state)
            if region:
                region_scores[region] += province_count.get(tag, {}).get(state, 0) or 1
        if region_scores:
            dominant_region = sorted(region_scores.items(), key=lambda item: (-item[1], item[0]))[0][0]
    preferred_region = capital_region or dominant_region
    scored = []
    for state in owned:
        scored.append((
            1 if preferred_region and strategic_by_state.get(state) == preferred_region else 0,
            barracks_by_country_state.get(tag, {}).get(state, 0),
            province_count.get(tag, {}).get(state, 0),
            state,
        ))
    scored.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3]))
    if capital and capital in owned_set:
        anchors.append(capital)
    for _, _, _, state in scored:
        if state not in anchors:
            anchors.append(state)
    return anchors or owned


def split_total(total: int, parts: int):
    base = total // parts
    rem = total % parts
    return [base + (1 if idx < rem else 0) for idx in range(parts)]


def army_parts(total_barracks: int, owned_states: int):
    basis = total_barracks if total_barracks > 0 else max(6, owned_states * 3)
    if basis >= 72:
        return 3
    if basis >= 28:
        return 2
    return 1


def fleet_parts(total_ports: int):
    if total_ports >= 10:
        return 2
    return 1


def render_country_block(
    tag: str,
    anchors: list[str],
    strategic_by_state: dict[str, str],
    barracks_states: dict[str, int],
    ports_states: dict[str, int],
):
    lines = [f"\tc:{tag} ?= {{"]
    total_barracks = sum(barracks_states.values())
    owned_states = len(anchors)
    parts = army_parts(total_barracks, owned_states)
    army_strength = total_barracks if total_barracks > 0 else max(6, owned_states * 3)
    army_chunks = split_total(army_strength, parts)
    army_states = anchors[:parts]
    for idx, (state, strength) in enumerate(zip(army_states, army_chunks), start=1):
        hq = strategic_by_state.get(state, "region_western_europe")
        cav = max(1, round(strength * 0.18)) if strength >= 8 else max(1, strength // 5)
        art = max(1, round(strength * 0.16)) if strength >= 8 else max(1, strength // 5)
        inf = max(2, strength - cav - art)
        lines.extend([
            "\t\tcreate_military_formation = {",
            "\t\t\ttype = army",
            f"\t\t\thq_region = sr:{hq}",
            f'\t\t\tname = "{tag}_army_{idx}"',
            "",
            f"\t\t\tcombat_unit = {{ type = unit_type:combat_unit_type_line_infantry state_region = s:{state} count = {inf} }}",
            f"\t\t\tcombat_unit = {{ type = unit_type:combat_unit_type_hussars state_region = s:{state} count = {cav} }}",
            f"\t\t\tcombat_unit = {{ type = unit_type:combat_unit_type_mobile_artillery state_region = s:{state} count = {art} }}",
            "\t\t}",
        ])
    total_ports = sum(ports_states.values())
    if total_ports > 0:
        fleet_count = fleet_parts(total_ports)
        port_states = sorted(ports_states.items(), key=lambda item: (-item[1], item[0]))
        fleet_chunks = split_total(total_ports, fleet_count)
        for idx, strength in enumerate(fleet_chunks, start=1):
            state = port_states[min(idx - 1, len(port_states) - 1)][0]
            hq = strategic_by_state.get(state, "region_western_europe")
            slo = max(1, math.ceil(strength / 3))
            frig = max(2, strength)
            lines.extend([
                "\t\tcreate_military_formation = {",
                "\t\t\ttype = fleet",
                f"\t\t\thq_region = sr:{hq}",
                f'\t\t\tname = "{tag}_fleet_{idx}"',
                "",
                "\t\t\tship = {",
                "\t\t\t\ttype = ship_type:ship_type_ship_of_the_line",
                f"\t\t\t\tcount = {slo}",
                "\t\t\t}",
                "",
                "\t\t\tship = {",
                "\t\t\t\ttype = ship_type:ship_type_frigate",
                f"\t\t\t\tcount = {frig}",
                "\t\t\t}",
                "\t\t}",
            ])
    lines.append("\t}")
    return "\n".join(lines)


def generate():
    owners_by_state, province_count, state_count_by_country, states_by_country = parse_states()
    capitals = parse_capitals()
    strategic_by_state = parse_strategic_regions()
    barracks_by_country_state, ports_by_country_state = parse_buildings()

    tags = sorted(states_by_country)
    rendered = ["MILITARY_FORMATIONS = {"]
    report = {
        "countries_with_states": len(tags),
        "countries": [],
        "missing_hq_region_states": [],
    }

    for tag in tags:
        anchors = choose_anchor_states(tag, capitals, states_by_country, province_count, barracks_by_country_state, strategic_by_state)
        if not anchors:
            continue
        for state in anchors:
            if state not in strategic_by_state:
                report["missing_hq_region_states"].append(state)
        rendered.append(
            render_country_block(
                tag,
                anchors,
                strategic_by_state,
                dict(barracks_by_country_state.get(tag, {})),
                dict(ports_by_country_state.get(tag, {})),
            )
        )
        report["countries"].append({
            "tag": tag,
            "capital": capitals.get(tag),
            "owned_states": len(states_by_country.get(tag, [])),
            "barracks": sum(barracks_by_country_state.get(tag, {}).values()),
            "ports": sum(ports_by_country_state.get(tag, {}).values()),
            "army_formations": army_parts(sum(barracks_by_country_state.get(tag, {}).values()), len(states_by_country.get(tag, []))),
            "fleet_formations": fleet_parts(sum(ports_by_country_state.get(tag, {}).values())) if sum(ports_by_country_state.get(tag, {}).values()) > 0 else 0,
            "anchor_states": anchors[:4],
        })

    rendered.append("}")
    OUTPUT_PATH.write_text("\n".join(rendered) + "\n", encoding="utf-8-sig", newline="")
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "countries_with_states": report["countries_with_states"],
        "countries_with_fleet": sum(1 for item in report["countries"] if item["fleet_formations"] > 0),
        "report": REPORT_PATH.relative_to(ROOT).as_posix(),
        "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    generate()
