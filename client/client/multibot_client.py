from inspect import getfile
from importlib import import_module
from os import path
from json import loads
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from .services import RelayState, BotConnection


class MultibotClient(object):
    root = path.dirname(getfile(import_module('client')))
    config_path = path.join(root, 'config')
    """description of class"""

    def __init__(self,
                 config_path=config_path,
                 input_adapter='chatterbot.input.TerminalAdapter',
                 output_adapter='chatterbot.output.TerminalAdapter'):
        self.__config(config_path, input_adapter, output_adapter)

        self.bot = ChatBot(
            'Multibot',
            database=None,
            silence_performance_warning=True,  # Bot is read only anyway
            # storage_adapter='chatterbot.storage.SQLStorageAdapter',
            input_adapter=input_adapter,
            output_adapter=output_adapter,
            logic_adapters=[{
                'import_path':
                'client.logic.MultibotRelayAdapter',
                'bot_connections':
                self.bot_connections,
                'state':
                self.state
            }],
            direct_line_host=self.ms_api.get('direct_line_host'),
            direct_line_conservationId=self.ms_api.get(
                'direct_line_conservationId'),
            direct_line_token_or_secret=self.ms_api.get(
                'direct_line_token_or_secret'))

        self.bot.set_trainer(ListTrainer)
        self.bot.train(['placeholder'])

        self.bot.read_only = True

    def __config(self, config_path, input_adapter, output_adapter):
        self.state = RelayState()

        bot_connections = []
        fp = open(path.join(config_path, 'bots.json'))
        bot_connections = loads(fp.read())
        fp.close()
        for i, connection in enumerate(bot_connections):
            bot_connections[i] = BotConnection(connection['name'],
                                               connection['url'])

        self.bot_connections = bot_connections

        self.ms_api = {}
        if input_adapter == 'chatterbot.input.Microsoft' or \
                output_adapter == 'chatterbot.output.Microsoft':
            fp = open(path.join(config_path, 'microsoft_api.json'))
            self.ms_api = loads(fp.read())
            fp.close()

    def start(self):
        # The following loop will execute each time the user enters input
        while True:
            try:
                # We pass None to this method because the parameter
                # is not used by the TerminalAdapter
                self.bot.get_response(None)

            # Press ctrl-c or ctrl-d on the keyboard to exit
            except (KeyboardInterrupt, EOFError, SystemExit):
                break
