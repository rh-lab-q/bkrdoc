#!/usr/bin/python
__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.parser import bkrdoc_parser
from bkrdoc.analysis.linter import linter


class OutputGenerator(object):

    def __init__(self, input_file):
        self.main_linter = linter.Linter()
        self.parser_ref = bkrdoc_parser.Parser(input_file)

    def analyse(self):
        self.parser_ref.parse_data()
        self.main_linter.errors += self.parser_ref.get_errors()
        self.main_linter.analyse(self.parser_ref.argparse_data_list)

    def print_to_stdout(self):
        #for elem in self._parser.argparse_data_list:
        #    print(elem)

        if not self.main_linter.errors:
            print("Static analysis revealed no errors.")
        else:
            for elem in self.main_linter.errors:
                print(elem.message)


# ***************** MAIN ******************
if __name__ == "__main__":
    gener = OutputGenerator("../../../examples/bkrlint/test.sh")
    #gener = OutputGenerator("../../../examples/tests/autopart-test.sh")
    gener.analyse()
    gener.print_to_stdout()