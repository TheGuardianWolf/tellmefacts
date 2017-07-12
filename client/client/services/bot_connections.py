from requests import get
from requests.exceptions import RequestException


class BotConnection(object):
    """
    A representation of a connection to a bot.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def ask(self, question):
        """
        Send a message to the bot over this connection and parse the response.

        :param question: Question to ask the bot.

        :returns: The response status and response text from the bot.
        """
        try:
            response = get(self.url + '/askmeanything',
                           timeout=1,
                           params={'q': question})

            # Unpack the response
            response_text = response.json()['response']
        except (ValueError, KeyError, RequestException):
            raise ValueError('Bot returned an invalid response.')

        return (response.status_code, response_text)


class BotConnectionManager(object):
    """
    A collection class for BotConnections.
    """

    def __init__(self, connection_list):
        self.connections = []
        for bot in connection_list:
            self.add(**bot)

    def add(self, name, url):
        """
        Adds a new bot connection to the collection.

        :param name: Name of the bot.

        :param url: Url that the bot can be reached at.
        """
        for bot in self.connections:
            if bot.name == name:
                raise ValueError(
                    'Bot name \'{}\' already exists.'.format(name))
        self.connections.append(BotConnection(name, url))

    def get(self, name):
        """
        Get a bot connection by name.

        :param name: Name of the bot to get.

        :returns: A `BotConnection` object.
        :rtype: BotConnection
        """
        for bot in self.connections:
            if bot.name == name:
                return bot
        return None

    def all(self):
        """
        Get all connections in collection.

        :returns: A list of `BotConnections` held by the object.
        """
        return self.connections
