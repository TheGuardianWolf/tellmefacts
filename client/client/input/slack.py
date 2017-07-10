from threading import Thread
from queue import Empty
from slackclient import SlackClient
from chatterbot.input import InputAdapter
from chatterbot.conversation import Statement
from re import compile
from time import sleep
from client.services import EventManager


class Slack(InputAdapter):
    """
    An input adapter that allows a ChatterBot instance to get input statements
    from a Slack Bot User using *Slack API*. The slack bot only responds if it
    is present in the channel the user is in, and must be mentioned with the
    bot name passed as an argument to this adapter.
    https://api.slack.com
    """

    def __init__(self, **kwargs):
        super(Slack, self).__init__(**kwargs)
        # Use event manager from args if available, create local otherwise
        self.events = kwargs.get('event_manager')
        if self.events is None:
            self.events = EventManager(
                ['input_ready', 'message', 'input_close'])
        else:
            self.events.add('input_ready')
            self.events.add('message')
            self.events.add('input_close')

        # Read about tokens here: https://api.slack.com/bot-users
        self.bot_user_token = kwargs.get('bot_user_token')
        self.bot_name = kwargs.get('bot_name', 'tellmefacts')

        # Use slack client from args if available, create local otherwise
        self.slack_client = kwargs.get('slack_client',
                                       SlackClient(self.bot_user_token))

        # Retrieve ids associated with the bot user of the provided token
        self.user_id = self.get_user_id()
        self.bot_id = self.get_bot_id()

        # Regex pattern to match bot mentions
        self.bot_mention = compile('^<@{}> (.*)$'.format(self.user_id))

        # Don't start event loop if start_event_loop is False
        if kwargs.get('start_event_loop', True):  # Used for testing
            self.start()

    def get_user_id(self):
        """
        Retrieves the bot user id from Slack.
        :returns: The bot user id.
        """
        self.logger.info('attempting to find user ID from Slack')
        api_call = self.slack_client.api_call('auth.test')
        if api_call.get('ok') and 'user_id' in api_call:
            user_id = api_call.get('user_id')
            self.logger.info('user ID recognised as \'{}\''.format(user_id))
            return user_id
        else:
            raise LookupError(
                'Could not find bot user id \'{}\'.'.format(self.bot_name))

    def get_bot_id(self):
        """
        Retrieves the bot id associated with the user id from Slack.
        :returns: The bot id.
        """
        self.logger.info('attempting to find bot ID from Slack')
        api_call = self.slack_client.api_call('users.info', user=self.user_id)
        if api_call.get('ok') and 'user' in api_call:
            bot_id = api_call.get('user').get('profile').get('bot_id')
            self.logger.info('bot ID recognised as \'{}\''.format(bot_id))
            return bot_id
        else:
            raise LookupError(
                'Could not find bot id \'{}\'.'.format(self.bot_name))

    def start(self):
        """
        Starts the Slack RTM event loop on a new thread.
        """
        self.logger.info('starting Slack RTM')

        if self.slack_client.rtm_connect():
            self.events.get('input_ready').set()
            self.logger.info('Slack RTM: connected, starting event loop')
            # Start the event loop with a polling rate of .2s (<1% CPU usage)
            self.event_thread = Thread(
                target=self.event_loop, args=(0.2, ), daemon=True)
            self.event_thread.start()

    def close(self):
        """
        Signals the Slack RTM event loop thread to close.
        """
        self.events.get('input_close').set()
        self.logger.info('Slack RTM: waiting for shutdown')
        self.event_thread.join(timeout=5)
        self.logger.info('Slack RTM: shutdown successful')

    def event_loop(self, polling_rate=0.2):
        """
        Worker function for the Slack RTM event loop
        :param polling_rate: Sets the interval which the RTM WebSocket stream
                             is read at.
        """
        # Below loop runs until the input_close event is set
        while not self.events.get('input_close').is_set():
            # Every rtm_read call returns a list of events
            rtm_list = self.slack_client.rtm_read()
            # For each event, parse the event type and store in an associated
            # queue if available
            for rtm_object in rtm_list:
                # If no event type is specified, it must be a message sent
                # receipt
                event_type = rtm_object.get('type', 'confirm_send')
                self.logger.info('Slack RTM: event recieved of type \'{}\''.
                                 format(event_type))
                if self.events.get(event_type) is not None:
                    self.events.get(event_type).data.put(rtm_object)
                    self.events.get(event_type).set()
            sleep(polling_rate)

        # Close event set, loop broken
        self.events.get('input_ready').clear()
        self.logger.info('Slack RTM: event loop stopped')

    def process_input(self, statement):
        """
        Returns a statement object based on the input source.
        """
        data = False
        while not data:
            if (self.events.get('input_close').is_set()):
                # Exit path if close event is set
                return None

            # Below loop runs until an event is available
            event = False
            while not event:
                if (self.events.get('input_close').is_set()):
                    # Exit path if close event is set
                    return None

                # Read from the message event data queue, timeout per second
                # so application doesn't hang with no message
                try:
                    event = self.events.get('message').data.get(timeout=1)
                except Empty:
                    pass

            self.logger.info('message recieved, checking for mention')
            # Check if message was sent by this bot
            if not event.get('bot_id', '') == self.bot_id:
                # Check if message matches the bot mention regex
                result = self.bot_mention.match(event.get('text', '').strip())
                if result is not None:
                    data = event
                    data['matched_text'] = result.group(1).strip()
                    self.logger.info('bot mentioned with matching text \'{}\''.
                                     format(data['matched_text']))
            else:
                self.logger.info('discarding message from self')

        self.events.get('message').clear()
        statement = Statement(data['matched_text'], extra_data=data)
        self.logger.info('processing user statement {}'.format(statement))
        return statement
