__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.linter.catalogue import Catalogue
from bkrdoc.analysis.parser import bkrdoc_parser, conditions_for_commands

class LinterSingleRules(common.LinterRule):
    """
    Class that checks for standalone rules that did not fit elsewhere.
    As of now this includes:
        Beakerlib environment must be set at the beginning.
        Journal must be started before any other command.
        Journal end can only be followed by several allowed commands.
        Deprecated commands.
    """

    ENV_NOT_SET = "BeakerLib environment was not set before a BeakerLib command was used."
    JOURNAL_NOT_STARTED = "Journal was not started before a BeakerLib command was used."
    JOURNAL_END = "Journal end was followed by a command other than journal print."

    def __init__(self):
        super(LinterSingleRules, self).__init__()
        self.errors = []
        self.journal_end_found = False
        self.beaker_env_checked = False
        self.journal_start_checked = False

    def analyse(self, line):
        rules = [self.check_environment_set,
                 self.check_journal_started,
                 self.check_journal_last_command,
                 self.check_deprecated_commands]
        for rule in rules:
            rule(line)

    def check_environment_set(self, line):
        self.constraint_check(line, self.sets_beaker_env, self.ENV_NOT_SET, 'beaker_env_checked')

    def check_journal_started(self, line):
        self.constraint_check(line, self.is_journal_start, self.JOURNAL_NOT_STARTED, 'journal_start_checked')

    def constraint_check(self, line, rule_to_check, error_msg, constraint_met):
        if hasattr(line, 'in_function'):
            return
        if getattr(self, constraint_met):
            return
        if rule_to_check(line):
            setattr(self, constraint_met, True)
            return

        if error_msg == self.ENV_NOT_SET:
            catalogue_lookup = 'beaker_env'
        else:
            catalogue_lookup = 'journal_beg'

        if line.argname in bkrdoc_parser.Parser.beakerlib_commands:
            self.add_error('2400', catalogue_lookup,
                           msg=error_msg, lineno=line.lineno)
            setattr(self, constraint_met, True)  # check once
            return

    def check_deprecated_commands(self, line):

        if line.argname not in Catalogue.deprecated_commands:
            return

        msg = line.argname + " command is deprecated"
        use_instead = Catalogue.deprecated_commands[line.argname]
        if use_instead:
            msg += ", instead use: " + ', '.join(use_instead)
        self.add_error('2000', line.argname, msg, line.lineno)

    def check_journal_last_command(self, line):

        if not self.journal_end_found:
            return

        if not common.LinterRule.is_allowed_outside_journal(line):
            self.add_error('2400', 'journal_end', self.JOURNAL_END, line.lineno)
            self.journal_end_found = False
            return

    @staticmethod
    def is_journal_start(line):
        cond = conditions_for_commands.ConditionsForCommands()
        return cond.is_journal_start(line.argname)

    @staticmethod
    def sets_beaker_env(command):
        return command.argname == 'UNKNOWN' and command.data[0] == '.' and command.data[1].endswith('beakerlib.sh')
