import pytest
from client import MultibotClient
from random import randint
from os import path
from json import loads
from requests import head
from requests.exceptions import RequestException
from multiprocessing.pool import ThreadPool
from threading import Thread


TEST_CONFIG_PATH = path.join(path.dirname(path.realpath(__file__)), 'config')
BOT_ID = 'fakebotid'
USER_ID = 'fakeid'
CHANNEL = 'abcd'
DUMMYBOTS = {
    'available': False,
    'tested': False
}


def check_dummybots():
    global DUMMYBOTS
    if not DUMMYBOTS['tested']:
        DUMMYBOTS['tested'] = True

        fp = open(path.join(TEST_CONFIG_PATH, 'bots.json'), 'r')
        bot_connections = loads(fp.read())
        fp.close()

        def worker(bot_url):
            try:
                r = head('{}/askmeanything?q=test'.format(bot_url), timeout=5)
                assert r.ok
                return r
            except (RequestException, AssertionError):
                return None

        urls = []
        for connection in bot_connections:
            urls.append(connection['url'])

        pool = ThreadPool(processes=3)
        bot_available = pool.map(worker, urls)

        for i, available in enumerate(bot_available):
            if available is None:
                DUMMYBOTS['available'] = False
                return
        DUMMYBOTS['available'] = True


@pytest.fixture(params=[True, False], ids=['patch_ask', 'no_patch_ask'])
def patch_bot_ask(request, mocker):
    if request.param:
        mocker.patch(
            'client.services.BotConnection.ask',
            return_value=(200, 'response'))
    else:
        if not pytest.config.getoption('--dummybot'):
            pytest.skip('need --dummybot option to run')
        else:
            check_dummybots()
            if not DUMMYBOTS.get('available'):
                pytest.xfail('one or more dummybot servers are unreachable')


@pytest.fixture()
def client(mocker, monkeypatch, patch_bot_ask):
    mock_api_call = {
        'ok': True,
        'user_id': USER_ID,
        'user': {
            'profile': {
                'bot_id': BOT_ID
            }
        }
    }
    m_api = mocker.patch(
        'client.multibot_client.SlackClient.api_call',
        return_value=mock_api_call)
    m_rtm_c = mocker.patch(
        'client.multibot_client.SlackClient.rtm_connect', return_value=True)
    events_input = []
    m_rtm_r = mocker.patch(
        'client.multibot_client.SlackClient.rtm_read',
        return_value=events_input)
    m_rtm_s = mocker.patch('slackclient.SlackClient.rtm_send_message')
    c = MultibotClient(config_path=TEST_CONFIG_PATH)
    monkeypatch.setattr(c.slack_client.server, 'websocket', True)
    t = Thread(target=c.start, args=())
    return_object = {
        'client': c,
        'events_input': events_input,
        'api_call': m_api,
        'rtm_connect': m_rtm_c,
        'rtm_read': m_rtm_r,
        'rtm_send_message': m_rtm_s
    }
    t.start()
    yield return_object
    c.close()
    t.join(timeout=5)


class TestClientIntegration(object):
    def query_bot(self, client, query):
        read_count = client.get('rtm_read').call_count
        send_count = client.get('rtm_send_message').call_count
        client.get('events_input').append({
            'type':
            'message',
            'text':
            '<@{}> {}'.format(USER_ID, query),
            'channel':
            CHANNEL
        })
        has_event = client.get('client').events.get('message').wait(timeout=1)
        assert has_event
        del client.get('events_input')[:]
        has_event = client.get('client').events.get('send').wait(timeout=1)
        assert has_event
        client.get('client').events.get('send').clear()
        assert client.get('rtm_read').call_count - read_count >= 1
        assert client.get('rtm_send_message').call_count - send_count == 1
        args, kwargs = client.get('rtm_send_message').call_args
        assert kwargs.get('channel') == CHANNEL
        return kwargs.get('message')

    def random_string(self, start=0, end=9000):
        """
        Generate a string based on a random number.
        """
        return str(randint(start, end))

    def test_simple_chat(self, client):
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
        assert self.query_bot(client, 'list'), ('1. Interesting Facts\n'
                                                '2. Strange Facts\n'
                                                '3. Unusual Facts')

        for i, connection in enumerate(client.get('client').bot_connections):
            assert self.query_bot(client, 'start_session {}'.format(
                connection['name'])) == 'You are now chatting with {}.'.format(
                    connection['name'])
            assert self.query_bot(
                client, self.random_string()).find(connection['name']) == 0
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
            client,
            'end_session') == 'You are currently not in an active session.'
        assert self.query_bot(client, 'start_session Unusual Facts'
                              ) == 'You are now chatting with Unusual Facts.'
        assert self.query_bot(
            client, 'start_session Strange Facts'
        ) == 'You are already in a chat session with Unusual Facts!'
