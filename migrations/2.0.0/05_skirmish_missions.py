"""2.0.0 migration 5 (#49, PR B): skirmish mission cards, indexed with their maps, and maps' products through them.

- skirmish-mission-cards: every skirmish mission card (104: two per skirmish map), with `format` (Standard, Four
  Player Team Battle, Four Player Free-For-All) and `scenario` (A or B; null until entered from the cards).
- Each gets a missions row with its map (map_id), and its map's products: source-contents rows to the missions row.
- A map used by a mission reaches its products through its missions, so its own source-contents rows go. Maps no
  mission uses yet (the raid maps, until raid missions are added) keep theirs.

The cards, maps and formats come from the wiki's skirmish mission pages, through imperial-assault-tools'
`ia wiki --skirmish` cache (its images are written separately, by the tools):
    uv run python migrations/2.0.0/05_skirmish_missions.py --wiki ../imperial-assault-tools/staging/wiki/skirmish.json
Running it again changes nothing.
"""
import argparse
import json
import re
import uuid
from pathlib import Path

DATA = Path('data')
TYPE = 'skirmish-mission-cards'


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def slug(name):
    return re.sub(r'-+', '-', ''.join(c if c.isalnum() else '-' for c in name.lower().replace("'", '')
                                      .replace('"', ''))).strip('-')


def main(wiki):
    if (DATA / f'{TYPE}.json').exists():
        print('Already migrated.')
        return
    cache = json.loads(Path(wiki).read_text(encoding='utf-8'))['missions']
    problems = [f"{m['name']}: {p}" for m in cache for p in m['problems']]
    assert not problems, '\n'.join(problems)

    rows = load('source-contents')
    products = {}
    for row in rows:
        if row['content_type'] == 'maps':
            products.setdefault(row['content_id'], []).append(row['source_id'])
    cards, index, linked = [], load('missions'), []
    for mission in cache:
        card = {'id': str(uuid.uuid4()), 'name': mission['name'], 'format': mission['format'], 'scenario': None,
                'image': f"{TYPE}/{slug(mission['name'])}.png"}
        cards.append(card)
        row = {'id': str(uuid.uuid4()), 'content_type': TYPE, 'content_id': card['id'], 'map_id': mission['map']['id']}
        index.append(row)
        assert products.get(row['map_id']), f"{mission['map']['text']} has no products"
        linked += [{'source_id': source, 'content_type': 'missions', 'content_id': row['id']}
                   for source in products[row['map_id']]]
    assert len({c['image'] for c in cards}) == len(cards), 'two cards would share an image'

    used = {row['map_id'] for row in index if row['map_id']}
    kept = [row for row in rows if not (row['content_type'] == 'maps' and row['content_id'] in used)]
    save(TYPE, cards)
    save('missions', index)
    save('source-contents', kept + linked)
    print(f'{len(cards)} skirmish missions on {len(used)} maps; {len(rows) - len(kept)} map product rows now go through '
          f'{len(linked)} mission rows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wiki', required=True, help="imperial-assault-tools' staging/wiki/skirmish.json")
    main(parser.parse_args().wiki)
