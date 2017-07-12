==============
Input Adapters
==============

The tellmefacts-client provides one additional input adapter to provide a
connection to the Slack API.

Slack input adapter
===========================

.. autofunction:: client.input.Slack

This is an input adapter that allows a ChatterBot instance to recieve messages
from a `Slack`_ channel using *RTM* protocol.

The input adapter automatically retrieves a bot user id from Slack's Web API
after being started, and uses this to find the associated bot id.

Slack RTM events
---------------------------

A new thread is started to read from the RTM stream, with message events being
stored in a queue. The main thread runs a loop that reads from the queue and
checks whether the bot is mentioned. Text after a mention is processed.

The RTM stream only sends events from channels that the bot is part of, so it
will need to be invited into channels by a team admin. The adapter will 
ignore self mentions if such a message ever occurs, but will not ignore other
bots.

Event manager
---------------------------

The input class automatically creates an :code:`EventManager` object if a shared
instance is not provided. These events are required to control the closing of
the RTM read thread. It is recommended that a shared :code:`EventManager` be
used across a multibot client.

Usage
---------------------------

The :code:`SlackClient` class seen below is found in the `slackclient`_ package.

Be sure to also see the documentation for the :ref:`Slack output adapter <slack-output-adapter>`.

.. code-block:: python

   chatbot = ChatBot(
       "My ChatterBot",
       input_adapter="chatterbot.input.Slack",
       slack_client=SlackClient('xoxp-1234123412341234-12341234-1234'),  # Optional
       bot_name="tellmefacts",
       bot_user_token="xoxp-1234123412341234-12341234-1234",
       start_event_loop=True,  # Optional
       event_manager=EventManager()  # Optional
   )

.. _Slack: https://api.slack.com/rtm
.. _slackclient: https://github.com/slackapi/python-slackclient
