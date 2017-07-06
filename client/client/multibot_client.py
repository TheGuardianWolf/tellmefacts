import logging
from inspect import getfile
from importlib import import_module
from os import path
from json import loads
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from .services import RelayState, BotConnectionManager


class MultibotClient(object):
    root = path.dirname(getfile(import_module('client')))
    config_path = path.join(root, 'config')
    """description of class"""

    def __init__(self,
                 config_path=config_path,
                 input_adapter='client.input.Slack',
                 output_adapter='client.output.Slack'):
        self.__config(config_path, input_adapter, output_adapter)
        
        logging.basicConfig(level=logging.INFO)
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
            bot_user_token=self.slack_api.get('bot_user_token'),
            bot_name=self.slack_api.get('bot_name'))

        self.bot.set_trainer(ListTrainer)
        self.bot.train(['placeholder'])

        self.bot.read_only = True

    def __config(self, config_path, input_adapter, output_adapter):
        fp = open(path.join(config_path, 'bots.json'))
        self.bot_connections = BotConnectionManager(loads(fp.read()))
        fp.close()

        self.slack_api = {}
        if input_adapter == 'client.input.Slack' or \
                output_adapter == 'client.output.Slack':
            fp = open(path.join(config_path, 'slack_api.json'))
            self.slack_api = loads(fp.read())
            fp.close()

        self.state = RelayState()

    def start(self):
        # The following loop will execute each time the user enters input
        while True:
            try:
                # We pass None to this method because the parameter
                # is not used by the TerminalAdapter
                self.bot.get_response()

            # Press ctrl-c or ctrl-d on the keyboard to exit
            except (KeyboardInterrupt, EOFError, SystemExit):
                self.bot.input.close()
                break
