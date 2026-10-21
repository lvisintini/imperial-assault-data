"""2.0.0 migration 6 (#49, PR C): raid missions, the two raids of FFG's Legends of the Alliance app.

- raid-missions: The Malastarian Outpost (the app's first raid, announced June 2019) and The Gray Cap Cantina (live in
  November 2019), from FFG's announcements. Raids are app content: no card, so no image.
- Each gets a missions row on its raid map, and the map's products (the Legends of the Alliance app): the raid maps'
  own source-contents rows move to their missions, so every map now reaches its products through its missions.

Run from the repo root: uv run python migrations/2.0.0/06_raid_missions.py. Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

DATA = Path('data')
TYPE = 'raid-missions'
RAIDS = ['The Malastarian Outpost', 'The Gray Cap Cantina']  # each played on the map of the same name


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main():
    if (DATA / f'{TYPE}.json').exists():
        print('Already migrated.')
        return
    maps = {m['name']: m for m in load('maps')}
    rows, index = load('source-contents'), load('missions')
    raids, moved = [], []
    for name in RAIDS:
        map_ = maps[name]
        raid = {'id': str(uuid.uuid4()), 'name': name}
        row = {'id': str(uuid.uuid4()), 'content_type': TYPE, 'content_id': raid['id'], 'map_id': map_['id']}
        raids.append(raid)
        index.append(row)
        products = [r for r in rows if r['content_type'] == 'maps' and r['content_id'] == map_['id']]
        assert products, f'{name} has no products'
        moved += [{'source_id': r['source_id'], 'content_type': 'missions', 'content_id': row['id']} for r in products]
    raid_maps = {maps[name]['id'] for name in RAIDS}
    kept = [r for r in rows if not (r['content_type'] == 'maps' and r['content_id'] in raid_maps)]
    save(TYPE, raids)
    save('missions', index)
    save('source-contents', kept + moved)
    print(f'{len(raids)} raid missions; {len(rows) - len(kept)} raid map product rows moved to their missions.')


if __name__ == '__main__':
    main()
