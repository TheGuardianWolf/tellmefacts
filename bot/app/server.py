import cherrypy
import inspect
import app
from os import path, environ
from app.controllers.RandomResponse import RandomResponse

class Server(object):
    # Values for server paths
    root = path.dirname(inspect.getfile(app))
    configPath = path.join(root, 'Config')

    def __init__(self):
        environ.putenv('TZ', 'UTC')
        self.globalConfig = {
            'server.socket_host': '0.0.0.0', 
            'server.socket_port': 80,
            'request.show_tracebacks': False 
        }

        self.routeConfig = {
            '/' : {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
                'tools.response_headers.on': True,     
                'tools.encode.encoding': 'utf-8',
                'tools.encode.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'text/plain;charset=utf-8')],
                'response.timeout': 10
            }
        }

        self.finishedSetup = False;

    def setup(self):
        randomResponse = RandomResponse(path.join(Server.configPath, 'responses.json'))
        cherrypy.tree.mount(None, '/', config=self.routeConfig)
        cherrypy.tree.mount(randomResponse, '/askmeanything', config=self.routeConfig)
        self.finishedSetup = True

    # a blocking call that starts the web application listening for requests
    def start(self):
        if not self.finishedSetup:
            self.setup()

        try:
            cherrypy.config.update(self.globalConfig)
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

