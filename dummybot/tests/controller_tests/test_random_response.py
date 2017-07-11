# -*- coding: utf-8 -*-
import pytest
from random import randint
from dummybot.controllers import RandomResponse
from re import compile


@pytest.fixture()
def random_response():
    responses = ['1234', '4456', '9846']
    return RandomResponse(responses)


class RandomResponseTests(object):
    # Responses must match this pattern
    response_pattern = compile('^#([0-9]+) (.*)$')

    def test_random_response(self, random_response):
        assert isinstance(random_response, list)
        assert len(random_response.responses) == 3

    def test_get(self, random_response):
        response_object = random_response.GET(str(randint(0, 9000)))

        assert isinstance(response_object, dict)
        assert 'response' in response_object

        assert isinstance(response_object['response'], str)
        cap = self.response_pattern.match(response_object['response'])
        assert cap.group(2) in random_response.responses
        for i, response in enumerate(random_response.responses):
            if (response == cap.group(2)):
                assert i + 1 == int(cap.group(1))
