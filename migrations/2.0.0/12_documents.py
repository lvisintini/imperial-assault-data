"""2.0.0 migration 12: the documents collection, and the document-for relation.

documents.json lists FFG's documents for the game: {id, name, category, version, file}. file is the PDF's path in
documents/ (in the repository and the release zips; the explorer links to the repository's copy, so the PDFs stay off
GitHub Pages), under the name FFG published it with. version is the document's version, from what it prints (the FAQ's
4, the tournament regulations' 3.4) or from its file name (Learn to Play's 17, the Skirmish Guide's 6, the Fundamental
Event Document's 2.1), null when it has none.

A document reaches products in one of two ways, or neither:
- the books in a product's box are its contents: source-contents rows (the Core Set's Learn to Play, Rules Reference
  Guide and Skirmish Guide, and each expansion's rulebook);
- documents published for a product, but not in its box, are record-links document-for / has-document to it (the
  campaign logs, the Legends of the Alliance rulebook, and the FAQ and player sheets, for the Core Set);
- organized-play documents (tournament regulations, floor rules, the Fundamental Event Document, the prize tracker)
  belong to no product.

The PDFs are the maintainer's (imperial-assault-tools' documents/ folder), copied here as they are:
    uv run python migrations/2.0.0/12_documents.py --from ../imperial-assault-tools/documents
Running it again changes nothing.
"""
import argparse
import json
import shutil
import uuid
from pathlib import Path

DATA = Path('data')
DOCUMENTS = Path('documents')
# (file, name, category, version, how it reaches a product: ('contents' | 'document-for', source) or None)
LIST = [
    ('swi01_learn_to_play_v17.pdf', 'Learn to Play', 'Learn to Play', '17', ('contents', 'Imperial Assault')),
    ('swi01_rules_reference.pdf', 'Rules Reference Guide', 'Rules Reference', None, ('contents', 'Imperial Assault')),
    ('swi01_skirmish_guide_v6.pdf', 'Skirmish Guide', 'Skirmish Guide', '6', ('contents', 'Imperial Assault')),
    ('campaignlog.pdf', 'Core Set Campaign Log', 'Campaign Log', None, ('document-for', 'Imperial Assault')),
    ('swi_faq_v4.pdf', 'Official FAQ', 'FAQ', '4', ('document-for', 'Imperial Assault')),
    ('imperial-assault-squadsheet.pdf', 'Squad Sheet', 'Player Sheet', None, ('document-for', 'Imperial Assault')),
    ('swi01-scoresheet.pdf', 'Score Sheet', 'Player Sheet', None, ('document-for', 'Imperial Assault')),
    ('swi_signup.pdf', 'Skirmish Sign-Up Sheet', 'Player Sheet', None, ('document-for', 'Imperial Assault')),
    ('imperial_assault_twin_shadows_rulebook.pdf', 'Twin Shadows Rulebook', 'Rulebook', None,
     ('contents', 'Twin Shadows')),
    ('imperial_assault_twin_shadows_campaign_log.pdf', 'Twin Shadows Campaign Log', 'Campaign Log', None,
     ('document-for', 'Twin Shadows')),
    ('return_to_hoth_rules.pdf', 'Return to Hoth Rulebook', 'Rulebook', None, ('contents', 'Return to Hoth')),
    ('return-to-hoth-campaignlog.pdf', 'Return to Hoth Campaign Log', 'Campaign Log', None,
     ('document-for', 'Return to Hoth')),
    ('swi24_rulebook.pdf', 'The Bespin Gambit Rulebook', 'Rulebook', None, ('contents', 'The Bespin Gambit')),
    ('swi24_campaignlog.pdf', 'The Bespin Gambit Campaign Log', 'Campaign Log', None,
     ('document-for', 'The Bespin Gambit')),
    ('jabbas_realm_rulebook.pdf', "Jabba's Realm Rulebook", 'Rulebook', None, ('contents', "Jabba's Realm")),
    ('swi32_campaignlog.pdf', "Jabba's Realm Campaign Log", 'Campaign Log', None, ('document-for', "Jabba's Realm")),
    ('swi46_rulebook_nomissions.pdf', 'Heart of the Empire Rulebook', 'Rulebook', None,
     ('contents', 'Heart of the Empire')),
    ('swi46_campaignguide.pdf', 'Heart of the Empire Campaign Log', 'Campaign Log', None,
     ('document-for', 'Heart of the Empire')),
    ('swi54_rulebook_webcompressed.pdf', 'Tyrants of Lothal Rulebook', 'Rulebook', None,
     ('contents', 'Tyrants of Lothal')),
    ('legends_of_the_alliance_rulebook_8-23-18.pdf', 'Legends of the Alliance Rulebook', 'Rulebook', None,
     ('document-for', 'Legends of the Alliance')),
    ('swi_tournament_regulations_v34.pdf', 'Skirmish Tournament Regulations', 'Tournament Regulations', '3.4', None),
    ('swi_tournament_regulations_v34_text_version.pdf', 'Skirmish Tournament Regulations (Text Version)',
     'Tournament Regulations', '3.4', None),
    ('fantasy_flight_floor_rules.pdf', 'Fantasy Flight Games Floor Rules', 'Organized Play', None, None),
    ('fundamental-event-document_21_final.pdf', 'Fundamental Event Document', 'Organized Play', '2.1', None),
    ('g19ix_prizetracker_ffg.pdf', 'Prize Tracker', 'Organized Play', None, None),
]


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main(originals):
    if (DATA / 'documents.json').exists():
        print('Already migrated.')
        return
    originals = Path(originals)
    assert {f.name for f in originals.glob('*.pdf')} == {entry[0] for entry in LIST}, 'the folder and LIST differ'
    sources = {s['name']: s['id'] for s in load('sources')}
    DOCUMENTS.mkdir(exist_ok=True)
    documents, rows, links = [], [], []
    for file, name, category, version, reaches in LIST:
        shutil.copyfile(originals / file, DOCUMENTS / file)
        document = {'id': str(uuid.uuid4()), 'name': name, 'category': category, 'version': version, 'file': file}
        documents.append(document)
        if reaches and reaches[0] == 'contents':
            rows.append({'source_id': sources[reaches[1]], 'content_type': 'documents', 'content_id': document['id'],
                         'quantity': 1})
        elif reaches:
            links.append({'from_type': 'documents', 'from_id': document['id'], 'to_type': 'sources',
                          'to_id': sources[reaches[1]], 'relation': 'document-for', 'reverse_relation': 'has-document'})
    save('documents', documents)
    save('source-contents', load('source-contents') + rows)
    save('record-links', load('record-links') + links)
    print(f'{len(documents)} documents: {len(rows)} in products, {len(links)} for products.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='originals', required=True, help="imperial-assault-tools' documents/ folder")
    main(parser.parse_args().originals)
