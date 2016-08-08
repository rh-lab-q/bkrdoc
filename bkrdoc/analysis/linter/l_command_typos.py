__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser


class LinterCommandTypos(common.LinterRule):
    """Class checking for typical command typos, Equals vs. Equal etc."""

    def __init__(self, parsed_input_list):
        super(LinterCommandTypos, self).__init__()
        self.parsed_input_list = parsed_input_list

    def analyse(self):
        def add_err(err_class, err_label):
            self.add_error(err_class, err_label,
                           "{} not recognized, perhaps you meant {}?".format(curr_command, command),
                           line.lineno)

        for line in self.parsed_input_list:
            if line.argname != 'UNKNOWN':
                continue
            curr_command = line.data[0]

            for command in bkrdoc_parser.Parser.beakerlib_commands:
                if curr_command.upper() == command.upper():
                    add_err('4000', 'letter_case')
                    break
                elif curr_command + "s" == command:
                    add_err('4000', 'end_s')
                    break
