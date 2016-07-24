__author__ = 'Zuzana Baranova'

import unittest
import argparse, sys
from bkrdoc.analysis.linter import output_generator, common, l_single_rules, linter, l_pair_functions
from bkrdoc.analysis.parser import statement_data_searcher


LSingleRules = l_single_rules.LinterSingleRules
LPairFunc = l_pair_functions.LinterPairFunctions
Namespace = argparse.Namespace
Severity  = common.Severity


def err(id, severity, msg, lineno):
    if severity is not None:
        severity = Severity[severity]
    return common.Error(id, severity, msg, lineno)


def get_errors_from_parse_list(parse_list):
    """Uses full linter analysis"""
    gener = output_generator.OutputGenerator(Namespace(file_in="",
                                                       enabled=None,
                                                       suppressed=None,
                                                       suppress_first=False))
    gener.main_linter.analyse(parse_list)
    return gener.main_linter.errors


def list_contains(self, sublist,_list):
        for elem in sublist:
            unittest.TestCase.assertIn(self, elem, _list)


class TestLinterClassInstances(unittest.TestCase):

    def test_inheritance(self):
        for rule in linter.Linter.linter_rules:
            self.assertTrue(issubclass(rule, common.LinterRule))
            self.assertTrue(callable(getattr(rule, 'analyse')))  # has an analyse method


class TestStandaloneRules(unittest.TestCase):

    list_contains_ = list_contains

    def test_empty(self):
        errors = get_errors_from_parse_list([])
        self.assertEqual(len(errors), 2)
        self.list_contains_([err('E2401','error',LSingleRules.ENV_NOT_SET, 0),
                             err('E2402','warning',LSingleRules.JOURNAL_NOT_STARTED, 0)],
                            errors)

    ns_beaker_env = Namespace(argname='UNKNOWN', data=['.', 'beakerlib.sh'], lineno=0)
    ns_journal = Namespace(argname='rlJournalStart', lineno=0)
    ns_rlrun = Namespace(argname='rlRun', command='command', lineno=0)
    ns_rlarch_depr = Namespace(argname='rlGetArch', lineno=0)

    def test_deprecated(self):
        parse_list = [self.ns_beaker_env, self.ns_journal, self.ns_rlrun, self.ns_rlarch_depr]
        errors = get_errors_from_parse_list(parse_list)
        err_msg = "rlGetArch command is deprecated, instead use: " + \
                  ', '.join(LSingleRules.deprecated_commands['rlGetArch'])
        self.assertEqual([err('E2001','error',err_msg, 0)], errors)

    def test_beaker_env(self):
        parse_list = [self.ns_journal, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err('E2401','error',LSingleRules.ENV_NOT_SET, 0)], errors)

    def test_journal_not_started(self):
        parse_list = [self.ns_beaker_env, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err('E2402','warning',LSingleRules.JOURNAL_NOT_STARTED, 0)], errors)


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

    ns_phase_start = Namespace(argname='rlPhaseStart', lineno=1)
    ns_phase_end = Namespace(argname='rlPhaseEnd', lineno=2)

    def test_no_end_present(self):
        parse_list = [self.ns_phase_start]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1001','error',"rlPhaseStart without a matching rlPhaseEnd", 1)], errors)

    def test_no_begin_present(self):
        parse_list = [self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1201','error',"rlPhaseEnd without a previous begin", 2)], errors)

    def test_before(self):
        parse_list = [self.ns_phase_start, self.ns_phase_start,
                      self.ns_phase_end, self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1101','warning',"rlPhaseStart before matching rlPhaseEnd", 1)], errors)

    def test_flags(self):

        ns_file_backup_a = Namespace(argname='rlFileBackup', namespace='a', lineno=1)
        ns_file_restore_a = Namespace(argname='rlFileRestore', namespace='a', lineno=2)
        ns_file_restore = Namespace(argname='rlFileRestore', namespace=None, lineno=3)

        parse_list = [ns_file_backup_a, ns_file_restore_a]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)

        parse_list = [ns_file_backup_a, ns_file_restore]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1202','error',"rlFileRestore without a previous begin", 3),
                          err('E1002','error',"rlFileBackup without a matching rlFileRestore with flag `a`", 1)],
                         errors)

    def test_list_flags(self):

        ns_service_start_a = Namespace(argname='rlServiceStart', service=['a'], lineno=1)
        ns_service_start_b = Namespace(argname='rlServiceStart', service=['b'], lineno=2)
        ns_service_stop_a_b = Namespace(argname='rlServiceStop', service=['a', 'b'], lineno=3)

        parse_list = [ns_service_start_a, ns_service_start_b, ns_service_stop_a_b]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)

    def test_restores_all(self):

        ns_bool_on_a = Namespace(argname='rlSEBooleanOn', boolean='a', lineno=1)
        ns_bool_off_a = Namespace(argname='rlSEBooleanOff', boolean='a', lineno=2)
        ns_bool_off_b = Namespace(argname='rlSEBooleanOff', boolean='b', lineno=3)
        ns_bool_restore_all = Namespace(argname='rlSEBooleanRestore', boolean=[], lineno=4)

        parse_list = [ns_bool_on_a, ns_bool_off_a, ns_bool_off_b, ns_bool_restore_all]
        errors = get_func_pair_errors(parse_list)
        self.assertEmpty(errors)


class TestArgparseParsingErrors(unittest.TestCase):

    # Py2 vs Py3: argparse returns a different error message
    TOO_FEW_ARGS = ["too few arguments",
                    "the following arguments are required: command"]

    def _test_command(self, command, command_list, err_expected):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(getattr(st_data_search, command), command_list)
        err_msg_got = st_data_search.get_errors()[0].message
        self.assertTrue(err_msg_got.startswith(err_expected))
        remainder = err_msg_got[len(err_expected):]
        self.assertTrue(remainder in self.TOO_FEW_ARGS, "got msg: " + remainder)

    def test_rlrun_error(self):
        message = "rlRun, usage: rlRun [-t] [-l] [-c] [-s] command [status] [comment] || "
        self._test_command("get_rlrun_data", ['rlRun'], message)

    def test_rlwaitfor_error(self):
        message = "rlWaitForCmd, usage: rlWaitForCmd [-p P] [-t T] [-d D] [-m M] [-r R] command || "
        self._test_command("get_rlwaitforxxx_data", ['rlWaitForCmd'], message)

    def test_float_error(self):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(st_data_search.get_rllogmetric_data, ['rlLogMetricLow', "0.9", 'notint'])
        err_msg = "rlLogMetricLow, invalid float value: 'notint'"
        self.assertEqual([err('E3001','error',err_msg,0)], st_data_search.get_errors())


class TestComplexFile(unittest.TestCase):

    list_contains_ = list_contains

    def test_complex(self):
        gener = output_generator.OutputGenerator(Namespace(file_in="./examples/bkrlint/test.sh",
                                                           enabled=None, suppressed=None, suppress_first=False))

        RLRUN = "rlRun, usage: rlRun [-t] [-l] [-c] [-s] command [status] [comment] || unrecognized arguments: -o"
        PHASEEND = "rlPhaseEnd without a previous begin"
        FILEBACKUP = "rlFileBackup without a matching rlFileRestore with flag `wut`"
        JOURNAL = "Journal was not started before a beakerlib command was used."
        GETARCH = "rlGetArch command is deprecated, instead use: rlGetPrimaryArch, rlGetSecondaryArch"

        gener.analyse()
        errors = gener.main_linter.errors
        self.assertEqual(len(errors), 5)
        expected_errors = [err('E3001', 'error', RLRUN, 12),
                           err('E1201', 'error', PHASEEND, 35),
                           err('E1002', 'error', FILEBACKUP, 14),
                           err('E2402', 'warning', JOURNAL, 0),
                           err('E2001', 'error', GETARCH, 17)]
        self.list_contains_(expected_errors, errors)


class TestOptions(unittest.TestCase):

    list_contains_ = list_contains

    args = Namespace(suppressed = ['E2102','3000','E4523','E1102'],
                     enabled = ['warning','E4523', 'E3001'],
                     suppress_first = True,
                     file_in = "")

    def test_option_setting(self):
        options = output_generator.OutputGenerator.Options(self.args)
        self.assertTrue(options.enabled[Severity.error])
        self.assertTrue(options.enabled[Severity.warning])
        self.assertFalse(options.enabled[Severity.info])

        self.list_contains_(['E3001'], options.enabled_by_id)
        self.list_contains_(['E3001', 'E1102'], options.suppressed_by_id)
        self.list_contains_([err('UNK_FLAG', None, "E4523 not recognized, continuing anyway--", 0),
                             err('UNK_FLAG', None, "E2102 not recognized, continuing anyway--", 0)],
                            options.unrecognized_options)

    def test_output_enabling(self):
        out_gen = output_generator.OutputGenerator(self.args) # enabled first
        err1 = err('E1002', 'error', "message", 1)
        err2 = err('E3001', 'warning', "message", 3)

        self.assertTrue(out_gen.is_enabled_severity(Severity.warning))
        self.assertTrue(out_gen.is_enabled_error(err1))
        self.assertFalse(out_gen.is_enabled_error(err2))


if __name__ == '__main__':
    unittest.main()
