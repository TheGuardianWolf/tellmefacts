# -*- coding: utf-8 -*-
import pytest
from chatterbot.conversation import Statement
from client.logic import MultibotRelayAdapter
from client.services import BotConnectionManager, KeywordManager


@pytest.fixture()
def multibot_adapter():
    """
    Create a multibot relay logic adapter object.
    """
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


@pytest.fixture()
def relay_state():
    """
    Create a relay state object.
    """
    return MultibotRelayAdapter.RelayState()


@pytest.fixture()
def keyword_command():
    """
    Create a keyword command object.
    """
    return MultibotRelayAdapter.KeywordCommand(**{
        'keyword': 'test',
        'has_args': False,
        'session_ignore': False,
        'handler': None
    })


class TestMultibotRelayAdapter(object):
    def call_handler(self, multibot_adapter, command, args=None, match=None):
        """
        Helper method to call a logic adapter command and test the response
        against a string.
        """
        # Get the keyword handler
        handler = getattr(multibot_adapter, command)
        if args is None:
            response = handler()
        else:
            response = handler(args)

        # Check that the response is a string
        assert isinstance(response, str)

        # Check that the response is as expected
        if match is not None:
            assert response == match

        return response

    def process(self, multibot_adapter, text, confidence=None, match=None):
        """
        Helper method to run the process method, test the response against a
        string and check confidence.
        """
        response_statement = multibot_adapter.process(text)

        # Check that the response is a `Statement`
        assert isinstance(response_statement, Statement)

        # Check the confidence of the response
        if confidence is not None:
            assert response_statement.confidence == confidence

        # Check that the response is as expected
        if match is not None:
            assert response_statement.text == match

        return response_statement

    def test_multibot_relay_adapter(self, multibot_adapter):
        """
        Test object attributes.
        """
        assert isinstance(multibot_adapter.state, multibot_adapter.RelayState)
        assert isinstance(multibot_adapter.bot_connections,
                          BotConnectionManager)
        assert isinstance(multibot_adapter.keywords, KeywordManager)

    def test_list(self, multibot_adapter):
        """
        Test listing the available bots.
        """
        self.call_handler(
            multibot_adapter,
            'list',
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_start_session_valid(self, multibot_adapter):
        """
        Test starting a session with a valid bot name as an argument.
        """
        self.call_handler(
            multibot_adapter,
            'start_session',
            'test_bot_1',
            match='You are now chatting with test_bot_1.')

    def test_start_session_invalid(self, multibot_adapter):
        """
        Test starting a session with an invalid bot name as an argument.
        """
        self.call_handler(
            multibot_adapter,
            'start_session',
            'test_bot_-1',
            match=('Sorry, no bot with that name was found. Type \'list\' to '
                   'see available bots.'))

    def test_start_session_none(self, multibot_adapter):
        """
        Test starting a session with no argument provided.
        """
        self.call_handler(
            multibot_adapter,
            'start_session',
            '',
            match=('No bot name was provided. Type \'list\' to see available '
                   'bots.'))

    def test_end_session_valid(self, multibot_adapter):
        """
        Test starting a session with a session in place.
        """
        self.call_handler(multibot_adapter, 'start_session', 'test_bot_1')
        self.call_handler(
            multibot_adapter,
            'end_session',
            match='Chat session with test_bot_1 ended.')

    def test_end_session_invalid(self, multibot_adapter):
        """
        Test ending a session with no current session.
        """
        self.call_handler(
            multibot_adapter,
            'end_session',
            match=('You are currently not in an active session.'))

    def test_process_list_with_args(self, multibot_adapter):
        """
        Test processing a statement containing the list command.
        """
        self.process(
            multibot_adapter,
            Statement('list arg'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_end_session_with_args(self, multibot_adapter):
        """
        Test processing a statement containing the end session command with
        arguments (not a valid command).
        """
        self.process(
            multibot_adapter,
            Statement('end_session arg'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_chat_before_connected(self, multibot_adapter):
        """
        Test processing a statement containing a chat string before being
        connected to a bot.
        """
        self.process(
            multibot_adapter,
            Statement('test'),
            confidence=0.1,
            match=(('You are currently not connected to any bot. '
                    'Connect to a bot with \'start_session <bot_name>\' or '
                    'type \'list\' for a list of available bots.')))

    def test_process_list_before_connected(self, multibot_adapter):
        """
        Test processing a statement containing the list command before being
        connected.
        """
        self.process(
            multibot_adapter,
            Statement('list'),
            confidence=1,
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_process_connect_valid(self, multibot_adapter):
        """
        Test processing a statement containing the connect command with valid
        arguments.
        """
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_1'),
            confidence=1,
            match='You are now chatting with test_bot_1.')

    def test_process_connect_invalid(self, multibot_adapter):
        """
        Test processing a statement containing the connect command with an
        unrecognised bot name.
        """
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_-1'),
            confidence=1,
            match=('Sorry, no bot with that name was found. Type \'list\' to '
                   'see available bots.'))

    def test_process_connect_none(self, multibot_adapter):
        """
        Test processing a statement containing the connect command with no bot
        specified.
        """
        self.process(
            multibot_adapter,
            Statement('start_session'),
            confidence=1,
            match=('No bot name was provided. Type \'list\' to see available '
                   'bots.'))

    def test_process_list_while_connected(self, multibot_adapter):
        """
        Test processing a statement containing the list command whilst
        connected to a bot.
        """
        self.process(
            multibot_adapter,
            Statement('list'),
            confidence=1,
            match=('1. test_bot_1\n'
                   '2. test_bot_2\n'
                   '3. test_bot_3'))

    def test_process_connect_valid_while_connected(self, multibot_adapter):
        """
        Test processing a statement containing the connect command whilst
        connected to a bot.
        """
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_2'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_connect_invalid_while_connected(self, multibot_adapter):
        """
        Test processing a statement containing the connect command with an
        unrecognised bot name whilst connected to a bot.
        """
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session test_bot_-1'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_connect_none_while_connected(self, multibot_adapter):
        """
        Test processing a statement containing the connect command with no bot
        specified whist connected to a bot.
        """
        self.process(multibot_adapter, Statement('start_session test_bot_1'))
        self.process(
            multibot_adapter,
            Statement('start_session'),
            confidence=1,
            match='You are already in a chat session with test_bot_1!')

    def test_process_chat_while_connected(self, mocker, multibot_adapter):
        """
        Test processing a statement containing a chat message whilst connected
        to a bot.
        """
        self.process(multibot_adapter, Statement('start_session test_bot_1'))

        # Patch the bot ask method to return a mock response instead of
        # actually sending a request.
        mock_response = [200, 'success']  # Real response is a tuple, not list
        mocker.patch.object(
            multibot_adapter.state.bot, 'ask', return_value=mock_response)
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match='test_bot_1: success')

        # Change the response to not found
        mock_response[0] = 404
        mock_response[1] = 'Not found'
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match=('test_bot_1: Selected bot is currently unavailable, please '
                   'try again later. (Error: {})'.format('404')))

        # Change the response to raise a ValueError (invalid response)
        multibot_adapter.state.bot.ask.side_effect = ValueError
        self.process(
            multibot_adapter,
            Statement('hello'),
            confidence=1,
            match=('test_bot_1: Selected bot is currently unavailable, please '
                   'try again later. (Error: Connection not established)'))

    def test_process_disconnect_while_connected(self, multibot_adapter):
        """
        Test processing a statement containing the end session command whilst
        connected to a bot.
        """
        self.process(multibot_adapter, Statement('start_session test_bot_2'))
        self.process(
            multibot_adapter,
            Statement('end_session'),
            confidence=1,
            match='Chat session with test_bot_2 ended.')

    def test_process_disconnect_while_disconnected(self, multibot_adapter):
        """
        Test processing a statement containing the end session command whilst
        not connected.
        """
        self.process(
            multibot_adapter,
            Statement('end_session'),
            confidence=1,
            match='You are currently not in an active session.')

    class TestRelayState(object):
        def test_relay_state(self, multibot_adapter, relay_state):
            """
            Test RelayState attributes.
            """
            bc = multibot_adapter.bot_connections.get('test_bot_2')
            relay_state.bot = bc
            assert relay_state.bot is bc

    class TestKeywordCommand(object):
        def test_keyword_command(self, keyword_command):
            """
            Test object attributes.
            """
            assert not keyword_command.session_ignore

        def test_match_has_args(self, keyword_command):
            """
            Test match against the regex pattern when the string has arguments.
            """
            result = keyword_command.match('command args')
            assert len(result.groups()) == 2
            assert result.group(1) == 'command'
            assert result.group(2) == 'args'

        def test_match_no_args(self, keyword_command):
            """
            Test match against the regex pattern when the string has no
            arguments.
            """
            result = keyword_command.match('command')
            assert len(result.groups()) == 2
            assert result.group(1) == 'command'
            assert result.group(2) == ''

        def test_match_invalid(self, keyword_command):
            """
            Test match against the regex pattern when the string is empty.
            """
            result = keyword_command.match('')
            assert result is None
