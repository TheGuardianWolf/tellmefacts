from cherrypy.test import helper
from json import loads
from dummybot import Server
from tempfile import TemporaryDirectory
from json import dumps
from os import path


class DummybotTests(helper.CPWebCase):
    def setup_server(self):
        temp_dir = TemporaryDirectory()
        responses = dumps(['test'])
        fp = open(path.join(temp_dir.name, 'responses.json'), 'w')
        fp.write(responses)
        fp.close()
        self.s = Server(config_path=temp_dir.name)

    def check_response(self):
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
        deserialisedBody = loads(self.body)
        self.assertIsInstance(deserialisedBody, dict)
        self.assertTrue('response' in deserialisedBody)

    def test_ask_random(self):
        self.getPage(
            '/askmeanything?q=Hello%20world',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_ask_unicode(self):
        """
        Test the case that a unicode string is passed in.
        """
        self.getPage(
            '/askmeanything?q=سلام',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_ask_emoji(self):
        """
        Test the case that the input string contains an emoji.
        """
        self.getPage(
            '/askmeanything?q=💩 ',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_ask_non_whitespace(self):
        """
        Test the case that a non-whitespace C1 control string is passed in.
        """
        self.getPage(
            '/askmeanything?q=',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_ask_two_byte_characters(self):
        """
        Test the case that a string containing two-byte characters is passed
        in.
        """
        self.getPage(
            '/askmeanything?q=田中さんにあげて下さい',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_ask_corrupted_text(self):
        """
        Test the case that a string contains "corrupted" text.
        """
        self.getPage(
            '/askmeanything?q=Ṱ̺̺̕h̼͓̲̦̳̘̲e͇̣̰̦̬͎ ̢̼̻̱̘h͚͎͙̜̣̲ͅi̦̲̣̰̤v̻͍e̺̭̳̪̰-m̢iͅn̖̺̞̲̯̰d̵̼̟͙̩̼̘̳.̨̹͈̣',
            headers=[('Content-Type', 'text/plain')])
        self.check_response()

    def test_different_method(self):
        """
        CherryPy defaults to decode the query-string
        using UTF-8, trying to send a query-string with
        a different encoding will raise a 404 since
        it considers it's a different URL.
        """
        self.getPage(
            '/askmeanything?q=Hello%20world',
            method='POST',
            headers=[('Content-Type', 'text/plain;charset=utf-8'),
                     ('Content-Length', '0')])
        self.assertStatus('405 Method Not Allowed')

    def test_no_params(self):
        """
        CherryPy defaults to decode the query-string
        using UTF-8, trying to send a query-string with
        a different encoding will raise a 404 since
        it considers it's a different URL.
        """
        self.getPage(
            '/askmeanything',
            headers=[('Content-Type', 'text/plain;charset=utf-8')])
        self.assertStatus('404 Not Found')

    def test_extra_params(self):
        """
        CherryPy defaults to decode the query-string
        using UTF-8, trying to send a query-string with
        a different encoding will raise a 404 since
        it considers it's a different URL.
        """
        self.getPage(
            '/askmeanything?q=o&p=0&h=--',
            headers=[('Content-Type', 'text/plain;charset=utf-8')])
        self.assertStatus('404 Not Found')
