"""2.0.0 migration 18: the campaign maps' images, which migration 16 left null.

imperial-assault-tools' ia maps drew them: each mission's tiles, placed as ImperialCommander2's mission files place
them, with the Vassal campaign module's tile sides (the dataset's map-tiles images). Tiles only, with no doors, tokens
or figures, on a transparent background at 64 px per square. A map whose sections replace each other during the
mission is drawn with its start section only. Its manifest names each image's map.

    uv run python migrations/2.0.0/18_campaign_map_images.py --from ../imperial-assault-tools/staging/campaign-maps
Running it again changes nothing.
"""
import argparse
import json
import shutil
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')


def main(drawn):
    maps = json.loads((DATA / 'maps.json').read_text(encoding='utf-8'))
    if all(m['image'] for m in maps):
        print('Already migrated.')
        return
    drawn = Path(drawn)
    images = {m['map_id']: m['file'] for m in json.loads((drawn / 'manifest.json').read_text(encoding='utf-8'))['maps']}
    missing = [m['name'] for m in maps if not m['image'] and m['id'] not in images]
    assert not missing, f'No image drawn for {missing}'
    for record in maps:
        if record['image'] is None:
            record['image'] = f"maps/{images[record['id']]}"
            for size in ('large', 'small'):
                shutil.copyfile(drawn / images[record['id']], IMAGES / size / record['image'])
    (DATA / 'maps.json').write_text(json.dumps(maps, indent=2), encoding='utf-8')
    print(f'{len(images)} campaign maps have an image.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='drawn', required=True, help="imperial-assault-tools' staging/campaign-maps folder")
    main(parser.parse_args().drawn)
