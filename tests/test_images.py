import os
import struct
import pytest

from tests.constants import CONTENT_TYPES
from tests.utils import get_data_for


class ImageDefinition:
    def __init__(self, image_subdir, ct, attr, dims, **kwargs):
        self.image_subdir = image_subdir
        self.content_type = ct
        self.attr = attr
        self.dims = dims
        self.additional_filters = kwargs

    def get_image_path_from_entry(self, entry):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), f'../images/{self.image_subdir}/{entry[self.attr]}')
        )

    def filter(self, content_type, entry):
        return all(
            [self.content_type == content_type] + [entry[k] == v for k, v in self.additional_filters.items()]
        )


class ImageTestHelper:

    SOURCE = (300, 300)

    LARGE_HERO = (1490, 1186)
    LARGE_STANDARD = (476, 740)
    LARGE_MINI = (424, 657)
    LARGE_MINI_FLIPPED = (657, 424)
    LARGE_STANDARD_FLIPPED = (740, 476)

    SMALL_HERO = (650, 515)
    SMALL_STANDARD = (301, 470)
    SMALL_MINI = (293, 454)
    SMALL_MINI_FLIPPED = (454, 293)
    SMALL_STANDARD_FLIPPED = (470, 301)

    ANY = None

    definitions = [
        ImageDefinition('large', CONTENT_TYPES.SOURCE, 'image', dims=SOURCE),
        ImageDefinition('large', CONTENT_TYPES.MAP, 'image', dims=ANY),
        ImageDefinition('large', CONTENT_TYPES.AGENDA, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.COMMAND, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.CONDITION, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.DEPLOYMENT, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.HERO, 'healthy', dims=LARGE_HERO),
        ImageDefinition('large', CONTENT_TYPES.HERO, 'wounded', dims=LARGE_HERO),
        ImageDefinition('large', CONTENT_TYPES.HERO_CLASS, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.IMPERIAL_CLASS_CARD, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.SUPPLY, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.STORY_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.HERO_SIDE_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.ALLY_SIDE_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.REGULAR_SIDE_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.REWARD, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.COMPANION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.UPGRADE, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.THREAT_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.SKIRMISH_MISSION, 'image', dims=LARGE_STANDARD_FLIPPED),
        ImageDefinition('large', CONTENT_TYPES.EPILOGUE, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.FORM_CARDS, 'image', dims=LARGE_MINI_FLIPPED),

        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.AGENDA_DECKS),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.COMMAND),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.COMPANION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.CONDITION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.DEPLOYMENT),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.IMPERIAL_CLASSES),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.HERO),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.UPGRADE),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.REWARD),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI, content_type=CONTENT_TYPES.SUPPLY),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.HERO_SIDE_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.ALLY_SIDE_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.REGULAR_SIDE_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.STORY_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.THREAT_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI_FLIPPED, content_type=CONTENT_TYPES.FORM_CARDS),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.EPILOGUE),

        ImageDefinition('small', CONTENT_TYPES.SOURCE, 'image', dims=SOURCE),
        ImageDefinition('small', CONTENT_TYPES.MAP, 'image', dims=ANY),
        ImageDefinition('small', CONTENT_TYPES.AGENDA, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.COMMAND, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.CONDITION, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.DEPLOYMENT, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.HERO, 'healthy', dims=SMALL_HERO),
        ImageDefinition('small', CONTENT_TYPES.HERO, 'wounded', dims=SMALL_HERO),
        ImageDefinition('small', CONTENT_TYPES.HERO_CLASS, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.IMPERIAL_CLASS_CARD, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.SUPPLY, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.STORY_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.HERO_SIDE_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.ALLY_SIDE_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.REGULAR_SIDE_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.REWARD, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.COMPANION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.UPGRADE, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.THREAT_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.SKIRMISH_MISSION, 'image', dims=SMALL_STANDARD_FLIPPED),
        ImageDefinition('small', CONTENT_TYPES.EPILOGUE, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.FORM_CARDS, 'image', dims=SMALL_MINI_FLIPPED),

        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.AGENDA_DECKS),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.COMMAND),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.COMPANION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.CONDITION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.DEPLOYMENT),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.IMPERIAL_CLASSES),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.HERO),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.UPGRADE),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.REWARD),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI, content_type=CONTENT_TYPES.SUPPLY),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.HERO_SIDE_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.ALLY_SIDE_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.REGULAR_SIDE_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.STORY_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.THREAT_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI_FLIPPED, content_type=CONTENT_TYPES.FORM_CARDS),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.EPILOGUE),
    ]

    @classmethod
    def get_paths_and_expected_sizes(cls, data):
        for content_type, models in data.items():
            for image_def in [image_def for image_def in cls.definitions if content_type == image_def.content_type]:
                for entry in models:
                    if not image_def.filter(content_type, entry) or image_def.dims is cls.ANY:
                        continue
                    yield (image_def.get_image_path_from_entry(entry), image_def.dims)

    @classmethod
    def get_paths(cls, data):
        for content_type, models in data.items():
            for image_def in [image_def for image_def in cls.definitions if content_type == image_def.content_type]:
                for entry in models:
                    if not image_def.filter(content_type, entry):
                            continue
                    yield image_def.get_image_path_from_entry(entry)


class TestImages:

    PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

    @classmethod
    def get_image_size(cls, fname):
        # All images are PNG; width and height are the first fields of the IHDR chunk.
        with open(fname, 'rb') as fhandle:
            head = fhandle.read(24)
        if len(head) != 24 or head[:8] != cls.PNG_SIGNATURE:
            return
        return struct.unpack('>II', head[16:24])

    def test_all_images_are_accounted_for_in_helper(self):
        helper_images = set(list(ImageTestHelper.get_paths(get_data_for(*CONTENT_TYPES.as_list))))
        image_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        files_found = set()
        for dir_path, _, file_names in os.walk(image_root):
            for f in file_names:
                files_found.add(os.path.join(dir_path, f))

        assert helper_images == files_found

    @pytest.mark.parametrize("image_path", list(ImageTestHelper.get_paths(get_data_for(*CONTENT_TYPES.as_list))))
    def test_image_paths(self, image_path):
        assert os.path.exists(image_path)
        assert os.path.isfile(image_path)

    @pytest.mark.parametrize(
        "image_path,expected_size",
        list(ImageTestHelper.get_paths_and_expected_sizes(get_data_for(*CONTENT_TYPES.as_list)))
    )
    def test_image_sizes(self, image_path, expected_size):
        assert self.get_image_size(image_path) == expected_size
