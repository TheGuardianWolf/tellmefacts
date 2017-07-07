from unittest import TestCase
from client.services import BotConnection, BotConnectionManager


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


class BotConnectionManagerTests(TestCase):
    def setUp(self):
        self.bcm = BotConnectionManager(
            [{
                'name': 'dummybot', 
                'url': 'http://dummybot'
            }]
        )
        self.assertEqual(len(self.bcm.connections), 1)
        self.assertIsInstance(self.bcm.connections[0], BotConnection)

    def test_add(self):
        self.bcm.add('added', 'http://added')
        self.assertEqual(len(self.bcm.connections), 2)
        self.assertIsInstance(self.bcm.connections[1], BotConnection)

    def test_get(self):
        bot = self.bcm.get('dummybot')
        self.assertIsInstance(bot, BotConnection)
        self.assertEquals(bot.name, 'dummybot')
        self.assertIsNone(self.bcm.get('none'))

    def test_all(self):
        self.assertEquals(len(self.bcm.all()), 1)


