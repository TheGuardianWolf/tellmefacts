# -*- coding: utf-8 -*-
import pytest
from client.services import RelayState, BotConnection


@pytest.fixture()
def relay_state():
    """
    Creates a relay state object.
    """
    return RelayState()


class TestRelayState(object):
    def test_relay_state(self, relay_state):
        """
        Test object attributes.
        """
        bc = BotConnection('dummybot', 'http://dummybot')
        relay_state.bot = bc
        assert relay_state.bot is bc
