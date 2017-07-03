from unittest import TestCase
from client import MultibotClient
from random import randint
from tempfile import TemporaryDirectory
from json import dumps
from os import path
from requests import head

class ClientTests(TestCase):
    def setUp(self):
        temp_dir = TemporaryDirectory()
        responses = dumps([
            {
                'name': 'Interesting Facts',
                'url': 'http://dummybot_1'
            },
            {
                'name': 'Strange Facts',
                'url': 'http://dummybot_2'
            },
            {
                'name': 'Unusual Facts',
                'url': 'http://dummybot_3'
            }
        ])
        fp = open(path.join(temp_dir.name, 'responses.json'), 'w')
        fp.write(responses)
        fp.close()
        self.bot = MultibotClient(config_path=temp_dir, data_path=temp_dir)

    def tearDown(self):
        '''
        Remove the test database.
        '''
        self.bot.storage.drop()

    def check_bot_up(self, bot_connection):
        head(bot_connection.url)

    def random_string(self, start=0, end=9000):
        '''
        Generate a string based on a random number.
        '''
        return str(randint(start, end))