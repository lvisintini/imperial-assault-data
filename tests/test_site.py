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
        """Every uuid field is an FK in FKS, the card back (BACK), or a link of MISSIONS, REWARDS or REQUIREMENTS
        (relations.js)."""
        relations = get_site_js('relations.js')
        site_fks = set(re.findall(r"\{child: '([a-z-]+)', field: '(\w+)', parent: '[a-z-]+'[^}]*\}", relations))
        back = dict(re.findall(r"(\w+): '([^']+)'", re.search(r"export const BACK = \{([^}]*)\}", relations)[1]))
        assert back['parent'] == CONTENT_TYPES.CARD
        site_fks |= {(content_type, back['field']) for content_type in CONTENT_TYPES.as_list
                     if back['field'] in get_schema(content_type)['properties']}
        for name in ('MISSIONS', 'REWARDS', 'REQUIREMENTS'):
            block = re.search(rf"export const {name} = \{{([^}}]*)\}}", relations)[1]
            spec = dict(re.findall(r"(\w+): '([^']+)'", block))
            site_fks |= {(spec['table'], field) for key, field in spec.items() if key in ('id', 'mission', 'source')}
        uuid = get_schema('definitions')['definitions']['uuid']['pattern']

        def references(prop):  # a uuid, or a nullable one
            return prop.get('pattern') == uuid or any(o.get('pattern') == uuid for o in prop.get('oneOf', []))

        schema_fks = {
            (content_type, field)
            for content_type in CONTENT_TYPES.as_list
            if content_type != CONTENT_TYPES.SOURCE_CONTENTS
            for field, prop in get_schema(content_type)['properties'].items()
            if field != 'id' and references(prop)
        }
        assert site_fks == schema_fks

    def test_back_parents_are_the_tests_parents(self):
        """FKS entries with back: 'children' are the parents whose cards share a back (TestCardBacksIntegrity)."""
        from tests.test_integrity import TestCardBacksIntegrity
        children = re.findall(r"\{child: '([a-z-]+)', field: '(\w+)', parent: '[a-z-]+'[^}]*back: 'children'[^}]*\}",
                              get_site_js('relations.js'))
        assert dict(children) == TestCardBacksIntegrity.PARENTS

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

    def test_source_type_order_is_the_schema_enum(self):
        entry = site_types()[CONTENT_TYPES.SOURCE]
        order = re.search(r"type: \[([^\]]*)\]", entry).group(1)
        assert strings(order) == get_schema(CONTENT_TYPES.SOURCE)['properties']['type']['enum']

    def test_mission_kind_order_is_the_schema_enum(self):
        entry = site_types()[CONTENT_TYPES.MISSIONS]
        order = re.search(r"content_type: \[([^\]]*)\]", entry).group(1)
        assert strings(order) == get_schema(CONTENT_TYPES.MISSIONS)['properties']['content_type']['enum']
        assert strings(order) == CONTENT_TYPES.mission_types

    def test_back_thumbnails_have_card_backs(self):
        """Types whose tiles show the card back (thumb: 'back') have a back_id, or cards that share one (back:
        'children' in FKS)."""
        relations = get_site_js('relations.js')
        for content_type, entry in site_types().items():
            if "thumb: 'back'" in entry:
                assert 'back_id' in get_schema(content_type)['properties'] or re.search(
                    rf"parent: '{content_type}'[^}}]*back: 'children'", relations), content_type
