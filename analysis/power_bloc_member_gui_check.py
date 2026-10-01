"""Validate GDP, population and living-standard member views and localization.

--write-localization creates the two small UI localization files once.
No assertion claims a live-engine or visual test.
"""
import json
import re
import sys
from pathlib import Path
from population_arable_prototype import spans

ROOT = Path(__file__).resolve().parents[1]
KEYS = {
    'simp_chinese': {
        'TOT_POWER_BLOC_SORT_GDP_DESC': 'GDP ↓',
        'TOT_POWER_BLOC_SORT_GDP_ASC': 'GDP ↑',
        'TOT_POWER_BLOC_SORT_GDP_TOOLTIP': '按当前GDP排列全部成员，包括主持国。点击切换升序或降序并刷新排列；搜索仍然有效。',
        'TOT_POWER_BLOC_SORT_POPULATION_DESC': '人口 ↓',
        'TOT_POWER_BLOC_SORT_POPULATION_ASC': '人口 ↑',
        'TOT_POWER_BLOC_SORT_POPULATION_TOOLTIP': '按当前总人口排列全部成员，包括主持国。点击切换升序或降序并刷新排列；各成员卡片显示实时总人口。',
        'TOT_POWER_BLOC_SORT_SOL_DESC': '生活水平 ↓',
        'TOT_POWER_BLOC_SORT_SOL_ASC': '生活水平 ↑',
        'TOT_POWER_BLOC_SORT_SOL_TOOLTIP': '按平均生活水平排列全部成员，包括主持国。点击切换升序或降序。',
    },
    'english': {
        'TOT_POWER_BLOC_SORT_GDP_DESC': 'GDP ↓',
        'TOT_POWER_BLOC_SORT_GDP_ASC': 'GDP ↑',
        'TOT_POWER_BLOC_SORT_GDP_TOOLTIP': 'Rank all members, including the host, by current GDP. Click to toggle ascending or descending and refresh the order. Search still applies.',
        'TOT_POWER_BLOC_SORT_POPULATION_DESC': 'Population ↓',
        'TOT_POWER_BLOC_SORT_POPULATION_ASC': 'Population ↑',
        'TOT_POWER_BLOC_SORT_POPULATION_TOOLTIP': 'Rank all members, including the host, by current total population. Click to toggle ascending or descending and refresh the order. Member cards display current total population.',
        'TOT_POWER_BLOC_SORT_SOL_DESC': 'SoL ↓',
        'TOT_POWER_BLOC_SORT_SOL_ASC': 'SoL ↑',
        'TOT_POWER_BLOC_SORT_SOL_TOOLTIP': 'Rank all members, including the host, by average Standard of Living. Click to toggle ascending or descending.',
    },
}


def localization_paths():
    for lang, values in KEYS.items():
        folder = 'replace/simp_chinese/common/gui' if lang == 'simp_chinese' else 'english'
        yield ROOT / ('localization/' + folder + '/tot_power_bloc_member_sort_l_' + lang + '.yml'), lang, values


def validate_gui_actions(tab):
    # Actions accept one data statement. Adjacent [calls][calls] are parsed as
    # trailing junk: the first call runs, but the GDP refresh never executes.
    actions = re.findall(r'\b(onclick|on_start)\s*=\s*"([^"\n]*)"', tab)
    assert len(actions) == 20, 'Expected two entry actions and two actions per sort button.'
    for event, expression in actions:
        assert re.fullmatch(r'\[[^\[\]]+\]', expression), (event, expression)
    return actions


def check():
    paths = ['gui/power_bloc_panel.gui',
        'common/scripted_guis/tot_power_bloc_member_sort.txt',
        'common/scripted_effects/tot_power_bloc_member_sort.txt']
    texts = [(ROOT / p).read_text(encoding='utf-8-sig') for p in paths]
    for path, text in zip(paths, texts):
        # GUI comments may contain apostrophes. Mask comments and strings before
        # checking structural braces; expressions inside strings are separate.
        masked = re.sub(r'"[^"\n]*"|#[^\n]*', '', text)
        balance = 0
        for char in masked:
            balance += (char == '{') - (char == '}')
            assert balance >= 0, path
        assert balance == 0, path
    gui, actions, effect = texts
    tab = next(b for _, b, _ in spans(gui, r'type power_bloc_panel_members_tab\s*=\s*flowcontainer\s*\{'))
    validate_gui_actions(tab)
    action_keys = set(re.findall(r'^(tot_power_bloc_members_(?:gdp|population|sol)_\w+)\s*=', actions, re.M))
    assert action_keys == {'tot_power_bloc_members_gdp_asc', 'tot_power_bloc_members_gdp_desc',
        'tot_power_bloc_members_population_asc', 'tot_power_bloc_members_population_desc',
        'tot_power_bloc_members_sol_asc', 'tot_power_bloc_members_sol_desc'}
    assert set(re.findall(r"GetScriptedGui\('([^']+)'\)", tab)) == action_keys
    assert tab.count("AddScope('tot_member_sort_host', PowerBloc.GetLeader.MakeScope)") == 7
    assert 'Scope.GetCountry' in tab
    assert 'Country.MatchesSearchQuery' in tab and 'PowerBloc.IsMember(Country.Self)' in tab
    assert 'GetPlayer.MakeScope.GetList(\'tot_power_bloc_gdp_members\')' in tab
    assert 'GetPlayer.MakeScope.GetList(\'tot_power_bloc_population_members\')' in tab
    assert 'GetPlayer.MakeScope.GetList(\'tot_power_bloc_sol_members\')' in tab
    for typename in ['power_bloc_leader', 'power_bloc_member_item']:
        body = next(b for _, b, _ in spans(gui, r'type ' + typename + r'\s*=\s*flowcontainer\s*\{'))
        assert 'Country.GetTotalPopulation|D' in body
        assert 'Country.GetFormattedStandardOfLivingAll|v' in body
        rows = [b for _, b, _ in spans(body, r'flowcontainer\s*=\s*\{') if '### PRESTIGE' in b]
        stats = min(rows, key=len)
        sizes = [int(re.search(r'size\s*=\s*\{\s*(\d+)', b)[1])
                 for _, b, _ in spans(stats, r'power_bloc_header_grid_item\s*=\s*\{')]
        assert len(sizes) == 4 and sum(sizes) + 3 * 15 <= 400, 'Stats overflow card'
    for key in ['name', 'prestige', 'leverage_advantage']:
        assert "PowerBloc.SortMembers('{}')".format(key) in tab
    assert "PowerBloc.SortMembers('gdp')" not in tab  # No guessed engine sort key.
    assert 'ordered_power_bloc_member' in effect and 'value = gdp' in effect
    assert 'scope:tot_member_sort_host.power_bloc' in effect
    assert 'root.var:tot_power_bloc_gdp_direction' in effect
    assert 'has_variable_list = tot_power_bloc_gdp_members' in effect
    assert 'value = 1' in actions and 'value = -1' in actions
    assert 'tot_power_bloc_refresh_gdp_member_list' in actions
    assert 'tot_power_bloc_refresh_population_member_list' in actions
    assert 'tot_power_bloc_refresh_sol_member_list' in actions
    assert 'value = total_population' in effect
    assert 'value = average_sol' in effect
    assert 'root.var:tot_power_bloc_population_direction' in effect
    assert re.search(r'ignoreinvisible = yes\s+sort_button', tab)
    for path, lang, values in localization_paths():
        raw = path.read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf')
        loc = raw.decode('utf-8-sig')
        assert loc.startswith('l_' + lang + ':')
        assert set(re.findall(r'^ (\w+):', loc, re.M)) == set(values)
    print(json.dumps(dict(status='static checks passed; not visually or engine tested',
        sort='GDP, population and living-standard ascending/descending; live values on all cards',
        includes_host=True, native_sort_and_search_preserved=True,
        selected_bloc_scope_used=True, independent_event_actions=True), ensure_ascii=False))


if __name__ == '__main__':
    if '--write-localization' in sys.argv:
        for path, lang, values in localization_paths():
            assert not path.exists(), path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('l_' + lang + ':\n' + ''.join(' {}: "{}"\n'.format(k, v)
                for k, v in values.items()), encoding='utf-8-sig')
    check()
