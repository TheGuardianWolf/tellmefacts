from re import compile


class Keyword(object):
    def __init__(self, keyword, has_args, handler, **kwargs):
        self.keyword = keyword
        self.has_args = has_args
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
        super(KeywordCommand, self).__init__(keyword, has_args, handler,
                                             **kwargs)
        self.session_ignore = kwargs.get('session_ignore', False)


class KeywordManager(object):
    def __init__(self, keywords_list):
        self.keywords = []
        for keyword in keywords_list:
            self.add(**keyword)

    def add(self, type, keyword, has_args, handler, **kwargs):
        for word in self.keywords:
            if word.keyword == keyword:
                raise ValueError('Keyword already exists')

        if type == 'command':
            keyword = KeywordCommand(keyword, has_args, handler, **kwargs)
        else:
            raise ValueError('No keyword type of \'{}\' exists'.format(type))

        self.keywords.append(keyword)

    def get(self, keyword):
        for word in self.keywords:
            if word.keyword == keyword:
                return word
        return None
