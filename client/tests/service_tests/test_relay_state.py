import pytest
from client.services import RelayState, BotConnection


@pytest.fixture()
def relay_state():
    return RelayState()


class TestRelayState(object):
    def test_attrs(self, relay_state):
        bc = BotConnection('dummybot', 'http://dummybot')
        relay_state.bot = bc
        assert relay_state.bot is bc
