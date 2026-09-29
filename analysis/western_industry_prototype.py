"""Extend the eastern test with an explicit western plan and stronger Hakurei.

Uses the same validated generator and preserves all existing eastern entries
except the stated Hakurei production increases. No map or population changes.
"""
import sys
import eastern_industry_prototype as economy

economy.PREFIX = 'western_industry_v1'
economy.CHECKPOINT = '1ff4183'
economy.BACKUP_PREFIX = 'western_industry_before_'
economy.HISTORY_LABEL = 'Eastern and western industry test v2'
economy.STATES.update(WA='STATE_WESTERN_AUSTRALIA', NT='STATE_NORTHERN_TERRITORY')
economy.ALIASES['maize'] = 'maize_farm'
economy.ARABLE_ADDITIONS.update(WA=['building_cotton_plantation'],
    NT=['building_maize_farm', 'building_sugar_plantation'])

for tag, state, levels in economy.PLAN:
    if tag == 'HAKR' and state == 'NSW':
        levels.update(food=3, clothes=3, furniture=2, paper=1, tools=2, wood=2, shipyard=2)

economy.PLAN.extend([
    ('BYKR', 'WA', dict(wheat=14, ranch=6, wine=4, cotton=4, wood=4,
        fish=2, food=4, clothes=2, furniture=1, paper=1, tools=1,
        government=2, port=2, university=1, construction=1)),
    ('HIGN', 'WA', dict(wheat=2, ranch=1, fish=1, wood=2, paper=2,
        glass=1, tools=1, food=1, temple=1, government=1, port=1)),
    ('YKMF', 'WA', dict(wheat=2, ranch=1, wine=1, wood=1, paper=1,
        glass=1, tools=1, clothes=1, food=1, government=1, port=1)),
    ('KYTO', 'WA', dict(coal=3, iron=2, wood=2, steel=3, tools=2,
        food=1, wine=2, wheat=2, ranch=1, clothes=1,
        government=1, port=1, construction=1)),
    ('RNGN', 'WA', dict(wheat=5, ranch=2, cotton=2, wood=3, coal=2,
        iron=2, steel=2, tools=2, furniture=2, glass=2, garden=1,
        food=1, government=1, university=1, port=1)),
    ('UKDO', 'WA', dict(wood=3, paper=2, tools=1, glass=1, garden=1,
        wheat=2, ranch=2, cotton=1, wine=1, food=1, clothes=1,
        government=1, port=1)),
    ('MKAI', 'NT', dict(wood=5, iron=3, maize=3, ranch=4, cotton=3,
        sugar=4, paper=2, tools=2, clothes=3, glass=1,
        food=2, engines=1, shipyard=1, government=2, port=2,
        university=1, construction=1)),
    ('MKAI', 'WA', dict(wood=1, paper=1, government=1)),
])

# Regional totals shared by the current owners, not capacities per country.
# Deliberate gameplay capacities; no claim of precise historical reserves.
economy.RESOURCE_UPDATES.update(
    WA=dict(coal=40, iron=48, wood=40, fish=16),
    NT=dict(wood=16, iron=20),
)

if __name__ == '__main__':
    economy.main('--apply' in sys.argv)
