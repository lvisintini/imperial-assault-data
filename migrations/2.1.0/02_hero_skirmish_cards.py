"""2.1.0 migration 02: record-links from each hero to its skirmish deployment card.

Every hero has a Skirmish-only deployment card of its name (Jyn Odan's, for her skirmish figure). A hero is that
card's campaign version, as a Campaign-only deployment card is its Skirmish-only twin's, so the link is
campaign-of / skirmish-of (docs/data-model.md → Record links): the hero's page shows it as its "Skirmish version",
the card's its "Campaign version".

Run from the repo root: uv run python migrations/2.1.0/02_hero_skirmish_cards.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def main():
    links = load('record-links')
    if any(link['from_type'] == 'heroes' and link['relation'] == 'campaign-of' for link in links):
        print('Already migrated.')
        return
    cards = load('deployment-cards')
    added = []
    for hero in load('heroes'):
        found = [card for card in cards if card['name'] == hero['name'] and card['modes'] == ['Skirmish']]
        assert len(found) == 1, (hero['name'], len(found))
        added.append({'from_type': 'heroes', 'from_id': hero['id'], 'to_type': 'deployment-cards',
                      'to_id': found[0]['id'], 'relation': 'campaign-of', 'reverse_relation': 'skirmish-of'})
    (DATA / 'record-links.json').write_text(json.dumps(links + added, indent=2, ensure_ascii=False) + '\n',
                                            encoding='utf-8')
    print(f'Added {len(added)} hero campaign-of links.')


if __name__ == '__main__':
    main()
