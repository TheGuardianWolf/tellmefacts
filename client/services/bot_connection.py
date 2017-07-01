from requests import get

class BotConnection(object):
    """description of class"""
    def __init__(self, url):
        self.url = url

    def ask(question):
        response = get(self.url + '/askmeanything', params={
            'q': question
        })

        return (response.status_code, response.text)

