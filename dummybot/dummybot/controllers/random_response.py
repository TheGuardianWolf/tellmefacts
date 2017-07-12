import cherrypy
from random import randint


@cherrypy.expose
class RandomResponse(object):
    """
    Randomly selects a response to return for HTTP GET requests.
    """

    def __init__(self, responses):
        self.responses = responses

    @cherrypy.tools.accept(media='text/plain')
    @cherrypy.tools.json_out()
    def GET(self, q):
        """
        GET method response method.
        """

        # Choose a random index within the list of responses
        i = randint(0, len(self.responses) - 1)

        # Return value is automatically JSON encoded
        return {
            'response': '#{} {}'.format(i + 1, self.responses[i])
        }
