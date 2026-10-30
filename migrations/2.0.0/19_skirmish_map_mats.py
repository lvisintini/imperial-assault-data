"""2.0.0 migration 19: the 13 skirmish map mats as products (#47).

FFG sold 13 skirmish maps on their own, as neoprene mats with their own product codes. Each becomes a source of type
"Skirmish Map Mat" with a source-contents row straight to its map (which its missions' products also reach).
imperial-assault-tools' ia mats staged them: name and product code from each mat's wiki infobox, wave and dates from
the wiki's main page (which lists each mat under a wave, with that wave's dates, like every other source), and the
image from FFG's product page as the Wayback Machine archived it.

    uv run python migrations/2.0.0/19_skirmish_map_mats.py --from ../imperial-assault-tools/staging/mats
Running it again changes nothing.
"""
import argparse
import json
import shutil
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
TYPE = 'Skirmish Map Mat'


def main(staged):
    sources = json.loads((DATA / 'sources.json').read_text(encoding='utf-8'))
    if any(s['type'] == TYPE for s in sources):
        print('Already migrated.')
        return
    staged = Path(staged)
    mats = json.loads((staged / 'manifest.json').read_text(encoding='utf-8'))['mats']
    maps = {m['id'] for m in json.loads((DATA / 'maps.json').read_text(encoding='utf-8'))}
    missing = [m['name'] for m in mats if m['map_id'] not in maps]
    assert not missing, f'No map for {missing}'
    contents = json.loads((DATA / 'source-contents.json').read_text(encoding='utf-8'))
    for mat in mats:
        source_id = str(uuid.uuid4())
        sources.append({'id': source_id, 'name': mat['name'], 'type': TYPE, 'wave': mat['wave'],
                        'product_code': mat['product_code'], 'announced_date': mat['announced_date'],
                        'release_date': mat['release_date'], 'image': mat['image']})
        contents.append({'source_id': source_id, 'content_type': 'maps', 'content_id': mat['map_id'], 'quantity': 1})
        for size in ('large', 'small'):
            shutil.copyfile(staged / size / mat['image'], IMAGES / size / mat['image'])
    (DATA / 'sources.json').write_text(json.dumps(sources, indent=2), encoding='utf-8')
    (DATA / 'source-contents.json').write_text(json.dumps(contents, indent=2), encoding='utf-8')
    print(f'{len(mats)} skirmish map mats added.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='staged', required=True, help="imperial-assault-tools' staging/mats folder")
    main(parser.parse_args().staged)
