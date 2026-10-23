"""2.0.0 migration 11: the miniatures collection, and record-links: figure-of, and requirements folded in.

miniatures.json lists every miniature sculpt: {id, name, description, affiliation, squares}. squares is the figure's
footprint on the map (1, 2 for 1x2, 4 for 2x2, 6 for 2x3); description tells apart sculpts that share a name: the
Stormtroopers pack's "Stormtroopers" are a 2nd pose of the Core Set's (null otherwise). A file named after a miniature
would combine the two (stormtroopers-2nd-pose). A product's miniatures are source-contents rows (content_type "miniatures") with how many figures of it
the product has as quantity.

record-links.json links records of any two types: {from_type, from_id, to_type, to_id, relation, reverse_relation}, the
relation read from each end (figure-of / has-figure). requirements.json (empty, migration 7) becomes its requires /
required-by and expands / expanded-by links, and goes. figure-of links a miniature to every record it stands for: the deployment cards with its name (regular and elite, campaign and skirmish;
not skirmish upgrades), and a hero's record. Some miniatures stand for more than one card: General Weiss's can be set
up as an AT-ST, and Captain Terro's as a Dewback Rider (OPTIONS).

The list is the maintainer's (miniatures.csv, next to this file: wave, product type, product, faction, mini, squares
and quantity per package), with the corrections they confirmed: Captain Terro's footprint is 2 squares, not 6; the
General Weiss pack's miniature is General Weiss (it stands for the AT-ST cards too), not the Core Set's AT-ST; the
Stormtroopers pack's Stormtroopers are Imperial; and both Stormtrooper sculpts are named "Stormtroopers". Read in its order, except that the Core Set's Luke Skywalker and Darth
Vader are the Luke Skywalker and Darth Vader packs' (they ship inside the Core Set; a contained pack's contents are
listed on the pack, see docs/data-model.md).

Run from the repo root: uv run python migrations/2.0.0/11_miniatures.py. Running it again changes nothing.
"""
import csv
import json
import re
import uuid
from pathlib import Path

DATA = Path('data')
CSV = Path(__file__).with_name('miniatures.csv')
PRODUCTS = {'Core set': 'Imperial Assault'}
# Core Set miniatures listed on the packs inside it.
IN_PACKS = {'Luke Skywalker': 'Luke Skywalker', 'Darth Vader': 'Darth Vader'}
# Sculpts that share a name, by (CSV product, name): the first sculpt has none.
DESCRIPTIONS = {('Stormtroopers', 'Stormtroopers'): '2nd pose'}
# requirements.json's relations, read from the source.
REVERSE = {'requires': 'required-by', 'expands': 'expanded-by'}
# Deployment cards a miniature stands for besides its own: (name, description) of the cards.
OPTIONS = {'General Weiss': [('AT-ST', None)], 'Captain Terro': [('Dewback Rider', None)]}
# A miniature whose name matches cards with several descriptions: the description of its cards.
CARD_DESCRIPTIONS = {('Imperial Assault', 'Luke Skywalker'): 'Hero of the Rebellion'}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def normalise(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def figure(miniature, to_type, record):
    return {'from_type': 'miniatures', 'from_id': miniature['id'], 'to_type': to_type, 'to_id': record['id'],
            'relation': 'figure-of', 'reverse_relation': 'has-figure'}


def main():
    if (DATA / 'miniatures.json').exists():
        print('Already migrated.')
        return
    sources = {s['name']: s['id'] for s in load('sources')}
    cards = [c for c in load('deployment-cards') if 'Skirmish Upgrade' not in (c['traits'] or [])]
    heroes = {normalise(h['name']): h for h in load('heroes')}

    def cards_named(name, description=None):
        """Deployment cards with this name: plural or singular (a "Rebel Trooper" miniature, "Rebel Troopers" cards),
        and "Name, Description" for a name the cards share ("Luke Skywalker, Jedi Knight")."""
        if ',' in name and description is None:
            name, description = (part.strip() for part in name.split(',', 1))
        key = normalise(name)
        for candidate in (key, key + 's', key.removesuffix('s')):
            found = [c for c in cards if normalise(c['name']) == candidate
                     and (description is None or c['description'] == description)]
            if found:
                return found
        return []

    miniatures, rows, links = {}, [], []
    with CSV.open(encoding='utf-8', newline='') as f:
        for line in csv.DictReader(f):
            name, product = line['Mini'], PRODUCTS.get(line['Product'], line['Product'])
            if product == 'Imperial Assault' and name in IN_PACKS:
                product = IN_PACKS[name]
            description = DESCRIPTIONS.get((line['Product'], name))
            key = (name, description)
            if key not in miniatures:
                miniatures[key] = {'id': str(uuid.uuid4()), 'name': name, 'description': description,
                                   'affiliation': line['Faction'], 'squares': int(line['Squares'])}
                mini = miniatures[key]
                own = cards_named(name, CARD_DESCRIPTIONS.get((PRODUCTS.get(line['Product'], line['Product']), name)))
                assert own, f'{name}: no deployment card'
                assert len({c['description'] for c in own}) == 1, f'{name}: several cards; pick in CARD_DESCRIPTIONS'
                stands_for = own + [c for other in OPTIONS.get(name, []) for c in cards_named(*other)]
                links += [figure(mini, 'deployment-cards', c) for c in stands_for]
                if normalise(name) in heroes:
                    links.append(figure(mini, 'heroes', heroes[normalise(name)]))
            mini = miniatures[key]
            assert (mini['affiliation'], mini['squares']) == (line['Faction'], int(line['Squares'])), name
            rows.append({'source_id': sources[product], 'content_type': 'miniatures', 'content_id': mini['id'],
                         'quantity': int(line['Qty per Package'])})
    linked = {link['to_id'] for link in links}
    assert all(c['id'] in linked for c in cards), [c['name'] for c in cards if c['id'] not in linked]
    assert all(h['id'] in linked for h in heroes.values()), [h['name'] for h in heroes.values()
                                                               if h['id'] not in linked]
    requirements = [{'from_type': r['content_type'], 'from_id': r['content_id'], 'to_type': 'sources',
                     'to_id': r['source_id'], 'relation': r['relation'], 'reverse_relation': REVERSE[r['relation']]}
                    for r in load('requirements')]
    save('miniatures', list(miniatures.values()))
    save('source-contents', load('source-contents') + rows)
    save('record-links', links + requirements)
    (DATA / 'requirements.json').unlink()
    print(f'{len(miniatures)} miniatures, {len(rows)} source-contents rows, {len(links)} figure-of links, '
          f'{len(requirements)} requirements.')


if __name__ == '__main__':
    main()
