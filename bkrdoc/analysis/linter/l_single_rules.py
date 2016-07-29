__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser


class LinterSingleRules(common.LinterRule):
    """
    Class that checks for standalone rules that did not fit elsewhere.
    As of now this includes:
        Beakerlib environment must be set at the beginning.
        Journal must be started before any other command.
        Journal end should be followed by no command (other than journal print).
        Deprecated commands.
    """

    deprecated_commands = {'rlGetArch': ['rlGetPrimaryArch', 'rlGetSecondaryArch'],
                           'rlLogLowMetric': ['rlLogMetricLow'],
                           'rlLogHighMetric': ['rlLogMetricHigh'],
                           'rlShowPkgVersion': ['rlShowPackageVersion']}

    ENV_NOT_SET = "Beakerlib environment was not set before a beakerlib command was used."
    JOURNAL_NOT_STARTED = "Journal was not started before a beakerlib command was used."
    JOURNAL_END = "Journal end was followed by a command other than journal print."

    def __init__(self, parsed_input_list):
        super(LinterSingleRules, self).__init__()
        self.errors = []
        self.parsed_input_list = parsed_input_list

    def analyse(self):
        self.check_environment_set()
        self.check_journal_started()
        self.check_journal_last_command()
        self.check_deprecated_commands()

    def check_environment_set(self):
        self.constraint_check(self.sets_beaker_env, self.ENV_NOT_SET)

    def check_journal_started(self):
        self.constraint_check(self.is_journal_start, self.JOURNAL_NOT_STARTED)

    def constraint_check(self, constraint_met, error_msg):
        if error_msg == self.ENV_NOT_SET:
            catalogue_lookup = 'beaker_env'
        else:
            catalogue_lookup = 'journal_beg'

        if not self.parsed_input_list:
            return

        for line in self.parsed_input_list:
            if constraint_met(line):
                return

            if self.is_beakerlib_command(line.argname):
                self.add_error('2400', catalogue_lookup,
                               msg=error_msg, lineno=line.lineno)
                return

    def check_deprecated_commands(self):

        for line in self.parsed_input_list:
            if line.argname not in self.deprecated_commands:
                continue
            msg = line.argname + " command is deprecated"
            use_instead = self.deprecated_commands[line.argname]
            if use_instead:
                msg += ", instead use: " + ', '.join(use_instead)
            self.add_error('2000', line.argname, msg, line.lineno)

    def check_journal_last_command(self):
        iter_parsed_list = iter(self.parsed_input_list)
        for line in iter_parsed_list:
            if not self.is_journal_end(line):
                continue
            for line_inner in iter_parsed_list:
                if not self.is_journal_print_or_end(line_inner):
                    self.add_error('2400', 'journal_end', self.JOURNAL_END, line_inner.lineno)
                    return

    @staticmethod
    def is_beakerlib_command(command):
        commands = bkrdoc_parser.Parser.all_commands + bkrdoc_parser.Parser.start_phase_names
        commands += ['rlJournalStart', 'rlJournalEnd', 'rlPhaseEnd']
        return command in commands

    @staticmethod
    def is_journal_start(line):
        return line.argname == "rlJournalStart"

    @staticmethod
    def is_journal_end(line):
        return line.argname == "rlJournalEnd"

    @staticmethod
    def is_journal_print_or_end(line):
        return line.argname in ['rlJournalPrint', 'rlJournalPrintText', 'rlJournalEnd']

    @staticmethod
    def sets_beaker_env(command):
        return command.argname == 'UNKNOWN' and command.data[0] == '.' and command.data[1].endswith('beakerlib.sh')

