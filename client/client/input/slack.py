from threading import Event
from queue import Queue


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
        self.slack_client = SlackClient(bot_user_token)
        self.bot_id = self.get_bot_id()
        self.start()

    def get_bot_id(self):
        self.logger.info('attempting to find bot ID from Slack')
        api_call = slack.api_call('users.list')
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.bot_name:
                    self.bot_id = user.get('id')
                    self.logger.info('bot ID recognised as \'{}\''.format(self.bot_id))
        else:
            raise LookupError('Could not find bot user \'{}\'.'.format(self.bot_name))

    def start(self):
        self.logger.info('starting Slack RTM')

        if slack_client.rtm_connect():
            self.events.get('ready').set()
            self.logger.info('Slack RTM connected, starting event loop')
            self.event_thread = Thread(target=self.event_loop, args=(1))

    def close(self):
        ''' Must use the close method to end the Slack RTM event loop '''
        self.events.get('ready').clear()

    @classmethod
    def event_loop(self, polling_rate=0.5):
        while events.get('ready').is_set():
            rtm_data = slack.rtm_read()
            rtm_list = loads(rtm_data)

            for rtm_object in rtm_list:
                event_type = rtm_object['type']
                self.logger.info('Slack RTM event recieved of type \'{}\''.format(event_type))
                if self.events.get(event_type) is not None:
                    self.events.get(event_type).set()
                    self.events.get(event_type).data.put(rtm_object)

    def process_input(self, statement):
        data = False
        while not data:
            data = self.events.get('message').data.get(timeout=3.5)
        self.events.get('message').clear()
        statement = Statement(data['text'], extra_data=data)
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
