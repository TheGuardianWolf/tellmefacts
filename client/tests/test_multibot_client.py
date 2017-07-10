# -*- coding: utf-8 -*-
import pytest
from client import MultibotClient
from random import randint
from json import dumps
from os import path
from threading import Thread
from time import sleep


@pytest.fixture()
def client(tmpdir, mocker):
    """
    Creates and patches for a multibot client object.
    """
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
        'client.services.BotConnection.ask', return_value=(200, 'response'))
    c = MultibotClient(
        config_path=tmpdir,
        input_adapter='chatterbot.input.VariableInputTypeAdapter',
        output_adapter='chatterbot.output.OutputAdapter')
    yield c
    c.close()


class TestMultibotClient(object):
    def query_bot(self, client, query):
        """
        Ask the currently set bot a question.
        """
        return str(client.bot.get_response(query))

    def random_string(self, start=0, end=9000):
        """
        Generate a string based on a random number.
        """
        return str(randint(start, end))

    def test_patch_slack_requests(self, client, mocker):
        """
        Test whether a request is sent to a different hostname after patching
        the Slack Requests class.
        """
        pass

    def test_simple_chat(self, client, mocker):
        """
        Test whether a simple chat to one bot goes as expected.
        """
        assert self.query_bot(client, 'list') == ('1. Interesting Facts\n'
                                                  '2. Strange Facts\n'
                                                  '3. Unusual Facts')
        assert self.query_bot(
            client, 'start_session Interesting Facts'
        ) == 'You are now chatting with Interesting Facts.'

        assert self.query_bot(
            client, self.random_string()) == 'Interesting Facts: response'
        assert self.query_bot(
            client,
            'end_session') == 'Chat session with Interesting Facts ended.'

    def test_multibot_chat(self, client):
        """
        Test whether a chat switching between multiple bots goes as expected.
        """
        assert self.query_bot(client, 'list'), ('1. Interesting Facts\n'
                                                '2. Strange Facts\n'
                                                '3. Unusual Facts')

        for i, connection in enumerate(client.bot_connections):
            assert self.query_bot(client, 'start_session {}'.format(
                connection['name'])) == 'You are now chatting with {}.'.format(
                    connection['name'])
            assert self.query_bot(
                client, self.random_string()) == '{}: response'.format(
                    connection['name'])
            assert self.query_bot(
                client, 'end_session') == 'Chat session with {} ended.'.format(
                    connection['name'])

    def test_invalid_chat(self, client):
        """
        Test whether a chat with invalid commands being sent goes as expected.
        """
        rand = self.random_string()
        assert self.query_bot(client, rand) == (
            'You are currently not connected to any bot. '
            'Connect to a bot with \'start_session <bot_name>\' or '
            'type \'list\' for a list of available bots.')
        assert self.query_bot(
            client,
            'end_session') == 'You are currently not in an active session.'
        assert self.query_bot(client, 'start_session Unusual Facts'
                              ) == 'You are now chatting with Unusual Facts.'
        assert self.query_bot(
            client, 'start_session Strange Facts'
        ) == 'You are already in a chat session with Unusual Facts!'

    def test_client_keyboard_interrupt(self, client, mocker):
        """
        Test ending application with a keyboard interrupt.
        """
        mocker.patch.object(
            client.bot.get_response, side_effect=KeyboardInterrupt)
        t = Thread(target=client.start, daemon=True)
        t.start()
        t.join(timeout=3)
        assert not t.is_alive()

    def test_client_close(self, client, monkeypatch):
        """
        Test closing the application from a seperate thread.
        """
        def wait_response(*args):
            sleep(0.5)

        monkeypatch.setattr(client.bot, 'get_response', wait_response)
        t = Thread(target=client.start, daemon=True)
        t.start()
        client.stop()
        t.join(timeout=3)
        assert not t.is_alive()

    def test_client_assertion_error(self, client, mocker):
        """
        Raising an AttributeError should not always be captured.
        """
        mocker.patch.object(
            client.bot.get_response, side_effect=AttributeError)
        with pytest.raises(AttributeError):
            client.start()
