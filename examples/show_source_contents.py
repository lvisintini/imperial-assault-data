import sys
import json
from itertools import groupby

version = (sys.version_info[0], sys.version_info[1])

# Just checking the python version to make sure that this script is not going to fail.
if (sys.version_info[0], sys.version_info[1]) < (3, 6):
    raise RuntimeError("Must be using Python 3.6 or higher")


SOURCES = [
    'sources',
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


# Load data from all the files (handle source-contents.json separately)
all_data = {}
for s in SOURCES:
    with open(f'./data/{s}.json') as f:
        all_data[s] = json.load(f)


# Load source-contents data from file
with open(f'./data/source-contents.json') as f:
    source_contents = json.load(f)

# We are going to group this entries by source id, so we need to have them ordered before doing that
source_contents = sorted(source_contents, key=lambda m: (m['source_id'], m['content_type']))
source_contents_grouped_by_source_id = groupby(source_contents, lambda x: x['source_id'])

for source_id, group in source_contents_grouped_by_source_id:

    # Get the data for the source (the product name contained within will be used later)
    source_data = next(iter([m for m in all_data['sources'] if m["id"] == source_id]))

    # Output the source name and type
    print(f"'{source_data['name']}' {source_data['type']}")

    # Group product contents by content_type
    product_contents_grouped_by_type = groupby(group, lambda x: x['content_type'])

    for content_type, sub_group in product_contents_grouped_by_type:

        # Output content type name
        print(f'\t- {content_type}')

        for i in sub_group:

            # Get data for content source content using the content_type and content_id attributes
            m = next(iter([m for m in all_data[content_type] if m["id"] == i['content_id']]), None)

            print(f'\t\t- {m["name"]}')

            # This content types have additional related components
            # We use the appropriate foreign key to fetch the additional data and print it.
            if content_type == 'imperial-classes':
                for n in [icc for icc in all_data['imperial-class-cards'] if icc['class_id'] == m['id']]:
                    print(f'\t\t\t- {n["name"]}')
            elif content_type == 'heroes':
                for n in [h for h in all_data['hero-class-cards'] if h['hero_id'] == m['id']]:
                    print(f'\t\t\t- {n["name"]}')
            elif content_type == 'agenda-decks':
                for n in [ac for ac in all_data['agenda-cards'] if ac['agenda_id'] == m['id']]:
                    print(f'\t\t\t- {n["name"]}')
