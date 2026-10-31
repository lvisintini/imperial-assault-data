"""2.0.0 migration 20: mission collections without "-cards", and the story missions that have no card.

- The mission collections drop "-cards" from their names, since not every mission is a card: campaign-story-missions,
  campaign-threat-missions, campaign-hero-side-missions, campaign-ally-side-missions, campaign-regular-side-missions
  and skirmish-missions. Their data files and image folders are renamed, their records' image paths and the missions
  index's content_type follow.
- Five story missions have no card, only a map, printed in their campaign guides: Aftermath, Captured (the Core Set's
  forced mission, still part of its story), Dark Recon, The Battle of Hoth and Trespass. Each gets a story mission
  (image and back_id null) and a missions row with its map, and the map's source-contents row becomes the mission's,
  as for every other mission.

    uv run python migrations/2.0.0/20_mission_collections.py
Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
RENAMED = {
    'campaign-story-mission-cards': 'campaign-story-missions',
    'campaign-threat-mission-cards': 'campaign-threat-missions',
    'campaign-hero-side-mission-cards': 'campaign-hero-side-missions',
    'campaign-ally-side-mission-cards': 'campaign-ally-side-missions',
    'campaign-regular-side-mission-cards': 'campaign-regular-side-missions',
    'skirmish-mission-cards': 'skirmish-missions',
}
STORY = 'campaign-story-missions'
CARDLESS = ['Aftermath', 'Captured', 'Dark Recon', 'The Battle of Hoth', 'Trespass']


def read(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def write(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def rename():
    for old, new in RENAMED.items():
        if not (DATA / f'{old}.json').exists():
            continue
        records = read(old)
        for record in records:
            record['image'] = new + record['image'].removeprefix(old)
        write(new, records)
        (DATA / f'{old}.json').unlink()
        for size in ('large', 'small'):
            (IMAGES / size / old).rename(IMAGES / size / new)
    missions = read('missions')
    for row in missions:
        row['content_type'] = RENAMED.get(row['content_type'], row['content_type'])
    write('missions', missions)


def add_cardless():
    """The cardless story missions not added yet; whether any were."""
    story = read(STORY)
    missing = [name for name in CARDLESS if name not in {s['name'] for s in story}]
    if not missing:
        return False
    maps = {m['name']: m['id'] for m in read('maps')}
    missions = read('missions')
    contents = read('source-contents')
    for name in missing:
        mission = {'id': str(uuid.uuid4()), 'name': name, 'back_id': None, 'image': None}
        row = {'id': str(uuid.uuid4()), 'content_type': STORY, 'content_id': mission['id'], 'map_id': maps[name]}
        story.append(mission)
        missions.append(row)
        moved = [r for r in contents if r['content_type'] == 'maps' and r['content_id'] == maps[name]]
        assert len(moved) == 1, f'{name}: {len(moved)} source-contents rows'
        moved[0].update({'content_type': 'missions', 'content_id': row['id']})
    write(STORY, story)
    write('missions', missions)
    write('source-contents', contents)
    return True


def main():
    renamed = any((DATA / f'{old}.json').exists() for old in RENAMED)
    rename()
    added = add_cardless()
    if not renamed and not added:
        print('Already migrated.')
        return
    print(f"Renamed {len(RENAMED)} mission collections; added {', '.join(CARDLESS)} as story missions.")


if __name__ == '__main__':
    main()
