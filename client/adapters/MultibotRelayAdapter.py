from chatterbot.logic import LogicAdapter


class MultibotRelayAdapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(MyLogicAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        if statement.text.startswith('Hey Mike'):
            return True
        else:
            return False

    def process(self, statement):
        from chatterbot.conversation import Statement
        import requests

        # Make a request to the temperature API
        response = requests.get('https://api.temperature.com/current?units=celsius')
        data = response.json()

        # Let's base the confidence value on if the request was successful
        if response.status_code == 200:
            confidence = 1
        else:
            confidence = 0

        temperature = data.get('temperature', 'unavailable')

        response_statement = Statement('The current temperature is {}'.format(temperature))

        return confidence, response_statement