import sys
import json
from itertools import groupby

version = (sys.version_info[0], sys.version_info[1])

if (sys.version_info[0], sys.version_info[1]) < (3, 6):
    raise RuntimeError("Must be using Python 3.6 or higher")


SOURCES = [
    'sources',
    'source-contents',
    'skirmish-maps',
    'agenda-cards',
    'agenda-decks',
    'command-cards',
    'condition-cards',
    'deployment-cards',
    'heroes',
    'hero-class-cards',
    'imperial-classes',
    'imperial-class-cards',
    'supply-cards',
    'story-mission-cards',
    'side-mission-cards',
    'reward-cards',
    'companion-cards',
    'upgrade-cards',
    'card-backs',
    'threat-mission-cards',
    'form-cards'
]

with open(f'./data/source-contents.json') as f:
    source_contents = json.load(f)
    source_contents = sorted(source_contents, key=lambda m: (m['source_id'], m['content_type']))

all_data = {}
for s in SOURCES:
    with open(f'./data/{s}.json') as f:
        all_data[s] = json.load(f)

for source, group in groupby(source_contents, lambda x: x['source_id']):
    source_data = next(iter([m for m in all_data['sources'] if m["id"] == source]))
    print(f"'{source_data['name']}' {source_data['type']}")
    for content_type, sub_group in groupby(group, lambda x: x['content_type']):
        print(f'\t- {content_type}')
        for i in sub_group:
            m = next(iter([m for m in all_data[content_type] if m["id"] == i['content_id']]), None)

            if not m:
                print(f'\t\tPROBLEM {i}')
            else:
                print(f'\t\t- {m["name"]}')
