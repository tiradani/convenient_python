import optparse

class InvalidOptionError(Exception): pass

class Options(optparse.OptionParser):
    """
    An abstract helper class designed to encapsulate command line arguments.
    """
    def __init__(self, usage):
        """
        @param usage: The usage string that should be displayed in the event of
        an error or if help was requested
        @type usage: str
        """
        optparse.OptionParser.__init__(self, usage=usage)
        self.usage = usage
        self.options = None
        self.args = None

    def validate_options(self):
        """
        The child class must implement this method.
        """
        raise NotImplementedError

    def validate_args(self):
        """
        The child class must implement this method.
        """
        raise NotImplementedError

    def parse(self):
        """
        Parses the command line and validates the options and arguments passed in
        """
        (options, args) = self.parse_args()
        self.options = options
        self.args = args

        self.validate_options()
        self.validate_args()