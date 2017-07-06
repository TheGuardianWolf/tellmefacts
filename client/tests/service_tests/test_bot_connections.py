from unittest import TestCase
from client.services import BotConnection
from requests import get


class BotConnectionTests(TestCase):
    def setUp(self):
        self.bc = BotConnection('dummybot', 'http://dummybot')

    def test_ask(self):
        try:
            (status, response_text) = self.bc.ask('test')
            self.assertTrue(status == '200')
            self.assertTrue(isinstance(response_text, str))
        except ValueError:
            # Can't test further if no dummybot servers are up.
            pass      
