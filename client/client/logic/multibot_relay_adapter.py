from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from requests.exceptions import RequestException
from ..services import KeywordCommand


class MultibotRelayAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bot_connections = kwargs.get('bot_connections', [])
        self.state = kwargs.get('state')
        if not isinstance(self.bot_connections, list):
            raise TypeError('Bot connections should be a list.')
        elif len(self.bot_connections) == 0:
            raise ValueError(('No bot connections have been provided.'))

        self.commands = [
            KeywordCommand('list', False, True, self.list),
            KeywordCommand('start_session', True, False, self.start_session),
            KeywordCommand('end_session', False, False, self.end_session)
        ]

    def process(self, statement):
        confidence = 1
        response_statement = Statement('')

        keyword_command = None
        result = KeywordCommand.match(statement.text)

        if result is not None:
            for command in self.commands:
                if command.keyword == result.group(1):
                    if self.state.bot is None or not command.session_ignore: 
                        if command.has_args:
                            if len(result.group(2)) > 0:
                                return command.handler(result.group(2))
                        else:
                            if len(result.group(2)) == 0:
                                return command.handler()
                        break

        if keyword_command is None and self.state.bot is not None:
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
        # Make a request to the temperature API
        try:
            (status, response) = self.state.bot.ask(text)
            assert status == 200
        except AssertionError:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: {})'.format(str(status)))
        except RequestException:
            response = ('Selected bot is currently unavailable, please try '
                        'again later. (Error: Connection not established)')

        response_statement = Statement(response)

        return (confidence, response_statement)

    def list(self):
        statement = ''
        for i, bot in enumerate(self.bot_connections):
            statement += '{}. {}\n'.format(str(i), bot.name)
        statement = statement.rstrip('\n')
        return (1, Statement(statement))

    def start_session(self, args):
        if self.state.bot is None:
            for bot in self.bot_connections:
                if bot.name == args:
                    self.state.bot = bot
                    return (1, Statement(
                        'You are now chatting with {}.'.format(bot.name)))
        else:
            return (1, Statement(
                'You are already in a chat session with {}!'.format(self.state.bot.name)))

        return (1, Statement(
            ('Sorry, no bot with that name was found. Type \'list\' to '
                'see available bots.')
        ))

    def end_session(self):
        if self.state.bot is None:
            return (1, Statement('You are currently not in an active session.'))
        else:
            bot_name = self.state.bot.name
            self.state.bot = None
            return (1, Statement('Chat session with {} ended.'.format(bot_name)))
