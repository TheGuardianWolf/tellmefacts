from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from client.services import (KeywordManager, BotConnectionManager, Keyword)
from re import compile


class MultibotRelayAdapter(LogicAdapter):
    """
    Multiplexes chat conversations to supported bots.
    """

    def __init__(self, **kwargs):
        super(MultibotRelayAdapter, self).__init__(**kwargs)

        bot_connections = kwargs.get('bot_connections', [])

        self.state = self.RelayState()
        self.bot_connections = BotConnectionManager(bot_connections)
        self.keywords = KeywordManager([{
            'type': self.KeywordCommand,
            'keyword': 'list',
            'has_args': False,
            'session_ignore': False,
            'handler': self.list
        }, {
            'type': self.KeywordCommand,
            'keyword': 'start_session',
            'has_args': True,
            'session_ignore': False,
            'handler': self.start_session
        }, {
            'type': self.KeywordCommand,
            'keyword': 'end_session',
            'has_args': False,
            'session_ignore': False,
            'handler': self.end_session
        }])

    def process(self, statement):
        """
        Infer either a command or chat message from the given statement.

        :param statement: An input statement to be processed.
        :type statement: Statement

        :returns: A processed response.
        :rtype: Statement
        """
        response_statement = Statement('')
        response_statement.confidence = 0

        # Look for a keyword command pattern match
        result = self.KeywordCommand.match(statement.text)

        # Possible command
        if result is not None:
            command = self.keywords.get(result.group(1))
            if command is not None:
                # Currently not connected, or command is not set to be ignored
                if self.state.bot is None or not command.session_ignore:
                    try:
                        response_statement = Statement(
                            command.handle(result.group(2)))
                        response_statement.confidence = 1
                        return response_statement
                    except ValueError:
                        # Happens when args not provided
                        pass

        # Statement treated as message to be sent to the selected bot
        if self.state.bot is not None:
            # Send a request for a response from the bot
            response_statement = Statement(self.bot_request(statement.text))
            response_statement.confidence = 1
        else:
            # No bot selected
            response_statement = Statement(
                ('You are currently not connected to any bot. '
                 'Connect to a bot with \'start_session <bot_name>\' or '
                 'type \'list\' for a list of available bots.'))
            response_statement.confidence = 0.1
        return response_statement

    def bot_request(self, text):
        """
        Send a request for a response to the currently selected
        `BotConnection`.

        :param text A message to send to the selected bot.

        :returns: A response from the bot.
        """
        bot = self.state.bot
        try:
            (status, response) = bot.ask(text)
            assert status == 200
        except AssertionError:
            # Some HTTP error occured
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: {})'.format(str(status)))
        except ValueError:
            # Some connection error occured
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: Connection not established)')

        response_statement = Statement(bot.name + ': ' + response)

        return response_statement

    def list(self):
        """
        List the currently available `BotConnection`s.

        :returns: A formatted text list of available bots.
        """
        statement = ''
        for i, bot in enumerate(self.bot_connections.all()):
            statement += '{}. {}\n'.format(str(i + 1), bot.name)
        statement = statement.rstrip('\n')  # Remove the last newline
        return statement

    def start_session(self, args=None):
        """
        Set a bot as the current `BotConnection`.

        :param args The name of a bot.

        :returns: A text response based on current connected status.
        """
        # Assign new bot if not set
        if self.state.bot is None:
            # Error if no args was provided
            if args is None or len(args) == 0:
                return ('No bot name was provided. Type \'list\' to see'
                        ' available bots.')

            try:
                bot = self.bot_connections.get(args)
                self.state.bot = bot
                return 'You are now chatting with {}.'.format(bot.name)
            except AttributeError:
                # Bot not found (is NoneType)
                pass
        else:
            return 'You are already in a chat session with {}!'.format(
                self.state.bot.name)

        # Nothing found with that name
        return ('Sorry, no bot with that name was found. Type \'list\' to '
                'see available bots.')

    def end_session(self):
        """
        Remove the currently selected `BotConnection`.

        :returns: A status message.
        """

        # Set current bot to None if is set
        if self.state.bot is None:
            return 'You are currently not in an active session.'
        else:
            bot_name = self.state.bot.name
            self.state.bot = None
            return 'Chat session with {} ended.'.format(bot_name)

    class RelayState(object):
        """
        Represents the current state of a relay object.
        """

        def __init__(self):
            self.bot = None  # Currently connected bot `BotConnection`

    class KeywordCommand(Keyword):
        """
        Represents a command that can be intercepted from a message. Commands
        are intended to modify operation of the bot in some way.
        """

        command_regexp = compile('^([^ ]+) ?(.*)$')  # Command regex pattern

        @classmethod
        def match(self, test):
            """
            Check if a test string matches the command pattern

            :param test: A text string to test.

            :returns: Return value of a regex match with the command pattern.
            """
            return self.command_regexp.match(test)

        def __init__(self, keyword, has_args, handler, **kwargs):
            super(MultibotRelayAdapter.KeywordCommand, self).__init__(
                keyword, has_args, handler)
            self.session_ignore = kwargs.get('session_ignore', False)
