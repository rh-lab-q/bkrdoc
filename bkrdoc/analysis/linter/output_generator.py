#!/usr/bin/python
__author__ = 'blurry'

from bkrdoc.analysis.parser import bkrdoc_parser
from bkrdoc.analysis.linter import linter


class OutputGenerator(object):

    def __init__(self, file):
        self._linter = linter.Linter()
        self._parser = bkrdoc_parser.Parser(file)

    def analyse(self):

        self._parser.parse_data()
        self._linter.errors += self._parser.get_errors()

        #for elem in self._parser.argparse_data_list:
        #    print(elem)

        self._linter.analyse(self._parser.argparse_data_list)


        if not self._linter.errors:
            print("Static analysis revealed no errors.")
        else:
            for elem in self._linter.errors:
                print(elem.message)


# ***************** MAIN ******************
if __name__ == "__main__":
    gener = OutputGenerator("../../../examples/bkrlint/test.sh")
    #gener = OutputGenerator("../../../examples/tests/autopart-test.sh")
    gener.analyse()
