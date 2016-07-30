__author__ = 'Zuzana Baranova'

import functools
from bkrdoc.analysis.linter.catalogue import catalogue


@functools.total_ordering
class Error(object):
    """Class symbolizing a static analysis error."""

    def __init__(self, id=None, type=None, message="", lineno=0):
        self.lineno = lineno
        self.message = message
        self.severity = type
        self.id = id

    def __repr__(self):
        return "{} [{}]".format(self.message, self.id)

    def __eq__(self, other):
        if not isinstance(other, Error):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.lineno == other.lineno:
            if self.id == 'UNK_FLAG':
                return True
            return other.id != 'UNK_FLAG'
        return self.lineno <= other.lineno


class LinterRule(object):
    """Superclass for individual classes that check for a specific type of errors.
    Each has to override the `analyse` method."""

    errors = []

    def __init__(self):
        self.errors = []

    def analyse(self):
        pass

    def add_error(self, err_class, err_label, msg, lineno=0, flag=None):
        try:
            id, severity = catalogue[err_class][err_label]
        except KeyError:
            id, severity = None, None
        if flag:
            msg += " with flag `" + flag + "`"
        self.errors.append(Error(id, severity, msg, lineno))

    def get_errors(self):
        return self.errors
