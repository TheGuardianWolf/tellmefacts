from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from requests import get
from re import match, compile


class MultibotRelayAdapter(LogicAdapter):
    command_list = ['list', 'start_session', 'end_session']
    command_regexp = compile('^([^ ]+) ?(.*)$')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bot_connections = kwargs.get('bot_connections', [])
        self.state = kwargs.get('state')
        if not isinstance(bot_connections, list) and len(self.bot_connections) == 0:
            raise ValueError('No bot connections could be made from bots configuration file.')

    def process(self, statement):
        confidence = 0
        response_statement = ''

        if self.state.bot is not None:
            result = command_regexp.match(statement.text)

            if result is not None and result.group(1) in command_list:
                (confidence, response_statement) = handle_command(result.group(1), result.group(2))
            else:
                (confidence, response_statement) = handle_chat(statement.text)
        else:
            (confidence, response_statement) = (
                1,
                Statement(('You are currently not connected to any bot. '
                          'Connect to a bot with \'start_session <bot_name>\' or '
                          'type \'list\' for a list of available bots.'))
            )

        return confidence, response_statement

    def handle_command(self, command, args):
        if len(args) == 0 and command == 'list':
            for i, bot in enumerate(self.bot_connections):
                print('{}. {}'.format(str(i), ['name']))
        elif command == 'start_session':
            for bot in self.bot_connections:
                if bot['name'] == args:
                    self.state.bot = bot
                    return (1, Statement('You are now chatting with {}.'.format(bot['name'])))
            return (1, Statement('Sorry, no bot with that name was found. Type \'list\' to see available bots.'))
        elif len(args) == 0 and command == 'end_session':
            if self.state.bot is None:
                return (1, Statement('You are currently not in an active session.'))
            else:
                bot_name = self.state.bot['name']
                self.state.bot = None
                return (1, Statement('Chat session with {} ended.'.format(bot_name)))
            

    def handle_chat(self, text):
        # Make a request to the temperature API
        (status, response) = self.state.bot.ask(response)

        # Let's base the confidence value on if the request was successful
        if not status == 200:
            response = 'Selected bot is currently unavailable, please try again later. (Error: {})'.format(str(status))

        response_statement = Statement(response)

        return (1, response_statement)