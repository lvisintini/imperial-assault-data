"""2.0.0 migration 1 (#33): numeric ids become UUIDs, and the duplicate Rebel Bossk (deployment card 17) is retired.

Every record that had an id gets uuid5(NAMESPACE, "<content type>:<old id>"), so anyone holding 1.x ids can work out
the new ones. Card backs, which had no id, get uuid5(NAMESPACE, "card-backs:<content type>:<variant>"). Foreign keys
(source-contents, agenda_id, hero_id, class_id) are rewritten to match. Records added from 2.0.0 on get a random
uuid4 instead.

Run from the repo root: uv run python migrations/2.0.0/01_uuid_ids.py. Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'https://github.com/lvisintini/imperial-assault-data')
DATA = Path('data')

# Child → parent foreign keys, as in docs/data-model.md.
FOREIGN_KEYS = {('agenda-cards', 'agenda_id'): 'agenda-decks', ('hero-class-cards', 'hero_id'): 'heroes',
                ('imperial-class-cards', 'class_id'): 'imperial-classes'}

# Bossk (deployment card 17, "Rebel") duplicates card 16: the wiki lists one Mercenary Bossk, in both The Bespin Gambit
# and the Bossk pack. The pack's row moves to card 16, which no longer needs "mercenary" in its iaspec.
RETIRED_BOSSK, BOSSK = 17, 16


def new_id(content_type, old_id):
    return str(uuid.uuid5(NAMESPACE, f'{content_type}:{old_id}'))


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main():
    files = {p.stem: load(p.stem) for p in sorted(DATA.glob('*.json'))}
    if isinstance(files['sources'][0]['id'], str):
        print('Already migrated.')
        return

    deployments = files['deployment-cards']
    deployments[:] = [d for d in deployments if d['id'] != RETIRED_BOSSK]
    next(d for d in deployments if d['id'] == BOSSK)['iaspec'] = 'bossk'

    rows = []
    for row in files['source-contents']:
        if (row['content_type'], row['content_id']) == ('deployment-cards', RETIRED_BOSSK):
            row = row | {'content_id': BOSSK}
        if row not in rows:
            rows.append(row)
    files['source-contents'] = [{
        'source_id': new_id('sources', row['source_id']),
        'content_type': row['content_type'],
        'content_id': new_id(row['content_type'], row['content_id']),
    } for row in rows]

    files['card-backs'] = [
        {'id': str(uuid.uuid5(NAMESPACE, f"card-backs:{back['content_type']}:{back['variant'] or ''}"))} | back
        for back in files['card-backs']
    ]

    for name, records in files.items():
        if name in ('source-contents', 'card-backs'):
            continue
        for record in records:
            record['id'] = new_id(name, record['id'])
            for (child, field), parent in FOREIGN_KEYS.items():
                if name == child:
                    record[field] = new_id(parent, record[field])

    for name, records in files.items():
        save(name, records)
    print(f'Migrated {len(files)} files; retired Bossk {RETIRED_BOSSK}.')


if __name__ == '__main__':
    main()
