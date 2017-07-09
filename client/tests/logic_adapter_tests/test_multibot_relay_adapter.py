import pytest
from chatterbot.conversation import Statement
from client.logic import MultibotRelayAdapter


@pytest.fixture()
def multibot_adapter():
    bot_connections = [{
        'name': 'test_bot_1',
        'url': 'http://dummybot_1'
    }, {
        'name': 'test_bot_2',
        'url': 'http://dummybot_2'
    }, {
        'name': 'test_bot_3',
        'url': 'http://dummybot_3'
    }]
    return MultibotRelayAdapter(bot_connections=bot_connections)


class TestMultibotRelayAdapter(object):
    def call_handler(self, multibot_adapter, command, args=None, match=None):
        handler = getattr(multibot_adapter, command)
        if args is None:
            response = handler()
        else:
            response = handler(args)
        assert isinstance(response, str)
        if match is not None:
            assert response == match
        return response

    def process(self, multibot_adapter, text, confidence=None, match=None):
        response_statement = multibot_adapter.process(text)
        assert isinstance(response_statement, Statement)
        if confidence is not None:
            assert response_statement.confidence == confidence
        if match is not None:
            assert response_statement.text == match
        return response_statement

    def test_list(self, multibot_adapter):
        self.call_handler(
            multibot_adapter,
            'list',
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_start_session_valid(self, multibot_adapter):
        self.call_handler(
            multibot_adapter,
            'start_session',
            'test_bot_1',
            match='You are now chatting with test_bot_1.')

    def test_start_session_invalid(self, multibot_adapter):
        self.call_handler(
            multibot_adapter,
            'start_session',
            'test_bot_-1',
            match=('Sorry, no bot with that name was found. Type \'list\' to '
                   'see available bots.'))

    def test_start_session_none(self, multibot_adapter):
        self.call_handler(
            multibot_adapter,
            'start_session',
            '',
            match=('No bot name was provided. Type \'list\' to see available '
                   'bots.'))

    def test_end_session_valid(self, multibot_adapter):
        self.call_handler(multibot_adapter, 'start_session', 'test_bot_1')
        self.call_handler(
            multibot_adapter,
            'end_session',
            match='Chat session with test_bot_1 ended.')

    def test_end_session_invalid(self, multibot_adapter):
        self.call_handler(
            multibot_adapter,
            'end_session',
            match=('You are currently not in an active session.'))

    def test_process_list_with_args(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('list arg'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_end_session_with_args(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('end_session arg'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_chat_before_connected(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('test'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_list_before_connected(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('list'),
            confidence=1,
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_process_connect_valid(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_1'),
            confidence=1,
            match='You are now chatting with test_bot_1.')

    def test_process_connect_invalid(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_-1'),
            confidence=1,
            match=('Sorry, no bot with that name was found. Type \'list\' to '
                   'see available bots.'))

    def test_process_connect_none(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('start_session'),
            confidence=1,
            match=('No bot name was provided. Type \'list\' to see available '
                   'bots.'))

    def test_process_list_while_connected(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('list'),
            confidence=1,
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_process_connect_valid_while_connected(self, multibot_adapter):
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_2'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_connect_invalid_while_connected(self, multibot_adapter):
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_-1'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_connect_none_while_connected(self, multibot_adapter):
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_chat_while_connected(self, mocker, multibot_adapter):
        self.process(multibot_adapter, Statement('start_session test_bot_1'))

        mock_response = (200, 'success')
        mocker.patch.object(
            multibot_adapter.state.bot, 'ask', return_value=mock_response)
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match='test_bot_1: success')

        mock_response[0] = 404
        mock_response[1] = 'Not found'
        # mock_not_found = (404, 'Not found')
        # mocker.patch.object(
        #     multibot_adapter.state.bot, 'ask', return_value=mock_not_found)
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match=('test_bot_1: Selected bot is currently unavailable, please '
                   'try again later. (Error: {})'.format('404')))
        
        multibot_adapter.state.bot.ask.side_effect = ValueError
        # mocker.patch.object(
        #     multibot_adapter.state.bot, 'ask', side_effect=ValueError)
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match=('test_bot_1: Selected bot is currently unavailable, please '
                   'try again later. (Error: Connection not established)'))

    def test_process_disconnect_while_connected(self, multibot_adapter):
        self.process(multibot_adapter, Statement('start_session test_bot_2'))
        self.process(
            multibot_adapter,
            Statement('end_session'),
            confidence=1,
            match='Chat session with test_bot_2 ended.')

    def test_process_disconnect_while_disconnected(self, multibot_adapter):
        self.process(
            multibot_adapter,
            Statement('end_session'),
            confidence=1,
            match='You are currently not in an active session.')
