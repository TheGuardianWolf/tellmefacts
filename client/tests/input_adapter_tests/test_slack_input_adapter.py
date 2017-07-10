import pytest
from client.input import Slack
from slackclient import SlackClient
from queue import Queue
from threading import Event


@pytest.fixture()
def slack_adapter(mocker):
    mock_api_call = {
        'ok': True,
        'user_id': 'fakeid',
        'user': {
            'profile': {
                'bot_id': 'fakebotid'
            }
        }
    }
    mocker.patch(
        'slackclient.SlackClient.api_call', return_value=mock_api_call)
    mocker.patch(
        'slackclient.SlackClient.rtm_connect', return_value=True)
    mocker.patch(
        'slackclient.SlackClient.rtm_read')
    sc = SlackClient('xoxp-1234123412341234-12341234-1234')
    s = Slack(slack_client=sc, bot_name='tellmefacts', start_event_loop=False)
    yield s
    try:
        s.close()
    except AttributeError:
        pass


class TestSlackInputAdapter(object):
    def test_init(self, slack_adapter):
        assert slack_adapter.user_id == 'fakeid'
        assert slack_adapter.bot_id == 'fakebotid'

    def test_start(self, slack_adapter):
        slack_adapter.start()
        assert slack_adapter.events.get('input_ready').is_set()

    def test_close(self, slack_adapter):
        slack_adapter.start()
        slack_adapter.close()
        assert not slack_adapter.events.get('input_ready').is_set()
        assert slack_adapter.event_thread is not None

    def test_event_loop(self, slack_adapter, mocker):
        mock_events = [{
            'type': 'message',
            'text': 'test'
        }]
        mocker.patch(
            'slackclient.SlackClient.rtm_read', return_value=mock_events)
        slack_adapter.start()
        assert slack_adapter.events.get('input_ready').is_set()
        assert slack_adapter.events.get('message').wait(timeout=1)
        message_data = slack_adapter.events.get('message').data.get_nowait()
        assert message_data is mock_events[0]

    def test_process_input(self, slack_adapter, mocker):
        mock_message = {
            'type': 'message',
            'text': '<@fakeid> test'
        }
        slack_adapter.events.get('message').data.put(mock_message)
        statement = slack_adapter.process_input(None)
        assert str(statement) == 'test'
        assert statement.extra_data is mock_message
