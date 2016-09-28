__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser


class LinterCommandTypos(common.LinterRule):
    """Class checking for typical command typos, Equals vs. Equal etc."""

    def __init__(self):
        super(LinterCommandTypos, self).__init__()

    def analyse(self, line):
        def add_err(err_label):
            self.add_error('4000', err_label,
                           "{} not recognized, perhaps you meant {}?".format(curr_command, command),
                           line.lineno)

        if line.argname != 'UNKNOWN':
            return
        curr_command = line.data[0]

        for command in bkrdoc_parser.Parser.beakerlib_commands:
            if curr_command.upper() == command.upper():
                add_err('letter_case')
                return
            elif curr_command + "s" == command:
                add_err('end_s')
                return

        if curr_command.startswith("rl") and len(curr_command)>2 and curr_command[2].isupper():
            self.add_error('4000', 'rl_command',
                           "{} is not recognized as a beakerlib command".format(curr_command),
                           line.lineno)
