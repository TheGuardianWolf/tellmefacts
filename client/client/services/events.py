from threading import Event
from queue import Queue


class DataEvent(Event):
    def __init__(self, type):
        super(DataEvent, self).__init__()
        self.type = type
        self.data = Queue()


class EventManager(object):
    def __init__(self, event_types):
        self.events = {}
        for event_type in event_types:
            self.add(event_type)

    def get(self, event_type):
        return self.events[event_type]

    def add(self, event_type):
        if event_type not in self.events:
            self.events[event_type] = DataEvent(event_type)
        else:
            raise ValueError(
                'event type \'{}\' already exists.'.format(event_type))
