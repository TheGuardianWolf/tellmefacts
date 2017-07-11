# -*- coding: utf-8 -*-
import pytest
from client.input import Slack
from slackclient import SlackClient
from threading import Thread, Event
from time import sleep
from queue import Empty


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
    mocker.patch('slackclient.SlackClient.rtm_connect', return_value=True)
    mocker.patch('slackclient.SlackClient.rtm_read')
    sc = SlackClient('xoxp-1234123412341234-12341234-1234')
    s = Slack(slack_client=sc, bot_name='tellmefacts', start_event_loop=False)
    yield s

    # Cleanup slack adapter
    s.close()


class TestSlackInputAdapter(object):
    def test_slack(self, slack_adapter):
        """
        Test object attributes.
        """
        assert slack_adapter.user_id == 'fakeid'
        assert slack_adapter.bot_id == 'fakebotid'

    def test_get_user_id_fail(self, slack_adapter, mocker):
        """
        Test when the user id is not found from Slack API response.
        """
        # Patch the slack client object's api call to return a bad response
        mocker.patch.object(
            slack_adapter.slack_client, 'api_call', return_value={'ok': False})

        # Should give a error when Slack API request fails
        with pytest.raises(ValueError):
            slack_adapter.get_user_id()

    def test_get_bot_id_fail(self, slack_adapter, mocker):
        """
        Test when the bot id is not found from Slack API response.
        """
        # Patch the slack client object's api call to return a bad response
        mocker.patch.object(
            slack_adapter.slack_client, 'api_call', return_value={'ok': False})\

        # Should give a error when Slack API request fails
        with pytest.raises(ValueError):
            # Use stored user id from fixture
            slack_adapter.get_bot_id()

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
        mock_events = [{'type': 'message', 'text': 'test'}]
        SlackClient.rtm_read.return_value = mock_events
        slack_adapter.start()

        # Check that the input is set as ready
        assert slack_adapter.events.get('input_ready').is_set()

        # Wait for a message event
        assert slack_adapter.events.get('message').wait(timeout=1)

        # Check message data is what was put in
        message_data = slack_adapter.events.get('message').data.get_nowait()
        assert message_data is mock_events[0]

    def test_process_input_mention(self, slack_adapter, mocker):
        """
        Test processing of various types of messages.
        """
        # Put the mock messages inside the data event queue
        mock_messages = [{
            'type': 'message',
            'text': '<@fakeid> self mention',
            'bot_id': 'fakebotid'
        }, {
            'type': 'message',
            'text': 'nomention'
        }, {
            'type': 'message',
            'text': '<@fakeid> mention'
        }]

        for message in mock_messages:
            slack_adapter.events.get('message').data.put(message)

        statement = None

        def worker():
            # Process until a vaild input is read (should be the last one)
            nonlocal statement
            statement = slack_adapter.process_input(None)

        # Run the loop on another thread in case it hangs (likely if code is
        # broken)
        t = Thread(target=worker, daemon=True)
        t.start()
        t.join(timeout=3)
        assert not t.is_alive()

        # Check that the statement is as expected
        assert str(statement) == 'mention'
        assert statement.extra_data is mock_messages[2]

    def test_process_input_close(self, slack_adapter, monkeypatch):
        """
        Test closing the process input loop before any valid data is recieved,
        should raise an exception that must be caught.
        """
        exception_raised = False

        def worker():
            try:
                slack_adapter.process_input(None)
            except StopIteration:
                nonlocal exception_raised
                exception_raised = True

        get_called = Event()

        def mock_get(timeout=1):
            get_called.set()
            sleep(timeout)
            raise Empty

        # Patch the get function to set an event when called
        monkeypatch.setattr(
            slack_adapter.events.get('message').data, 'get', mock_get)

        # Test closing whilst waiting for an event
        t = Thread(target=worker, daemon=True)
        t.start()
        assert get_called.wait(timeout=3)
        slack_adapter.close()
        t.join(timeout=3)
        assert not t.is_alive()
        assert exception_raised

        # Test closing whilst waiting for data
        exception_raised = False
        get_called.clear()
        t = Thread(target=worker, daemon=True)
        t.start()  # Close event hasn't been reset, so should end immediately
        t.join(timeout=3)
        assert not t.is_alive()
        assert exception_raised
        assert not get_called.is_set()  # Inner loop should not run