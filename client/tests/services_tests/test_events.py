import pytest
from threading import Event
from queue import Queue
from client.services import DataEvent, EventManager


@pytest.fixture()
def data_event():
    return DataEvent('ready')


class TestDataEvent(object):
    def test_data_event(self, data_event):
        assert data_event.type == 'ready'
        assert isinstance(data_event.data, Queue)
        assert isinstance(data_event, Event)


@pytest.fixture()
def event_manager():
    return EventManager(['ready', 'close'])


class TestEventManager(object):
    def test_event_manager(self, event_manager):
        assert isinstance(event_manager.events, dict)
        assert len(event_manager.events) == 2
    
    def test_get(self, event_manager):
        assert isinstance(event_manager.get('close'), DataEvent)
        assert isinstance(event_manager.get('ready'), DataEvent)
        assert event_manager.get('none') is None

    def test_add(self, event_manager):
        event_manager.add('test')
        assert isinstance(event_manager.get('test'), DataEvent)
        with pytest.raises(ValueError):
            event_manager.add('test')
