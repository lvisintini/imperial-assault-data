"""2.0.0 migration 15: the rules sheets in the ally and villain packs and the expansions' skirmish sheets.

Each ally and villain pack has a two-sided rules sheet, and each expansion a skirmish sheet. FFG never published them,
so these are the maintainer's scans (300 DPI), made into 200 DPI PDFs by imperial-assault-tools' ia sheets. Each is a
document of category Rules Sheet ("Han Solo Rules Sheet", "Twin Shadows Skirmish Rules Sheet"), in its product's box: a
source-contents row. They have no version. The Ahsoka Tano and Thrawn packs' sheets aren't scanned yet.

    uv run python migrations/2.0.0/15_rules_sheets.py --from ../imperial-assault-tools/staging/sheets
Running it again changes nothing.
"""
import argparse
import json
import shutil
import uuid
from pathlib import Path

DATA = Path('data')
DOCUMENTS = Path('documents')
CATEGORY = 'Rules Sheet'
# (file, name, product)
LIST = [
    ('agent-blaise-rules-sheet.pdf', 'Agent Blaise Rules Sheet', 'Agent Blaise'),
    ('alliance-rangers-rules-sheet.pdf', 'Alliance Rangers Rules Sheet', 'Alliance Rangers'),
    ('alliance-smuggler-rules-sheet.pdf', 'Alliance Smuggler Rules Sheet', 'Alliance Smuggler'),
    ('bt-1-and-0-0-0-rules-sheet.pdf', 'BT-1 and 0-0-0 Rules Sheet', 'BT-1 and 0-0-0'),
    ('bantha-rider-rules-sheet.pdf', 'Bantha Rider Rules Sheet', 'Bantha Rider'),
    ('boba-fett-rules-sheet.pdf', 'Boba Fett Rules Sheet', 'Boba Fett'),
    ('bossk-rules-sheet.pdf', 'Bossk Rules Sheet', 'Bossk'),
    ('captain-terro-rules-sheet.pdf', 'Captain Terro Rules Sheet', 'Captain Terro'),
    ('chewbacca-rules-sheet.pdf', 'Chewbacca Rules Sheet', 'Chewbacca'),
    ('darth-vader-rules-sheet.pdf', 'Darth Vader Rules Sheet', 'Darth Vader'),
    ('dengar-rules-sheet.pdf', 'Dengar Rules Sheet', 'Dengar'),
    ('echo-base-troopers-rules-sheet.pdf', 'Echo Base Troopers Rules Sheet', 'Echo Base Troopers'),
    ('emperor-palpatine-rules-sheet.pdf', 'Emperor Palpatine Rules Sheet', 'Emperor Palpatine'),
    ('ezra-bridger-and-kanan-jarrus-rules-sheet.pdf', 'Ezra Bridger and Kanan Jarrus Rules Sheet',
     'Ezra Bridger and Kanan Jarrus'),
    ('general-sorin-rules-sheet.pdf', 'General Sorin Rules Sheet', 'General Sorin'),
    ('general-weiss-rules-sheet.pdf', 'General Weiss Rules Sheet', 'General Weiss'),
    ('greedo-rules-sheet.pdf', 'Greedo Rules Sheet', 'Greedo'),
    ('han-solo-rules-sheet.pdf', 'Han Solo Rules Sheet', 'Han Solo'),
    ('heart-of-the-empire-skirmish-rules-sheet.pdf', 'Heart of the Empire Skirmish Rules Sheet', 'Heart of the Empire'),
    ('hera-syndulla-and-c1-10p-rules-sheet.pdf', 'Hera Syndulla and C1-10P Rules Sheet', 'Hera Syndulla and C1-10P'),
    ('hired-guns-rules-sheet.pdf', 'Hired Guns Rules Sheet', 'Hired Guns'),
    ('hondo-ohnaka-rules-sheet.pdf', 'Hondo Ohnaka Rules Sheet', 'Hondo Ohnaka'),
    ('ig-88-rules-sheet.pdf', 'IG-88 Rules Sheet', 'IG-88'),
    ('isb-infiltrators-rules-sheet.pdf', 'ISB Infiltrators Rules Sheet', 'ISB Infiltrators'),
    ('jabba-the-hutt-rules-sheet.pdf', 'Jabba the Hutt Rules Sheet', 'Jabba the Hutt'),
    ('jabbas-realm-skirmish-rules-sheet.pdf', "Jabba's Realm Skirmish Rules Sheet", "Jabba's Realm"),
    ('jawa-scavenger-rules-sheet.pdf', 'Jawa Scavenger Rules Sheet', 'Jawa Scavenger'),
    ('kayn-somos-rules-sheet.pdf', 'Kayn Somos Rules Sheet', 'Kayn Somos'),
    ('lando-calrissian-rules-sheet.pdf', 'Lando Calrissian Rules Sheet', 'Lando Calrissian'),
    ('leia-organa-rules-sheet.pdf', 'Leia Organa Rules Sheet', 'Leia Organa'),
    ('luke-skywalker-rules-sheet.pdf', 'Luke Skywalker Rules Sheet', 'Luke Skywalker'),
    ('luke-skywalker-jedi-knight-rules-sheet.pdf', 'Luke Skywalker, Jedi Knight Rules Sheet',
     'Luke Skywalker, Jedi Knight'),
    ('maul-rules-sheet.pdf', 'Maul Rules Sheet', 'Maul'),
    ('obi-wan-kenobi-rules-sheet.pdf', 'Obi-Wan Kenobi Rules Sheet', 'Obi-Wan Kenobi'),
    ('r2-d2-and-c-3po-rules-sheet.pdf', 'R2-D2 and C-3PO Rules Sheet', 'R2-D2 and C-3PO'),
    ('rebel-saboteurs-rules-sheet.pdf', 'Rebel Saboteurs Rules Sheet', 'Rebel Saboteurs'),
    ('rebel-troopers-rules-sheet.pdf', 'Rebel Troopers Rules Sheet', 'Rebel Troopers'),
    ('return-to-hoth-skirmish-rules-sheet.pdf', 'Return to Hoth Skirmish Rules Sheet', 'Return to Hoth'),
    ('royal-guard-champion-rules-sheet.pdf', 'Royal Guard Champion Rules Sheet', 'Royal Guard Champion'),
    ('sabine-wren-and-zeb-orrelios-rules-sheet.pdf', 'Sabine Wren and Zeb Orrelios Rules Sheet',
     'Sabine Wren and Zeb Orrelios'),
    ('stormtroopers-rules-sheet.pdf', 'Stormtroopers Rules Sheet', 'Stormtroopers'),
    ('the-bespin-gambit-skirmish-rules-sheet.pdf', 'The Bespin Gambit Skirmish Rules Sheet', 'The Bespin Gambit'),
    ('the-grand-inquisitor-rules-sheet.pdf', 'The Grand Inquisitor Rules Sheet', 'The Grand Inquisitor'),
    ('twin-shadows-skirmish-rules-sheet.pdf', 'Twin Shadows Skirmish Rules Sheet', 'Twin Shadows'),
    ('tyrants-of-lothal-skirmish-rules-sheet.pdf', 'Tyrants of Lothal Skirmish Rules Sheet', 'Tyrants of Lothal'),
    ('wookiee-warriors-rules-sheet.pdf', 'Wookiee Warriors Rules Sheet', 'Wookiee Warriors'),
]


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main(pdfs):
    documents = load('documents')
    if any(d['category'] == CATEGORY for d in documents):
        print('Already migrated.')
        return
    pdfs = Path(pdfs)
    assert {f.name for f in pdfs.glob('*.pdf')} == {file for file, _, _ in LIST}, 'the folder and LIST differ'
    sources = {s['name']: s['id'] for s in load('sources')}
    rows = []
    for file, name, product in LIST:
        shutil.copyfile(pdfs / file, DOCUMENTS / file)
        document = {'id': str(uuid.uuid4()), 'name': name, 'category': CATEGORY, 'version': None, 'file': file}
        documents.append(document)
        rows.append({'source_id': sources[product], 'content_type': 'documents', 'content_id': document['id'],
                     'quantity': 1})
    save('documents', documents)
    save('source-contents', load('source-contents') + rows)
    print(f'{len(rows)} rules sheets, each in its product.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='pdfs', required=True, help="imperial-assault-tools' staging/sheets folder")
    main(parser.parse_args().pdfs)
