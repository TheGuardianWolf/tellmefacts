from slackclient import SlackClient


class Slack(OutputAdapter):
    """description of class"""

    def __init__(self, **kwargs):
        self.bot_user_token = kwargs.get('bot_user_token')
        self.slack_client = SlackClient(bot_user_token)
        self.default_channel = kwargs.get('default_channel', '#general')

    def process_response(self, statement, session_id=None):
        input_statement = self.chatbot.conversation_sessions.get(session_id).conversation.get_last_input_statement()
        channel = input_statement.extra_data.get('channel', self.default_channel)
        self.logger.info('sending message \'{}\' to channel \'{}\''.format(str(statement)), channel)
        r = self.slack_client.api_call('chat.postMessage', channel=channel, text=str(statement), as_user=False)
        self.logger.info('Slack API responded with \'{}\''.format(r))
        return statement