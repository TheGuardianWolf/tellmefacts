import cherrypy
from random import randint

@cherrypy.expose
class RandomResponse(object):
    def __init__(self, responses):
        if not isinstance(responses, list):
            raise TypeError('Responses must be in a list.')

        self.responses = responses

    @cherrypy.tools.accept(media='text/plain')
    @cherrypy.tools.json_out()
    def GET(self, q):
        return {
            'response': self.responses[randint(0, len(self.responses) - 1)]
        }