import cherrypy
import inspect
import app
from os import path, environ
from app.controllers.RandomResponse import RandomResponse

class Server(object):
    # Values for server paths
    root = path.dirname(inspect.getfile(app))
    configPath = path.join(appRoot, 'Config')

    def __init__(self):
        environ.putenv('TZ', 'UTC')

        self.globalConfig = {
            'server.socket_host': '0.0.0.0', 
            'server.socket_port': 80,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.encode.encoding': 'utf-8',
            'tools.encode.on': True,
            'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/plain')],
            'response.timeout': 10
        }

    def mountTree(self):
        cherrypy.tree.mount(RandomResponse(path.join(Server.configPath, 'responses.json')), '/')

    # a blocking call that starts the web application listening for requests
    def start(self):
        self.mountTree()
        cherrypy.config.update(self.globalConfig)
        if hasattr(cherrypy.engine, 'signal_handler'):
            cherrypy.engine.signal_handler.subscribe()
        if hasattr(cherrypy.engine, 'console_control_handler'):
            cherrypy.engine.console_control_handler.subscribe()
        try:
            cherrypy.engine.start()
        except:
            sys.exit(1)
        else:
            cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()

