from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from ..services import KeywordManager


class MultibotRelayAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(MultibotRelayAdapter, self).__init__(**kwargs)

        self.bot_connections = kwargs.get('bot_connections', [])
        self.state = kwargs.get('state')
        if not isinstance(self.bot_connections, list):
            raise TypeError('Bot connections should be a list.')
        elif len(self.bot_connections) == 0:
            raise ValueError(('No bot connections have been provided.'))

        self.keywords = KeywordManager([
            {
                'type': 'command',
                'keyword': 'list',
                'has_args': False,
                'session_ignore': False,
                'handler': self.list
            },
            {
                'type': 'command',
                'keyword': 'start_session',
                'has_args': True,
                'session_ignore': False,
                'handler': self.start_session
            },
            {
                'type': 'command',
                'keyword': 'end_session',
                'has_args': False,
                'session_ignore': False,
                'handler': self.end_session
            }
        ])

    def process(self, statement):
        confidence = 1
        response_statement = Statement('')

        result = KeywordCommand.match(statement.text)

        if result is not None:
            command = self.keywords.get('command', result.group(1))
            if self.state.bot is None or not command.session_ignore:
                try:
                    return command.handle(result.group(2))
                except ValueError:
                    # Happens when a user enters args for a no-args
                    # command
                    pass

        if self.state.bot is not None:
            (confidence, response_statement) = self.bot_request(statement.text)
        else:
            confidence = 1
            response_statement = Statement(
                ('You are currently not connected to any bot. '
                 'Connect to a bot with \'start_session <bot_name>\' or '
                 'type \'list\' for a list of available bots.'))
        return confidence, response_statement

    def bot_request(self, text):
        confidence = 1

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

        return (confidence, response_statement)

    def list(self):
        statement = ''
        for i, bot in enumerate(self.bot_connections.all()):
            statement += '{}. {}\n'.format(str(i + 1), bot.name)
        statement = statement.rstrip('\n')
        return (1, Statement(statement))

    def start_session(self, args=None):
        if self.state.bot is None:
            if args is None or len(args) == 0:
                return (1, Statement(
                    ('No bot name was provided. Type \'list\' to see available'
                     ' bots.')))

            try:
                bot = self.bot_connections.get(args)
                self.state.bot = bot
                return (1, Statement(
                    'You are now chatting with {}.'.format(bot.name)))
            except AttributeError:
                # Bot not found (is NoneType)
                pass
        else:
            return (
                1,
                Statement('You are already in a chat session with {}!'.format(
                    self.state.bot.name)))

        return (1, Statement(
            ('Sorry, no bot with that name was found. Type \'list\' to '
             'see available bots.')))

    def end_session(self):
        if self.state.bot is None:
            return (1,
                    Statement('You are currently not in an active session.'))
        else:
            bot_name = self.state.bot.name
            self.state.bot = None
            return (1,
                    Statement('Chat session with {} ended.'.format(bot_name)))
