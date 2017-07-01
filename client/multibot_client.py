from os import path
from json import loads, JSONDecodeError
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from .services import BotConnection
from .services import RelayState


class MultibotClient(object):
    root = path.dirname(inspect.getfile(import_module('dummybot')))
    configPath = path.join(root, 'config')

    """description of class"""
    def __init__(self):
        state = RelayState()
        connections = []
        
        try:
            fp = open(path.join(configPath,'bots.json'))  
            bots = loads(fp.read())
            if not isinstance(bots, list):
                raise TypeError()
            fp.close()
        except (FileNotFoundError, TypeError, JSONDecodeError):
            pass

        self.bot = ChatBot(
            'Multibot',
            read_only=True,
            silence_performance_warning=True,
            input_adapter='chatterbot.input.TerminalAdapter',
            output_adapter='chatterbot.output.TerminalAdapter',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                    'threshold': 0.99,
                    'default_response': 'I am sorry, but I do not understand. Please try again. Type \'help\' for a list of valid commands.'
                },
                {
                    'import_path': 'client.logic.MultibotRelayAdapter',
                    'bot_connections': connections,
                    'state': state
                },
                {
                    'import_path': 'client.logic.CommandAdapter'
                }
            ]
        )

        self.bot.set_trainer(ListTrainer)
        self.bot.train([
            'placeholder'
        ])

    def start(self):     
        # The following loop will execute each time the user enters input
        while True:
            try:
                # We pass None to this method because the parameter
                # is not used by the TerminalAdapter
                bot_input = self.bot.get_response(None)

            # Press ctrl-c or ctrl-d on the keyboard to exit
            except (KeyboardInterrupt, EOFError, SystemExit):
                break


