# -*- coding: utf-8 -*-
import pytest
from client.input import Slack
from slackclient import SlackClient


@pytest.fixture()
def slack_adapter(mocker):
    """
    Create a slack input adapter.
    """
    # Create a combined api response object for user id and bot id
    mock_api_call = {
        'ok': True,
        'user_id': 'fakeid',
        'user': {
            'profile': {
                'bot_id': 'fakebotid'
            }
        }
    }

    # Patch slackclient to not send requests
    mocker.patch(
        'slackclient.SlackClient.api_call', return_value=mock_api_call)
    mocker.patch(
        'slackclient.SlackClient.rtm_connect', return_value=True)
    mocker.patch(
        'slackclient.SlackClient.rtm_read')
    sc = SlackClient('xoxp-1234123412341234-12341234-1234')
    s = Slack(slack_client=sc, bot_name='tellmefacts', start_event_loop=False)
    yield s

    # Cleanup slack client
    try:
        s.close()
    except AttributeError:
        pass


class TestSlackInputAdapter(object):
    def test_slack(self, slack_adapter):
        """
        Test object attributes.
        """
        assert slack_adapter.user_id == 'fakeid'
        assert slack_adapter.bot_id == 'fakebotid'

    def test_start(self, slack_adapter):
        """
        Test starting the event loop.
        """
        slack_adapter.start()
        assert slack_adapter.events.get('input_ready').is_set()

    def test_close(self, slack_adapter):
        """
        Test closing the event loop.
        """
        slack_adapter.start()
        slack_adapter.close()
        assert not slack_adapter.events.get('input_ready').is_set()
        assert slack_adapter.event_thread is not None

    def test_event_loop(self, slack_adapter, mocker):
        """
        Test event loop actions.
        """
        # Set new event to be given to the loop
        mock_events = [{
            'type': 'message',
            'text': 'test'
        }]
        SlackClient.rtm_read.return_value = mock_events
        slack_adapter.start()

        # Check that the input is set as ready
        assert slack_adapter.events.get('input_ready').is_set()

        # Wait for a message event
        assert slack_adapter.events.get('message').wait(timeout=1)

        # Check message data is what was put in
        message_data = slack_adapter.events.get('message').data.get_nowait()
        assert message_data is mock_events[0]

    def test_process_input(self, slack_adapter, mocker):
        """
        Test processing of messages from the event loop.
        """
        # Set the mock message to mention the bot
        mock_message = {
            'type': 'message',
            'text': '<@fakeid> test'
        }
        slack_adapter.events.get('message').data.put(mock_message)
        statement = slack_adapter.process_input(None)

        # Check that the statement is as expected
        assert str(statement) == 'test'
        assert statement.extra_data is mock_message
