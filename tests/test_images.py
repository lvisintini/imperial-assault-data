import os
import struct
import imghdr
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

    def get_dims_for_entry(self, entry):
        return self.dims

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

    SMALL_HERO = (650, 515)
    SMALL_STANDARD = (301, 470)
    SMALL_MINI = (293, 454)
    SMALL_MINI_FLIPPED = (454, 293)

    ANY = None

    definitions = [
        ImageDefinition('large', CONTENT_TYPES.SOURCE, 'image', dims=SOURCE),
        ImageDefinition('large', CONTENT_TYPES.SKIRMISH_MAP, 'image', dims=ANY),
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
        ImageDefinition('large', CONTENT_TYPES.SIDE_MISSION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.REWARD, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.COMPANION, 'image', dims=LARGE_STANDARD),
        ImageDefinition('large', CONTENT_TYPES.UPGRADE, 'image', dims=LARGE_MINI),
        ImageDefinition('large', CONTENT_TYPES.THREAT_MISSION, 'image', dims=LARGE_STANDARD),
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
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.SIDE_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.STORY_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_STANDARD, content_type=CONTENT_TYPES.THREAT_MISSION),
        ImageDefinition('large', CONTENT_TYPES.CARD, 'image', dims=LARGE_MINI_FLIPPED, content_type=CONTENT_TYPES.FORM_CARDS),

        ImageDefinition('small', CONTENT_TYPES.SOURCE, 'image', dims=SOURCE),
        ImageDefinition('small', CONTENT_TYPES.SKIRMISH_MAP, 'image', dims=ANY),
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
        ImageDefinition('small', CONTENT_TYPES.SIDE_MISSION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.REWARD, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.COMPANION, 'image', dims=SMALL_STANDARD),
        ImageDefinition('small', CONTENT_TYPES.UPGRADE, 'image', dims=SMALL_MINI),
        ImageDefinition('small', CONTENT_TYPES.THREAT_MISSION, 'image', dims=SMALL_STANDARD),
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
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.SIDE_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.STORY_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_STANDARD, content_type=CONTENT_TYPES.THREAT_MISSION),
        ImageDefinition('small', CONTENT_TYPES.CARD, 'image', dims=SMALL_MINI_FLIPPED, content_type=CONTENT_TYPES.FORM_CARDS),
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

    @staticmethod
    def get_image_size(fname):
        # https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib/20380514#20380514
        with open(fname, 'rb') as fhandle:
            head = fhandle.read(24)
            if len(head) != 24:
                return
            if imghdr.what(fname) == 'png':
                check = struct.unpack('>i', head[4:8])[0]
                if check != 0x0d0a1a0a:
                    return
                width, height = struct.unpack('>ii', head[16:24])
            elif imghdr.what(fname) == 'gif':
                width, height = struct.unpack('<HH', head[6:10])
            elif imghdr.what(fname) == 'jpeg':
                try:
                    fhandle.seek(0)  # Read 0xff next
                    size = 2
                    ftype = 0
                    while not 0xc0 <= ftype <= 0xcf:
                        fhandle.seek(size, 1)
                        byte = fhandle.read(1)
                        while ord(byte) == 0xff:
                            byte = fhandle.read(1)
                        ftype = ord(byte)
                        size = struct.unpack('>H', fhandle.read(2))[0] - 2
                    # We are at a SOFn block
                    fhandle.seek(1, 1)  # Skip `precision' byte.
                    height, width = struct.unpack('>HH', fhandle.read(4))
                except Exception:  #IGNORE:W0703
                    return
            else:
                return
            return width, height

    def test_all_images_are_accounted_for_in_helper(self):
        helper_images = set(list(ImageTestHelper.get_paths(get_data_for(*CONTENT_TYPES.as_list))))
        image_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        files_found = set()
        for dir_path, _, file_names in os.walk(image_root):
            for f in file_names:
                files_found.add(os.path.join(dir_path, f))

        assert helper_images == files_found

    @pytest.mark.parametrize("image_path", ImageTestHelper.get_paths(get_data_for(*CONTENT_TYPES.as_list)))
    def test_image_paths(self, image_path):
        assert os.path.exists(image_path)
        assert os.path.isfile(image_path)

    @pytest.mark.parametrize(
        "image_path,expected_size", ImageTestHelper.get_paths_and_expected_sizes(get_data_for(*CONTENT_TYPES.as_list))
    )
    def test_image_sizes(self, image_path, expected_size):

        assert self.get_image_size(image_path) == expected_size
