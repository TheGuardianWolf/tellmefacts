from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from client.services import (KeywordManager, BotConnectionManager, RelayState,
                             KeywordCommand)


class MultibotRelayAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(MultibotRelayAdapter, self).__init__(**kwargs)

        bot_connections = kwargs.get('bot_connections', [])

        self.state = RelayState()
        self.bot_connections = BotConnectionManager(bot_connections)
        self.keywords = KeywordManager([{
            'type': 'command',
            'keyword': 'list',
            'has_args': False,
            'session_ignore': False,
            'handler': self.list
        }, {
            'type': 'command',
            'keyword': 'start_session',
            'has_args': True,
            'session_ignore': False,
            'handler': self.start_session
        }, {
            'type': 'command',
            'keyword': 'end_session',
            'has_args': False,
            'session_ignore': False,
            'handler': self.end_session
        }])

    def process(self, statement):
        response_statement = Statement('')
        response_statement.confidence = 0
        result = KeywordCommand.match(statement.text)

        if result is not None:
            command = self.keywords.get(result.group(1))
            if command is not None:
                if self.state.bot is None or not command.session_ignore:
                    try:
                        response_statement = Statement(
                            command.handle(result.group(2)))
                        response_statement.confidence = 1
                        return response_statement
                    except ValueError:
                        # Happens when args not provided
                        pass

        if self.state.bot is not None:
            response_statement = Statement(self.bot_request(statement.text))
            response_statement.confidence = 1
        else:
            response_statement = Statement(
                ('You are currently not connected to any bot. '
                 'Connect to a bot with \'start_session <bot_name>\' or '
                 'type \'list\' for a list of available bots.'))
            response_statement.confidence = 0.1
        return response_statement

    def bot_request(self, text):
        bot = self.state.bot

        try:
            (status, response) = bot.ask(text)
            assert status == 200
        except AssertionError:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: {})'.format(str(status)))
        except ValueError:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: Connection not established)')

        response_statement = Statement(bot.name + ': ' + response)

        return response_statement

    def list(self):
        statement = ''
        for i, bot in enumerate(self.bot_connections.all()):
            statement += '{}. {}\n'.format(str(i + 1), bot.name)
        statement = statement.rstrip('\n')
        return statement

    def start_session(self, args=None):
        if self.state.bot is None:
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

        return ('Sorry, no bot with that name was found. Type \'list\' to '
                'see available bots.')

    def end_session(self):
        if self.state.bot is None:
            return 'You are currently not in an active session.'
        else:
            bot_name = self.state.bot.name
            self.state.bot = None
            return 'Chat session with {} ended.'.format(bot_name)
