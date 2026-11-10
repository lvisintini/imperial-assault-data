"""2.1.0 migration 01: record-links from each companion to what puts it into play, and a related card.

companion-of / has-companion joins record-links (docs/data-model.md → Record links): a companion card → the hero,
cards or Imperial class that deploy it. The data has no card text, so these come from the wiki
(imperial-assault.fandom.com): each companion's page names what deploys it, and that card's text says so ("place the
Pit Droid companion in your space", "deploy 88-Z", "put J4X-7 into play"). Cards that only mention a companion
(Jarrod Kelvin's class cards, the other Reactive Defenses cards) aren't linked.

related-to (both ways) also joins: two records that bear on each other without one deploying, being a version of or
standing for the other. The Droid Mastery command card is related-to J4X-7: it acts on the companion (and can put it
back into play), but J4X-7 comes with Jarrod Kelvin.

A companion's links are appended in the order below: its first is the page the explorer puts it under when it's
reached from elsewhere (a product, search).

Run from the repo root: uv run python migrations/2.1.0/01_companions.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')

# companion → [(type, name, elite or None)], in link order.
DEPLOYERS = {
    'Cam Droid': [('reward-cards', 'Cam Droid', None)],
    'Junk Droid': [('deployment-cards', 'Ugnaught Tinkerer', False), ('deployment-cards', 'Ugnaught Tinkerer', True)],
    'R5 Astromech': [('upgrade-cards', 'R5 Astromech', None)],
    'Pit Droid': [('supply-cards', 'Pit Droid', None)],
    'Salacious B. Crumb': [('deployment-cards', 'Indentured Jester', None)],
    '88-Z': [('imperial-classes', 'Reactive Defenses', None), ('imperial-class-cards', 'Active Surveillance', None)],
    'J4X-7': [('heroes', 'Jarrod Kelvin', None), ('deployment-cards', 'Jarrod Kelvin', None)],
}

# (type, name) related-to (companion name).
RELATED = [(('command-cards', 'Droid Mastery'), 'J4X-7')]


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def one(records, name, elite):
    found = [r for r in records if r['name'] == name and (elite is None or r['elite'] == elite)]
    assert len(found) == 1, (name, elite, len(found))
    return found[0]


def main():
    links = load('record-links')
    if any(link['relation'] == 'companion-of' for link in links):
        print('Already migrated.')
        return
    companions = load('companion-cards')
    added = []
    for companion, deployers in DEPLOYERS.items():
        card = one(companions, companion, None)
        for content_type, name, elite in deployers:
            record = one(load(content_type), name, elite)
            added.append({'from_type': 'companion-cards', 'from_id': card['id'], 'to_type': content_type,
                          'to_id': record['id'], 'relation': 'companion-of', 'reverse_relation': 'has-companion'})
    for (content_type, name), companion in RELATED:
        record = one(load(content_type), name, None)
        added.append({'from_type': content_type, 'from_id': record['id'], 'to_type': 'companion-cards',
                      'to_id': one(companions, companion, None)['id'], 'relation': 'related-to',
                      'reverse_relation': 'related-to'})
    assert {companion['name'] for companion in companions} == set(DEPLOYERS)
    (DATA / 'record-links.json').write_text(json.dumps(links + added, indent=2, ensure_ascii=False) + '\n',
                                            encoding='utf-8')
    print(f'Added {len(added)} links.')


if __name__ == '__main__':
    main()
