#!/usr/bin/python
__author__ = 'Jiri_Kulda'

import shlex

class TestFunction:
    """Class for working with functions from the BeakerLib test"""

    statement_list = []

    data_list = []

    name = ""

    def __init__(self, fname):
        self.statement_list = []
        lex = shlex.shlex(fname)
        self.name = lex.get_token()
        self.data_list = []

    def add_line(self, line):
        self.statement_list.append(line)

    def add_data(self, data):
        self.data_list.append(data)

    def is_function_data_empty(self):
        return len(self.data_list) == 0