from requests import get
from requests.exceptions import RequestException


class BotConnection(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def ask(self, question):
        try:
            response = get(self.url + '/askmeanything', timeout=1, params={
                'q': question
            })

            response_text = response.json()['response']
        except (ValueError, KeyError, RequestException):
            raise ValueError('Bot returned an invalid response.')

        return (response.status_code, response_text)


class BotConnectionManager(object):
    """description of class"""
    def __init__(self, connection_list):
        self.connections = []
        for bot in connection_list:
            self.add(**bot)

    def add(self, name, url):
        self.connections.append(BotConnection(name, url))

    def get(self, name):
        for bot in self.connections:
            if bot.name == name:
                return bot
        return None

    def all(self):
        return self.connections
