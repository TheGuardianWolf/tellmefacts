==============
Logic Adapters
==============

The tellmefacts-client provides one additional logic adapter to provide the
framework required to process keyword commands and multiplex bot connections.

Multibot Relay Adapter
==================

.. autofunction:: client.logic.MultibotRelayAdapter

The :code:`MultibotRelayAdapter` multiplexes chat conversations between multiple
supported bots. Chat strings are also compared with known keywords to provide
user commands list and to switch between available bots.

How it works
------------

The input statement is checked to see whether it is in the format of a keyword
command. If a match is found, the keyword is checked against known keywords
supported by the relay. If the keyword is known by the relay, then the handler
for the keyword is called.

Otherwise, the statement is treated as a chat message and relayed to the
currently selected bot if an active session exists.

Command methods
------------

Handler methods are registered on initialisation of the adapter, and called if
the matching keyword is given as an input statement with appropriate arguments.
Keywords can be set to be ignored if the user is currently in an active session
with a bot.

**list**

Has arguments: No

Ignored in an active session: No

Lists the currently available bots the client can connect to as set in the
configuration.

**start_session**

Has arguments: Yes

Ignored in an active session: No

Start a session with one of the available bots on the list. Invalid names will
produce an error message. Cannot start another session if currently in a
session.

**end_session**

Has arguments: No

Ignored in an active session: No

Ends a current bot session. If not in an active session, an error is produced.

Usage
------------

.. code-block:: python

   chatbot = ChatBot(
       "My ChatterBot",
       logic_adapters=[{
            'import_path': 'client.logic.MultibotRelayAdapter',
            'bot_connections': [{
                'name': 'bot_1',
                'url': 'http://dummybot_1'
            }, {
                'name': 'bot_2',
                'url': 'http://dummybot_2'
            }, {
                'name': 'bot_3',
                'url': 'http://dummybot_3'
            }]
        }]
   )
