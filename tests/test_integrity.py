import json
import os
import re
import unicodedata
from os import path
from pathlib import Path

import pytest

from tests.constants import CONTENT_TYPES, DEPLOYMENT_TRAITS, GAME_MODES, BUFF_TYPES
from tests.utils import get_data, get_data_for, get_schema, flatten_list
from collections import Counter


class TestIntegrity:

    @staticmethod
    def fetch_fk_data(data, fk_id):
        return next(iter([d for d in data if d["id"] == fk_id]), None)

    @pytest.mark.parametrize("content_type", list(set(CONTENT_TYPES.as_list).difference(CONTENT_TYPES.without_ids)))
    def test_ids_are_unique(self, content_type):
        """Ids are UUIDs (the schemas check the format); within a file they must not repeat."""
        ids = [d["id"] for d in get_data(content_type)]
        duplicates = [i for i, count in Counter(ids).items() if count > 1]
        assert not duplicates, duplicates

    def test_ids_are_unique_across_files(self, all_data):
        ids = [d["id"] for name, data in all_data.items() if name not in CONTENT_TYPES.without_ids for d in data]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("source_contents_entry", get_data(CONTENT_TYPES.SOURCE_CONTENTS))
    def test_source_contents_foreign_keys(self, source_contents_entry, all_data):
        fk_content_type_data = all_data.get(source_contents_entry["content_type"])

        assert fk_content_type_data is not None
        assert source_contents_entry["content_id"] != source_contents_entry["source_id"]  # a product isn't in itself
        assert self.fetch_fk_data(fk_content_type_data, source_contents_entry["content_id"]) is not None
        assert self.fetch_fk_data(all_data[CONTENT_TYPES.SOURCE], source_contents_entry["source_id"]) is not None

    @pytest.mark.parametrize("agenda_card_entry", get_data(CONTENT_TYPES.AGENDA))
    def test_agenda_deck_foreign_keys(self, agenda_card_entry, agenda_decks):
        assert self.fetch_fk_data(agenda_decks, agenda_card_entry["agenda_id"]) is not None

    @pytest.mark.parametrize("hero_class_card_entry", get_data(CONTENT_TYPES.HERO_CLASS))
    def test_hero_class_cards_foreign_keys(self, hero_class_card_entry, heroes):
        assert self.fetch_fk_data(heroes, hero_class_card_entry["hero_id"]) is not None

    @pytest.mark.parametrize("imperial_class_card_entry", get_data(CONTENT_TYPES.IMPERIAL_CLASS_CARD))
    def test_imperial_class_cards_foreign_keys(self, imperial_class_card_entry, imperial_classes):
        assert self.fetch_fk_data(imperial_classes, imperial_class_card_entry["class_id"]) is not None


class TestCardBacksIntegrity:
    """Every card points at its back (card-backs) through back_id (docs/data-model.md → Card backs)."""

    # Records with an image but no back: products, maps, the backs themselves, heroes (their backs are on their class
    # cards) and map tiles (a tile's back is its other side).
    NO_BACK = [CONTENT_TYPES.SOURCE, CONTENT_TYPES.MAP, CONTENT_TYPES.CARD, CONTENT_TYPES.HERO, CONTENT_TYPES.MAP_TILES]
    # A child type's cards share their parent's back.
    PARENTS = {CONTENT_TYPES.HERO_CLASS: 'hero_id', CONTENT_TYPES.IMPERIAL_CLASS_CARD: 'class_id',
               CONTENT_TYPES.AGENDA: 'agenda_id'}

    @staticmethod
    def card_types():
        return [t for t in CONTENT_TYPES.as_list if 'back_id' in get_schema(t)['properties']]

    def test_every_type_with_images_has_backs_but_the_exceptions(self):
        imaged = [t for t in CONTENT_TYPES.as_list
                  if set(get_schema(t)['properties']) & {'image', 'healthy', 'side_a'} and t not in self.NO_BACK]
        assert sorted(imaged) == sorted(self.card_types())

    def test_back_ids_resolve_and_every_back_is_used(self):
        backs = {b['id'] for b in get_data(CONTENT_TYPES.CARD)}
        used = {r['back_id'] for t in self.card_types() for r in get_data(t) if r['back_id']}
        assert used - backs == set()
        assert backs - used == set()

    @pytest.mark.parametrize("content_type", list(PARENTS))
    def test_a_parents_cards_share_a_back(self, content_type):
        backs = {}
        for card in get_data(content_type):
            backs.setdefault(card[self.PARENTS[content_type]], set()).add(card['back_id'])
        assert {parent: ids for parent, ids in backs.items() if len(ids) > 1} == {}

    def test_only_story_missions_without_a_card_have_no_back(self):
        """A story mission without a card (no image) has no back, and every other card has one."""
        for content_type in self.card_types():
            for record in get_data(content_type):
                if content_type == CONTENT_TYPES.STORY_MISSION:
                    assert (record['image'] is None) == (record['back_id'] is None), record['name']
                else:
                    assert record['back_id'] is not None, (content_type, record['id'])

    def test_back_names_are_unique(self):
        names = [b['name'] for b in get_data(CONTENT_TYPES.CARD)]
        assert len(names) == len(set(names))


class TestSourcesIntegrity:
    # Copies per content type in the Core Set's own rows, as FFG's component list counts them (Learn to Play, p. 3),
    # less what the dataset keeps elsewhere: the Luke Skywalker and Darth Vader deployment cards are on their packs
    # (FFG counts 39).
    CORE_SET_COPIES = {
        CONTENT_TYPES.DEPLOYMENT: 37, CONTENT_TYPES.COMMAND: 42, CONTENT_TYPES.REWARD: 18, CONTENT_TYPES.UPGRADE: 36,
        CONTENT_TYPES.SUPPLY: 12, CONTENT_TYPES.CONDITION: 12, 'side missions': 14,
    }

    def test_miniatures_are_told_apart(self):
        """Sculpts that share a name have different descriptions."""
        names = Counter((m['name'], m['description']) for m in get_data(CONTENT_TYPES.MINIATURES))
        assert [name for name, count in names.items() if count > 1] == []

    def test_every_miniature_is_in_a_product(self):
        listed = {r['content_id'] for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)
                  if r['content_type'] == CONTENT_TYPES.MINIATURES}
        assert {m['name'] for m in get_data(CONTENT_TYPES.MINIATURES) if m['id'] not in listed} == set()

    def test_core_set_copies_match_ffgs_component_list(self):
        core = next(s['id'] for s in get_data(CONTENT_TYPES.SOURCE) if s['name'] == 'Imperial Assault')
        missions = {m['id']: m['content_type'] for m in get_data(CONTENT_TYPES.MISSIONS)}
        copies = Counter()
        for row in get_data(CONTENT_TYPES.SOURCE_CONTENTS):
            if row['source_id'] == core:
                content_type = missions.get(row['content_id'], row['content_type'])
                copies['side missions' if 'side-mission' in content_type else content_type] += row['quantity']
        assert {key: copies[key] for key in self.CORE_SET_COPIES} == self.CORE_SET_COPIES

    def test_no_duplicate_product_codes(self):
        codes = [s['product_code'] for s in get_data(CONTENT_TYPES.SOURCE) if s['product_code'] is not None]
        duplicates = [code for code, count in Counter(codes).items() if count > 1]
        if duplicates:
            pytest.fail(f"The following product codes are duplicated: {', '.join(duplicates)}")

    @pytest.mark.parametrize("entry", [
        s for s in get_data(CONTENT_TYPES.SOURCE) if s['announced_date'] and s['release_date']
    ], ids=lambda s: s['name'])
    def test_release_date_is_not_before_announced_date(self, entry):
        assert entry['release_date'] >= entry['announced_date']

    @staticmethod
    def inside():
        """(container id, product id) for every product that ships inside another (a source-contents row to a source)."""
        return [(r['source_id'], r['content_id']) for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)
                if r['content_type'] == CONTENT_TYPES.SOURCE]

    def test_products_inside_products_are_one_level_deep(self):
        """A pack ships inside a box, not inside another pack, and in one box only."""
        inside = self.inside()
        packs = [pack for _, pack in inside]
        assert len(packs) == len(set(packs))
        assert not {container for container, _ in inside} & set(packs)

    def test_included_products_dont_repeat_their_containers_contents(self):
        """A pack's contents are listed once, on the pack; the box that includes it gets them through the pack."""
        contents = {}
        for row in get_data(CONTENT_TYPES.SOURCE_CONTENTS):
            contents.setdefault(row['source_id'], set()).add((row['content_type'], row['content_id']))
        for container, pack in self.inside():
            shared = contents.get(pack, set()) & contents.get(container, set())
            assert not shared, (pack, shared)


class TestDocumentsIntegrity:
    """Every document's PDF is in documents/, and every PDF there is a document's."""

    def test_files_exist_and_none_is_orphaned(self):
        folder = path.join(path.dirname(__file__), '../documents')
        files = [d['file'] for d in get_data(CONTENT_TYPES.DOCUMENTS)]
        assert len(files) == len(set(files))
        assert set(files) == set(os.listdir(folder))

    def test_names_are_unique(self):
        names = [d['name'] for d in get_data(CONTENT_TYPES.DOCUMENTS)]
        assert len(names) == len(set(names))

    def test_every_pack_and_expansion_has_its_rules_sheet(self):
        sheets = {d['id'] for d in get_data(CONTENT_TYPES.DOCUMENTS) if d['category'] == 'Rules Sheet'}
        boxes = Counter(r['source_id'] for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)
                        if r['content_type'] == CONTENT_TYPES.DOCUMENTS and r['content_id'] in sheets)
        for source in get_data(CONTENT_TYPES.SOURCE):
            expected = 1 if source['type'] in ('Ally Pack', 'Villain Pack', 'Expansion') else 0
            assert boxes[source['id']] == expected, source['name']


class TestRecordLinksIntegrity:
    """record-links (docs/data-model.md → Record links). The schema ties each relation to its reverse and the types
    it links; these check the records."""

    @pytest.mark.parametrize("link", get_data(CONTENT_TYPES.RECORD_LINKS))
    def test_links_resolve(self, link, all_data):
        assert link['from_id'] != link['to_id']  # nothing links to itself
        assert TestIntegrity.fetch_fk_data(all_data[link['from_type']], link['from_id']) is not None
        assert TestIntegrity.fetch_fk_data(all_data[link['to_type']], link['to_id']) is not None

    def test_links_dont_repeat(self):
        links = [(link['from_id'], link['to_id'], link['relation']) for link in get_data(CONTENT_TYPES.RECORD_LINKS)]
        assert len(links) == len(set(links))

    def test_the_schema_rejects_improper_pairs(self):
        from jsonschema import Draft4Validator
        validator = Draft4Validator(get_schema(CONTENT_TYPES.RECORD_LINKS))
        link = {'from_type': CONTENT_TYPES.MINIATURES, 'from_id': '00000000-0000-4000-8000-000000000000',
                'to_type': CONTENT_TYPES.HERO, 'to_id': '00000000-0000-4000-8000-000000000001',
                'relation': 'figure-of', 'reverse_relation': 'has-figure'}
        assert validator.is_valid(link)
        assert not validator.is_valid(link | {'reverse_relation': 'required-by'})  # another relation's reverse
        assert not validator.is_valid(link | {'from_type': CONTENT_TYPES.SOURCE})   # a type figure-of doesn't link
        assert not validator.is_valid(link | {'relation': 'requires', 'reverse_relation': 'required-by'})  # to a hero
        assert not validator.is_valid(link | {'relation': 'elite-of', 'reverse_relation': 'regular-of'})  # a miniature

    @staticmethod
    def linked(relation):
        return {(link['from_id'], link['to_id']) for link in get_data(CONTENT_TYPES.RECORD_LINKS)
                if link['relation'] == relation}

    @staticmethod
    def same_card(a, b):
        return (a['name'], a['description'], a['affiliation']) == (b['name'], b['description'], b['affiliation'])

    def test_forms_are_of_the_cards_their_images_name(self):
        """A form card is a form of every deployment card its image is named after (form-cards/<card>-<form>.png)."""
        cards = get_data(CONTENT_TYPES.DEPLOYMENT)
        slug = lambda *parts: re.sub(r'[^a-z0-9]+', '-', ' '.join(parts).lower()).strip('-')
        expected = {(form['id'], card['id']) for form in get_data(CONTENT_TYPES.FORM_CARDS) for card in cards
                    if form['image'] == f"{CONTENT_TYPES.FORM_CARDS}/{slug(card['name'], form['name'])}.png"}
        assert {form for form, _ in expected} == {form['id'] for form in get_data(CONTENT_TYPES.FORM_CARDS)}
        assert self.linked('form-of') == expected

    def test_elite_cards_are_of_their_regular_cards(self):
        """elite-of links an elite card to each regular card of the same name, description and affiliation whose
        modes overlap its own."""
        cards = get_data(CONTENT_TYPES.DEPLOYMENT)
        assert self.linked('elite-of') == {
            (elite['id'], regular['id']) for elite in cards if elite['elite'] for regular in cards
            if not regular['elite'] and self.same_card(elite, regular) and set(elite['modes']) & set(regular['modes'])}

    def test_campaign_cards_are_of_their_skirmish_twins(self):
        """campaign-of links every Campaign-only card to its one Skirmish-only twin (same name, description,
        affiliation and elite)."""
        cards = get_data(CONTENT_TYPES.DEPLOYMENT)
        expected = {(campaign['id'], skirmish['id']) for campaign in cards if campaign['modes'] == ['Campaign']
                    for skirmish in cards if skirmish['modes'] == ['Skirmish'] and self.same_card(campaign, skirmish)
                    and campaign['elite'] == skirmish['elite']}
        assert self.linked('campaign-of') == expected
        assert sorted(campaign for campaign, _ in expected) == sorted(
            c['id'] for c in cards if c['modes'] == ['Campaign'])

    def test_every_figure_has_a_miniature(self):
        """Every hero, and every deployment card but skirmish upgrades, has a miniature; every miniature stands for
        something."""
        figures = [link for link in get_data(CONTENT_TYPES.RECORD_LINKS) if link['relation'] == 'figure-of']
        linked = {link['to_id'] for link in figures}
        cards = [c for c in get_data(CONTENT_TYPES.DEPLOYMENT) if 'Skirmish Upgrade' not in (c['traits'] or [])]
        assert [r['name'] for r in cards + get_data(CONTENT_TYPES.HERO) if r['id'] not in linked] == []
        assert {m['id'] for m in get_data(CONTENT_TYPES.MINIATURES)} == {link['from_id'] for link in figures}


class TestMissionsIntegrity:
    """missions.json indexes every mission; products and rewards attach to its rows (docs/data-model.md)."""

    @staticmethod
    def mission_records():
        return [(content_type, record) for content_type in CONTENT_TYPES.mission_types
                for record in get_data(content_type)
                if content_type != CONTENT_TYPES.AGENDA or record['mission']]

    def test_every_mission_is_indexed_once(self):
        indexed = Counter((m['content_type'], m['content_id']) for m in get_data(CONTENT_TYPES.MISSIONS))
        assert indexed == Counter((content_type, r['id']) for content_type, r in self.mission_records())

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.MISSIONS), ids=lambda m: m['id'])
    def test_index_rows_resolve(self, entry, all_data):
        record = TestIntegrity.fetch_fk_data(all_data[entry['content_type']], entry['content_id'])
        assert record is not None
        assert entry['content_type'] != CONTENT_TYPES.AGENDA or record['mission']
        assert entry['map_id'] is None or TestIntegrity.fetch_fk_data(all_data[CONTENT_TYPES.MAP], entry['map_id'])

    def test_missions_reach_products_only_through_the_index(self):
        linked = {r['content_type'] for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)}
        assert not linked & set(CONTENT_TYPES.mission_types)

    def test_agenda_missions_have_their_decks_products(self):
        products = {}
        for row in get_data(CONTENT_TYPES.SOURCE_CONTENTS):
            products.setdefault(row['content_id'], set()).add(row['source_id'])
        cards = {c['id']: c for c in get_data(CONTENT_TYPES.AGENDA)}
        for mission in get_data(CONTENT_TYPES.MISSIONS):
            if mission['content_type'] == CONTENT_TYPES.AGENDA:
                deck = cards[mission['content_id']]['agenda_id']
                assert products.get(mission['id']) == products.get(deck), cards[mission['content_id']]['name']

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.HERO_SIDE_MISSION), ids=lambda m: m['name'])
    def test_hero_side_missions_heroes_resolve(self, entry, heroes):
        assert TestIntegrity.fetch_fk_data(heroes, entry['hero_id']) is not None

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.MISSION_REWARDS))
    def test_mission_rewards_resolve(self, entry, all_data):
        assert TestIntegrity.fetch_fk_data(all_data[CONTENT_TYPES.MISSIONS], entry['mission_id']) is not None
        if entry['credits']:
            assert entry['content_type'] is None and entry['content_id'] is None
        else:
            assert entry['content_type'] not in (None, CONTENT_TYPES.MISSIONS, CONTENT_TYPES.MISSION_REWARDS)
            assert TestIntegrity.fetch_fk_data(all_data[entry['content_type']], entry['content_id']) is not None

    def test_mission_rewards_dont_repeat(self):
        rows = [(r['mission_id'], r['content_type'], r['content_id'], r['credits'])
                for r in get_data(CONTENT_TYPES.MISSION_REWARDS)]
        assert len(rows) == len(set(rows))

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.EPILOGUE), ids=lambda e: e['name'])
    def test_epilogues_missions_resolve(self, entry, all_data):
        assert TestIntegrity.fetch_fk_data(all_data[CONTENT_TYPES.MISSIONS], entry['mission_id']) is not None

    def test_a_skirmish_maps_cards_are_scenarios_a_and_b(self):
        scenarios = {c['id']: c['scenario'] for c in get_data(CONTENT_TYPES.SKIRMISH_MISSION)}
        by_map = {}
        for mission in get_data(CONTENT_TYPES.MISSIONS):
            if mission['content_id'] in scenarios:
                by_map.setdefault(mission['map_id'], []).append(scenarios[mission['content_id']])
        assert {map_id: s for map_id, s in by_map.items() if sorted(s) != ['A', 'B']} == {}

    def test_a_missions_location_is_a_book_page_or_rules_sheet_in_its_product(self):
        """Campaign and agenda missions say where their rules are: a rulebook in their product's box (the Core Set's
        Campaign Guide, an expansion's rulebook) with a page, or a pack's rules sheet; skirmish and raid missions
        don't."""
        sources = {s['id']: s for s in get_data(CONTENT_TYPES.SOURCE)}
        documents = {d['id']: d for d in get_data(CONTENT_TYPES.DOCUMENTS)}
        products, books = {}, {}
        for row in get_data(CONTENT_TYPES.SOURCE_CONTENTS):
            products.setdefault(row['content_id'], []).append(sources[row['source_id']])
            if row['content_type'] == CONTENT_TYPES.DOCUMENTS:
                document = documents[row['content_id']]
                books.setdefault(row['source_id'], {})[document['name']] = document['category']
        wrong = []
        for mission in get_data(CONTENT_TYPES.MISSIONS):
            location = mission['location']
            if mission['content_type'] in (CONTENT_TYPES.SKIRMISH_MISSION, CONTENT_TYPES.RAID_MISSION):
                ok = location is None
            else:
                (product,) = products[mission['id']]
                book, _, page = (location or '').partition(', page ')
                category = books.get(product['id'], {}).get(book)
                ok = (category == 'Rulebook' and page.isdigit()) if page else category == 'Rules Sheet'
            if not ok:
                wrong.append((mission['id'], location))
        assert wrong == []

    def test_every_mission_has_a_map(self):
        assert [m['id'] for m in get_data(CONTENT_TYPES.MISSIONS) if not m['map_id']] == []

    def test_maps_are_named_once(self):
        names = [m['name'] for m in get_data(CONTENT_TYPES.MAP)]
        assert len(names) == len(set(names))

    def test_maps_reach_products_through_their_missions(self):
        """Every map is used by a mission and is in its missions' products, so it has no source-contents rows of its
        own, except from a Skirmish Map Mat."""
        mats = {s['id'] for s in get_data(CONTENT_TYPES.SOURCE) if s['type'] == 'Skirmish Map Mat'}
        used = {m['map_id'] for m in get_data(CONTENT_TYPES.MISSIONS) if m['map_id']}
        direct = {r['content_id'] for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)
                  if r['content_type'] == CONTENT_TYPES.MAP and r['source_id'] not in mats}
        assert direct == set()
        assert {m['id'] for m in get_data(CONTENT_TYPES.MAP)} == used

    def test_a_skirmish_map_mat_is_one_skirmish_map(self):
        """A mat holds exactly one map, used by skirmish missions, and no two mats hold the same map."""
        mats = {s['id'] for s in get_data(CONTENT_TYPES.SOURCE) if s['type'] == 'Skirmish Map Mat'}
        rows = [r for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS) if r['source_id'] in mats]
        skirmish = {m['map_id'] for m in get_data(CONTENT_TYPES.MISSIONS)
                    if m['content_type'] == CONTENT_TYPES.SKIRMISH_MISSION}
        assert mats and sorted(r['source_id'] for r in rows) == sorted(mats)
        assert all(r['content_type'] == CONTENT_TYPES.MAP and r['quantity'] == 1 for r in rows)
        assert {r['content_id'] for r in rows} <= skirmish and len({r['content_id'] for r in rows}) == len(rows)

    def test_a_choice_has_alternatives(self):
        """Rows with choice: true are a pick-one group, so a mission has none or at least two."""
        choices = Counter(r['mission_id'] for r in get_data(CONTENT_TYPES.MISSION_REWARDS) if r['choice'])
        assert all(count >= 2 for count in choices.values())


class TestMapTilesIntegrity:
    """Map tiles and the tile sides each map is built from (docs/data-model.md → Maps and map tiles)."""

    def test_tiles_are_named_once_and_in_a_product(self):
        tiles = get_data(CONTENT_TYPES.MAP_TILES)
        names = [t['name'] for t in tiles]
        assert len(names) == len(set(names))
        in_products = {r['content_id'] for r in get_data(CONTENT_TYPES.SOURCE_CONTENTS)
                       if r['content_type'] == CONTENT_TYPES.MAP_TILES}
        assert [t['name'] for t in tiles if t['id'] not in in_products] == []

    @staticmethod
    def grid_of(image_path):
        """(width, height, squares) of a tile side's image: 64 px per square inside the tab margins, a square counted
        when the tile is at its centre."""
        from PIL import Image
        with Image.open(Path('images', 'large', image_path)) as image:
            alpha = image.convert('RGBA').getchannel('A')
        width, height = alpha.width // 64, alpha.height // 64
        x0, y0 = (alpha.width - width * 64) // 2, (alpha.height - height * 64) // 2
        squares = sum(alpha.getpixel((x0 + i * 64 + 32, y0 + j * 64 + 32)) > 127
                      for i in range(width) for j in range(height))
        return width, height, squares

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.MAP_TILES), ids=lambda t: t['name'])
    def test_a_tiles_squares_and_grid_are_its_images(self, entry):
        """squares, width and height are side A's image's; side B has as many squares, its image the same size or
        turned a quarter."""
        a, b = self.grid_of(entry['side_a']), self.grid_of(entry['side_b'])
        assert a == (entry['width'], entry['height'], entry['squares'])
        assert b in (a, (a[1], a[0], a[2]))

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.MAP_LAYOUTS))
    def test_layouts_resolve(self, entry, all_data):
        assert TestIntegrity.fetch_fk_data(all_data[CONTENT_TYPES.MAP], entry['map_id']) is not None
        assert TestIntegrity.fetch_fk_data(all_data[CONTENT_TYPES.MAP_TILES], entry['tile_id']) is not None

    def test_every_map_has_a_layout(self):
        laid_out = {r['map_id'] for r in get_data(CONTENT_TYPES.MAP_LAYOUTS)}
        assert [m['name'] for m in get_data(CONTENT_TYPES.MAP) if m['id'] not in laid_out] == []

    def test_layouts_dont_repeat(self):
        rows = [(r['map_id'], r['tile_id'], r['side']) for r in get_data(CONTENT_TYPES.MAP_LAYOUTS)]
        assert len(rows) == len(set(rows))

    @staticmethod
    def product_codes():
        """{source id: (product code, 0)}; a product without a code sorts right after the last coded product released
        on or before it: (that code, 1). The Luke and Vader packs follow the Core Set."""
        sources = get_data(CONTENT_TYPES.SOURCE)
        coded = sorted((s['release_date'] or '9999', s['product_code']) for s in sources if s['product_code'])
        codes = {}
        for s in sources:
            if s['product_code']:
                codes[s['id']] = (s['product_code'], 0)
            else:
                before = [code for date, code in coded if date <= (s['release_date'] or '9999')]
                codes[s['id']] = (before[-1] if before else '', 1)
        return codes

    @staticmethod
    def products_of(content_type):
        codes = TestMapTilesIntegrity.product_codes()
        found = {}
        for row in get_data(CONTENT_TYPES.SOURCE_CONTENTS):
            if row['content_type'] == content_type:
                found.setdefault(row['content_id'], []).append(codes[row['source_id']])
        return found

    def test_tiles_are_in_product_code_and_number_order(self):
        products = self.products_of(CONTENT_TYPES.MAP_TILES)
        keys = [(min(products[t['id']]), t['number']) for t in get_data(CONTENT_TYPES.MAP_TILES)]
        assert keys == sorted(keys)

    def test_layouts_are_in_order(self):
        """By the map's mission product (its missions' earliest product code), the map's name, then the tile's product
        code descending, its number and the side."""
        missions = self.products_of(CONTENT_TYPES.MISSIONS)
        first = {}
        for mission in get_data(CONTENT_TYPES.MISSIONS):
            if mission['map_id'] and mission['id'] in missions:
                first.setdefault(mission['map_id'], []).extend(missions[mission['id']])
        names = {m['id']: m['name'].casefold() for m in get_data(CONTENT_TYPES.MAP)}
        tile_products = self.products_of(CONTENT_TYPES.MAP_TILES)
        codes = sorted({c for found in tile_products.values() for c, _ in found}, reverse=True)
        tiles = {t['id']: (codes.index(min(c for c, _ in tile_products[t['id']])), t['number'])
                 for t in get_data(CONTENT_TYPES.MAP_TILES)}
        keys = [(min(first[r['map_id']]), names[r['map_id']], *tiles[r['tile_id']], r['side'])
                for r in get_data(CONTENT_TYPES.MAP_LAYOUTS)]
        assert keys == sorted(keys)

    @staticmethod
    def sections():
        """{map id: [None, then its hidden sections' names in order]}: the images a map's placements are on."""
        return {m['id']: [None] + [h['name'] for h in m['hidden_sections']] for m in get_data(CONTENT_TYPES.MAP)}

    def test_a_map_has_a_whole_image_when_it_has_hidden_sections(self):
        maps = get_data(CONTENT_TYPES.MAP)
        assert [m['name'] for m in maps if bool(m['whole_image']) != bool(m['hidden_sections'])] == []

    def test_placements_are_on_the_maps_images(self):
        sections = self.sections()
        wrong = [(r['map_id'], p['section']) for r in get_data(CONTENT_TYPES.MAP_LAYOUTS) for p in r['placements']
                 if p['section'] not in sections[r['map_id']]]
        assert wrong == []
        used = {(r['map_id'], p['section']) for r in get_data(CONTENT_TYPES.MAP_LAYOUTS) for p in r['placements']}
        assert [(m, s) for m, names in sections.items() for s in names if (m, s) not in used] == []

    def test_placements_are_sorted_and_dont_repeat(self):
        sections = self.sections()
        for row in get_data(CONTENT_TYPES.MAP_LAYOUTS):
            keys = [(sections[row['map_id']].index(p['section']), p['y'], p['x']) for p in row['placements']]
            assert keys == sorted(keys) and len(keys) == len(set(keys)), row

    def test_each_maps_frame_starts_at_0_0(self):
        frames = {}
        for row in get_data(CONTENT_TYPES.MAP_LAYOUTS):
            for p in row['placements']:
                x, y = frames.get(row['map_id'], (p['x'], p['y']))
                frames[row['map_id']] = (min(x, p['x']), min(y, p['y']))
        assert {m: f for m, f in frames.items() if f != (0, 0)} == {}

    def test_every_copy_is_placed_and_no_image_places_more_than_the_copies(self):
        """A tile a hidden section reuses is placed more often than count, but never more than count times on one
        image (the map's, or one hidden section's)."""
        names = {m['id']: m['name'] for m in get_data(CONTENT_TYPES.MAP)}
        tiles = {t['id']: t['name'] for t in get_data(CONTENT_TYPES.MAP_TILES)}
        wrong = []
        for row in get_data(CONTENT_TYPES.MAP_LAYOUTS):
            label = f"{names[row['map_id']]}: {tiles[row['tile_id']]}{row['side']} x{row['count']}"
            if len(row['placements']) < row['count']:
                wrong.append(f"{label}, placed {len(row['placements'])} times")
            for section, n in Counter(p['section'] for p in row['placements']).items():
                if n > row['count']:
                    wrong.append(f'{label}, placed {n} times on {section or "the map"}')
        assert wrong == []

    def test_skirmish_and_raid_maps_place_each_copy_once(self):
        maps = {m['map_id'] for m in get_data(CONTENT_TYPES.MISSIONS)
                if m["content_type"] in (CONTENT_TYPES.SKIRMISH_MISSION, CONTENT_TYPES.RAID_MISSION)}
        assert [r for r in get_data(CONTENT_TYPES.MAP_LAYOUTS)
                if r['map_id'] in maps and len(r['placements']) != r['count']] == []


class TestDeploymentsIntegrity:
    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_have_skirmish_game_mode_only(self, entry):
        assert entry['modes'] == [GAME_MODES.SKIRMISH, ]

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_do_not_have_health(self, entry):
        assert entry['health'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_do_not_have_speed(self, entry):
        assert entry['speed'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_do_not_have_deployment_group(self, entry):
        assert entry['deployment_group'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_do_not_have_reinforce_cost(self, entry):
        assert entry['reinforce_cost'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if d['deployment_group'] is not None
    ])
    def test_reinforce_cost_only_available_if_appropriate(self, entry):
        if entry['deployment_group'] > 1:
            assert entry['reinforce_cost'] is not None
            assert entry['reinforce_cost'] > 0
        else:
            assert entry['reinforce_cost'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT)
        if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE not in d['traits'] and d['unique']
    ])
    def test_unique_deployment_does_not_have_a_reinforce_cost(self, entry):
        assert entry['reinforce_cost'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT)
        if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE not in d['traits'] and d['unique']
    ])
    def test_unique_deployment_have_a_deployment_group_of_1(self, entry):
        assert entry['deployment_group'] == 1

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if d['deployment_group'] is not None and d['deployment_group'] > 1
    ])
    def test_deployment_has_reinforce_cost_if_deployment_group(self, entry):
        assert entry['reinforce_cost'] > 0

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if d['reinforce_cost'] is not None and d['reinforce_cost'] > 1
    ])
    def test_deployment_has_deployment_group_if_reinforce_cost(self, entry):
        assert entry['deployment_group'] > 1


class TestHeroClassCardIntegrity:
    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.HERO_CLASS) if d['type'] == BUFF_TYPES.FEAT
    ])
    def test_feat_has_no_traits(self, entry):
        assert entry['traits'] is None


class TestRewardIntegrity:

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.REWARD) if d['type'] in (BUFF_TYPES.FEAT, BUFF_TYPES.GROUP_ATTACHMENT)
    ])
    def test_feat_has_no_traits(self, entry):
        assert entry['traits'] is None

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.REWARD) if d['type'] == BUFF_TYPES.GROUP_ATTACHMENT
    ], ids=lambda r: r['name'])
    def test_group_attachments_are_for_the_imperial_player(self, entry):
        assert entry['for'] == 'Imperial player'

    @pytest.mark.parametrize("entry", get_data(CONTENT_TYPES.REWARD), ids=lambda r: r['name'])
    def test_boons_are_for_the_rebels_and_banes_for_the_imperial_player(self, entry):
        assert entry['for'] == {'Boon': 'Rebel players', 'Bane': 'Imperial player'}.get(entry['class'], entry['for'])

    def test_agenda_missions_reward_the_imperial_player(self):
        agenda = {m['id'] for m in get_data(CONTENT_TYPES.MISSIONS) if m['content_type'] == CONTENT_TYPES.AGENDA}
        rewards = {r['id']: r for r in get_data(CONTENT_TYPES.REWARD)}
        given = {r['content_id'] for r in get_data(CONTENT_TYPES.MISSION_REWARDS)
                 if r['mission_id'] in agenda and r['content_type'] == CONTENT_TYPES.REWARD}
        assert given and all(rewards[i]['for'] == 'Imperial player' for i in given)


class TestCanonicalNames:
    def test_no_duplicate_iaspec_names(self):
        canonical_names = [
            m['iaspec']
            for m in flatten_list(
                get_data_for(
                    CONTENT_TYPES.DEPLOYMENT, CONTENT_TYPES.COMMAND, CONTENT_TYPES.COMPANION
                ).values()
            )
        ]

        Counter(canonical_names)

        duplicates = [item for item, count in Counter(canonical_names).items() if count > 1]

        if duplicates:
            pytest.fail(f"The following canonical names are duplicated: {', '.join(duplicates)}")

    # How iaspec values are built (docs/data-model.md, iaspec): elite + name, then, only while another card would get
    # the same value, name plus one of mode, affiliation or description. `elite` only when a regular card of the same
    # name exists, and of a Campaign and a Skirmish twin only the Campaign card adds its mode: the IA Skirmish
    # Specification's practice. imperial-assault-tools suggests them with the same rule.
    IASPEC_STRATEGIES = [('elite', 'name'), ('elite', 'name', 'modes'), ('elite', 'name', 'affiliation'),
                         ('elite', 'name', 'description')]
    IASPEC_RECORDS = flatten_list(get_data_for(
        CONTENT_TYPES.DEPLOYMENT, CONTENT_TYPES.COMMAND, CONTENT_TYPES.COMPANION
    ).values())
    # The spec's own spellings of cards the rule would spell otherwise: a key keeps them to interoperate.
    SPEC_SPELLINGS = {
        'furyofkashyyyk': 'furyofkashyyk',
        'sarlaccsweep': 'sarlacsweep',
        'temporaryallianceimperial': 'temporaryallianceempire',
        'temporaryalliancemercenary': 'tempoaryalliancescum',
        'lukeskywalkerherooftherebellion': 'lukeskywalker',
        'lukeskywalkerjediknight': 'lukeskywalkerjedi',
    }
    SPEC = json.loads((Path(__file__).parent / 'fixtures' / 'iaspec-spec.json').read_text(encoding='utf-8'))

    @staticmethod
    def normalise(text):
        text = unicodedata.normalize('NFKD', text)
        return re.sub(r'[\W_]+', '', text.encode('ascii', 'ignore').decode()).lower()

    REGULAR_NAMES = set(map(normalise, (r['name'] for r in IASPEC_RECORDS if not r.get('elite'))))

    @classmethod
    def iaspec_part(cls, record, attr):
        value = record.get(attr)
        if attr == 'elite':
            regular = cls.normalise(record['name']) in cls.REGULAR_NAMES
            return 'elite' if value and not record.get('unique') and regular else ''
        if attr == 'modes':
            return 'campaign' if value == ['Campaign'] else ''
        return value or ''

    @classmethod
    def iaspec_key(cls, record, strategy):
        return cls.normalise(''.join(cls.iaspec_part(record, attr) for attr in strategy))

    @pytest.mark.parametrize('record', IASPEC_RECORDS, ids=lambda r: r['iaspec'])
    def test_iaspec_follows_the_rule(self, record):
        clashing = [r for r in self.IASPEC_RECORDS if r is not record]
        for strategy in self.IASPEC_STRATEGIES:
            clashing = [r for r in clashing if self.iaspec_key(r, strategy) == self.iaspec_key(record, strategy)]
            if not clashing:
                break
        key = self.iaspec_key(record, strategy)
        assert record['iaspec'] == self.SPEC_SPELLINGS.get(key, key)

    @pytest.mark.parametrize('key', sorted(set(SPEC['deployments'] + SPEC['command_cards'])))
    def test_every_spec_key_is_a_cards_iaspec(self, key):
        assert key in {r['iaspec'] for r in self.IASPEC_RECORDS}

    def test_spec_spellings_are_the_specs(self):
        assert set(self.SPEC_SPELLINGS.values()) <= set(self.SPEC['deployments'] + self.SPEC['command_cards'])

    # Elite and mode belong in `elite` and `modes`: ia enter pre-fills names from file names like "Elite Death
    # Troopers campaign".
    MODE_WORDS = re.compile(r'\b(elite|regular|skirmish|campaign)\b', re.IGNORECASE)

    @pytest.mark.parametrize('record', IASPEC_RECORDS + get_data(CONTENT_TYPES.FORM_CARDS), ids=lambda r: r['name'])
    def test_names_have_no_elite_or_mode_words(self, record):
        assert not self.MODE_WORDS.search(record['name'])
        assert not self.MODE_WORDS.search(record.get('description') or '')
