from slackclient import SlackClient
from chatterbot.output import OutputAdapter
from client.services import EventManager


class Slack(OutputAdapter):
    """
    An input adapter that allows a ChatterBot instance to send responses via a
    Slack Bot User using *Slack API*. The adapter sends to the channel the last
    input statement was sent from, or to a default channel if the input is not
    from a Slack input adapter.
    https://api.slack.com
    """

    def __init__(self, **kwargs):
        super(Slack, self).__init__(**kwargs)
        # Use event manager from args if available, create local otherwise
        self.events = kwargs.get('event_manager')
        if self.events is None:
            self.events = EventManager(['send'])
        else:
            self.events.add('send')

        # Read about tokens here: https://api.slack.com/bot-users
        self.bot_user_token = kwargs.get('bot_user_token')
        self.slack_client = kwargs.get('slack_client',
                                       SlackClient(self.bot_user_token))

        # Set a default channel if input statements don't have channel data
        self.default_channel = kwargs.get('default_channel', '#general')

    def send_message(self, statement, channel):
        """
        Send a message to a Slack channel. Sending is either through RTM or
        web API depending on the current input adapter status.

        :param statement: Message to be sent to the Slack channel.

        :param channel: Slack channel to send the message to.
        """
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
        """
        Send the processed response to the Slack channel of the input from
        which it was generated from.

        :param statement: Message to be sent to the Slack channel.

        :param session_id: Id of the current user session.
        """

        # Get the last generated input statement
        input_statement = self.chatbot.conversation_sessions.get(
            session_id).conversation.get_last_input_statement()

        # Get the channel from statement data
        channel = input_statement.extra_data.get('channel',
                                                 self.default_channel)

        self.send_message(statement, channel)
        return statement
