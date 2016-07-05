__author__ = 'Zuzana Baranova'


class Error(object):
    """Class symbolizing a static analysis error."""

    def __init__(self, line=0, message=""):
        self.line = line
        self.message = message


class LinterRule(object):
    """Superclass for individual classes that check for a specific type of errors.
    Each has to override the `analyse` method."""

    errors = []

    def __init__(self):
        self.errors = []

    def analyse(self):
        pass

    def add_error(self, msg, flag=None):
        if flag is not None:
            msg += " with flag `" + flag + "`"
        self.errors.append(Error(message=msg))

    def get_errors(self):
        return self.errors
