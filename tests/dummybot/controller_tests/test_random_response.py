from unittest import TestCase
from random import randint
from dummybot.controllers import RandomResponse


class RandomResponseTests(TestCase):
    def setUp(self):
        self.responses = ['1234', '4456', '9846']
        self.random_response = RandomResponse(self.responses)

    def test_get(self):
        response_object = self.random_response.GET(str(randint(0, 9000)))
        self.assertTrue(isinstance(response_object, dict))
        self.assertIn('response', response_object)
        self.assertTrue(isinstance(response_object['response'], str))
        self.assertIn(response_object['response'], self.responses)
