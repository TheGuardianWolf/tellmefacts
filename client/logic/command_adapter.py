from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement

class CommandAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def can_process(self, statement):
        return True
        chat_session = self.get_chat_session(request)

        response = self.chatterbot.get_response(input_data, chat_session.id_string)

    def process(self, statement):
        confidence = 0.99
        response_statement = Statement('I am sorry, but I do not understand. Please try again. Type \'help\' for a list of valid commands.')
        return (confidence, response_statement)