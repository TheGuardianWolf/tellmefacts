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
    data_path = path.join(root, 'data')

    """description of class"""
    def __init__(self, config_path=config_path, data_path=data_path):
        self.__config()

        self.bot = ChatBot(
            'Multibot',
            database=path.join(data_path, 'database.db'),
            read_only=True,
            silence_performance_warning=True,
            # storage_adapter='chatterbot.storage.SQLStorageAdapter',
            input_adapter='chatterbot.input.TerminalAdapter',
            output_adapter='chatterbot.output.TerminalAdapter',
            logic_adapters=[
                {
                    'import_path': 'client.logic.MultibotRelayAdapter',
                    'bot_connections': self.bot_connections,
                    'state': self.state
                }
            ],
        )

        self.bot.set_trainer(ListTrainer)
        self.bot.train(['placeholder'])

    def __config(self):
        self.state = RelayState()

        bot_connections = []
        fp = open(path.join(self.config_path, 'bots.json'))
        bot_connections = loads(fp.read())
        fp.close()
        for i, connection in enumerate(bot_connections):
            bot_connections[i] = BotConnection(
                connection['name'], connection['url'])

        self.bot_connections = bot_connections

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
