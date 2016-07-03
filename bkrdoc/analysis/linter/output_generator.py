#!/usr/bin/python
__author__ = 'blurry'

from bkrdoc.analysis.parser import bkrdoc_parser
from bkrdoc.analysis.linter import linter

class OutputGenerator(object):
    file_ = ""
    parser = ""
    # phases = []

    def __init__(self, file):
        self.parser = bkrdoc_parser.Parser(file)
        self.parser.parse_data()

    def analyse(self):

        #for elem in self.parser.argparse_data_list:
        #    print(elem)

        _linter = linter.Linter()
        _linter.analyse(self.parser.argparse_data_list)

        if not _linter.errors:
            print("Static analysis revealed no errors.")
        else :
            for elem in _linter.errors:
                print(elem.message)


# ***************** MAIN ******************
if __name__ == "__main__":
    gener = OutputGenerator("../../../examples/bkrlint/test.sh")
    #gener = OutputGenerator("../../../examples/tests/autopart-test.sh")
    gener.analyse()
