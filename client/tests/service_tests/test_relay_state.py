from unittest import TestCase
from client.services import RelayState, BotConnection


class RelayStateTests(TestCase):
    def setUp(self):
        self.rs = RelayState()

    def test_attrs(self):
        bc = BotConnection('dummybot', 'http://dummybot')
        self.rs.bot = bc
        self.assertIs(self.rs.bot, bc)
