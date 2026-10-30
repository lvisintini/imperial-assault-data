"""2.0.0 migration 17: the Ahsoka Tano and Thrawn packs' rules sheets, which migration 15 didn't have.

They came as PDFs (a scanner's, and a printed one), which imperial-assault-tools' ia sheets rebuilt at 200 DPI like
the other sheets. Each is a Rules Sheet document in its pack's box, as in migration 15.

    uv run python migrations/2.0.0/17_last_rules_sheets.py --from ../imperial-assault-tools/staging/sheets
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
    ('ahsoka-tano-rules-sheet.pdf', 'Ahsoka Tano Rules Sheet', 'Ahsoka Tano'),
    ('thrawn-rules-sheet.pdf', 'Thrawn Rules Sheet', 'Thrawn'),
]


def load(name):
    return json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))


def save(name, records):
    (DATA / f'{name}.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def main(pdfs):
    documents = load('documents')
    if any(d['name'] == LIST[0][1] for d in documents):
        print('Already migrated.')
        return
    pdfs = Path(pdfs)
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
