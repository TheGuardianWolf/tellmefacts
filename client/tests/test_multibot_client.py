# -*- coding: utf-8 -*-
import pytest
from chatterbot.conversation import Statement
from slackclient import SlackClient
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
    # Create and write a bots.json file to the temp directory
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

    # Patch asking bots for a response to be always successful
    mocker.patch(
        'client.services.BotConnection.ask', return_value=(200, 'response'))

    # Create client with simple adapters to read from and write to. Slack
    # requests module starts off patched.
    c = MultibotClient(
        config_path=tmpdir,
        input_adapter='chatterbot.input.VariableInputTypeAdapter',
        output_adapter='chatterbot.output.OutputAdapter',
        api_hostname='localhost')
    yield c

    # Cleanup with the close function
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
        # Patch required objects for requests
        m_post = mocker.patch(
            'slackclient._slackrequest.requests.post',
            return_value=mocker.Mock(text='{"ok":true}'))

        # Function to check the post request parameters are as expected
        def check_slack_request(hostname):
            assert m_post.called
            args, kwargs = m_post.call_args
            assert args[0] == 'https://{0}/api/{1}'.format(hostname,
                                                           'chat.postMessage')
            assert 'user-agent' in kwargs.get('headers')
            assert kwargs.get('data').get('channel') == '#general'
            assert kwargs.get('data').get('text') == 'test'
            assert kwargs.get('data').get(
                'token') == 'xoxp-1234123412341234-12341234-1234'
            assert kwargs.get('files') is None
            assert kwargs.get('timeout') is None
            assert kwargs.get('proxies') is None

        # Send a message via slack api call (slackclient's request class was
        # patched in fixture)
        sc = SlackClient('xoxp-1234123412341234-12341234-1234')
        sc.api_call('chat.postMessage', text='test', channel='#general')

        # Check now
        check_slack_request('localhost')

        # Try patch to another hostname
        client.patch_slack_requests('localhost:8080')
        sc.api_call('chat.postMessage', text='test', channel='#general')

        # Check again
        check_slack_request('localhost:8080')

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
            client, 'Ṱ̺̺̕h̼͓̲̦̳̘̲e͇̣̰̦̬͎ ̢̼̻̱̘h͚͎͙̜̣̲ͅi̦̲̣̰̤v̻͍e̺̭̳̪̰-m̢iͅn̖̺̞̲̯̰d̵̼̟͙̩̼̘̳.̨̹͈̣') == 'Interesting Facts: response'
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

        # Test connecting to, chatting with, and disconnecting from all bot
        # connections
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
        # Try to chat when not connected to a bot
        rand = self.random_string()
        assert self.query_bot(client, rand) == (
            'You are currently not connected to any bot. '
            'Connect to a bot with \'start_session <bot_name>\' or '
            'type \'list\' for a list of available bots.')

        # Try to end the session without being in a session
        assert self.query_bot(
            client,
            'end_session') == 'You are currently not in an active session.'

        # Try to start a new session whilst a session is currently in place
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
            client.bot, 'get_response', side_effect=KeyboardInterrupt)
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

        # Patch get_response to wait an amount of time instead of raising an
        # exception with the default None argument in application start
        monkeypatch.setattr(client.bot, 'get_response', wait_response)
        t = Thread(target=client.start, daemon=True)
        t.start()
        client.close()
        t.join(timeout=3)
        assert not t.is_alive()
