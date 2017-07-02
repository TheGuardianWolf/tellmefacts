import cherrypy
import sys
from inspect import getfile
from warnings import warn
from json import loads, JSONDecodeError
from importlib import import_module
from os import path, environ
from .controllers import RandomResponse


class Server(object):
    # Values for server paths
    root = path.dirname(getfile(import_module('dummybot')))
    config_path = path.join(root, 'config')

    def __init__(self, config_path=config_path):
        self.__config(config_path)
        self.__setup()

    def __config(self, config_path):
        environ.putenv('TZ', 'UTC')
        self.server_config = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 80,
            'request.show_tracebacks': False
        }

        self.route_config = {
            '/': {
                'request.dispatch':
                cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on':
                True,
                'tools.encode.encoding':
                'utf-8',
                'tools.encode.on':
                True,
                'tools.response_headers.on':
                True,
                'tools.response_headers.headers':
                [('Content-Type', 'text/plain;charset=utf-8')],
                'response.timeout':
                10
            }
        }

        responses = ['The sky is blue.', 'Water is wet.', 'Rocks are hard.']
        try:
            fp = open(path.join(config_path, 'responses.json'), 'r')
            responses = loads(fp.read())
            fp.close()
            assert isinstance(responses, list)
        except (FileNotFoundError, JSONDecodeError, AssertionError):
            warn('No responses config loaded, using defaults.', Warning)
        self.responses = responses

    def __setup(self):
        random_response = RandomResponse(self.responses)
        cherrypy.tree.mount(None, '/', config=self.route_config)
        cherrypy.tree.mount(
            random_response, '/askmeanything', config=self.route_config)

    # a blocking call that starts the web application listening for requests
    def start(self):
        cherrypy.config.update(self.server_config)
        cherrypy.engine.signal_handler.subscribe()
        #cherrypy.engine.console_control_handler.subscribe()

        try:
            cherrypy.engine.start()
        except:
            sys.exit(1)
        else:
            cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()
