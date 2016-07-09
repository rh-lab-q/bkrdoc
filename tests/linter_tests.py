__author__ = 'Zuzana Baranova'

import unittest
import argparse
from bkrdoc.analysis.linter import output_generator, common, l_single_rules, linter, l_pair_functions
from bkrdoc.analysis.parser import statement_data_searcher


LSingleRules = l_single_rules.LinterSingleRules
LPairFunc = l_pair_functions.LinterPairFunctions
Namespace = argparse.Namespace


def err(msg):
    return common.Error(message=msg)


def get_errors_from_parse_list(parse_list):
    """Uses full linter analysis"""
    gener = output_generator.OutputGenerator("")
    gener._linter.analyse(parse_list)
    return gener._linter.errors


def list_contains(self, sublist,_list):
        for elem in sublist:
            unittest.TestCase.assertIn(self, elem, _list)


class TestLinterClassInstances(unittest.TestCase):

    def test_inheritance(self):
        for rule in linter.Linter.linter_rules:
            self.assertTrue(issubclass(rule, common.LinterRule))
            self.assertTrue(callable(getattr(rule, 'analyse')))  # has an analyse method


class TestStandaloneRules(unittest.TestCase):

    _list_contains = list_contains

    def test_empty(self):
        errors = get_errors_from_parse_list([])
        self.assertEqual(len(errors), 2)
        self._list_contains([err(LSingleRules.ENV_NOT_SET), err(LSingleRules.JOURNAL_NOT_STARTED)], errors)

    ns_beaker_env = Namespace(argname='UNKNOWN', data=['.', 'beakerlib.sh'])
    ns_journal = Namespace(argname='rlJournalStart')
    ns_rlrun = Namespace(argname='rlRun', command='command')
    ns_rlarch_depr = Namespace(argname='rlGetArch')

    def test_deprecated(self):
        parse_list = [self.ns_beaker_env, self.ns_journal, self.ns_rlrun, self.ns_rlarch_depr]
        errors = get_errors_from_parse_list(parse_list)
        err_msg = "rlGetArch command is deprecated, instead use: " + \
                  ', '.join(LSingleRules.deprecated_commands['rlGetArch'])
        self.assertEqual([err(err_msg)], errors)

    def test_beaker_env(self):
        parse_list = [self.ns_journal, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err(LSingleRules.ENV_NOT_SET)], errors)

    def test_journal_not_started(self):
        parse_list = [self.ns_beaker_env, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err(LSingleRules.JOURNAL_NOT_STARTED)], errors)


def get_func_pair_errors(parse_list):
    """Uses pair functions analysis only"""
    pair_func = LPairFunc(parse_list)
    pair_func.analyse()
    return pair_func.get_errors()


class TestPairFunctions(unittest.TestCase):

    def assertEmpty(self, _list):
        self.assertFalse(_list)

    def test_empty(self):
        errors = get_func_pair_errors([])
        self.assertEmpty(errors)

    ns_phase_start = Namespace(argname='rlPhaseStart')
    ns_phase_end = Namespace(argname='rlPhaseEnd')

    def test_no_end_present(self):
        parse_list = [self.ns_phase_start]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err("rlPhaseStart without a matching rlPhaseEnd")], errors)

    def test_no_begin_present(self):
        parse_list = [self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err("rlPhaseEnd without a previous begin")], errors)

    def test_before(self):
        parse_list = [self.ns_phase_start, self.ns_phase_start,
                      self.ns_phase_end, self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err("rlPhaseStart before matching rlPhaseEnd")], errors)

    def test_flags(self):

        ns_file_backup_a = Namespace(argname='rlFileBackup', namespace='a')
        ns_file_restore_a = Namespace(argname='rlFileRestore', namespace='a')
        ns_file_restore = Namespace(argname='rlFileRestore', namespace=None)

        parse_list = [ns_file_backup_a, ns_file_restore_a]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)

        parse_list = [ns_file_backup_a, ns_file_restore]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err("rlFileRestore without a previous begin"),
                          err("rlFileBackup without a matching rlFileRestore with flag `a`")],
                         errors)

    def test_list_flags(self):

        ns_service_start_a = Namespace(argname='rlServiceStart', service=['a'])
        ns_service_start_b = Namespace(argname='rlServiceStart', service=['b'])
        ns_service_stop_a_b = Namespace(argname='rlServiceStop', service=['a', 'b'])

        parse_list = [ns_service_start_a, ns_service_start_b, ns_service_stop_a_b]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)

    def test_restores_all(self):

        ns_bool_on_a = Namespace(argname='rlSEBooleanOn', boolean='a')
        ns_bool_off_a = Namespace(argname='rlSEBooleanOff', boolean='a')
        ns_bool_off_b = Namespace(argname='rlSEBooleanOff', boolean='b')
        ns_bool_restore_all = Namespace(argname='rlSEBooleanRestore', boolean=[])

        parse_list = [ns_bool_on_a, ns_bool_off_a, ns_bool_off_b, ns_bool_restore_all]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)


class TestArgparseParsingErrors(unittest.TestCase):

    def test_rlrun_error(self):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(st_data_search.get_rlrun_data, ['rlRun'])
        err_msg = "rlRun [-h] [-t] [-l] [-c] [-s] argname command [status] [comment] " \
                  "|| the following arguments are required: command"
        self.assertEqual([err(err_msg)], st_data_search.get_errors())

    # the only method that takes multiple params -- realized as a tuple
    def test_rlwaitfor_error(self):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(st_data_search.get_rlwaitforxxx_data, (['rlWaitForCmd'], 'rlWaitForCmd'))
        err_msg = "rlWaitForCmd [-h] [-p P] [-t T] [-d D] [-m M] [-r R] argname command " \
                  "|| the following arguments are required: command"
        self.assertEqual([err(err_msg)], st_data_search.get_errors())


class TestComplexFile(unittest.TestCase):

    _list_contains = list_contains

    def test_complex(self):
        gener = output_generator.OutputGenerator("./examples/bkrlint/test.sh")
        gener.analyse()
        errors = gener._linter.errors
        self.assertEqual(len(errors), 6)
        expected_errors = [err("rlRun [-h] [-t] [-l] [-c] [-s] argname command [status] [comment] || unrecognized arguments: -o"),
                           err("rlMount server share mountpoint || the following arguments are required: share, mountpoint"),
                           err("rlPhaseEnd without a previous begin"),
                           err("rlFileBackup without a matching rlFileRestore with flag `wut`"),
                           err("Journal was not started before a beakerlib command was used."),
                           err("rlGetArch command is deprecated, instead use: rlGetPrimaryArch, rlGetSecondaryArch")]
        self._list_contains(expected_errors, errors)


if __name__ == '__main__':
    unittest.main()
