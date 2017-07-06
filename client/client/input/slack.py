from threading import Event, Thread
from queue import Queue
from slackclient import SlackClient
from chatterbot.input import InputAdapter
from chatterbot.conversation import Statement
from re import compile


class Slack(InputAdapter):
    event_types = ['ready', 'message']
    """description of class"""

    def __init__(self, **kwargs):
        super(Slack, self).__init__(**kwargs)
        self.events = {}
        self.last_object = None
        for event in self.event_types:
            self.events[event] = self.SlackEvent(event)

        self.bot_user_token = kwargs.get('bot_user_token')
        self.bot_name = kwargs.get('bot_name', 'tellmefacts')
        self.slack_client = SlackClient(self.bot_user_token)
        self.bot_id = self.get_bot_id()
        self.bot_mention = compile('^<@{}> (.*)$'.format(self.bot_id))
        self.start()

    def get_bot_id(self):
        self.logger.info('attempting to find bot ID from Slack')
        api_call = self.slack_client.api_call('auth.test')
        if api_call.get('ok') and 'user_id' in api_call:
            bot_id = api_call.get('user_id')
            self.logger.info('bot ID recognised as \'{}\''.format(bot_id))
            return bot_id
        else:
            raise LookupError(
                'Could not find bot user \'{}\'.'.format(self.bot_name))

    def start(self):
        self.logger.info('starting Slack RTM')

        if self.slack_client.rtm_connect():
            self.events.get('ready').set()
            self.logger.info('Slack RTM connected, starting event loop')
            self.event_thread = Thread(target=self.event_loop, args=(1))
            self.event_thread.start()

    def close(self):
        ''' Must use the close method to end the Slack RTM event loop '''
        self.events.get('ready').clear()
        self.event_thread.join()

    @classmethod
    def event_loop(self, polling_rate=0.5):
        while self.events.get('ready').is_set():
            rtm_list = self.slack_client.rtm_read()

            for rtm_object in rtm_list:
                event_type = rtm_object['type']
                self.logger.info('Slack RTM event recieved of type \'{}\''.
                                 format(event_type))
                if self.events.get(event_type) is not None:
                    self.events.get(event_type).set()
                    self.events.get(event_type).data.put(rtm_object)

    def process_input(self, statement):
        data = False
        while not data:
            event = False
            while not event:
                event = self.events.get('message').data.get(timeout=3.5)
            result = self.bot_mention.match(event.get('text', ''))
            if result is not None:
                data = event
                data['matched_text'] = result.group(1)

        self.events.get('message').clear()
        statement = Statement(data['matched_text'], extra_data=data)
        self.logger.info('processing user statement {}'.format(statement))
        return statement

    class SlackEvent(object):
        def __init__(self, type):
            self.type = type
            self.event = Event()
            self.data = Queue()

        def set(self):
            return self.event.set()

        def is_set(self):
            return self.event.is_set()

        def clear(self):
            return self.event.clear()

        def wait(self, **kwargs):
            return self.event.wait(**kwargs)
