from threading import Event
from queue import Queue


class DataEvent(Event):
    """
    Represents an event that is optionally associated with data (like a
    message).
    """
    def __init__(self, type):
        super(DataEvent, self).__init__()
        self.type = type
        self.data = Queue()


class EventManager(object):
    """
    A collection class for `DataEvent`s.
    """
    def __init__(self, event_types):
        self.events = {}
        for event_type in event_types:
            self.add(event_type)

    def get(self, event_type):
        """
        Get a `DataEvent` by event type.

        :param event_type: Name of the `DataEvent` type to get.

        :returns: A `DataEvent` object.
        :rtype: DataEvent
        """
        return self.events.get(event_type)

    def add(self, event_type):
        """
        Add a `DataEvent` type.

        :param event_type: Name of the `DataEvent` type to add.
        """
        # Only add events if they don't exist
        if event_type not in self.events:
            self.events[event_type] = DataEvent(event_type)
        else:
            raise ValueError(
                'event type \'{}\' already exists.'.format(event_type))
