from inspect import getfile
from importlib import import_module
from os import path
from json import loads
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from slackclient import SlackClient
from client.services import EventManager
from slackclient._slackrequest import SlackRequest
from tempfile import TemporaryDirectory


class MultibotClient(object):
    """
    A Slackbot conversation multiplexer.
    """

    # Resolve file paths
    root = path.dirname(getfile(import_module('client')))
    config_path = path.join(root, 'config')

    def __init__(self,
                 config_path=config_path,
                 input_adapter='client.input.Slack',
                 output_adapter='client.output.Slack',
                 api_hostname=None):
        self.config(config_path, input_adapter, output_adapter)
        if api_hostname is not None:
            self.patch_slack_requests(api_hostname)
        self.events = EventManager(['close'])
        self.slack_client = SlackClient(self.slack_api.get('bot_user_token'))
        self.temp_folder = TemporaryDirectory()
        self.bot = ChatBot(
            'Multibot',
            database=path.join(self.temp_folder.name, 'client-db.json'),
            storage_adapter='chatterbot.storage.JsonFileStorageAdapter',
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

        # Put placeholder data into the chatterbot storage otherwise it picks
        # the no-knowledge adapter's response always
        self.bot.set_trainer(ListTrainer)
        self.bot.train(['placeholder'])

        # Set bot to not learn from conversations
        self.bot.read_only = True

    def config(self, config_path, input_adapter, output_adapter):
        """
        Load configurations from config files.

        :param config_path: Path to the config folder.
        :param input_adapter: An import path for the input_adapter module.
        :param output_adapter: An import path for the output_adapter module.
        """
        # Load bots configuration
        fp = open(path.join(config_path, 'bots.json'))
        self.bot_connections = loads(fp.read())
        fp.close()

        # Load slack api configuration
        self.slack_api = {}
        if input_adapter == 'client.input.Slack' or \
                output_adapter == 'client.output.Slack':
            fp = open(path.join(config_path, 'slack_api.json'))
            self.slack_api = loads(fp.read())
            fp.close()

    def patch_slack_requests(self, api_hostname):
        """
        Patch the slack requests module to send to a host other than slack.com

        :param api_hostname: A valid hostname (e.g. slack.com).
        """
        try:
            # See if there's a stored version of the orignal method
            slack_client_do = self.__slack_client_do
        except AttributeError:
            # Store unpatched method
            self.__slack_client_do = SlackRequest.do
            slack_client_do = SlackRequest.do

        def patched_do(obj,
                       token,
                       request="?",
                       post_data=None,
                       domain=api_hostname,
                       timeout=None):
            return slack_client_do(obj, token, request, post_data, domain,
                                   timeout)

        SlackRequest.do = patched_do

    def start(self):
        """
        Start parsing input from the input adapter.
        """
        try:
            # The following loop will execute each time the user enters input
            while not self.events.get('close').is_set():
                try:
                    self.bot.get_response(None)
                except StopIteration:
                    pass
        # Press ctrl-c or on the keyboard to exit
        except (KeyboardInterrupt, SystemExit):
            self.close()

    def close(self):
        """
        Trigger close event and signal running threads to close.
        """
        self.events.get('close').set()
        try:
            self.bot.input.close()
        except AttributeError:
            pass
        self.bot.storage.drop()
