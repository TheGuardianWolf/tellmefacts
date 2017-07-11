from re import compile


class Keyword(object):
    """
    Represents a keyword that can be intercepted from a message.
    """

    def __init__(self, keyword, has_args, handler):
        self.keyword = keyword
        self.has_args = has_args
        self.handler = handler

    def handle(self, args=None):
        """
        Calls the handler of a `Keyword` object with an optional argument.

        :param args: Argument in text form.

        :returns: Return value from calling the handler function.
        """
        # Check if the keyword has arguments
        if self.has_args:
            return self.handler(args)
        else:
            if args is not None and len(args) > 0:
                raise ValueError('Keyword does not accept arguments.')
            return self.handler()


class KeywordCommand(Keyword):
    """
    Represents a command that can be intercepted from a message. Commands
    are intended to modify operation of the bot in some way.
    """

    command_regexp = compile('^([^ ]+) ?(.*)$')  # Command regex pattern

    @classmethod
    def match(self, test):
        """
        Check if a test string matches the command pattern

        :param test: A text string to test.

        :returns: Return value of a regex match with the command pattern.
        """
        return self.command_regexp.match(test)

    def __init__(self, keyword, has_args, handler, **kwargs):
        super(KeywordCommand, self).__init__(keyword, has_args, handler)
        self.session_ignore = kwargs.get('session_ignore', False)


class KeywordManager(object):
    """
    A collection class for `Keyword`s.
    """
    def __init__(self, keywords_list):
        self.keywords = []
        for keyword in keywords_list:
            self.add(**keyword)

    def add(self, type, keyword, has_args, handler, **kwargs):
        """
        Add a `Keyword` to the collection.

        :param type: Type of keyword to add.

        :param keyword: The keyword string.

        :param has_args: Boolean value indicating whether the handler accepts
                         arguments.

        :param handler: A handler function to call when keyword is detected.

        :param kwargs: Additional arguments to the keyword type
        """

        # Check if keyword already exists in collection.
        for word in self.keywords:
            if word.keyword == keyword:
                raise ValueError('Keyword already exists')

        # Check for a known keyword type
        if type == 'command':
            keyword = KeywordCommand(keyword, has_args, handler, **kwargs)
        else:
            raise ValueError('No keyword type of \'{}\' exists'.format(type))

        self.keywords.append(keyword)

    def get(self, keyword):
        """
        Get a `Keyword` by keyword string.

        :param keyword: Keyword string of the `Keyword` to get.

        :returns: A `Keyword` object.
        :rtype: Keyword
        """
        # Search through the list of keywords for the matching one
        for word in self.keywords:
            if word.keyword == keyword:
                return word

        # Return `None` if not found
        return None
