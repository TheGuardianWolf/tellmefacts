# -*- coding: utf-8 -*-
import pytest
from client.output import Slack
from chatterbot.conversation import Statement
from slackclient import SlackClient


@pytest.fixture()
def slack_adapter(mocker):
    """
    Create and patches for an output slack adapter.
    """
    # Patch methods in the slackclient library so that no real requests to
    # Slack are made
    mock_api_call = {'ok': True}
    mocker.patch(
        'slackclient.SlackClient.api_call', return_value=mock_api_call)
    mocker.patch('slackclient.SlackClient.rtm_read')
    mocker.patch('slackclient.SlackClient.rtm_send_message', autospec=True)
    sc = SlackClient('xoxp-1234123412341234-12341234-1234')
    s = Slack(slack_client=sc, bot_name='tellmefacts')
    return s


class TestSlackOutputAdapter(object):
    def test_slack(self, slack_adapter):
        """
        Test object attributes.
        """
        assert slack_adapter.default_channel == '#general'

    def test_send_message_api(self, slack_adapter, monkeypatch):
        """
        Test sending a full response through Slack RTM after retrieving channel
        data from the last input statement.
        """
        slack_adapter.send_message(Statement('hi'), 'abcd')

        # Check whether the call had the correct side effects
        assert slack_adapter.events.get('send').is_set()
        assert slack_adapter.slack_client.api_call.called

        # Check call args
        args, kwargs = slack_adapter.slack_client.api_call.call_args
        assert kwargs['text'] == 'hi'
        assert kwargs['channel'] == 'abcd'
        assert not kwargs['as_user']

        # Clear send event as this method is a consumer of the event
        slack_adapter.events.get('send').clear()

    def test_send_message_rtm(self, slack_adapter, monkeypatch):
        """
        Test sending a message through Slack RTM.
        """
        # Pretend that websockets is connected
        monkeypatch.setattr(slack_adapter.slack_client.server, 'websocket',
                            True)

        slack_adapter.send_message(Statement('hi'), 'abcd')

        # Check whether the call had the correct side effects
        assert slack_adapter.events.get('send').is_set()
        assert slack_adapter.slack_client.rtm_send_message.called

        # Check call args
        args, kwargs = slack_adapter.slack_client.rtm_send_message.call_args
        assert kwargs['message'] == 'hi'
        assert kwargs['channel'] == 'abcd'

        # Clear send event as this method is a consumer of the event
        slack_adapter.events.get('send').clear()

    def test_process_response_api(self, slack_adapter, mocker, monkeypatch):
        """
        Test sending a full response through Slack Web API after retrieving
        channel data from the last input statement.
        """
        # Create and set the chatbot object for this adapter to contain one
        # last input statement with a known channel.
        mock_sessions = mocker.Mock(conversation_sessions=mocker.Mock(
            get=mocker.Mock(return_value=mocker.Mock(conversation=mocker.Mock(
                get_last_input_statement=mocker.Mock(return_value=Statement(
                    'input', extra_data={'channel': 'abcd'})))))))
        monkeypatch.setattr(slack_adapter, 'chatbot', mock_sessions)

        # Test adapter echo
        assert str(slack_adapter.process_response(Statement('test'))) == 'test'

        # Check that the call produced the right side effects
        assert slack_adapter.events.get('send').is_set()
        assert slack_adapter.slack_client.api_call.called

        # Check call args
        args, kwargs = slack_adapter.slack_client.api_call.call_args
        assert kwargs['text'] == 'test'
        assert kwargs['channel'] == 'abcd'
        assert not kwargs['as_user']

        # Clear send event as this method is a consumer of the event
        slack_adapter.events.get('send').clear()

    def test_process_response_rtm(self, slack_adapter, mocker, monkeypatch):
        """
        Test sending a full response through Slack RTM after retrieving channel
        data from the last input statement.
        """
        # Create and set the chatbot object for this adapter to contain one
        # last input statement with a known channel.
        mock_sessions = mocker.Mock(conversation_sessions=mocker.Mock(
            get=mocker.Mock(return_value=mocker.Mock(conversation=mocker.Mock(
                get_last_input_statement=mocker.Mock(return_value=Statement(
                    'input', extra_data={'channel': 'abcd'})))))))
        monkeypatch.setattr(slack_adapter, 'chatbot', mock_sessions)

        # Pretend websockets is connected
        monkeypatch.setattr(slack_adapter.slack_client.server, 'websocket',
                            True)

        # Test adapter echo
        assert str(slack_adapter.process_response(Statement('test'))) == 'test'

        # Check that the call produced the right side effects
        assert slack_adapter.events.get('send').is_set()
        assert slack_adapter.slack_client.rtm_send_message.called

        # Check call args
        args, kwargs = slack_adapter.slack_client.rtm_send_message.call_args
        assert kwargs['message'] == 'test'
        assert kwargs['channel'] == 'abcd'

        # Clear send event as this method is a consumer of the event
        slack_adapter.events.get('send').clear()