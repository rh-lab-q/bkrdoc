__author__ = 'blurry'

from bkrdoc.analysis.linter import l_pair_functions

class Linter(object):

    errors = []

    def __init__(self):
        self.errors = []

    def analyse(self, list):
        _pair_func_ref = l_pair_functions.LinterPairFunctions()
        _pair_func_ref.analyse(list)
        self.errors += _pair_func_ref.get_errors()

