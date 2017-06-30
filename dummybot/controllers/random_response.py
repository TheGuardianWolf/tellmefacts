import cherrypy
from json import loads, dumps, JSONDecodeError
from random import randint

@cherrypy.expose
class RandomResponse(object):
    def __init__(self, responsesFile):
        self.responses = ['The sky is blue.', 'Water is wet.', 'Rocks are hard.']

        try:
            fp = open(responsesFile, 'r')
            responses = loads(fp.read())
            assert isinstance(responses, list)
            self.responses = responses
        except (FileNotFoundError, JSONDecodeError, AssertionError):
            print('WARNING: No responses config loaded, using defaults.')

    @cherrypy.tools.accept(media='text/plain')
    @cherrypy.tools.json_out()
    def GET(self, q):
        return {
            'response': self.responses[randint(0, len(self.responses) - 1)]
        }