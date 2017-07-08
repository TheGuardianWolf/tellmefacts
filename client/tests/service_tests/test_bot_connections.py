import pytest
from client.services import BotConnection, BotConnectionManager


@pytest.fixture()
def bot_connection():
    return BotConnection('dummybot', 'http://dummybot')


class TestBotConnection(object):
    def test_ask(self, mocker, bot_connection):
        r = mocker.patch(
            'client.services.bot_connection.requests.get', autospec=True)
        r.json.return_value = {'response': 'hello'}
        r.status_code = 200
        (status, response_text) = self.bc.ask('test')
        assert status == 200
        assert response_text == 'hello'

        r.json.return_value = {}
        with pytest.raises(ValueError):
            self.bc.ask('test')


@pytest.fixture()
def bot_connection_manager():
    return BotConnectionManager([{
        'name': 'dummybot',
        'url': 'http://dummybot'
    }])


class TestBotConnectionManager(object):
    def test_bot_connection_manager(self, bot_connection_manager):
        assert len(bot_connection_manager.connections) == 1
        assert isinstance(bot_connection_manager.connections[0], BotConnection)

    def test_add(self, bot_connection_manager):
        bot_connection_manager.add('added', 'http://added')
        assert len(bot_connection_manager.connections) == 2
        assert isinstance(bot_connection_manager.connections[1], BotConnection)

    def test_get(self, bot_connection_manager):
        bot = bot_connection_manager.get('dummybot')
        assert isinstance(bot, BotConnection)
        assert bot.name == 'dummybot'
        assert bot_connection_manager.get('none') is None

    def test_all(self, bot_connection_manager):
        assert len(bot_connection_manager.all()) == 1
