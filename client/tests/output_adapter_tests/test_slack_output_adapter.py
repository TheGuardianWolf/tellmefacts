import pytest
from client.output import Slack
from chatterbot.conversation import Statement
from slackclient import SlackClient


@pytest.fixture()
def slack_adapter(mocker):
    mock_api_call = {'ok': True}
    mocker.patch(
        'slackclient.SlackClient.api_call', return_value=mock_api_call)
    mocker.patch('slackclient.SlackClient.rtm_read')
    mocker.patch('slackclient.SlackClient.rtm_send_message', autospec=True)
    sc = SlackClient('xoxp-1234123412341234-12341234-1234')
    s = Slack(slack_client=sc, bot_name='tellmefacts')
    return s


class TestSlackOutputAdapter(object):
    def test_init(self, slack_adapter):
        assert slack_adapter.user_id == 'fakeid'
        assert slack_adapter.bot_id == 'fakebotid'
        assert slack_adapter.default_channel == '#general'

    def test_send_message(self, slack_adapter):
        slack_adapter.send_message(Statement('hi'), 'abcd')
        print(slack_adapter.slack_client.api_call.call_args)
        slack_adapter.slack_client.server.websocket = True
        slack_adapter.send_message(Statement('hi'), 'abcd')
        print(slack_adapter.slack_client.rtm_send_message.call_args)
        assert 0

    def test_process_response(self, slack_adapter, mocker):
        input_statement = Statement('input', extra_data={'channel': 'abcd'})

        chatbot = mocker.patch.object(slack_adapter.chatbot)
        chatbot.conversation_sessions = {'session_id': {}}

        session = mocker.patch.object(
            chatbot.conversation_sessions['session_id'])
        session.conversation.return_value = input_statement

        assert slack_adapter.process_response(Statement('test')) == 'test'
        print(slack_adapter.slack_client.api_call.call_args)
        assert 0
