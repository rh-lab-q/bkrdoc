__author__ = 'Zuzana Baranova'


class Error(object):
    """Class symbolizing a static analysis error."""

    def __init__(self, line=0, message=""):
        self.line = line
        self.message = message

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class LinterRule(object):
    """Superclass for individual classes that check for a specific type of errors.
    Each has to override the `analyse` method."""

    errors = []

    def __init__(self):
        self.errors = []

    def analyse(self):
        pass

    def add_error(self, msg, flag=None):
        if flag:
            msg += " with flag `" + flag + "`"
        self.errors.append(Error(message=msg))

    def get_errors(self):
        return self.errors
