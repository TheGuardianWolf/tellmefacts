from inspect import getfile
from importlib import import_module
from os import path
from json import loads
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from slackclient import SlackClient
from client.services import EventManager


class MultibotClient(object):
    root = path.dirname(getfile(import_module('client')))
    config_path = path.join(root, 'config')
    """description of class"""

    def __init__(self,
                 config_path=config_path,
                 input_adapter='client.input.Slack',
                 output_adapter='client.output.Slack'):
        self.__config(config_path, input_adapter, output_adapter)

        self.events = EventManager(['close'])
        self.slack_client = SlackClient(self.slack_api.get('bot_user_token'))
        self.bot = ChatBot(
            'Multibot',
            database=None,
            silence_performance_warning=True,  # Bot is read only anyway
            input_adapter=input_adapter,
            output_adapter=output_adapter,
            logic_adapters=[{
                'import_path':
                'client.logic.MultibotRelayAdapter',
                'bot_connections':
                self.bot_connections
            }],
            bot_user_token=self.slack_api.get('bot_user_token'),
            bot_name=self.slack_api.get('bot_name'),
            slack_client=self.slack_client,
            event_manager=self.events)

        self.bot.set_trainer(ListTrainer)
        self.bot.train(['placeholder'])

        self.bot.read_only = True

    def __config(self, config_path, input_adapter, output_adapter):
        fp = open(path.join(config_path, 'bots.json'))
        self.bot_connections = loads(fp.read())
        fp.close()

        self.slack_api = {}
        if input_adapter == 'client.input.Slack' or \
                output_adapter == 'client.output.Slack':
            fp = open(path.join(config_path, 'slack_api.json'))
            self.slack_api = loads(fp.read())
            fp.close()

    def start(self):
        try:
            # The following loop will execute each time the user enters input
            while not self.events.get('close').is_set():
                try:
                    self.bot.get_response(None)
                except AttributeError as e:
                    if not str(e) == '\'NoneType\' object has no attribute \'text\'':
                        raise e
        # Press ctrl-c or ctrl-d on the keyboard to exit
        except (KeyboardInterrupt, EOFError, SystemExit):
            self.close()

    def close(self):
        self.events.get('close').set()
        try:
            self.bot.input.close()
            self.bot.storage.drop()
        except AttributeError:
            pass
