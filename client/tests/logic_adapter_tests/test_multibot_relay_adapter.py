from unittest import TestCase
from chatterbot.conversation import Statement
from client.logic import MultibotRelayAdapter


class MultibotRelayAdapterTests(TestCase):
    def setUp(self):
        self.bot_connections = [{
            'name': 'test_bot_1',
            'url': 'http://dummybot_1'
        }, {
            'name': 'test_bot_2',
            'url': 'http://dummybot_2'
        }, {
            'name': 'test_bot_3',
            'url': 'http://dummybot_3'
        }]
        self.adapter = MultibotRelayAdapter(
            bot_connections=self.bot_connections)

    def call_handler(self, command, args=None, match=None):
        handler = getattr(self.adapter, command)
        if args is None:
            response = handler()
        else:
            response = handler(args)
        self.assertIsInstance(response, str)
        if match is not None:
            self.assertEqual(response, match)
        return response

    def process(self, text, confidence=None, match=None):
        response_statement = self.adapter.process(text)
        self.assertIsInstance(response_statement, Statement)
        if confidence is not None:
            self.assertEqual(response_statement.confidence, confidence)
        if match is not None:
            self.assertEqual(response_statement.text, match)
        return response_statement

    def test_list(self):
        self.call_handler('list', None, ('1. test_bot_1\n'
                                         '2. test_bot_2\n'
                                         '3. test_bot_3'))

    def test_start_session_valid(self):
        self.call_handler('start_session', 'test_bot_1',
                          'You are now chatting with test_bot_1.')

    def test_start_session_invalid(self):
        self.call_handler('start_session', 'test_bot_-1', (
            'Sorry, no bot with that name was found. Type \'list\' to '
            'see available bots.'))

    def test_start_session_none(self):
        self.call_handler(
            'start_session', '',
            'No bot name was provided. Type \'list\' to see available bots.')

    def test_end_session_valid(self):
        self.call_handler('start_session', 'test_bot_1')
        self.call_handler('end_session', None,
                          'Chat session with test_bot_1 ended.')

    def test_end_session_invalid(self):
        self.call_handler('end_session', None,
                          'You are currently not in an active session.')

    def test_process_list_with_args(self):
        self.process(
            Statement('list arg'), 0.1,
            ('You are currently not connected to any bot. '
             'Connect to a bot with \'start_session <bot_name>\' or '
             'type \'list\' for a list of available bots.'))

    def test_process_end_session_with_args(self):
        self.process(
            Statement('end_session arg'), 0.1,
            ('You are currently not connected to any bot. '
             'Connect to a bot with \'start_session <bot_name>\' or '
             'type \'list\' for a list of available bots.'))

    def test_process_chat_before_connected(self):
        self.process(
            Statement('test'), 0.1,
            ('You are currently not connected to any bot. '
             'Connect to a bot with \'start_session <bot_name>\' or '
             'type \'list\' for a list of available bots.'))

    def test_process_list_before_connected(self):
        self.process(
            Statement('list'), 1, ('1. test_bot_1\n'
                                   '2. test_bot_2\n'
                                   '3. test_bot_3'))

    def test_process_connect_valid(self):
        self.process(
            Statement('start_session test_bot_1'), 1,
            'You are now chatting with test_bot_1.')

    def test_process_connect_invalid(self):
        self.process(
            Statement('start_session test_bot_-1'), 1,
            ('Sorry, no bot with that name was found. Type \'list\' to '
             'see available bots.'))

    def test_process_connect_none(self):
        self.process(
            Statement('start_session'), 1,
            'No bot name was provided. Type \'list\' to see available bots.')

    def test_process_list_while_connected(self):
        self.process(
            Statement('list'), 1, ('1. test_bot_1\n'
                                   '2. test_bot_2\n'
                                   '3. test_bot_3'))

    def test_process_connect_valid_while_connected(self):
        self.process(Statement('start_session test_bot_1'))
        self.process(
            Statement('start_session test_bot_2'), 1,
            'You are already in a chat session with test_bot_1!')

    def test_process_connect_invalid_while_connected(self):
        self.process(Statement('start_session test_bot_1'))
        self.process(
            Statement('start_session test_bot_-1'), 1,
            'You are already in a chat session with test_bot_1!')

    def test_process_connect_none_while_connected(self):
        self.process(Statement('start_session test_bot_1'))
        self.process(
            Statement('start_session'), 1,
            'You are already in a chat session with test_bot_1!')

    def test_process_chat_while_connected(self):
        self.process(Statement('start_session test_bot_1'))

        response_statement = self.process(Statement('hello'), 1)

        try:
            (status, response) = self.adapter.state.bot.ask('hello')
            assert status == 200
        except AssertionError:
            response = (
                'test_bot_1: Selected bot is currently unavailable, please try'
                ' again later. (Error: {})'.format(str(status)))
            self.assertEqual(response, str(response_statement))
        except ValueError:
            response = (
                'test_bot_1: Selected bot is currently unavailable, please try'
                ' again later. (Error: Connection not established)')
            self.assertEqual(response, str(response_statement))
        else:
            self.assertIsInstance(response_statement, Statement)

    def test_process_disconnect_while_connected(self):
        self.process(Statement('start_session test_bot_2'))
        self.process(
            Statement('end_session'), 1, 'Chat session with test_bot_2 ended.')

    def test_process_disconnect_while_disconnected(self):
        self.process(
            Statement('end_session'), 1,
            'You are currently not in an active session.')
