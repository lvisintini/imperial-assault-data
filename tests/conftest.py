import pytest

from tests.constants import CONTENT_TYPES
from tests.utils import get_data, get_data_for


@pytest.fixture
def sources():
    return get_data(CONTENT_TYPES.SOURCE)


@pytest.fixture
def source_contents():
    return sorted(get_data(CONTENT_TYPES.SOURCE_CONTENTS), key=lambda m: (m['source_id'], m['content_type']))


@pytest.fixture
def skirmish_maps():
    return get_data(CONTENT_TYPES.SKIRMISH_MAP)


@pytest.fixture
def agenda_cards():
    return get_data(CONTENT_TYPES.AGENDA)


@pytest.fixture
def agenda_decks():
    return get_data(CONTENT_TYPES.AGENDA_DECKS)


@pytest.fixture
def command_cards():
    return get_data(CONTENT_TYPES.COMMAND)


@pytest.fixture
def condition_cards():
    return get_data(CONTENT_TYPES.CONDITION)


@pytest.fixture
def deployment_cards():
    return get_data(CONTENT_TYPES.DEPLOYMENT)


@pytest.fixture
def heroes():
    return get_data(CONTENT_TYPES.HERO)


@pytest.fixture
def hero_class_cards():
    return get_data(CONTENT_TYPES.HERO_CLASS)


@pytest.fixture
def imperial_classes():
    return get_data(CONTENT_TYPES.IMPERIAL_CLASSES)


@pytest.fixture
def imperial_class_cards():
    return get_data(CONTENT_TYPES.IMPERIAL_CLASS_CARD)


@pytest.fixture
def supply_cards():
    return get_data(CONTENT_TYPES.SUPPLY)


@pytest.fixture
def story_mission_cards():
    return get_data(CONTENT_TYPES.STORY_MISSION)


@pytest.fixture
def side_mission_cards():
    return get_data(CONTENT_TYPES.SIDE_MISSION)


@pytest.fixture
def reward_cards():
    return get_data(CONTENT_TYPES.REWARD)


@pytest.fixture
def companion_cards():
    return get_data(CONTENT_TYPES.COMPANION)


@pytest.fixture
def upgrade_cards():
    return get_data(CONTENT_TYPES.UPGRADE)


@pytest.fixture
def card_backs():
    return get_data(CONTENT_TYPES.CARD)


@pytest.fixture
def threat_mission_cards():
    return get_data(CONTENT_TYPES.THREAT_MISSION)


@pytest.fixture
def form_cards():
    return get_data(CONTENT_TYPES.FORM_CARDS)


@pytest.fixture
def all_data():
    return get_data_for(CONTENT_TYPES.as_list)
