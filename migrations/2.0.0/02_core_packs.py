"""2.0.0 migration 2 (#29): sources gain `included_in`, and the Luke Skywalker Ally Pack and Darth Vader Villain Pack,
which ship inside the Core Set, become sources of their own.

- `included_in` (nullable): the source a product ships inside. Null for everything except the two new packs.
- Source 31 (the Luke Skywalker, Jedi Knight Ally Pack, renamed to plain "Luke Skywalker" in 1.4.0) gets FFG's name
  back, "Luke Skywalker, Jedi Knight", and its image moves to match, so the new Core Set pack can be "Luke Skywalker".
- The packs share the Core Set's wave (0) and dates, and have no product code of their own.
- The two packs' contents (per the wiki's pack pages) move off the Core Set: their source-contents rows now point at
  the pack. The Core Set box still contains them, through `included_in`.
- Fixes the agenda deck name "Lord Vaders Command" → "Lord Vader's Command".

The packs' images (from the wiki) are written separately, by the tools; this script only touches data/.
Run from the repo root: uv run python migrations/2.0.0/02_core_packs.py. Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

DATA = Path('data')
CORE = 'Imperial Assault'
JEDI_KNIGHT_PACK = 'ced23ac2-0189-5d08-888a-4256da79cf42'  # source 31 in 1.x
PACKS = {
    'Luke Skywalker': {
        'type': 'Ally Pack', 'image': 'sources/luke-skywalker.png',
        'contents': {
            'deployment-cards': [('Luke Skywalker', 'Hero of the Rebellion')],
            'command-cards': ['Deflection', 'Knowledge and Defense', 'Meditation', 'Son of Skywalker',
                              'Telekinetic Throw'],
            'reward-cards': ['The Ways of the Force'],
            'side-mission-cards': ['Sympathy for the Rebellion'],
            'skirmish-maps': ['Moisture Farm'],
        },
    },
    'Darth Vader': {
        'type': 'Villain Pack', 'image': 'sources/darth-vader.png',
        'contents': {
            'deployment-cards': [('Darth Vader', 'Lord of the Sith')],
            'command-cards': ['Regroup', 'Close the Gap', 'Force Lightning', 'Lure of the Dark Side',
                              'Lord of the Sith'],
            'agenda-decks': ["Lord Vader's Command"],
            'skirmish-maps': ['Massassi Ruins'],
        },
    },
}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def with_included_in(source, included_in=None):
    """The source with `included_in` placed before `image`, like the other fields added after 1.x."""
    fields = {k: v for k, v in source.items() if k not in ('included_in', 'image')}
    return fields | {'included_in': source.get('included_in', included_in), 'image': source['image']}


def main():
    sources, rows = load('sources'), load('source-contents')
    if 'included_in' in sources[0]:
        print('Already migrated.')
        return

    decks = load('agenda-decks')
    for deck in decks:
        if deck['name'] == 'Lord Vaders Command':
            deck['name'] = "Lord Vader's Command"
    save('agenda-decks', decks)

    sources = [with_included_in(s) for s in sources]
    jedi_knight = next(s for s in sources if s['id'] == JEDI_KNIGHT_PACK)
    jedi_knight.update(name='Luke Skywalker, Jedi Knight', image='sources/luke-skywalker-jedi-knight.png')
    core = next(s for s in sources if s['name'] == CORE)

    for name, pack in PACKS.items():
        source = {'id': str(uuid.uuid4()), 'name': name, 'type': pack['type'], 'wave': core['wave'],
                  'product_code': None, 'announced_date': core['announced_date'], 'release_date': core['release_date'],
                  'included_in': core['id'], 'image': pack['image']}
        sources.append(source)
        for content_type, wanted in pack['contents'].items():
            records = load(content_type)
            for want in wanted:
                name_, description = want if isinstance(want, tuple) else (want, None)
                [record] = [r for r in records
                            if r['name'] == name_ and (description is None or r.get('description') == description)]
                [row] = [r for r in rows if r['source_id'] == core['id'] and r['content_type'] == content_type
                         and r['content_id'] == record['id']]
                row['source_id'] = source['id']

    save('sources', sources)
    save('source-contents', rows)
    print(f"Added {', '.join(PACKS)} inside {CORE}; renamed source 31 to {jedi_knight['name']!r}.")


if __name__ == '__main__':
    main()
