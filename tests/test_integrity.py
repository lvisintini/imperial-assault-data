from os import path
from itertools import product, chain

import pytest

from tests.constants import CONTENT_TYPES
from tests.utils import get_data


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

    @pytest.mark.parametrize("image_subdir,entry", product(
        ('small', 'large'),
        chain(*[
            get_data(ct) for ct in CONTENT_TYPES.as_list if ct not in CONTENT_TYPES.without_image_attr
        ])
    ))
    def test_image_paths(self, image_subdir, entry):
        absolute_path = path.abspath(path.join(path.dirname(__file__), f'../images/{image_subdir}/{entry["image"]}'))
        assert path.exists(absolute_path)
        assert path.isfile(absolute_path)

    @pytest.mark.parametrize("image_attr,image_subdir,entry", product(
        ('wounded', 'healthy'), ('small', 'large'), get_data(CONTENT_TYPES.HERO)
    ))
    def test_hero_image_paths(self, image_attr, image_subdir, entry):
        absolute_path = path.abspath(path.join(path.dirname(__file__), f'../images/{image_subdir}/{entry[image_attr]}'))
        assert path.exists(absolute_path)
        assert path.isfile(absolute_path)
