__author__ = 'Zuzana Baranova'

from enum import Enum

class Severity(Enum):
    error = 1
    warning = 2
    info = 3

class Error(object):
    """Class symbolizing a static analysis error."""

    def __init__(self, id=None, type=None,  message="", line=0):
        self.line = line
        self.message = message
        self.severity = type
        self.id = id

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

    def add_error(self, id, severity, msg, flag=None):
        if flag:
            msg += " with flag `" + flag + "`"
        self.errors.append(Error(id, severity, message=msg))

    def get_errors(self):
        return self.errors
