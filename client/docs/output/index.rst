===============
Output Adapters
===============

The tellmefacts-client provides one additional output adapter to provide a
connection to the Slack API.

Slack output adapter
=====================

.. autofunction:: client.output.Slack

This is an output adapter that allows a ChatterBot instance to send responses
to a `Slack`_ channel using *RTM* or *Web API*.

When provided with a statement, the adapter looks for the most recent input
message that is part of the session identified with the :code:`session_id`
parameter. If the input adapter is a Slack adapter, the statement should
contain the original Slack event as part of its :code:`extra_data` attribute.
This is used to retrieve the channel that the response should be sent to. If
the channel can't be found, then it defaults to the channel as set by the
:code:`default_channel` parameter.

Sending method
---------------------

The adapter will choose to either send responses through *RTM* or *Web API*,
depending on the current state of the websockets connection in its
:code:`SlackClient` object.

This means that if a shared SlackClient is used between a Slack input adapter
and a Slack output adapter, *RTM* will be used. Otherwise, unless a websockets
connection is explicitly started, the output adapter will use *Web API*.

Shared objects
---------------------

It is recommended that a shared :code:`EventManager` object and
:code:`SlackClient` object is passed in to the main client class if the input
adapter is also a Slack adapter; to take advantage of a unified event management
object and enable the use of *RTM* to send messages.

Usage
---------------------

The :code:`SlackClient` class seen below is found in the `slackclient`_ package.

Be sure to also see the documentation for the :ref:`Slack input adapter <slack-input-adapter>`.

.. code-block:: python

   chatbot = ChatBot(
       "My ChatterBot",
       output_adapter="chatterbot.output.Slack",
       slack_client="https://directline.botframework.com",  # Optional
       bot_user_token="xoxp-1234123412341234-12341234-1234",
       default_channel="#general", # Optional
       event_manager=EventManager()  # Optional
   )

.. _Slack: https://api.slack.com/rtm
.. _slackclient: https://github.com/slackapi/python-slackclient
