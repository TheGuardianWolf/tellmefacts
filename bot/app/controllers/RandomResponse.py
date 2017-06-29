import cherrypy
from json import loads, dumps, JSONDecodeError
from random import randint

@cherrypy.expose
class RandomResponse(object):
    def __init__(self, responsesFile):
        self.responses = ['The sky is blue.', 'Water is wet.', 'Rocks are hard.']

        try:
            fp = open(responsesFile, 'r')
            responses = loads(fp)
            assert isinstance(responses, list)
            self.responses = responses
        except (FileNotFoundError, JSONDecodeError, AssertionError):
            cherrypy.log.error('No responses config loaded, using defaults.', severity=2)

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPError(400, 'Request type incorrect or lacking parameters.')

    @cherrypy.tools.accept(media='text/plain')
    @cherrypy.tools.json_out()
    def GET(self, q):
        return {
            'response': self.responses[randint(0, len(self.responses))]
        }