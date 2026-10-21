"""2.0.0 migration 7 (#47, #29): products inside products through source-contents, and the requirements collection.

- sources.included_in goes. A product that ships inside another (the Luke Skywalker Ally Pack and the Darth Vader
  Villain Pack, in the Core Set) is instead a source-contents row of its container: {source_id: <the Core Set>,
  content_type: "sources", content_id: <the pack>}. The pack's own contents stay listed on the pack.
- requirements.json (new, empty): what a record requires or expands, {content_type, content_id, relation, source_id}.
- sources.type gains "Skirmish Map Mat" and "Raid Map Mat" (schema only; the mats themselves come later).

Run from the repo root: uv run python migrations/2.0.0/07_sources_relations.py. Running it again changes nothing.
"""
import json
from pathlib import Path

DATA = Path('data')


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main():
    sources = load('sources')
    if 'included_in' not in sources[0]:
        print('Already migrated.')
        return
    rows = load('source-contents')
    inside = [{'source_id': s['included_in'], 'content_type': 'sources', 'content_id': s['id']}
              for s in sources if s['included_in']]
    for source in sources:
        del source['included_in']
    save('sources', sources)
    save('source-contents', rows + inside)
    save('requirements', [])
    print(f'{len(inside)} products now listed in their container; requirements.json created.')


if __name__ == '__main__':
    main()
