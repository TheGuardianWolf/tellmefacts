==========
MultibotClient
==========

This class creates and configures objects required for the bot to function.
Configuration is loaded from files from the config folder during initialisation.
The input and output adapters can be switched out with others to connect the
client to other services.

.. autoclass:: client.MultibotClient
   :members:

   :param config_path: Absolute path to a directory containing json config files.
   :type config_path: str

   :param input_adapter: The import path to an input adapter class.
   :type input_adapter: str

   :param output_adapter: The import path to an output adapter class.
   :type output_adapter: str

   :param api_hostname: An alternative api hostname for requests to be sent (default: slack.com).
   :type api_hostname: str

Example parameters
===========================

.. code-block:: python

    MultibotClient(
        config_path='/path/to/a/folder'
        input_adapter='chatterbot.input.TerminalAdapter'
        output_adapter='chatterbot.output.TerminalAdapter'
        api_hostname='localhost')

Enable logging
==============

The Slack bot uses ChatterBot's built in logging. You can enable logging by
setting the logging level through the logging module. The launcher script also
has a verbose switch to enable logging.

.. code-block:: python

   import logging

   logging.basicConfig(level=logging.INFO)

Hostname patching
==============

The :code:`MultibotClient` class is able to patch the slackclient's requests to
be sent to another hostname. This can be used to debug the application by
connecting it to a mock Slack API.

Events
==============

:code:`Events` from the :code:`threading` module are available for use to
synchronise with the client's I/O processes. By default the following events
are created:

**input_ready** - set when the async input event thread is started

**message** - set when a message is available from the event thread

**input_close** - signal that controls the closing of the event thread

**send** - set when a message is sent to Slack

**close** - signal that controls the closing of the application (mainly used for testing)

These should be declared through the :code:`EventManager` class in the services
module, and passed in as an initialisation argument.