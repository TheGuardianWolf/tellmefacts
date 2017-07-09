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
        assert slack_adapter.default_channel == '#general'

    def test_send_message(self, slack_adapter):
        slack_adapter.send_message(Statement('hi'), 'abcd')
        assert slack_adapter.slack_client.api_call.called
        args, kwargs = slack_adapter.slack_client.api_call.call_args
        assert kwargs['text'] == 'hi'
        assert kwargs['channel'] == 'abcd'
        assert not kwargs['as_user']

        slack_adapter.slack_client.server.websocket = True
        slack_adapter.send_message(Statement('hi'), 'abcd')
        assert slack_adapter.slack_client.rtm_send_message.called
        args, kwargs = slack_adapter.slack_client.rtm_send_message.call_args
        assert kwargs['message'] == 'hi'
        assert kwargs['channel'] == 'abcd'

    def test_process_response(self, slack_adapter, mocker, monkeypatch):
        mock_sessions = mocker.Mock(conversation_sessions=mocker.Mock(
            get=mocker.Mock(return_value=mocker.Mock(conversation=mocker.Mock(
                get_last_input_statement=mocker.Mock(return_value=Statement(
                    'input', extra_data={'channel': 'abcd'})))))))
        monkeypatch.setattr(slack_adapter, 'chatbot', mock_sessions)
        assert str(slack_adapter.process_response(Statement('test'))) == 'test'
        assert slack_adapter.slack_client.api_call.called
        args, kwargs = slack_adapter.slack_client.api_call.call_args
        assert kwargs['text'] == 'test'
        assert kwargs['channel'] == 'abcd'
        assert not kwargs['as_user']
