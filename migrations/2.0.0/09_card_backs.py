"""2.0.0 migration 9 (#52): card backs become a catalog, and every card points at its back through back_id.

- card-backs.json loses content_type and variant: a back is {id, name, image}. Its name is today's deck and variant,
  as the explorer showed it ("Deployment: Rebel", "Rebel Hero: Biv Bodhrik"; "Side Mission" for a deck with one back).
- Backs that were one row per content type for the same image (the side mission back, one per side mission
  collection since migration 4) become one back, keeping the 1.x-derived id.
- Every card gets back_id (just before its image field), found once with the matching rules this release retires (variant =
  affiliation for deployment cards, the hero's or class's name for their class cards, the tier for upgrades, the
  product's name for story and threat missions, the mission card's name for epilogues; child cards take their
  parent's). Heroes, Imperial classes and agenda decks get none: their backs are on their cards.
- Skirmish mission cards get a new back, "Skirmish Mission", from the maintainer's scan (card-backs/skirmish-mission.png,
  written before this runs at the skirmish mission cards' size by imperial-assault-tools' images.encode).

Run from the repo root: uv run python migrations/2.0.0/09_card_backs.py. Running it again changes nothing.
"""
import json
import uuid
from pathlib import Path

DATA = Path('data')
IMAGES = Path('images')
SKIRMISH_BACK = {'name': 'Skirmish Mission', 'image': 'card-backs/skirmish-mission.png'}
# Card types, and the parent whose back a child type's cards have.
CARDS = [
    'agenda-cards', 'command-cards', 'companion-cards', 'condition-cards', 'deployment-cards', 'epilogue-cards',
    'form-cards', 'hero-class-cards', 'imperial-class-cards', 'reward-cards', 'supply-cards', 'upgrade-cards',
    'campaign-story-mission-cards', 'campaign-threat-mission-cards', 'campaign-hero-side-mission-cards',
    'campaign-ally-side-mission-cards', 'campaign-regular-side-mission-cards', 'skirmish-mission-cards',
]
PARENTS = {'agenda-cards': ('agenda_id', 'agenda-decks'), 'hero-class-cards': ('hero_id', 'heroes'),
           'imperial-class-cards': ('class_id', 'imperial-classes')}


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def matcher(content_type):
    """The retired rule: whether a back's variant fits a record of content_type."""
    if content_type == 'deployment-cards':
        return lambda record, variant: record['affiliation'] == variant
    if content_type in ('heroes', 'imperial-classes', 'condition-cards'):
        return lambda record, variant: record['name'] == variant
    if content_type == 'upgrade-cards':
        return lambda record, variant: f"Tier {record['tier']}" == variant
    if content_type in ('campaign-story-mission-cards', 'campaign-threat-mission-cards'):
        sources = {s['id']: s['name'] for s in load('sources')}
        index = {m['content_id']: m['id'] for m in load('missions')}
        products = {}
        for row in load('source-contents'):
            products.setdefault(row['content_id'], set()).add(sources[row['source_id']])
        return lambda record, variant: variant in products[index[record['id']]]
    if content_type == 'epilogue-cards':
        cards = {r['id']: r['name'] for t in {m['content_type'] for m in load('missions')} for r in load(t)}
        missions = {m['id']: cards[m['content_id']] for m in load('missions')}
        return lambda record, variant: missions[record['mission_id']] == variant
    return lambda record, variant: True


def main():
    backs = load('card-backs')
    if 'variant' not in backs[0]:
        print('Already migrated.')
        return
    assert all((IMAGES / size / SKIRMISH_BACK['image']).exists() for size in ('large', 'small')), \
        'write the skirmish mission back first (see above)'

    # The catalog: one back per image, keeping a 1.x-derived (uuid5) id where the image had several rows.
    catalog, kept = [], {}
    for back in backs:
        if back['image'] in kept:
            if uuid.UUID(back['id']).version == 5:
                kept[back['image']]['id'] = back['id']
            continue
        variant = back['variant'] if back['variant'] and back['variant'] not in back['deck'] else None
        kept[back['image']] = {'id': back['id'], 'name': f"{back['deck']}: {variant}" if variant else back['deck'],
                               'image': back['image']}
        catalog.append(kept[back['image']])
    skirmish = {'id': str(uuid.uuid4())} | SKIRMISH_BACK
    catalog.append(skirmish)
    names = [b['name'] for b in catalog]
    assert len(names) == len(set(names)), 'back names collide'

    # back_id on every card, from the retired rules.
    def back_of(content_type, record):
        if content_type in PARENTS:
            field, parent_type = PARENTS[content_type]
            return back_of(parent_type, next(r for r in load(parent_type) if r['id'] == record[field]))
        if content_type == 'skirmish-mission-cards':
            return skirmish['id']
        match = matchers.setdefault(content_type, matcher(content_type))
        found = [b for b in backs if b['content_type'] == content_type and match(record, b['variant'])]
        assert len(found) == 1, f"{content_type} {record['name']}: {len(found)} backs"
        return kept[found[0]['image']]['id']

    matchers, by_parent = {}, {}
    for content_type in CARDS:
        records = []
        for record in load(content_type):
            if content_type in PARENTS:  # one lookup per parent
                parent_id = record[PARENTS[content_type][0]]
                if parent_id not in by_parent:
                    by_parent[parent_id] = back_of(content_type, record)
                back_id = by_parent[parent_id]
            else:
                back_id = back_of(content_type, record)
            card = {}
            for field, value in record.items():
                if field == 'image':
                    card['back_id'] = back_id
                card[field] = value
            records.append(card)
        save(content_type, records)
    save('card-backs', catalog)
    used = {r['back_id'] for t in CARDS for r in load(t)}
    assert used == {b['id'] for b in catalog}, 'a back no card uses'
    print(f'{len(backs)} card-back rows → {len(catalog)} backs (with the skirmish mission back); '
          f'back_id on {len(CARDS)} card types.')


if __name__ == '__main__':
    main()
