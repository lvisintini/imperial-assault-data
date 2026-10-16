import re
from os import path

from tests.constants import CONTENT_TYPES
from tests.utils import get_data, get_schema


def get_site_js(name):
    with open(path.join(path.dirname(__file__), f'../site/js/{name}'), 'r') as file_object:
        return file_object.read()


class TestSite:
    """The data explorer's config (site/js) has to keep up with the data model."""

    def test_types_cover_every_content_type(self):
        files = re.findall(r"\{file: '([a-z-]+)'", get_site_js('types.js'))
        assert len(files) == len(set(files))
        assert set(files) == set(CONTENT_TYPES.as_list)

    def test_foreign_keys_cover_every_id_field(self):
        site_fks = set(re.findall(r"\{child: '([a-z-]+)', field: '(\w+)', parent: '[a-z-]+'\}", get_site_js('relations.js')))
        schema_fks = {
            (content_type, field)
            for content_type in CONTENT_TYPES.as_list
            if content_type != CONTENT_TYPES.SOURCE_CONTENTS
            for field in get_schema(content_type)['properties']
            if field.endswith('_id')
        }
        assert site_fks == schema_fks

    def test_card_back_rules_cover_types_with_several_backs(self):
        block = re.search(r"CARD_BACK_MATCH = \{(.*?)\};", get_site_js('relations.js'), re.S).group(1)
        rules = set(re.findall(r"'([a-z-]+)':", block))
        backs_per_type = {}
        for back in get_data(CONTENT_TYPES.CARD):
            backs_per_type[back['content_type']] = backs_per_type.get(back['content_type'], 0) + 1
        assert {content_type for content_type, n in backs_per_type.items() if n > 1} <= rules
        assert rules <= set(backs_per_type)
