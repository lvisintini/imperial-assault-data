import re
from os import path

from tests.constants import CONTENT_TYPES
from tests.utils import get_data, get_schema


def get_site_js(name):
    with open(path.join(path.dirname(__file__), f'../site/js/{name}'), 'r') as file_object:
        return file_object.read()


def site_types():
    """content type → its entry's source text in types.js."""
    entries = get_site_js('types.js').split("file: '")[1:]
    return {entry.split("'", 1)[0]: entry for entry in entries}


def strings(js_list):
    return re.findall(r"'([^']*)'", js_list)


class TestSite:
    """The data explorer's config (site/js) has to keep up with the data model."""

    def test_types_cover_every_content_type(self):
        files = re.findall(r"file: '([a-z-]+)'", get_site_js('types.js'))
        assert len(files) == len(set(files))
        assert set(files) == set(CONTENT_TYPES.as_list) == set(site_types())

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

    def test_default_sorts_use_schema_fields(self):
        for content_type, entry in site_types().items():
            if 'hidden: true' in entry:
                continue
            sort = re.search(r"sort: \[([^\]]*)\]", entry)
            keys = [key.removeprefix('-') for key in strings(sort.group(1))] if sort else ['name']
            assert set(keys) <= set(get_schema(content_type)['properties']), content_type

    def test_facet_config_uses_schema_fields(self):
        """facets, groups and order in types.js name schema fields, derived facets, or 'source'/'wave' (facets.js)."""
        definitions = get_schema('definitions')['definitions']
        for content_type, entry in site_types().items():
            facets = re.search(r"facets: \[(.*?)\n    \],", entry, re.S)
            derived = {}
            if facets:
                for spec in re.findall(r"\{([^}]*)\}", facets.group(1)):
                    derived[re.search(r"id: '([^']+)'", spec).group(1)] = re.search(r"trait: '([^']+)'", spec).group(1)
                named = strings(re.sub(r"\{[^}]*\}", '', facets.group(1)))
            else:
                named = []
            groups = re.search(r"groups: \[([^\]]*)\]", entry)
            order = re.search(r"order: \{(.*?)\}", entry, re.S)
            fields = set(get_schema(content_type)['properties']) if 'hidden: true' not in entry else set()
            known = fields | set(derived) | {'source', 'wave'}
            assert set(named) <= known, content_type
            assert set(strings(groups.group(1)) if groups else []) <= set(named) | set(derived), content_type
            for field in re.findall(r"(\w+): \[", order.group(1)) if order else []:
                assert field in fields, (content_type, field)
            for trait in derived.values():
                assert trait in definitions['deployment-trait']['enum'], (content_type, trait)

    def test_deployment_affiliation_order_is_the_schema_enum(self):
        entry = site_types()[CONTENT_TYPES.DEPLOYMENT]
        order = re.search(r"affiliation: \[([^\]]*)\]", entry).group(1)
        assert strings(order) == get_schema('definitions')['definitions']['affiliation']['enum']
