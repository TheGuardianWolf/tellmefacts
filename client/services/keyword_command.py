from re import compile

class KeywordCommand(object):
    command_regexp = compile('^([^ ]+) ?(.*)$')

    @classmethod
    def match(test):
        return command_regexp.match(test)

    def __init__(self, keyword, has_args, handler):
        self.keyword = keyword
        self.has_args = has_args
        self.handler = handler

