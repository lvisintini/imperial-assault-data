"""2.0.0 migration 14 (#34): record-links for forms and deployment card variants.

Three relations join record-links (docs/data-model.md → Record links):
- form-of / has-form: a form card → the deployment cards it's a form of. The Clawdite Shapeshifter's three forms
  (Scout, Senator, Streetrat) are forms of both its cards, regular and elite.
- elite-of / regular-of: an elite deployment card → the regular card of the same name, description and affiliation
  whose modes overlap its own. Most pairs share their modes; the Jawa Scavengers' regular card (Campaign and
  Skirmish) is the regular of both its elite cards (one Campaign, one Skirmish).
- campaign-of / skirmish-of: a Campaign-only deployment card → its Skirmish-only twin: same name, description,
  affiliation and elite. Every Campaign-only card has one. The Riot Troopers and Death Troopers are a square: regular
  and elite, each in a Campaign and a Skirmish card.

This replaces #31's counterpart_id idea (one field can't hold both kinds), and #3's form link.

Run from the repo root: uv run python migrations/2.0.0/14_variants.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')
FORM_OF = 'Clawdite Shapeshifter'  # the deployment cards the form cards are forms of


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def link(from_type, from_record, to_type, to_record, relation, reverse_relation):
    return {'from_type': from_type, 'from_id': from_record['id'], 'to_type': to_type, 'to_id': to_record['id'],
            'relation': relation, 'reverse_relation': reverse_relation}


def same_card(a, b):
    return (a['name'], a['description'], a['affiliation']) == (b['name'], b['description'], b['affiliation'])


def main():
    links = load('record-links')
    if any(l['relation'] == 'form-of' for l in links):
        print('Already migrated.')
        return
    cards = load('deployment-cards')
    shapeshifters = [c for c in cards if c['name'] == FORM_OF]
    assert len(shapeshifters) == 2
    new = [link('form-cards', form, 'deployment-cards', card, 'form-of', 'has-form')
           for form in load('form-cards') for card in shapeshifters]
    new += [link('deployment-cards', elite, 'deployment-cards', regular, 'elite-of', 'regular-of')
            for elite in cards if elite['elite'] for regular in cards
            if not regular['elite'] and same_card(elite, regular) and set(elite['modes']) & set(regular['modes'])]
    new += [link('deployment-cards', campaign, 'deployment-cards', skirmish, 'campaign-of', 'skirmish-of')
            for campaign in cards if campaign['modes'] == ['Campaign'] for skirmish in cards
            if skirmish['modes'] == ['Skirmish'] and same_card(campaign, skirmish)
            and campaign['elite'] == skirmish['elite']]
    campaign_only = {c['id'] for c in cards if c['modes'] == ['Campaign']}
    assert campaign_only == {l['from_id'] for l in new if l['relation'] == 'campaign-of'}
    (DATA / 'record-links.json').write_text(json.dumps(links + new, indent=2), encoding='utf-8')
    counts = {r: sum(l['relation'] == r for l in new) for r in ('form-of', 'elite-of', 'campaign-of')}
    print(f'Added {len(new)} links: {counts}.')


if __name__ == '__main__':
    main()
