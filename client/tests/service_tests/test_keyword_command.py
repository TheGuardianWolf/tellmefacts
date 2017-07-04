from unittest import TestCase
from client.services import KeywordCommand


class KeywordCommandTests(TestCase):
    def test_handle_has_args(self):
        def handler(i=None):
            return i
        bc_has_args = KeywordCommand('test', True, True, handler)
        self.assertTrue(bc_has_args.handle(True))

    def test_handle_no_args(self):
        def handler():
            return None
        bc_no_args = KeywordCommand('test', False, True, handler)
        self.assertIsNone(bc_no_args.handle())

    def test_match_has_args(self):
        result = KeywordCommand.match('command args')
        self.assertIs(len(result.groups()), 3)
        self.assertEqual(result.group(1), 'command')
        self.assertEqual(result.group(2), 'args')

    def test_match_no_args(self):
        result = KeywordCommand.match('command')
        self.assertIs(len(result.groups()), 3)
        self.assertEqual(result.group(1), 'command')
        self.assertEqual(result.group(2), '')

    def test_match_invalid(self):
        result = KeywordCommand.match('')
        self.assertIsNone(result)
