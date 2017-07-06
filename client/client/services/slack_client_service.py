from threading import Thread, Event
from slackclient import SlackClient
from time import sleep
from logging import getLogger
from json import loads


class SlackClientService(object):
    """description of class"""

    def __init__(self, bot_name, bot_user_token, logger=getLogger(__name__)):
        self.slack = SlackClient(bot_user_token)
        self.logger = logger
        self.bot_name = bot_name
        self.get_bot_id()
        self.events = {
            'ready': Event(),
            'message': Event()
        }
        self.handlers = {
            'ready': None,
            'message': None
        }

    def get_bot_id(self):
        self.logger.info('Attempting to find bot ID from Slack')
        api_call = slack.api_call('users.list')
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.bot_name:
                    self.bot_id = user.get('id')
                    self.logger.info('Bot ID recognised as \'{}\''.format(self.bot_id))
        else:
            raise LookupError('Could not find bot user \'{}\'.'.format(self.bot_name))

    def start(self):
        self.logger.info('Starting Slack RTM')

        if slack_client.rtm_connect():
            self.ready.set()
            self.logger.info('Slack RTM connected, starting event loop')
            self.event_thread = Thread(target=self.event_loop, args=(self.events, 1))

    def close(self):
        self.logger.info('Attempting to close Slack RTM')
        self.events.get('ready').clear()
        self.event_thread.join()
        self.logger.info('Closed Slack RTM')

    def attach_handler(event_type, handler):
        pass

    @staticmethod
    def event_loop(events, polling_rate):
        while events.get('ready').is_set():
            rtm_data = slack.rtm_read()
            rtm_object = loads(rtm_data)

            self.logger.info('Slack RTM data recieved of type \'{}\''.format(rtm_object['type']))
            sleep(polling_rate)

