from cherrypy.test import helper
from json import loads, JSONDecodeError
from random import randint
from dummybot import Server
from client.services import BotConnection


class BotConnectionTests(helper.CPWebCase):
    def setUp(self):
        self.bc = BotConnection()

    def setup_server(self):
        self.s = Server()

    def test_ask_question(self):
        (status, response_text) = self.bc.ask(str(randint(start, end)))
        self.assertTrue(status == '200')
        self.assertTrue(isinstance(response_text, str))
