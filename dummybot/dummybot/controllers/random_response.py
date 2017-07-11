import cherrypy
from random import randint


@cherrypy.expose
class RandomResponse(object):
    def __init__(self, responses):
        self.responses = responses

    @cherrypy.tools.accept(media='text/plain')
    @cherrypy.tools.json_out()
    def GET(self, q):
        i = randint(0, len(self.responses) - 1)
        return {
            'response': '#{} {}'.format(i + 1, self.responses[i])
        }
