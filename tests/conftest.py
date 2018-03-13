import pytest

from tests.constants import CONTENT_TYPES
from tests.utils import get_data, get_data_for


@pytest.fixture
def source_contents():
    return sorted(get_data(CONTENT_TYPES.SOURCE_CONTENTS), key=lambda m: (m['source_id'], m['content_type']))


@pytest.fixture
def agenda_decks():
    return get_data(CONTENT_TYPES.AGENDA_DECKS)


@pytest.fixture
def heroes():
    return get_data(CONTENT_TYPES.HERO)


@pytest.fixture
def imperial_classes():
    return get_data(CONTENT_TYPES.IMPERIAL_CLASSES)


@pytest.fixture
def threat_mission_cards():
    return get_data(CONTENT_TYPES.THREAT_MISSION)


@pytest.fixture
def form_cards():
    return get_data(CONTENT_TYPES.FORM_CARDS)


@pytest.fixture
def all_data():
    return get_data_for(*CONTENT_TYPES.as_list)
