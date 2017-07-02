from re import compile

class KeywordCommand(object):
    command_regexp = compile('^([^ ]+) ?(.*)$')

    @classmethod
    def match(self, test):
        return self.command_regexp.match(test)

    def __init__(self, keyword, has_args, session_ignore, handler):
        self.keyword = keyword
        self.has_args = has_args
        self.session_ignore = session_ignore
        self.handler = handler

