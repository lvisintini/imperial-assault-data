import pytest

from tests.constants import CONTENT_TYPES, DEPLOYMENT_TRAITS, GAME_MODES, BUFF_TYPES
from tests.utils import get_data, get_data_for, flatten_list
from collections import Counter


class TestIntegrity:

    @staticmethod
    def fetch_fk_data(data, fk_id):
        return next(iter([d for d in data if d["id"] == fk_id]), None)

    @pytest.mark.parametrize("content_type", list(set(CONTENT_TYPES.as_list).difference(CONTENT_TYPES.without_ids)))
    def test_no_skipped_or_duplicate_id_numbers(self, content_type):
        data = get_data(content_type)
        assert set(range(len(data))) == set([d["id"] for d in data])

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


class TestDeploymentsIntegrity:
    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.DEPLOYMENT) if DEPLOYMENT_TRAITS.SKIRMISH_UPGRADE in d['traits']
    ])
    def test_skirmish_upgrades_have_skirmish_game_mode_only(self, entry):
        assert entry['modes'] == [GAME_MODES.SKIRMISH, ]

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
    def test_unique_deployment_does_not_have_a_reinforce_cost(self, entry):
        assert entry['traits'] is None


class TestRewardIntegrity:

    @pytest.mark.parametrize("entry", [
        d for d in get_data(CONTENT_TYPES.REWARD) if d['type'] == BUFF_TYPES.FEAT
    ])
    def test_unique_deployment_does_not_have_a_reinforce_cost(self, entry):
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
