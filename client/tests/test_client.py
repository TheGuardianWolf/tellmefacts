import pytest
from client import MultibotClient
from random import randint
from json import dumps
from os import path


@pytest.fixture()
def client(tmpdir, mocker):
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
    fp = open(path.join(tmpdir, 'bots.json'), 'w')
    fp.write(responses)
    fp.close()
    mocker.patch(
        'client.service.bot_connections.BotConnection.ask',
        return_value=(200, 'response'))
    c = MultibotClient(
        config_path=tmpdir,
        input_adapter='chatterbot.input.VariableInputTypeAdapter',
        output_adapter='chatterbot.output.OutputAdapter')
    yield c
    c.bot.storage.drop()


class TestClient(object):
    def query_bot(self, client, query):
        return str(client.bot.get_response(query))

    def random_string(self, start=0, end=9000):
        '''
        Generate a string based on a random number.
        '''
        return str(randint(start, end))

    def test_simple_chat(self, client, mocker):
        assert self.query_bot(client, 'list') == ('1. Interesting Facts\n'
                                                  '2. Strange Facts\n'
                                                  '3. Unusual Facts')
        assert self.query_bot(
            client, 'start_session Interesting Facts'
        ) == 'You are now chatting with Interesting Facts.'

        # mocker.patch.object(
        #     client.bot.logic.state.bot, 'ask', return_value=(200, 'response'))
        assert self.query_bot(
            self.random_string()) == 'Interesting Facts: response'
        assert self.query_bot(
            'end_session') == 'Chat session with Interesting Facts ended.'

    def test_multibot_chat(self, client):
        self.assertEqual(
            self.query_bot(client, 'list'), ('1. Interesting Facts\n'
                                             '2. Strange Facts\n'
                                             '3. Unusual Facts'))

        for i, connection in enumerate(self.client.bot_connections):
            self.assertEqual(
                self.query_bot(client,
                               'start_session {}'.format(connection['name'])),
                'You are now chatting with {}.'.format(connection['name']))
            assert self.query_bot(
                client, self.random_string()) == '{}: response'.format(
                    connection['name'])
            assert self.query_bot(
                client, 'end_session') == 'Chat session with {} ended.'.format(
                    connection['name'])

    def test_invalid_chat(self, client):
        rand = self.random_string()
        assert self.query_bot(client, rand) == (
            'You are currently not connected to any bot. '
            'Connect to a bot with \'start_session <bot_name>\' or '
            'type \'list\' for a list of available bots.')
        assert self.query_bot(
            client, 'end_session'
        ) == 'You are currently not in an active session.'
        assert self.query_bot(
            client, 'start_session Unusual Facts'
        ) == 'You are now chatting with Unusual Facts.'
        assert self.query_bot(
            client, 'start_session Strange Facts'
        ) == 'You are already in a chat session with Unusual Facts!'
