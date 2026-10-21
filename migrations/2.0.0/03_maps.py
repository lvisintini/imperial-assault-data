"""2.0.0 migration 3 (#50): `skirmish-maps` becomes `maps`, one collection for every mission's map, and the maps the
dataset lacked are added from the Skirmish Map Project (github.com/nickv2002/Imperial-Assault-Skirmish-Map-Project),
whose half-res images are the ones boardwars serves.

- data/skirmish-maps.json → data/maps.json; images/{large,small}/skirmish-maps/ → images/{large,small}/maps/; the
  records' image paths and source-contents' content_type follow.
- New maps: The Dune Sea, the three four-player maps and the two raid maps. Their images are written separately (by
  the tools); this script only touches data/ and moves the existing image folders.
- Raid maps are played with FFG's Legends of the Alliance app, which becomes a source (type App).
- Until the missions index (#49) carries maps' product links, maps keep their own source-contents rows, so the new
  ones get rows to their products too.

Run from the repo root: uv run python migrations/2.0.0/03_maps.py. Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
OLD, NEW = 'skirmish-maps', 'maps'
APP = {'name': 'Legends of the Alliance', 'type': 'App', 'wave': None, 'product_code': None, 'announced_date': None,
       'release_date': '2017-11-20', 'included_in': None, 'image': 'sources/legends-of-the-alliance.png'}
# name → the source it comes in (from the Skirmish Map Project's README and the wiki).
NEW_MAPS = {
    'The Dune Sea': 'Luke Skywalker, Jedi Knight',
    'Hoth Battlefield': 'Return to Hoth',
    'Nal Hutta Borderlands': "Jabba's Realm",
    'Temple Gardens': 'Heart of the Empire',
    'The Malastarian Outpost': APP['name'],
    'The Gray Cap Cantina': APP['name'],
}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def slug(name):
    return ''.join(c if c.isalnum() else '-' for c in name.lower().replace("'", '')).strip('-').replace('--', '-')


def main():
    if (DATA / f'{NEW}.json').exists():
        print('Already migrated.')
        return

    (DATA / f'{OLD}.json').rename(DATA / f'{NEW}.json')
    for size in ('large', 'small'):
        (IMAGES / size / OLD).rename(IMAGES / size / NEW)

    sources = load('sources')
    sources.append({'id': str(uuid.uuid4())} | APP)
    by_name = {s['name']: s for s in sources}

    maps = load(NEW)
    for record in maps:
        record['image'] = record['image'].replace(f'{OLD}/', f'{NEW}/', 1)
    rows = load('source-contents')
    for row in rows:
        if row['content_type'] == OLD:
            row['content_type'] = NEW
    for name, source in NEW_MAPS.items():
        record = {'id': str(uuid.uuid4()), 'name': name, 'image': f'{NEW}/{slug(name)}.png'}
        maps.append(record)
        rows.append({'source_id': by_name[source]['id'], 'content_type': NEW, 'content_id': record['id']})

    save('sources', sources)
    save(NEW, maps)
    save('source-contents', rows)
    print(f'Renamed {OLD} to {NEW}; added {len(NEW_MAPS)} maps and the {APP["name"]} source.')


if __name__ == '__main__':
    main()
