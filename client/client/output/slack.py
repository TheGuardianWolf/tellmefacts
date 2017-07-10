from slackclient import SlackClient
from chatterbot.output import OutputAdapter
from client.services import EventManager


class Slack(OutputAdapter):
    """description of class"""

    def __init__(self, **kwargs):
        super(Slack, self).__init__(**kwargs)
        self.events = kwargs.get('event_manager')
        if self.events is None:
            self.events = EventManager(['send'])
        else:
            self.events.add('send')
        self.bot_user_token = kwargs.get('bot_user_token')
        self.slack_client = kwargs.get('slack_client',
                                       SlackClient(self.bot_user_token))
        self.default_channel = kwargs.get('default_channel', '#general')

    def send_message(self, statement, channel):
        self.logger.info('sending message \'{}\' to channel \'{}\''.format(
            str(statement), channel))

        if self.slack_client.server.websocket is not None:
            r = self.slack_client.rtm_send_message(
                channel=channel, message=str(statement))
            self.logger.info('message sent over websocket')
        else:
            r = self.slack_client.api_call(
                'chat.postMessage',
                channel=channel,
                text=str(statement),
                as_user=False)

            self.logger.info('Slack API responded with \'ok:{}\''.format(
                r.get('ok', False)))
        self.events.get('send').set()

    def process_response(self, statement, session_id=None):
        input_statement = self.chatbot.conversation_sessions.get(
            session_id).conversation.get_last_input_statement()
        channel = input_statement.extra_data.get('channel',
                                                 self.default_channel)

        self.send_message(statement, channel)
        return statement
