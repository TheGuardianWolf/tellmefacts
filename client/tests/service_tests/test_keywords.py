from unittest import TestCase
from client.services import Keyword, KeywordCommand, KeywordManager


class KeywordTests(TestCase):
    def test_handle_has_args(self):
        def handler(i=None):
            return i
        bc_has_args = Keyword('test', True, handler)
        self.assertTrue(bc_has_args.handle(True))

    def test_handle_no_args(self):
        def handler():
            return None
        bc_no_args = Keyword('test', False, handler)
        self.assertIsNone(bc_no_args.handle())


class KeywordCommandTests(TestCase):
    def test_init(self):
        kc = KeywordCommand(**{
                'keyword': 'test',
                'has_args': False,
                'session_ignore': False,
                'handler': None
            })
        self.assertFalse(kc.session_ignore)

    def test_match_has_args(self):
        result = KeywordCommand.match('command args')
        self.assertIs(len(result.groups()), 2)
        self.assertEqual(result.group(1), 'command')
        self.assertEqual(result.group(2), 'args')

    def test_match_no_args(self):
        result = KeywordCommand.match('command')
        self.assertIs(len(result.groups()), 2)
        self.assertEqual(result.group(1), 'command')
        self.assertEqual(result.group(2), '')

    def test_match_invalid(self):
        result = KeywordCommand.match('')
        self.assertIsNone(result)


class KeywordManagerTests(TestCase):
    def setUp(self):
        self.km = KeywordManager(
            [{
                'type': 'command',
                'keyword': 'test',
                'has_args': False,
                'session_ignore': False,
                'handler': None
            }]
        )
        self.assertEqual(len(self.km.keywords), 1)
        self.assertIsInstance(self.km.keywords[0], KeywordCommand)
        self.assertFalse(self.km.keywords[0].session_ignore)

    def test_add(self):
        self.km.add('command', 'test_2', False, None, session_ignore=False)
        self.assertEqual(len(self.km.keywords), 2)
        self.assertIsInstance(self.km.keywords[1], KeywordCommand)
        self.assertFalse(self.km.keywords[1].session_ignore)
        with self.assertRaises(ValueError):
            self.km.add('command', 'test_2', False, None, session_ignore=False)

    def test_get(self):
        command = self.km.get('test')
        self.assertIsInstance(command, KeywordCommand)
        self.assertEquals(command.keyword, 'test')
        self.assertIsNone(self.km.get('none'))
