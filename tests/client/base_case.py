from unittest import TestCase
from client import MultibotClient
from random import randint


class ClientTestCase(TestCase):
    def setUp(self, tmpdir):
        self.bot = MultibotClient(config_path=tmpdir, data_path=tmpdir)

    def tearDown(self):
        """
        Remove the test database.
        """
        self.bot.storage.drop()

    def random_string(self, start=0, end=9000):
        """
        Generate a string based on a random number.
        """
        return str(randint(start, end))
