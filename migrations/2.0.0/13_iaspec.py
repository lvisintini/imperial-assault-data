"""2.0.0 migration 13 (#32): iaspec values match the IA Skirmish Specification's keys.

iaspec is the key the IA Skirmish Specification (github.com/kingargyle/iaskirmish-data, Tabletop Admiral's list format;
IACP Skirmish Async uses the same keys today) exchanges skirmish lists with. Its keys are in tests/fixtures/
iaspec-spec.json, and the rule our values follow, for the cards the spec has and the ones it lacks, is in
docs/data-model.md (iaspec):
- `elite` only when a regular card of the same name exists (atst, not eliteatst; crosstraining, not elitecrosstraining);
- of a Campaign and a Skirmish twin, the Skirmish card keeps the bare value (the spec is skirmish-only) and the
  Campaign card gets `campaign` (agentblaise / agentblaisecampaign);
- six values are the spec's own spellings, which a key must keep to interoperate (furyofkashyyk, sarlacsweep,
  temporaryallianceempire, tempoaryalliancescum, lukeskywalker, lukeskywalkerjedi).

Run from the repo root: uv run python migrations/2.0.0/13_iaspec.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')
# (id, iaspec before, iaspec after)
CHANGES = [
    ('f2a1c20b-ce85-5f1a-bb2b-c9b964b11d18', 'eliteatst', 'atst'),  # AT-ST
    ('9b8816ae-d1aa-5705-ab1f-5b84c88e3d4b', 'agentblaiseskirmish', 'agentblaise'),  # Agent Blaise, ISB Interrogator
    ('26c67b31-7ec7-54ef-9a54-f3c2f68f740a', 'elitebantharider', 'bantharider'),  # Bantha Rider
    ('75818806-367d-5455-a5c0-9df46565fde1', 'elitecrosstraining', 'crosstraining'),  # Cross-Training
    ('3cca6575-e1d4-5667-8cfa-2019e00fb2c9', 'elitedewbackrider', 'dewbackrider'),  # Dewback Rider
    ('91849e7c-897b-5538-9577-4f9f0af61a36', 'elitefeedingfrenzy', 'feedingfrenzy'),  # Feeding Frenzy
    ('0d0ca1bb-af26-519b-b0b5-797bcb482c04', 'furyofkashyyyk', 'furyofkashyyk'),  # Fury Of Kashyyyk
    ('8d6bdf20-183f-50bd-bd97-dfc07accd2e1', 'jabbathehuttskirmish', 'jabbathehutt'),  # Jabba the Hutt, Vile Gangster
    ('80c02e76-9c20-5d07-995f-5c98653bed66', 'elitejawascavengerskirmish', 'elitejawascavenger'),  # Jawa Scavenger
    ('59e37fde-c6ac-53c5-abcf-23d3abe213d4', 'leiaorganaskirmish', 'leiaorgana'),  # Leia Organa, Rebel Commander
    # Luke Skywalker, Hero of the Rebellion
    ('ae9ce593-c113-5001-829d-c912baa7ac07', 'lukeskywalkerherooftherebellion', 'lukeskywalker'),
    # Luke Skywalker, Jedi Knight
    ('0e7a2a60-9311-5b31-ba94-c0f9d6c44173', 'lukeskywalkerjediknight', 'lukeskywalkerjedi'),
    ('ebb4df5e-ef8e-550a-8de2-6eb0b3ec072c', 'obiwankenobiskirmish', 'obiwankenobi'),  # Obi-Wan Kenobi, Jedi Knight
    ('fe22e57b-bfdb-50ae-9c11-3f000308efb6', 'r2d2skirmish', 'r2d2'),  # R2-D2, Loyal Astromech
    ('01a90474-fb91-59ce-80d8-6e33f402e073', 'eliterancorcampaign', 'rancorcampaign'),  # Rancor
    ('b928a15b-034b-57dd-9f0e-025a17b7d02a', 'eliterancorskirmish', 'rancor'),  # Rancor
    ('7b6bda51-10b4-5936-82ac-e1a7a4ce349a', 'elitesc2mrepulsortank', 'sc2mrepulsortank'),  # SC2-M Repulsor Tank
    # Temporary Alliance, A Common Enemy
    ('df25d4e2-b8b4-548f-9f5b-c4c570d45d23', 'temporaryalliancemercenary', 'tempoaryalliancescum'),
    # Temporary Alliance, Hired Guns
    ('138acad0-0139-56dd-867c-fd5e4092f33f', 'temporaryallianceimperial', 'temporaryallianceempire'),
    ('f2137455-7401-51fd-ae3d-f9f8c32e11b3', 'eliteatdp', 'atdp'),  # AT-DP
    ('aedbe382-a938-5b33-882c-61abcb82b53f', 'riottrooperskirmish', 'riottrooper'),  # Riot Trooper
    ('54d2a283-3930-58f3-8b3f-1a6df968fbfa', 'eliteriottrooperskirmish', 'eliteriottrooper'),  # Riot Trooper
    ('a1b90237-b396-5ead-a33c-96ab39debba8', 'thrawnskirmish', 'thrawn'),  # Thrawn, Grand Admiral
    ('5f98d5e5-3fde-5d1b-b3d4-f581c8f560ab', 'deathtrooperskirmish', 'deathtrooper'),  # Death Trooper
    ('afc3ddab-a84d-53e4-b618-28cc5c7281e6', 'elitedeathtrooperskirmish', 'elitedeathtrooper'),  # Death Trooper
    ('55f57317-1839-5ecf-9bb9-297aebfee172', 'hondoohnakaskirmish', 'hondoohnaka'),  # Hondo Ohnaka, Friend for hire
    ('4e24aa9f-aee8-5291-afe3-b8c7b9562046', 'ezrabridgerskirmish', 'ezrabridger'),  # Ezra Bridger, Spectre-6
    ('506dbdde-f631-5110-ab2f-babb2042cfa2', 'kananjarrusskirmish', 'kananjarrus'),  # Kanan Jarrus, Spectre-1
    ('e9636aee-1434-5477-9dab-937cabae927b', 'sabinewrenskirmish', 'sabinewren'),  # Sabine Wren, Spectre-5
    ('a7921eee-70f1-517d-a6bb-3aff27cb5cb7', 'eliteextraarmor', 'extraarmor'),  # Extra Armor
    ('1b925785-42f7-5389-bfde-3be6eef8ad8d', 'sarlaccsweep', 'sarlacsweep'),  # Sarlacc Sweep
]


def main():
    changes = {record_id: (before, after) for record_id, before, after in CHANGES}
    done = 0
    for name in ('deployment-cards', 'command-cards'):
        path = DATA / f'{name}.json'
        records = json.loads(path.read_text(encoding='utf-8'))
        for record in records:
            if record['id'] in changes:
                before, after = changes[record['id']]
                assert record['iaspec'] in (before, after), record['iaspec']
                done += record['iaspec'] == after
                record['iaspec'] = after
        path.write_text(json.dumps(records, indent=2), encoding='utf-8')
    print('Already migrated.' if done == len(CHANGES) else f'{len(CHANGES) - done} iaspec values changed.')


if __name__ == '__main__':
    main()
