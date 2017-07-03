from requests import get
from requests.exceptions import RequestException
from json import loads, JSONDecodeError


class BotConnection(object):
    """description of class"""
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def ask(self, question):
        try:
            response = get(self.url + '/askmeanything', timeout=1, params={
                'q': question
            })

            response_text = loads(response.text)['response']
        except (JSONDecodeError, KeyError, RequestException):
            raise ValueError('Bot returned an invalid response.')

        return (response.status_code, response_text)
