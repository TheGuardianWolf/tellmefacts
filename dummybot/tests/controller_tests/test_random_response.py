from unittest import TestCase
from random import randint
from dummybot.controllers import RandomResponse
from re import compile


class RandomResponseTests(TestCase):
    def setUp(self):
        self.responses = ['1234', '4456', '9846']
        self.response_template = compile('^#([0-9]+) (.*)$')
        self.random_response = RandomResponse(self.responses)

    def test_get(self):
        response_object = self.random_response.GET(str(randint(0, 9000)))
        
        self.assertIsInstance(response_object, dict)
        self.assertIn('response', response_object)
        
        self.assertIsInstance(response_object['response'], str)
        cap = self.response_template.match(response_object['response'])
        self.assertIn(cap.group(2), self.responses)
        for i, response in enumerate(self.responses):
            if (response == cap.group(2)):
                self.assertEqual(i, int(cap.group(1)))
