__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import l_pair_functions, l_single_rules


class Linter(object):

    errors = []
    linter_rules = [l_pair_functions.LinterPairFunctions,
                    l_single_rules.LinterSingleRules]

    def __init__(self):
        self.errors = []

    def analyse(self, _list):

        for rule in self.linter_rules:
            rule_ref = rule(_list)
            rule_ref.analyse()
            self.errors += rule_ref.get_errors()

