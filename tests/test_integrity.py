import re
import unicodedata

import pytest

from tests.constants import CONTENT_TYPES, DEPLOYMENT_TRAITS, GAME_MODES, BUFF_TYPES
from tests.utils import get_data, get_data_for, flatten_list
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
        assert source_contents_entry["content_type"] != CONTENT_TYPES.SOURCE
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


class TestSourcesIntegrity:
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

    @pytest.mark.parametrize("entry", [
        s for s in get_data(CONTENT_TYPES.SOURCE) if s['included_in'] is not None
    ], ids=lambda s: s['name'])
    def test_included_in_is_another_standalone_source(self, entry):
        sources = {s['id']: s for s in get_data(CONTENT_TYPES.SOURCE)}
        container = sources.get(entry['included_in'])
        assert container is not None and container['id'] != entry['id']
        assert container['included_in'] is None  # one level: a pack inside a box, not inside another pack

    def test_included_products_dont_repeat_their_containers_contents(self):
        """A pack's contents are listed once, on the pack; the box that includes it gets them through included_in."""
        rows = get_data(CONTENT_TYPES.SOURCE_CONTENTS)
        contents = {}
        for row in rows:
            contents.setdefault(row['source_id'], set()).add((row['content_type'], row['content_id']))
        for source in get_data(CONTENT_TYPES.SOURCE):
            if source['included_in'] is not None:
                shared = contents.get(source['id'], set()) & contents.get(source['included_in'], set())
                assert not shared, (source['name'], shared)


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
        d for d in get_data(CONTENT_TYPES.REWARD) if d['type'] == BUFF_TYPES.FEAT
    ])
    def test_feat_has_no_traits(self, entry):
        assert entry['traits'] is None


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

    # How iaspec values are built: elite + name, then, only while another card would get the same value, name plus
    # one of mode, affiliation or description. imperial-assault-tools suggests them with the same rule.
    IASPEC_STRATEGIES = [('elite', 'name'), ('elite', 'name', 'modes'), ('elite', 'name', 'affiliation'),
                         ('elite', 'name', 'description')]
    IASPEC_RECORDS = flatten_list(get_data_for(
        CONTENT_TYPES.DEPLOYMENT, CONTENT_TYPES.COMMAND, CONTENT_TYPES.COMPANION
    ).values())

    @staticmethod
    def iaspec_part(record, attr):
        value = record.get(attr)
        if attr == 'elite':
            return 'elite' if value and not record.get('unique') else ''
        if attr == 'modes':
            return value[0] if value and len(value) == 1 else ''
        return value or ''

    @classmethod
    def iaspec_key(cls, record, strategy):
        text = unicodedata.normalize('NFKD', ''.join(cls.iaspec_part(record, attr) for attr in strategy))
        return re.sub(r'[\W_]+', '', text.encode('ascii', 'ignore').decode()).lower()

    @pytest.mark.parametrize('record', IASPEC_RECORDS, ids=lambda r: r['iaspec'])
    def test_iaspec_follows_the_rule(self, record):
        clashing = [r for r in self.IASPEC_RECORDS if r is not record]
        for strategy in self.IASPEC_STRATEGIES:
            clashing = [r for r in clashing if self.iaspec_key(r, strategy) == self.iaspec_key(record, strategy)]
            if not clashing:
                break
        assert record['iaspec'] == self.iaspec_key(record, strategy)
