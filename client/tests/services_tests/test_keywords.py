import pytest
from client.services import Keyword, KeywordCommand, KeywordManager


@pytest.fixture(params=[True, False], ids=['has_args', 'no_args'])
def keyword(request):
    def handler(i=None):
        return i

    return Keyword('test', request.param, handler)


class TestKeyword(object):
    def test_handle(self, keyword):
        if keyword.has_args:
            assert keyword.handle(True)
        else:
            assert keyword.handle() is None
            with pytest.raises(ValueError):
                keyword.handle(True)


@pytest.fixture()
def keyword_command():
    return KeywordCommand(**{
        'keyword': 'test',
        'has_args': False,
        'session_ignore': False,
        'handler': None
    })


class TestKeywordCommand(object):
    def test_keyword_command(self, keyword_command):
        assert not keyword_command.session_ignore

    def test_match_has_args(self):
        result = KeywordCommand.match('command args')
        assert len(result.groups()) == 2
        assert result.group(1) == 'command'
        assert result.group(2) == 'args'

    def test_match_no_args(self):
        result = KeywordCommand.match('command')
        assert len(result.groups()) == 2
        assert result.group(1) == 'command'
        assert result.group(2) == ''

    def test_match_invalid(self):
        result = KeywordCommand.match('')
        assert result is None


@pytest.fixture()
def keyword_manager():
    return KeywordManager([{
        'type': 'command',
        'keyword': 'test',
        'has_args': False,
        'session_ignore': False,
        'handler': None
    }])


class TestKeywordManager(object):
    def test_keyword_manager(self, keyword_manager):
        assert len(keyword_manager.keywords) == 1
        assert isinstance(keyword_manager.keywords[0], KeywordCommand)
        assert not keyword_manager.keywords[0].session_ignore

    def test_add(self, keyword_manager):
        keyword_manager.add(
            'command', 'test_2', False, None, session_ignore=False)
        assert len(keyword_manager.keywords) == 2
        assert isinstance(keyword_manager.keywords[1], KeywordCommand)
        assert not keyword_manager.keywords[1].session_ignore
        with pytest.raises(ValueError):
            keyword_manager.add(
                'command', 'test_2', False, None, session_ignore=False)

    def test_get(self, keyword_manager):
        command = keyword_manager.get('test')
        assert isinstance(command, KeywordCommand)
        assert command.keyword == 'test'
        assert keyword_manager.get('none') is None
