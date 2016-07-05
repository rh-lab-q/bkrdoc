__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser


class LinterSingleRules(common.LinterRule):
    """
    Class that checks for standalone rules that did not fit elsewhere.
    As of now this includes:
        Beakerlib environment must be set at the beginning.
        Journal must be started before any other command.
    """

    ENV_NOT_SET = "Beakerlib environment was not set before a beakerlib command was used."
    JOURNAL_NOT_STARTED = "Journal was not started before a beakerlib command was used."

    def __init__(self, _list):
        self.errors = []
        self._list = _list

    def analyse(self):
        self.check_environment_set()
        self.check_journal_started()

    def check_environment_set(self):
        self.constraint_check(self.sets_beaker_env, self.ENV_NOT_SET)

    def check_journal_started(self):
        self.constraint_check(self.is_journal_start, self.JOURNAL_NOT_STARTED)

    def constraint_check(self, constraint_met, error_msg):
        for line in self._list:
            if constraint_met(line):
                return

            if self.is_beakerlib_command(line.argname):
                self.add_error(msg=error_msg)
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
    def sets_beaker_env(command):
        return command.argname == 'UNKNOWN' and command.data[0] == '.' and command.data[1].endswith('beakerlib.sh')

