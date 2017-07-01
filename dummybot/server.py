import cherrypy
import inspect
from json import loads, JSONDecodeError
from importlib import import_module
from os import path, environ
from .controllers import RandomResponse

class Server(object):
    # Values for server paths
    root = path.dirname(inspect.getfile(import_module('dummybot')))
    configPath = path.join(root, 'config')

    def __init__(self):
        environ.putenv('TZ', 'UTC')
        self.serverConfig = {
            'server.socket_host': '0.0.0.0', 
            'server.socket_port': 80,
            'request.show_tracebacks': False 
        }

        self.routeConfig = {
            '/' : {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.encode.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'text/plain;charset=utf-8')],
                'response.timeout': 10
            }
        }

        responses = ['The sky is blue.', 'Water is wet.', 'Rocks are hard.']

        try:
            fp = open(path.join(Server.configPath, 'responses.json'), 'r')
            responses = loads(fp.read())
            fp.close()
            assert isinstance(responses, list)
        except (FileNotFoundError, JSONDecodeError, AssertionError):
            print('WARNING: No responses config loaded, using defaults.')

        randomResponse = RandomResponse(responses)
        cherrypy.tree.mount(None, '/', config=self.routeConfig)
        cherrypy.tree.mount(randomResponse, '/askmeanything', config=self.routeConfig)

    # a blocking call that starts the web application listening for requests
    def start(self):
        try:
            cherrypy.config.update(self.serverConfig)
            cherrypy.engine.signal_handler.subscribe()
            cherrypy.engine.console_control_handler.subscribe()
            cherrypy.engine.start()
        except:
            sys.exit(1)
        else:
            cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()

