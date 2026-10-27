"""2.0.0 migration 16: map tiles, the tiles each map is built from, and a map for every campaign mission.

Every mission reaches its tiles the same way: missions.map_id → maps → map-layouts → map-tiles, and tiles reach
products through source-contents.

- maps: every campaign mission (story, threat, side and agenda missions: the campaign rows of the missions index)
  gets a map named after it, with no image yet (image null), and its missions row points at it. Five campaign
  missions have no card, so no missions row: each campaign's introduction and finale (MAPS_WITHOUT_MISSIONS); their
  maps are in their products directly, through source-contents.
- map-tiles.json: {id, name, number, side_a, side_b}, a tile each: 138 across the Core Set and the six expansions,
  named after their product and number ("Core Set 01", "Twin Shadows 01"). Each side's image is cut on the tile's
  outline (tabs kept, notches transparent), 64 px per square plus 32 px on each axis that has tabs: the Vassal
  campaign module's images (vassal/ in imperial-assault-tools). A tile's copies per product come from
  map-tiles.csv, next to this file (counted by the maintainer).
- map-layouts.json (no ids): {map_id, tile_id, side, count}, the tile sides a map uses and how many times it places
  each. The campaign maps' layouts come from ImperialCommander2 (github.com/GlowPuff/ImperialCommander2), summed over
  each mission's map sections; a map built from sections that replace each other during its mission (Heart of the
  Empire's Into a Corner) can place a side more often than a box has copies.

imperial-assault-tools' ia ic2 and ia tiles stage both sources in staging/map-tiles:
    uv run python migrations/2.0.0/16_map_tiles.py --from ../imperial-assault-tools/staging/map-tiles
Running it again changes nothing.
"""
import argparse
import csv
import json
import shutil
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
COPIES = Path(__file__).with_name('map-tiles.csv')
CAMPAIGN_TYPES = ('campaign-story-mission-cards', 'campaign-threat-mission-cards', 'campaign-hero-side-mission-cards',
                  'campaign-ally-side-mission-cards', 'campaign-regular-side-mission-cards', 'agenda-cards')
# Campaign missions with no card (introductions and finales), and their products.
MAPS_WITHOUT_MISSIONS = {
    'Aftermath': 'Imperial Assault', 'Captured': 'Imperial Assault', 'Dark Recon': 'Heart of the Empire',
    'The Battle of Hoth': 'Return to Hoth', 'Trespass': "Jabba's Realm",
}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main(staged):
    if (DATA / 'map-tiles.json').exists():
        print('Already migrated.')
        return
    staged = Path(staged)
    manifest = json.loads((staged / 'manifest.json').read_text(encoding='utf-8'))
    sources = {s['name']: s['id'] for s in load('sources')}
    with open(COPIES, newline='', encoding='utf-8') as file:
        copies = {(row['product'], int(row['number'])): int(row['copies']) for row in csv.DictReader(file)}
    assert set(copies) == {(t['product'], t['number']) for t in manifest['tiles']}, 'map-tiles.csv and the tiles differ'

    tiles, rows = [], []
    for staged_tile in manifest['tiles']:
        tile = {'id': str(uuid.uuid4()), 'name': staged_tile['name'], 'number': staged_tile['number'],
                'side_a': staged_tile['side_a'], 'side_b': staged_tile['side_b']}
        for side in ('side_a', 'side_b'):
            for size in ('large', 'small'):
                (IMAGES / size / 'map-tiles').mkdir(parents=True, exist_ok=True)
                shutil.copyfile(staged / 'images' / tile[side], IMAGES / size / tile[side])
        tiles.append(tile)
        rows.append({'source_id': sources[staged_tile['product']], 'content_type': 'map-tiles',
                     'content_id': tile['id'], 'quantity': copies[staged_tile['product'], staged_tile['number']]})
    tile_ids = {(t['product'], t['number']): tile['id'] for t, tile in zip(manifest['tiles'], tiles)}

    maps, missions = load('maps'), load('missions')
    by_card = {(m['content_type'], m['content_id']): m for m in missions}
    names = {}
    for row in missions:
        if row['content_type'] in CAMPAIGN_TYPES:
            card = next(r for r in load(row['content_type']) if r['id'] == row['content_id'])
            names[row['id']] = card['name']
    new_maps = {}
    for row in missions:
        if row['id'] in names:
            assert row['map_id'] is None, f"{names[row['id']]} has a map already"
            new_maps[row['id']] = {'id': str(uuid.uuid4()), 'name': names[row['id']], 'image': None}
            row['map_id'] = new_maps[row['id']]['id']
    without = {name: {'id': str(uuid.uuid4()), 'name': name, 'image': None} for name in MAPS_WITHOUT_MISSIONS}
    rows += [{'source_id': sources[MAPS_WITHOUT_MISSIONS[name]], 'content_type': 'maps', 'content_id': m['id'],
              'quantity': 1} for name, m in without.items()]

    layouts = []
    for layout in manifest['layouts']:
        if layout['mission']:
            map_id = new_maps[by_card[layout['mission']['content_type'], layout['mission']['id']]['id']]['id']
        else:
            map_id = without[layout['name']]['id']
        layouts += [{'map_id': map_id, 'tile_id': tile_ids[t['product'], t['number']], 'side': t['side'],
                     'count': t['count']} for t in layout['tiles']]

    save('maps', maps + list(new_maps.values()) + list(without.values()))
    save('missions', missions)
    save('map-tiles', tiles)
    save('map-layouts', layouts)
    save('source-contents', load('source-contents') + rows)
    print(f'{len(tiles)} tiles, {len(new_maps) + len(without)} campaign maps ({len(without)} without a mission), '
          f'{len(layouts)} layout rows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='staged', required=True, help="imperial-assault-tools' staging/map-tiles folder")
    main(parser.parse_args().staged)
