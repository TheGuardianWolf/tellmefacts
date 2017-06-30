from cherrypy.test import helper
from json import loads, JSONDecodeError
from dummybot import Server


class test_responses(helper.CPWebCase):
    def setup_server():
        s = Server()

    def test_recieve_random_phrase(self):
        self.getPage(
            '/askmeanything?q=Hello%20world',
            headers=[('Content-Type', 'text/plain')])
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
        try:
            deserialisedBody = loads(self.body)
        except JSONDecodeError:
            raise AssertionError('Response body does not contain a JSON object.')

        assert isinstance(deserialisedBody, dict)
        assert 'response' in deserialisedBody

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
