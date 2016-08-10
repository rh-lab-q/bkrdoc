__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import l_pair_functions, l_single_rules, l_within_phase, l_arg_types, l_command_typos


class Linter(object):

    errors = []
    linter_rules = [l_pair_functions.LinterPairFunctions,
                    l_single_rules.LinterSingleRules,
                    l_within_phase.LinterWithinPhase,
                    l_arg_types.LinterArgTypes,
                    l_command_typos.LinterCommandTypos]

    def __init__(self):
        self.errors = []
        self.rule_refs = []

        for rule in self.linter_rules:
            self.rule_refs.append(rule())

    def analyse(self, _list):
        for line in _list:
            for rule_ref in self.rule_refs:
                rule_ref.analyse(line)

        for rule_ref in self.rule_refs:
            self.errors += rule_ref.get_errors()

