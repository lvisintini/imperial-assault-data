"""2.0.0 migration 8 (#51): reward cards get `class` and `for`.

- class: "Boon" or "Bane" for Return to Hoth's threat mission rewards, "Regular" for every other reward card.
- for: who receives the card, "Imperial player" or "Rebel players".

Both come from the cards' wiki pages: Imperial rewards use the wiki's Imperial class card infobox (category "Imperial
Class Reward"), Rebel rewards the reward, hero class or item infoboxes, and Boons and Banes have their own categories.
Hunt Them Down is the one exception: the wiki gives it the Imperial infobox, but it's a hero class reward (Past Life
Enemies, a hero side mission). Every card a mission gives agrees with the mission: agenda missions, `imperial_reward`
and `threat_reward` give Imperial cards, a mission's `reward` gives Rebel ones (tests/test_integrity.py checks the
agenda missions).

Run from the repo root: uv run python migrations/2.0.0/08_reward_fields.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')
BOONS = ['Networks Restored', 'Resurgence', 'Invigorated by Success', 'Strategy Executed']
BANES = ['Supply Disruption', 'Constant Advantage', 'Weary from Toil', 'Distractions']
IMPERIAL = [
    'Bounty', 'Surveillance Operatives', 'Imperial Industry', 'Old Wounds', 'Special Operations', 'Supply Deficit',
    'Bred for War', 'Mercenary Ties', '501st Training', 'Tusken Weaponry', 'Tactical Advance', 'Mechanical Salvage',
    'Explosives Clearance', 'Mercenary Aid', 'Power of the Shard', 'Tracked Movements', 'Vaders Legion', *BANES,
]


def main():
    path = DATA / 'reward-cards.json'
    rewards = json.loads(path.read_text(encoding='utf-8'))
    if 'class' in rewards[0]:
        print('Already migrated.')
        return
    names = {r['name'] for r in rewards}
    assert set(BOONS + IMPERIAL) <= names, set(BOONS + IMPERIAL) - names
    migrated = []
    for reward in rewards:
        class_ = 'Boon' if reward['name'] in BOONS else 'Bane' if reward['name'] in BANES else 'Regular'
        for_ = 'Imperial player' if reward['name'] in IMPERIAL else 'Rebel players'
        image = reward.pop('image')
        migrated.append(reward | {'class': class_, 'for': for_, 'image': image})
    path.write_text(json.dumps(migrated, indent=2), encoding='utf-8')
    print(f"{len(migrated)} reward cards: {len(IMPERIAL)} for the Imperial player, {len(BOONS)} Boons, {len(BANES)} Banes.")


if __name__ == '__main__':
    main()
