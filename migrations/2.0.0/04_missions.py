"""2.0.0 migration 4 (#49, PR A): campaign mission collections, the missions index, and mission rewards.

- story-mission-cards and threat-mission-cards become campaign-story-mission-cards and campaign-threat-mission-cards.
- side-mission-cards splits by color, which is dropped: Red → campaign-hero-side-mission-cards (with hero_id, the hero
  the mission is for), Green → campaign-ally-side-mission-cards, Grey → campaign-regular-side-mission-cards.
- missions.json indexes every mission: one row per mission card, and per agenda card that is a mission, with the map it
  is played on (map_id; null for campaign missions until their maps have images).
- Missions reach their products through the index: their source-contents rows now point at index rows, and agenda
  missions get rows for their deck's products.
- mission-rewards.json lists what each mission gives: reward or deployment cards, or credits; rows with choice: true
  are alternatives (pick one). Story mission rewards aren't on the wiki; they come later.
- card-backs: the story and threat backs follow the rename; the side mission back becomes one row per new collection.
- Names fixed to the wiki's titles (see NAMES), and the reward card "Adrenalin Implant" becomes "Adrenal Implant".

Heroes and rewards come from imperial-assault-tools' `ia wiki --missions` cache, run on this data before migrating:
    uv run python migrations/2.0.0/04_missions.py --wiki ../imperial-assault-tools/staging/wiki/missions.json
Running it again changes nothing.
"""
import argparse
import json
import shutil
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
RENAMED = {'story-mission-cards': 'campaign-story-mission-cards',
           'threat-mission-cards': 'campaign-threat-mission-cards'}
SIDE = 'side-mission-cards'
SPLIT = {'Red': 'campaign-hero-side-mission-cards', 'Green': 'campaign-ally-side-mission-cards',
         'Grey': 'campaign-regular-side-mission-cards'}
# The index's order: campaign missions as the game introduces them, then agenda missions.
MISSION_TYPES = ['campaign-story-mission-cards', 'campaign-threat-mission-cards', 'campaign-hero-side-mission-cards',
                 'campaign-ally-side-mission-cards', 'campaign-regular-side-mission-cards', 'agenda-cards']
# Misspelt names → the wiki's page titles.
NAMES = {
    'Despertate Hour': 'Desperate Hour', 'Vipers Den': "Viper's Den", 'Cloud Citys Secret': "Cloud City's Secret",
    'A Heros Welcome': "A Hero's Welcome", 'Unfninished Business': 'Unfinished Business',
    'Brace For Impact': 'Brace for Impact', 'Strength Of Command': 'Strength of Command',
    'Anchorhead Affair': 'The Anchorhead Affair',
}
REWARD_RENAMES = {'Adrenalin Implant': ('Adrenal Implant', 'reward-cards/adrenal-implant.png')}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def move_image(old, new):
    for size in ('large', 'small'):
        (IMAGES / size / new).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(IMAGES / size / old, IMAGES / size / new)


def products(rows, mission_types):
    """{(content_type, id): {source ids}} for every mission, agenda missions through their deck."""
    found = {}
    for row in rows:
        found.setdefault((row['content_type'], row['content_id']), set()).add(row['source_id'])
    result = {}
    for content_type in mission_types:
        for record in load(content_type):
            if content_type == 'agenda-cards':
                if record['mission']:
                    result[content_type, record['id']] = found.get(('agenda-decks', record['agenda_id']), set())
            else:
                result[content_type, record['id']] = found.get((content_type, record['id']), set())
    return result


def main(wiki):
    if (DATA / 'missions.json').exists():
        print('Already migrated.')
        return
    cache = json.loads(Path(wiki).read_text(encoding='utf-8'))['missions']
    rows = load('source-contents')
    before = {key[1]: sources for key, sources in
              products(rows, ['story-mission-cards', 'threat-mission-cards', SIDE, 'agenda-cards']).items()}

    # Renames and the side mission split.
    for old, new in RENAMED.items():
        records = load(old)
        for record in records:
            record['name'] = NAMES.get(record['name'], record['name'])
            record['image'] = record['image'].replace(f'{old}/', f'{new}/', 1)
        save(new, records)
        (DATA / f'{old}.json').unlink()
        for size in ('large', 'small'):
            (IMAGES / size / old).rename(IMAGES / size / new)
    split = {new: [] for new in SPLIT.values()}
    for record in load(SIDE):
        new = SPLIT[record['color']]
        image = record['image'].replace(f'{SIDE}/', f'{new}/', 1)
        move_image(record['image'], image)
        fields = {'id': record['id'], 'name': NAMES.get(record['name'], record['name'])}
        if record['color'] == 'Red':
            hero = cache[record['id']]['hero']
            assert hero and hero['id'], f"{record['name']}: no hero in the wiki cache"
            fields['hero_id'] = hero['id']
        split[new].append(fields | {'image': image})
    for new, records in split.items():
        save(new, records)
    (DATA / f'{SIDE}.json').unlink()
    for size in ('large', 'small'):
        (IMAGES / size / SIDE).rmdir()
    agenda = load('agenda-cards')
    for record in agenda:
        record['name'] = NAMES.get(record['name'], record['name'])
    save('agenda-cards', agenda)
    rewards = load('reward-cards')
    for record in rewards:
        if record['name'] in REWARD_RENAMES:
            record['name'], image = REWARD_RENAMES[record['name']]
            move_image(record['image'], image)
            record['image'] = image
    save('reward-cards', rewards)

    # The index, and products through it.
    side_type = {r['id']: new for new, records in split.items() for r in records}
    missions, index_of = [], {}
    for content_type in MISSION_TYPES:
        for record in load(content_type):
            if content_type == 'agenda-cards' and not record['mission']:
                continue
            row = {'id': str(uuid.uuid4()), 'content_type': content_type, 'content_id': record['id'], 'map_id': None}
            missions.append(row)
            index_of[record['id']] = row
    agenda_missions = {}
    for record in agenda:
        if record['mission']:
            agenda_missions.setdefault(record['agenda_id'], []).append(record)
    moved = []
    for row in rows:
        content_type = RENAMED.get(row['content_type'], side_type.get(row['content_id'], row['content_type']))
        if content_type in MISSION_TYPES:
            moved.append({'source_id': row['source_id'], 'content_type': 'missions',
                          'content_id': index_of[row['content_id']]['id']})
            continue
        moved.append(row)
        if row['content_type'] == 'agenda-decks':
            moved += [{'source_id': row['source_id'], 'content_type': 'missions',
                       'content_id': index_of[card['id']]['id']} for card in agenda_missions.get(row['content_id'], [])]
    after = {}
    for row in moved:
        if row['content_type'] == 'missions':
            mission = next(m for m in missions if m['id'] == row['content_id'])
            after.setdefault(mission['content_id'], set()).add(row['source_id'])
    assert after == before, 'a mission changed products'

    # Rewards, from the wiki cache.
    mission_rewards, problems = [], []
    for mission in missions:
        entry = cache.get(mission['content_id'])
        assert entry, f"{mission['content_type']} {mission['content_id']}: not in the wiki cache"
        problems += [f"{entry['name']}: {p}" for p in entry['problems']]
        mission_rewards += [{'mission_id': mission['id'], 'content_type': r['content_type'],
                             'content_id': r['content_id'], 'credits': r['credits'], 'choice': r['choice']}
                            for r in entry['rewards']]

    # Card backs: the side mission back is one row per new collection (until #52 makes backs a catalog).
    backs = []
    for back in load('card-backs'):
        if back['content_type'] == SIDE:
            backs += [back | {'id': back['id'] if new.endswith('regular-side-mission-cards') else str(uuid.uuid4()),
                              'content_type': new} for new in SPLIT.values()]
        else:
            backs.append(back | {'content_type': RENAMED.get(back['content_type'], back['content_type'])})

    save('missions', missions)
    save('source-contents', moved)
    save('mission-rewards', mission_rewards)
    save('card-backs', backs)
    print(f'{len(missions)} missions indexed, {len(mission_rewards)} mission rewards.')
    print('Not loaded (from the wiki cache):', *problems, sep='\n  ')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wiki', required=True, help="imperial-assault-tools' staging/wiki/missions.json")
    main(parser.parse_args().wiki)
