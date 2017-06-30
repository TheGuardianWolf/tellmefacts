from chatterbot import ChatBot

class Client(object):
    """description of class"""
    def __init__(self):
        self.bot = ChatBot(
            'Norman',
            input_adapter='chatterbot.input.TerminalAdapter',
            output_adapter='chatterbot.output.TerminalAdapter',
            logic_adapters=[
                'app.adapters.MultibotRelayAdapter'
            ]
        )

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


