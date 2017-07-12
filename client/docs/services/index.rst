==============
Services
==============

Service classes are helpers for adapters to add some additional functionality,
and to promote seperation of concerns within the client classes.

Most service classes provided in this module are collections of data objects.

Bot Connection Manager
==================

The :code:`BotConnectionManager` class is a collection of :code:`BotConnection`
objects. These represent supported bots that the client are able to connect to.

.. autoclass:: client.services.BotConnectionManager
   :members:

   :param connection_list: A list of bot connections in dictionary form. Arguments for creating the connection are parsed from dictionary key-value pairs.
   :type connection_list: list(dict)

Bot Connection
------------------

.. autoclass:: client.services.BotConnection
   :members:

   :param name: Identifier for the bot, should be unique.
   :type name: str

   :param url: The URL for the bot connection (example: http://localhost:8080)
   :type url: str

Event Manager
==================

The :code:`EventManager` class is a collection of :code:`DataEvent`
objects. These represent events that have associated data, such as a Slack RTM
event.

.. autoclass:: client.services.EventManager
   :members:

   :param event_types: A list of event type names (strings). Each name should be unique.
   :type event_types: list(str)

Data Event
------------------

.. autoclass:: client.services.DataEvent
   :members:

   :param type: Name of the event type.
   :type name: str

Keyword Manager
==================

The :code:`KeywordManager` class is a collection of :code:`Keyword` objects.
These represent a string to be intercepted from normal messages.

.. autoclass:: client.services.KeywordManager
   :members:

   :param event_types: A list of event type names (strings). Each name should be unique.
   :type event_types: list(str)

Keyword
------------

.. autoclass:: client.services.Keyword
   :members:

   :param keyword: The keyword string to intercept. Should be unique.
   :type name: str

   :param has_args: Flag handler to have arguments.
   :type url: bool

   :param handler: Function to call on handle method.
   :type url: func
