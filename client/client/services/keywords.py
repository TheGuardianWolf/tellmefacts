from re import compile

class Keyword(object):
    def __init__(self, keyword, has_args, handler, **kwargs):
        self.keyword = keyword
        self.has_args = has_args
        self.session_ignore = kwargs.get('session_ignore', False)
        self.handler = handler

    def handle(self, args=None):
        if self.has_args:
            return self.handler(args)
        else:
            if args is not None and len(args) > 0:
                raise ValueError('Keyword does not accept arguments.')
            return self.handler()

class KeywordCommand(Keyword):
    command_regexp = compile('^([^ ]+) ?(.*)$')

    @classmethod
    def match(self, test):
        return self.command_regexp.match(test)

    def __init__(self, keyword, has_args, handler, **kwargs):
        super(KeywordCommand, self).__init__(keyword, has_args, handler, **kwargs)

class KeywordManager(object):
    def __init__(self, keywords_list):
        self.keywords = []
        for keyword in keywords_list:
            self.add(**keyword)

    def add(type, keyword, has_args, handler, **kwargs):
        if type == 'command':
            keyword = KeywordCommand(keyword, has_args, handler, **kwargs)
        else:
            raise ValueError('No keyword type of \'{}\' exists'.format(type))

        self.keywords.append(keyword)

    def get(type, keyword):
        for word in self.keywords:
            if word.keyword == keyword:
                return word
        return None