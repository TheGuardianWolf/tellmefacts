from unittest import TestCase
from chatterbot.conversation import Statement
from client.logic import MultibotRelayAdapter
from client.services import RelayState, BotConnection


class MultibotRelayAdapterTests(TestCase):
    def setUp(self):
        self.state = RelayState()
        self.bot_connections = [
            BotConnection('test_bot_1', 'http://dummybot_1'),
            BotConnection('test_bot_2', 'http://dummybot_2'),
            BotConnection('test_bot_3', 'http://dummybot_3')
        ]
        self.adapter = MultibotRelayAdapter(
            bot_connections=self.bot_connections,
            relay_state=self.state)

    def call_method(self, command, args=None):
        handler = getattr(self.adapter, command)
        if args is not None:
            (confidence, response_statement) = handler()
        else:
            (confidence, response_statement) = handler(args)
        self.assertEqual(confidence, 1)
        self.assertIsInstance(response_statement, Statement)
        return response_statement

    def test_list(self):
        response_statement = self.call_method('list')
        self.assertEqual(
            str(response_statement), ('1. test_bot_1\n'
                                      '2. test_bot_2\n'
                                      '3. test_bot_3'))

    def test_start_session_valid(self):
        response_statement = self.call_method('start_session', 'test_bot_1')
        self.assertEqual(
            str(response_statement), 'You are now chatting with test_bot_1.')

    def test_start_session_invalid(self):
        response_statement = self.call_method('start_session', 'test_bot_-1')
        self.assertEqual(
            str(response_statement),
            ('Sorry, no bot with that name was found. Type \'list\' to '
             'see available bots.'))

    def test_start_session_none(self):
        response_statement = self.call_method('start_session', '')
        self.assertEqual(
            str(response_statement),
            ('No bot name was provided. Type \'list\' to see available bots.'))

    def test_end_session_valid(self):
        self.call_method('start_session', 'test_bot_1')
        response_statement = self.call_method('end_session')
        self.assertEqual(
            str(response_statement), 'Chat session with test_bot_1 ended.')

    def test_end_session_invalid(self):
        response_statement = self.call_method('end_session')
        self.assertEqual(
            str(response_statement),
            'You are currently not in an active session.')

    def test_process_chat_before_connected(self):
        response_statement = self.call_method('process', Statement('test'))
        self.assertEqual(
            str(response_statement),
            ('You are currently not connected to any bot. '
             'Connect to a bot with \'start_session <bot_name>\' or '
             'type \'list\' for a list of available bots.'))

    def test_process_list_before_connected(self):
        response_statement = self.call_method('process', Statement('list'))
        self.assertEqual(
            str(response_statement), ('1. test_bot_1\n'
                                      '2. test_bot_2\n'
                                      '3. test_bot_3'))

    def test_process_connect_valid(self):
        response_statement = self.call_method(
            'process', Statement('start_session test_bot_1'))
        self.assertEqual(
            str(response_statement), 'You are now chatting with test_bot_1.')

    def test_process_connect_invalid(self):
        response_statement = self.call_method(
            'process', Statement('start_session test_bot_-1'))
        self.assertEqual(
            str(response_statement),
            ('Sorry, no bot with that name was found. Type \'list\' to '
             'see available bots.'))

    def test_process_connect_none(self):
        response_statement = self.call_method(
            'process', Statement('start_session'))
        self.assertEqual(
            str(response_statement),
            ('No bot name was provided. Type \'list\' to see available bots.'))

    def test_process_list_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_1'))
        response_statement = self.call_method('process', Statement('list'))
        self.assertEqual(
            str(response_statement), ('1. test_bot_1\n'
                                      '2. test_bot_2\n'
                                      '3. test_bot_3'))

    def test_process_connect_valid_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_1'))
        response_statement = self.call_method(
            'process', Statement('start_session test_bot_2'))
        self.assertEqual(
            str(response_statement),
            'You are already in a chat session with test_bot_1!')

    def test_process_connect_invalid_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_1'))
        response_statement = self.call_method(
            'process', Statement('start_session test_bot_-1'))
        self.assertEqual(
            str(response_statement),
            'You are already in a chat session with test_bot_1!')

    def test_process_connect_none_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_1'))
        response_statement = self.call_method(
            'process', Statement('start_session'))
        self.assertEqual(
            str(response_statement),
            ('No bot name was provided. Type \'list\' to see available bots.'))

    def test_process_chat_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_1'))

        response_statement = self.call_method(
            'process', Statement('hello'))

        try:
            (status, response) = self.state.bot.ask('test')
        except AssertionError:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: {})'.format(str(status)))
        except ValueError:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: Connection not established)')

        self.assertEqual(response, str(response_statement))

    def test_process_disconnect_while_connected(self):
        self.call_method('process', Statement('start_session test_bot_2'))
        response_statement = self.call_method(
            'process', Statement('end_session'))
        self.assertEqual(
            str(response_statement), 'Chat session with test_bot_2 ended.')

    def test_process_disconnect_while_disconnected(self):
        response_statement = self.call_method(
            'process', Statement('end_session'))
        self.assertEqual(
            str(response_statement),
            ('You are currently not connected to any bot. '
             'Connect to a bot with \'start_session <bot_name>\' or '
             'type \'list\' for a list of available bots.'))
