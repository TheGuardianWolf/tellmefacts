import pytest
from client.services import Keyword, KeywordCommand, KeywordManager


@pytest.fixture(params=[True, False])
def keyword():
    def handler(i=None):
        return i
    return Keyword('test', True, handler)


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
    return KeywordManager(
            [{
                'type': 'command',
                'keyword': 'test',
                'has_args': False,
                'session_ignore': False,
                'handler': None
            }]
        )


class TestKeywordManager(object):
    def test_keyword_manager(self, keyword_manager):
        self.assertEqual(len(keyword_manager.keywords), 1)
        self.assertIsInstance(keyword_manager.keywords[0], KeywordCommand)
        self.assertFalse(keyword_manager.keywords[0].session_ignore)

    def test_add(self, keyword_manager):
        keyword_manager.add('command', 'test_2', False, None, session_ignore=False)
        self.assertEqual(len(self.km.keywords), 2)
        self.assertIsInstance(self.km.keywords[1], KeywordCommand)
        self.assertFalse(self.km.keywords[1].session_ignore)
        with self.assertRaises(ValueError):
            self.km.add('command', 'test_2', False, None, session_ignore=False)

    def test_get(self, keyword_manager):
        command = keyword_manager.get('test')
        self.assertIsInstance(command, KeywordCommand)
        self.assertEquals(command.keyword, 'test')
        self.assertIsNone(self.km.get('none'))
