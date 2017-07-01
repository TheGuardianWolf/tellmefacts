from requests import get


class BotConnection(object):
    """description of class"""
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def ask(self, question):
        response = get(self.url + '/askmeanything', timeout=1, params={
            'q': question
        })

        return (response.status_code, response.text)
