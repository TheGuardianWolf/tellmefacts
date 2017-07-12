# -*- coding: utf-8 -*-
import pytest
from client.services import Keyword, KeywordCommand, KeywordManager


@pytest.fixture(params=[True, False], ids=['has_args', 'no_args'])
def keyword(request):
    """
    Create a keyword object.
    """
    def handler(i=None):
        return i

    return Keyword('test', request.param, handler)


class TestKeyword(object):
    def test_keyword(self, keyword):
        """
        Test object attributes.
        """
        assert keyword.keyword == 'test'
        assert isinstance(keyword.has_args, bool)
        assert callable(keyword.handler)

    def test_handle(self, keyword):
        """
        Test calling the keyword handler function.
        """
        if keyword.has_args:
            assert keyword.handle(True)
        else:
            assert keyword.handle() is None
            with pytest.raises(ValueError):
                keyword.handle('args')


@pytest.fixture()
def keyword_manager():
    """
    Create a keyword manager object.
    """
    return KeywordManager([{
        'type': 'command',
        'keyword': 'test',
        'has_args': False,
        'session_ignore': False,
        'handler': None
    }])


class TestKeywordManager(object):
    def test_keyword_manager(self, keyword_manager):
        """
        Test object attributes.
        """
        assert len(keyword_manager.keywords) == 1
        assert isinstance(keyword_manager.keywords[0], KeywordCommand)
        assert not keyword_manager.keywords[0].session_ignore

    def test_add(self, keyword_manager):
        """
        Test adding a new command to the collection.
        """
        keyword_manager.add(
            'command', 'test_2', False, None, session_ignore=False)
        assert len(keyword_manager.keywords) == 2
        assert isinstance(keyword_manager.keywords[1], KeywordCommand)
        assert not keyword_manager.keywords[1].session_ignore

        # Adding another keyword with the same keyword should raise an error
        with pytest.raises(ValueError):
            keyword_manager.add(
                'command', 'test_2', False, None, session_ignore=False)

    def test_add_invalid(self, keyword_manager):
        """
        Test adding a keyword of an unrecognised type is rejected.
        """
        # Adding a keyword with an unrecognised type should raise an error
        with pytest.raises(ValueError):
            keyword_manager.add(
                'invalid', 'test_2', False, None, session_ignore=False)

    def test_get(self, keyword_manager):
        """
        Test retrieving a keyword from the collection.
        """
        command = keyword_manager.get('test')
        assert isinstance(command, KeywordCommand)
        assert command.keyword == 'test'
        assert keyword_manager.get('none') is None
