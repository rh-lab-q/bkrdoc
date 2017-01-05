__author__ = 'Zuzana Baranova'

import functools
from bkrdoc.analysis.linter.catalogue import Catalogue

CATALOGUE = Catalogue.table


@functools.total_ordering
class Error(object):
    """Class symbolizing a static analysis error."""

    def __init__(self, err_id=None, type=None, message="", lineno=0):
        self.lineno = lineno
        self.message = message
        self.severity = type
        self.err_id = err_id

    def __repr__(self):
        return "{} [{}]".format(self.message, self.err_id)

    def __eq__(self, other):
        if not isinstance(other, Error):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.lineno == other.lineno:
            if self.err_id == 'UNK_FLAG':
                return True
            return other.err_id != 'UNK_FLAG' and self.err_id < other.err_id
        return self.lineno < other.lineno


class LinterRule(object):
    """Superclass for individual classes that check for a specific type of errors.
    Each has to override the `analyse` method."""

    errors = []

    def __init__(self):
        self.errors = []

    def analyse(self, line):
        pass

    def add_error(self, err_class, err_label, msg, lineno=0, flag=None):
        try:
            err_id, severity = CATALOGUE[err_class].value[err_label]
        except ValueError:
            err_id, severity, _ = CATALOGUE[err_class].value[err_label]
        except KeyError:
            err_id, severity = None, None
        if flag:
            msg += " with flag `" + flag + "`"
        self.errors.append(Error(err_id, severity, msg, lineno))

    def get_errors(self):
        return self.errors

    @staticmethod
    def is_allowed_outside_journal(command):
        """ Checks whether the input is allowed outside journal. """
        allowed_commands = ['rlJournalPrint', 'rlJournalPrintText', 'rlJournalEnd',
                            'rlReport', 'rlGetTestState']
        return command in allowed_commands
