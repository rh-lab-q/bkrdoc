__author__ = 'Zuzana Baranova'

import argparse
from bkrdoc.analysis.linter import l_pair_functions, l_single_rules, l_within_phase, l_arg_types, l_command_typos
from bkrdoc.analysis.parser import data_containers

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
            self.recursive_analyse(line)
        for rule_ref in self.rule_refs:
            self.errors += rule_ref.get_errors()

    def recursive_analyse(self, line):
        if isinstance(line, argparse.Namespace):
            self.analyse_command(line)
        elif any([self.is_type(line, type_) for type_ in ['for loop', 'condition', 'case']]):
            for statement in line.statement_list:
                self.recursive_analyse(statement)
        else:
            print('line not a loop')

    def analyse_command(self, command):
        for rule_ref in self.rule_refs:
            rule_ref.analyse(command)

    def is_type(self, line, argument):
        return self.is_container(line) and line.argname == argument

    @staticmethod
    def is_container(line):
        dc = data_containers
        return any([isinstance(line, container) for container in [dc.SimpleContainer,
                                                                  dc.DataContainer,
                                                                  dc.LoopContainer,
                                                                  dc.CaseContainer]])
