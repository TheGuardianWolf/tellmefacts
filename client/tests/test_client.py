from unittest import TestCase
from client import MultibotClient
from random import randint
from tempfile import TemporaryDirectory
from json import dumps
from os import path
from requests import get
from requests.exceptions import RequestException


class ClientTests(TestCase):
    def setUp(self):
        temp_dir = TemporaryDirectory()
        temp_path = temp_dir.name
        responses = dumps([{
            'name': 'Interesting Facts',
            'url': 'http://dummybot_1'
        }, {
            'name': 'Strange Facts',
            'url': 'http://dummybot_2'
        }, {
            'name': 'Unusual Facts',
            'url': 'http://dummybot_3'
        }])
        fp = open(path.join(temp_dir.name, 'responses.json'), 'w')
        fp.write(responses)
        fp.close()
        self.client = MultibotClient(
            config_path=temp_path,
            input_adapter='chatterbot.input.VariableInputTypeAdapter',
            output_adapter='chatterbot.output.OutputAdapter')
        self.bot_availablity = []
        for connection in self.client.bot_connections:
            self.bot_availablity.append(self.check_bot_up(connection))

    def tearDown(self):
        '''
        Remove the test database.
        '''
        self.client.bot.storage.drop()

    def check_bot_up(self, bot_connection):
        return False
        try:
            r = get(bot_connection.url + '/askmeanything?q=test', timeout=1)
            assert r.ok
            return True
        except (RequestException, AssertionError):
            return False

    def query_bot(self, query):
        return str(self.client.bot.get_response(query))

    def random_string(self, start=0, end=9000):
        '''
        Generate a string based on a random number.
        '''
        return str(randint(start, end))

    def test_simple_chat(self):
        self.assertEqual(
            self.query_bot('list'), ('1. Interesting Facts\n'
                                     '2. Strange Facts\n'
                                     '3. Unusual Facts'))
        self.assertEqual(
            self.query_bot('start_session Interesting Facts'),
            'You are now chatting with Interesting Facts.')
        if self.bot_availablity[0]:
            rand = self.random_string()
            self.assertIsInstance(str(self.query_bot(rand)), str)
        self.assertEqual(
            self.query_bot('end_session'),
            'Chat session with Interesting Facts ended.')

    def test_multibot_chat(self):
        self.assertEqual(
            self.query_bot('list'), ('1. Interesting Facts\n'
                                     '2. Strange Facts\n'
                                     '3. Unusual Facts'))

        for connection in self.client.bot_connections:
            self.assertEqual(
                self.query_bot('start_session {}'.format(connection.name)),
                'You are now chatting with {}.'.format(connection.name))
            if self.bot_availablity[0]:
                rand = self.random_string()
                self.assertIsInstance(str(self.query_bot(rand)), str)
            self.assertEqual(
                self.query_bot('end_session'),
                'Chat session with {} ended.'.format(connection.name))

    def test_invalid_chat(self):
        if self.bot_availablity[0]:
            rand = self.random_string()
            self.assertEqual(
                self.query_bot(rand),
                ('You are currently not connected to any bot. '
                 'Connect to a bot with \'start_session <bot_name>\' or '
                 'type \'list\' for a list of available bots.'))
        self.assertEqual(
            self.query_bot('end_session'),
            'You are currently not in an active session.')
        self.assertEqual(
            self.query_bot('start_session Unusual Facts'),
            'You are now chatting with Unusual Facts.')
        self.assertEqual(
            self.query_bot('start_session Strange Facts'),
            'You are already in a chat session with Unusual Facts!')
