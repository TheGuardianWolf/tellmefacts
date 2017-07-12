import cherrypy
import sys
from inspect import getfile
from warnings import warn
from json import loads, JSONDecodeError
from importlib import import_module
from os import path, environ
from .controllers import RandomResponse


class Server(object):
    """
    A multibot relay client compatible bot server.
    """

    # Resolve file paths
    root = path.dirname(getfile(import_module('dummybot')))
    config_path = path.join(root, 'config')

    def __init__(self, config_path=config_path):
        self.config(config_path)
        self.setup()

    def config(self, config_path):
        """
        Load configurations from config files.

        :param config_path: Path to the config folder.
        """
        environ.putenv('TZ', 'UTC')

        # Set server to run on localhost and port 80
        self.server_config = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 80,
            'request.show_tracebacks': False
        }

        # Set dispatcher to be a RESTful method dispatcher
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

        # Set default responses
        responses = ['The sky is blue.', 'Water is wet.', 'Rocks are hard.']

        # Try read configuration to replace default responses.
        try:
            fp = open(
                    path.join(config_path, 'responses.json'),
                    'r',
                    encoding='utf8')
            responses = loads(fp.read())
            fp.close()
            assert isinstance(responses, list)
        except (FileNotFoundError, JSONDecodeError, AssertionError):
            warn('No responses config loaded, using defaults.', Warning)
        self.responses = responses

    def setup(self):
        """
        Set up the cherrypy routes.
        """
        random_response = RandomResponse(self.responses)
        cherrypy.tree.mount(None, '/', config=self.route_config)
        cherrypy.tree.mount(
            random_response, '/askmeanything', config=self.route_config)

    def start(self):
        """
        Start server and block thread.
        """
        cherrypy.config.update(self.server_config)
        cherrypy.engine.signal_handler.subscribe()

        # Can't subscribe to console control in Docker as no TTY is started.
        try:
            cherrypy.engine.console_control_handler.subscribe()
        except AttributeError:
            pass

        try:
            cherrypy.engine.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit(1)
        else:
            cherrypy.engine.block()

    def stop(self):
        """
        Stop the cherrypy engine.
        """
        cherrypy.engine.stop()
