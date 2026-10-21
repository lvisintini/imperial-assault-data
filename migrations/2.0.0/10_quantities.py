"""2.0.0 migration 10 (#30): source-contents rows say how many copies of a record a product has (quantity).

Every row gets quantity 1, except the rows below: the "(xN)" markers on the wiki's product pages (imperial-assault-tools'
`ia wiki` cache, staging/wiki/products.json), matched to rows by product, type and name, and for deployment cards by
elite and mode (a bare name with xN is the regular card; its elite is listed apart). Deflection and Regroup, which the
wiki lists on the Core Set and on the Luke Skywalker and Darth Vader packs, are the packs' (#29). Heroic (x3) and
Legendary (x2), Core Set reward cards, aren't in the dataset.

Run from the repo root: uv run python migrations/2.0.0/10_quantities.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')
# (source name, content type, content id, quantity)
QUANTITIES = [
    ('Imperial Assault', 'deployment-cards', '8ab9c881-2ea6-5e88-99df-40caac828a75', 2),  # Stormtrooper
    ('Imperial Assault', 'deployment-cards', '9901e4e1-f2bf-556a-bc4d-6719be9f9055', 2),  # Imperial Officer
    ('Imperial Assault', 'deployment-cards', '91139b33-3d62-5d51-bd87-f4d92b454bb0', 2),  # Probe Droid
    ('Imperial Assault', 'command-cards', 'd0c73637-96e0-5f82-9d3e-587e669ec2ad', 2),  # Pummel
    ('Imperial Assault', 'command-cards', '79c4d338-094d-5a01-9ae7-394684ec933c', 2),  # Marksman
    ('Imperial Assault', 'command-cards', '240f2d12-d82a-5a1c-89e2-047dc7d60968', 2),  # Sit Tight
    ('Imperial Assault', 'command-cards', '73d15eda-df2f-5a99-85a3-1000f4923817', 2),  # Expose Weakness
    ('Imperial Assault', 'command-cards', 'd76f6672-c11d-5104-94a1-21116afb3a52', 2),  # Recovery
    ('Imperial Assault', 'command-cards', 'f5bea603-31cb-5f33-8ff6-6d7592bb0cb2', 2),  # Take Initiative
    ('Imperial Assault', 'command-cards', '10be4a0a-4d87-5383-b209-9b5797d2b92d', 2),  # Rally
    ('Imperial Assault', 'command-cards', '647a841c-d74f-52ce-b0a3-15ebfd4dd1b4', 2),  # To the Limit
    ('Imperial Assault', 'command-cards', '53fe5315-1a9d-5c26-bba8-4401908fa235', 2),  # Fleet Footed
    ('Imperial Assault', 'command-cards', 'f16c0db6-52c4-5747-87d0-9d8be122577e', 2),  # Take Cover
    ('Imperial Assault', 'command-cards', '17a8d439-b590-57f3-90d3-82630c81b308', 2),  # Deadeye
    ('Imperial Assault', 'command-cards', '6287abef-f564-5ffc-bcad-5b21fd1c5569', 2),  # Celebration
    ('Imperial Assault', 'command-cards', 'b29e2a38-01a0-50bf-aa99-eee4550c4d99', 2),  # Urgency
    ('Imperial Assault', 'command-cards', '0c44f104-418a-5ff4-bb36-488d3d3a1beb', 2),  # Element of Surprise
    ('Imperial Assault', 'command-cards', 'b1589ad7-e505-5d6e-9fd0-b0e5ad235b04', 2),  # Planning
    ('Imperial Assault', 'supply-cards', 'a704696b-2659-5039-8b5c-2fe814a843f0', 2),  # Shock Grenade
    ('Imperial Assault', 'supply-cards', 'f6cc1e28-f76e-5dc8-a6a5-da79b61ea7d5', 2),  # Adrenal Stim
    ('Imperial Assault', 'supply-cards', '66ca6a92-b177-536b-b480-8559a1d323e5', 2),  # Emergency Medpac
    ('Imperial Assault', 'supply-cards', 'f34418c6-d057-58cc-bd54-1fbd17ffb2a4', 2),  # Bacta Infusion
    ('Imperial Assault', 'condition-cards', '2d38bd5d-67a0-5b00-962a-c1e9b507fe68', 4),  # Stunned
    ('Imperial Assault', 'condition-cards', '4def469d-0db7-5306-92be-eff4307f757d', 4),  # Bleeding
    ('Imperial Assault', 'condition-cards', 'bbeb6a4c-4767-52d0-a0ac-01423dd6b20e', 4),  # Focused
    ('General Weiss', 'command-cards', 'b13a038b-37d1-5a11-98ab-1d82613e30fd', 2),  # Explosive Weaponry
    ('Royal Guard Champion', 'command-cards', '9b760c6f-1677-5ea7-ba85-fce84d2e6c80', 2),  # Bodyguard
    ('Royal Guard Champion', 'command-cards', '30b20bc3-0f7a-5775-9559-5122833f7ce4', 2),  # Parting Blow
    ('IG-88', 'command-cards', '4e525c64-4e8b-5287-81f2-ffccf98a9a85', 2),  # Repair
    ('IG-88', 'command-cards', 'ea6b0aa9-e702-5811-9325-6a520f9bb8de', 2),  # Merciless
    ('Han Solo', 'command-cards', 'd62a9cd5-935e-57e3-9311-ec0291ac3170', 2),  # Slippery Target
    ('Chewbacca', 'command-cards', 'e285e447-3ee5-5ef2-b4e7-e6743930c69c', 2),  # Wookiee Rage
    ('Rebel Troopers', 'command-cards', '4bcaebd8-4b1b-51d3-8613-c9fe0f5f44bd', 2),  # Reinforcements
    ('Rebel Saboteurs', 'command-cards', 'ba7a2822-b360-5df7-aa17-de01b908b1c0', 2),  # Collect Intel
    ('Twin Shadows', 'condition-cards', '47d9361e-aaa7-58f8-9b2a-3dedb592d663', 4),  # Weakened
    ('Stormtroopers', 'command-cards', '4bcaebd8-4b1b-51d3-8613-c9fe0f5f44bd', 2),  # Reinforcements
    ('Wookiee Warriors', 'command-cards', '30b20bc3-0f7a-5775-9559-5122833f7ce4', 2),  # Parting Blow
    ('Hired Guns', 'command-cards', 'd62a9cd5-935e-57e3-9311-ec0291ac3170', 2),  # Slippery Target
    ('Bantha Rider', 'command-cards', 'aab311c5-3749-5a78-a311-0e4ec78e4f2c', 2),  # Jundland Terror
    ('Bantha Rider', 'command-cards', '30b20bc3-0f7a-5775-9559-5122833f7ce4', 2),  # Parting Blow
    ('Return to Hoth', 'deployment-cards', '7dd6ad99-e3a1-52a5-a42d-99282d9e5d51', 2),  # Targeting Computer (Skirmish)
    ('Return to Hoth', 'condition-cards', '47d9361e-aaa7-58f8-9b2a-3dedb592d663', 4),  # Weakened
    ('The Bespin Gambit', 'deployment-cards', 'd2c7de25-5a95-5ed8-a73e-4c99317287cf', 2),  # Ugnaught Tinkerer
    ('The Bespin Gambit', 'deployment-cards', 'dc2920b8-b976-5f28-8ad0-2a7166991d74', 2),  # Wing Guard
    ('The Bespin Gambit', 'condition-cards', 'e64e5a82-3604-5aae-9868-3195ce17391e', 4),  # Hidden
    ('Agent Blaise', 'command-cards', 'ba7a2822-b360-5df7-aa17-de01b908b1c0', 2),  # Collect Intel
    ("Jabba's Realm", 'deployment-cards', '73375e4c-8405-58e1-827b-4a71e84cebde', 2),  # Jet Trooper
    ("Jabba's Realm", 'deployment-cards', '643073cc-0fa1-574b-b0b1-6b6c2edf7201', 2),  # Gamorrean Guard
    ("Jabba's Realm", 'deployment-cards', 'ff1500f4-cbd6-5015-b7d6-2b6a0e0820ec', 2),  # Weequay Pirate
    ("Jabba's Realm", 'condition-cards', '47d9361e-aaa7-58f8-9b2a-3dedb592d663', 4),  # Weakened
    ("Jabba's Realm", 'condition-cards', 'e64e5a82-3604-5aae-9868-3195ce17391e', 4),  # Hidden
    ('Heart of the Empire', 'deployment-cards', '216123cf-61c8-524e-8d8d-63bf44831dcd', 2),  # Riot Trooper (Campaign)
    ('Heart of the Empire', 'deployment-cards', 'aedbe382-a938-5b33-882c-61abcb82b53f', 2),  # Riot Trooper (Skirmish)
    ('Heart of the Empire', 'deployment-cards', '2c5e972c-9e3e-5bfe-9a78-5517a97b1cb6', 2),  # Sentry Droid
    ('Heart of the Empire', 'deployment-cards', 'b082689e-633b-51c7-ab34-c93fc3d04159', 2),  # Clawdite Shapeshifter
    ('Heart of the Empire', 'condition-cards', '47d9361e-aaa7-58f8-9b2a-3dedb592d663', 4),  # Weakened
    ('Tyrants of Lothal', 'deployment-cards', 'eb51c24b-d9a5-5f0e-a7e7-42db1f7b5036', 2),  # Death Trooper (Campaign)
    ('Tyrants of Lothal', 'deployment-cards', '5f98d5e5-3fde-5d1b-b3d4-f581c8f560ab', 2),  # Death Trooper (Skirmish)
    ('Tyrants of Lothal', 'deployment-cards', '375509e2-4789-5f2c-a57d-c0017ce28124', 2),  # Death Trooper (elite) (Campaign)
    ('Tyrants of Lothal', 'deployment-cards', 'afc3ddab-a84d-53e4-b618-28cc5c7281e6', 2),  # Death Trooper (elite) (Skirmish)
    ('Tyrants of Lothal', 'condition-cards', '47d9361e-aaa7-58f8-9b2a-3dedb592d663', 4),  # Weakened
    ('Sabine Wren and Zeb Orrelios', 'command-cards', '1c01a448-7544-5b3c-9454-d1aaab55d2ee', 3),  # Escalating Hostility
    ('Luke Skywalker', 'command-cards', '7acd9e29-7a0b-5a12-8dcb-eedb9e4d2e22', 2),  # Deflection
    ('Darth Vader', 'command-cards', 'a1027cc2-1011-5021-898b-e6c85cc6956c', 2),  # Regroup
]


def main():
    path = DATA / 'source-contents.json'
    rows = json.loads(path.read_text(encoding='utf-8'))
    if 'quantity' in rows[0]:
        print('Already migrated.')
        return
    sources = {s['name']: s['id'] for s in json.loads((DATA / 'sources.json').read_text(encoding='utf-8'))}
    quantities = {(sources[source], content_type, content_id): n for source, content_type, content_id, n in QUANTITIES}
    keys = [(r['source_id'], r['content_type'], r['content_id']) for r in rows]
    assert set(quantities) <= set(keys), set(quantities) - set(keys)
    rows = [row | {'quantity': quantities.get(key, 1)} for row, key in zip(rows, keys)]
    path.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print(f'{len(rows)} rows, {len(quantities)} with more than one copy.')


if __name__ == '__main__':
    main()
