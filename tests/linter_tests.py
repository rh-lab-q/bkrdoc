__author__ = 'Zuzana Baranova'

import unittest
import argparse
from bkrdoc.analysis.linter import output_generator, common, catalogue, linter
from bkrdoc.analysis.linter import l_single_rules, l_pair_functions, l_arg_types, l_within_phase, l_command_typos
from bkrdoc.analysis.parser import statement_data_searcher


LSingleRules = l_single_rules.LinterSingleRules
LPairFunc = l_pair_functions.LinterPairFunctions
LArgTypes = l_arg_types.LinterArgTypes
LWithinPhase = l_within_phase.LinterWithinPhase
LTypos = l_command_typos.LinterCommandTypos
Namespace = argparse.Namespace
Severity = catalogue.Severity


def err(err_id, severity, msg, lineno=0):
    if severity is not None:
        severity = Severity[severity]
    return common.Error(err_id, severity, msg, lineno)


def filter_outside_phase_errors(err_list):
    return [error for error in err_list if error.err_id != 'E1503']

def get_errors_from_parse_list(parse_list):
    """Uses full linter analysis"""
    gener = output_generator.OutputGenerator(Namespace(file_in="",
                                                       enabled=None,
                                                       suppressed=None,
                                                       suppress_first=False,
                                                       catalogue=False))
    gener.main_linter.analyse(parse_list)
    return filter_outside_phase_errors(gener.main_linter.errors)


def list_contains(self, sublist, list_):
    for elem in sublist:
        unittest.TestCase.assertIn(self, elem, list_, "{} not found".format(elem))


def assert_empty(self, list_):
    self.assertFalse(list_)


class TestLinterClassInstances(unittest.TestCase):

    def test_inheritance(self):
        for rule in linter.Linter.linter_rules:
            self.assertTrue(issubclass(rule, common.LinterRule))
            self.assertTrue(callable(getattr(rule, 'analyse')))  # has an analyse method


class TestStandaloneRules(unittest.TestCase):

    list_contains_ = list_contains
    assert_empty_ = assert_empty

    def test_empty(self):
        errors = get_errors_from_parse_list([])
        self.assert_empty_(errors)

    ns_beaker_env = Namespace(argname='UNKNOWN', data=['.', 'beakerlib.sh'], lineno=0)
    ns_journal = Namespace(argname='rlJournalStart', lineno=0)
    ns_rlrun = Namespace(argname='rlRun', command='command', lineno=0, status='0')
    ns_rlarch_depr = Namespace(argname='rlGetArch', lineno=0)

    def test_deprecated(self):
        parse_list = [self.ns_beaker_env, self.ns_journal, self.ns_rlrun, self.ns_rlarch_depr]
        errors = get_errors_from_parse_list(parse_list)
        err_msg = "rlGetArch command is deprecated, instead use: " + \
                  ', '.join(catalogue.Catalogue.deprecated_commands['rlGetArch'])
        self.assertEqual([err('E2001', 'error', err_msg, 0)], errors)

    def test_beaker_env(self):
        parse_list = [self.ns_journal, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err('E2401', 'error', LSingleRules.ENV_NOT_SET, 0)], errors)

    def test_journal_not_started(self):
        parse_list = [self.ns_beaker_env, self.ns_rlrun]
        errors = get_errors_from_parse_list(parse_list)
        self.assertEqual([err('E2402', 'warning', LSingleRules.JOURNAL_NOT_STARTED, 0)], errors)


def get_func_pair_errors(parse_list):
    """Uses pair functions analysis only"""
    pair_func = LPairFunc()
    for line in parse_list:
        pair_func.analyse(line)
    return pair_func.get_errors()


class TestPairFunctions(unittest.TestCase):

    assert_empty_ = assert_empty

    def test_empty(self):
        errors = get_func_pair_errors([])
        self.assert_empty_(errors)

    ns_phase_start = Namespace(argname='rlPhaseStart', lineno=1)
    ns_phase_end = Namespace(argname='rlPhaseEnd', lineno=2)

    def test_no_end_present(self):
        parse_list = [self.ns_phase_start]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1001', 'error', "rlPhaseStart without a matching rlPhaseEnd", 1)], errors)

    def test_no_begin_present(self):
        parse_list = [self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1201', 'error', "rlPhaseEnd without a previous begin", 2)], errors)

    def test_before(self):
        parse_list = [self.ns_phase_start, self.ns_phase_start,
                      self.ns_phase_end, self.ns_phase_end]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1101', 'warning', "rlPhaseStart before matching rlPhaseEnd", 1)], errors)

    def test_flags(self):

        ns_file_backup_a = Namespace(argname='rlFileBackup', namespace='a', lineno=1)
        ns_file_restore_a = Namespace(argname='rlFileRestore', namespace='a', lineno=2)
        ns_file_restore = Namespace(argname='rlFileRestore', namespace=None, lineno=3)

        parse_list = [ns_file_backup_a, ns_file_restore_a]
        errors = get_func_pair_errors(parse_list)
        self.assert_empty_(errors)

        parse_list = [ns_file_backup_a, ns_file_restore]
        errors = get_func_pair_errors(parse_list)
        self.assertEqual([err('E1202', 'error', "rlFileRestore without a previous begin", 3),
                          err('E1002', 'error', "rlFileBackup without a matching rlFileRestore with flag `a`", 1)],
                         errors)

    def test_list_flags(self):

        ns_service_start_a = Namespace(argname='rlServiceStart', service=['a'], lineno=1)
        ns_service_start_b = Namespace(argname='rlServiceStop', service=['b'], lineno=2)
        ns_service_stop_a_b = Namespace(argname='rlServiceRestore', service=['a', 'b'], lineno=3)

        parse_list = [ns_service_start_a, ns_service_start_b, ns_service_stop_a_b]
        errors = get_func_pair_errors(parse_list)
        self.assert_empty_(errors)

    def test_restores_all(self):

        ns_bool_on_a = Namespace(argname='rlSEBooleanOn', boolean='a', lineno=1)
        ns_bool_off_a = Namespace(argname='rlSEBooleanOff', boolean='a', lineno=2)
        ns_bool_off_b = Namespace(argname='rlSEBooleanOff', boolean='b', lineno=3)
        ns_bool_restore_all = Namespace(argname='rlSEBooleanRestore', boolean=[], lineno=4)

        parse_list = [ns_bool_on_a, ns_bool_off_a, ns_bool_off_b, ns_bool_restore_all]
        errors = get_func_pair_errors(parse_list)
        self.assert_empty_(errors)


class TestArgparseParsingErrors(unittest.TestCase):

    # Py2 vs Py3: argparse returns a different error message
    TOO_FEW_ARGS = ["too few arguments",
                    "the following arguments are required: command"]

    def _test_command(self, command, command_list, err_expected):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(getattr(st_data_search, command), command_list)
        err_msg_got = st_data_search.get_errors()[0].message
        self.assertTrue(err_msg_got.startswith(err_expected), "got msg: " + err_msg_got)
        remainder = err_msg_got[len(err_expected):]
        self.assertTrue(remainder in self.TOO_FEW_ARGS, "got msg: " + remainder)

    def test_rlrun_error(self):
        message = "rlRun, usage: rlRun [-t] [-l] [-c] [-s] command [status] [comment] || "
        self._test_command("get_rlrun_data", ['rlRun'], message)

    def test_rlwaitfor_error(self):
        message = "rlWaitForCmd, usage: rlWaitForCmd [-p PID] [-t TIME] [-d DELAY] [-m COUNT] [-r RETVAL]\n\
                    command || "
        self._test_command("get_rlwaitforxxx_data", ['rlWaitForCmd'], message)

    def test_too_many_args(self):
        st_data_search = statement_data_searcher.StatementDataSearcher()
        st_data_search.check_err(st_data_search.get_rlfilesubmit_data,
                                 ['rlFileSubmit', '-s', '/', 'path', 'req_name', 'fluff', 'more_fluff'])
        err_msg = "rlFileSubmit, too many arguments (unrecognized args: ['fluff', 'more_fluff'])"
        self.assertEqual([err('E3002', 'warning', err_msg, 0)], st_data_search.get_errors())


class TestComplexFile(unittest.TestCase):

    list_contains_ = list_contains

    def test_complex(self):
        gener = output_generator.OutputGenerator(Namespace(file_in="./examples/bkrlint/test.sh",
                                                           enabled=None, suppressed=None,
                                                           suppress_first=False, catalogue=False))

        RLRUN = "rlRun, too many arguments (unrecognized args: ['-o'])"
        PHASEEND = "rlPhaseEnd without a previous begin"
        FILEBACKUP = "rlFileBackup without a matching rlFileRestore with flag `wut`"
        JOURNAL = "Journal was not started before a beakerlib command was used."
        GETARCH = "rlGetArch command is deprecated, instead use: rlGetPrimaryArch, rlGetSecondaryArch"

        gener.analyse()
        errors = filter_outside_phase_errors(gener.main_linter.errors)
        self.assertEqual(len(errors), 5)
        expected_errors = [err('E3002', 'warning', RLRUN, 12),
                           err('E1201', 'error', PHASEEND, 35),
                           err('E1002', 'error', FILEBACKUP, 14),
                           err('E2402', 'warning', JOURNAL, 9),
                           err('E2001', 'error', GETARCH, 17)]
        self.list_contains_(expected_errors, errors)


class TestOptions(unittest.TestCase):

    list_contains_ = list_contains

    args = Namespace(suppressed=['E2102', '3000', 'E4523', 'E1101'],
                     enabled=['warning', 'E4523', 'E3001'],
                     suppress_first=True, catalogue=False,
                     file_in="")

    def test_option_setting(self):
        options = output_generator.OutputGenerator.Options(self.args)
        self.assertTrue(options.enabled[Severity.error])
        self.assertTrue(options.enabled[Severity.warning])
        self.assertFalse(options.enabled[Severity.info])

        self.list_contains_(['E3001'], options.enabled_by_id)
        self.list_contains_(['E3001', 'E1101'], options.suppressed_by_id)
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


class TestArgTypes(unittest.TestCase):

    assert_empty_  = assert_empty
    list_contains_ = list_contains

    def test_rlrun_valid(self):
        argtypes = LArgTypes()
        for status in ['0', '1,2,3,4', '2-5', '12,3-9,8,255', '0.3,5.2-9.1']:
            argtypes.check_status(status, "")
            self.assert_empty_(argtypes.errors)

    def test_rlrun_invalid(self):
        argtypes = LArgTypes()
        for status in ['0.0.0', '256', '-3', '5-3', 'a', '3,1,e.2', '1.b', '3-']:
            argtypes.check_status(status, argtypes.STATUS_NOT_INT)
        self.assertEqual(len(argtypes.errors), 8)

    def test_rlwatchdog_valid(self):
        argtypes = LArgTypes()
        for signal in ['KILL', 'SIGABRT', 'CHLD', 'SIGTSTP']:
            argtypes.check_signal(signal, "")
        self.assert_empty_(argtypes.errors)

    def test_rlwatchdog_invalid(self):
        argtypes = LArgTypes()
        argtypes.argname = 'rlWatchdog'
        for signal in ['puppies', '7a']:
            argtypes.check_signal(signal, argtypes.SIGNAL)
        self.assertEqual(len(argtypes.errors), 2)
        self.list_contains_([err('E3012', 'info',
                                 "{}, `{}` {}".format(argtypes.argname, 'puppies', argtypes.SIGNAL), 0)],
                            argtypes.errors)

    def test_rlreport(self):
        argtypes = LArgTypes()
        argtypes.argname = 'rlReport'
        for result in ['PASS', 'FAIL', 'FALL', 'WARN', 'sthelse', 'PasS']:
            argtypes.check_result(result, argtypes.RESULT)
        self.assertEqual(len(argtypes.errors), 2)
        self.list_contains_([err('E3014', 'warning',
                                 "{}, `{}` {}".format(argtypes.argname, 'FALL', argtypes.RESULT), 0)],
                            argtypes.errors)

    def test_rhel_fedora(self):
        argtypes = LArgTypes()
        argtypes.argname = 'rlOS'
        types = ['>=3', '=>2', '=0', '=-1', '<1', 'a', '=e', '>2.3']
        argtypes.check_os_type(types, argtypes.OS_TYPE_INVALID)
        self.assertEqual(len(argtypes.errors), 4)
        self.list_contains_([err('E3015', 'error',
                                 "{}, `{}` - {}".format(argtypes.argname, '=e', argtypes.OS_TYPE_INVALID), 0),
                             err('E3015', 'error',
                                 "{}, `{}` - {}".format(argtypes.argname, '=>2', argtypes.OS_TYPE_INVALID), 0)],
                            argtypes.errors)

    def test_lib_format(self):
        for lib in ["a//b", "/a", "/a/b", "a/", "a/b/"]:
            self.assertFalse(LArgTypes.is_library_import_format(lib), "Failed for: " + lib)
        for lib in ["a/b", "abcde/fgh.ase^2"]:
            self.assertTrue(LArgTypes.is_library_import_format(lib), "Failed for: " + lib)

    def test_version(self):
        argtypes = LArgTypes()
        argtypes.argname = 'rlCmpVersion'
        for version in ['abcs', 'e458', 'c22.sd-asd1._55', '$NAME', '$al26.0p', '5']:
            argtypes.check_version(version, argtypes.VERSION)
        self.assert_empty_(argtypes.errors)

        err_temp = []
        for version in ['a%', 'a$a', '+q', 'u$', '']:
            argtypes.check_version(version, argtypes.VERSION)
            err_temp.append(err('E3029', 'error',
                                "{}, {} (was `{}`)".format(argtypes.argname, argtypes.VERSION, version), 0))
        self.assertEqual(len(argtypes.errors), 5)
        self.list_contains_(err_temp, argtypes.errors)

    def test_param_expansion(self):
        argtypes = LArgTypes()
        argtypes.analyse(Namespace(argname='rlLogMetricLow', name='name', value="$VAL",
                                   tolerance="$TOL", lineno=1))
        self.assert_empty_(argtypes.errors)

    def test_metrics_invalid(self):
        argtypes = LArgTypes()
        err_temp = []
        for tol in ["notint", "-3", "2.2.2"]:
            argtypes.analyse(Namespace(argname='rlLogMetricHigh', name='name', value="$VAL",
                                       tolerance=tol, lineno=0))
            err_temp.append(err('E3022', 'error', "{}, `{}` - {} {}".format('rlLogMetricHigh',
                                                                            tol,
                                                                            "logmetric tolerance",
                                                                            argtypes.NONNEGATIVE)))
        self.list_contains_(err_temp, argtypes.errors)

def analyse_with_rule(self, rule, parse_list, expected_err_list):
    rule_ref = rule()
    for line in parse_list:
        rule_ref.analyse(line)
    self.assertEqual(len(filter_outside_phase_errors(rule_ref.errors)), len(expected_err_list))
    self.list_contains_(expected_err_list, rule_ref.errors)


class TestTypos(unittest.TestCase):

    UNRECOGNIZED = "not recognized, perhaps you meant"

    list_contains_ = list_contains
    analyse_with_rule_ = analyse_with_rule

    def test_case_sensitivity(self):
        parse_list = [Namespace(argname='UNKNOWN', data=['rlPhasestartSetup'], lineno=0),
                      Namespace(argname='UNKNOWN', data=['rlcheckmakefilerequires'], lineno=0)]
        expected_errors = [err('E4001', 'error',
                               "{} {} {}?".format('rlPhasestartSetup', self.UNRECOGNIZED, 'rlPhaseStartSetup')),
                           err('E4001', 'error',
                               "{} {} {}?".format('rlcheckmakefilerequires', self.UNRECOGNIZED, 'rlCheckMakefileRequires'))]
        self.analyse_with_rule_(LTypos, parse_list, expected_errors)

    def test_ending_s(self):
        parse_list = [Namespace(argname='UNKNOWN', data=['rlAssertEqual'], lineno=0),
                      Namespace(argname='UNKNOWN', data=['rlAssertExist'], lineno=0)]
        expected_errors = [err('E4002', 'error',
                               "{} {} {}?".format('rlAssertEqual', self.UNRECOGNIZED, 'rlAssertEquals')),
                           err('E4002', 'error',
                               "{} {} {}?".format('rlAssertExist', self.UNRECOGNIZED, 'rlAssertExists'))]
        self.analyse_with_rule_(LTypos, parse_list, expected_errors)


class TestWithinPhase(unittest.TestCase):

    list_contains_ = list_contains
    analyse_with_rule_ = analyse_with_rule

    def test_empty_phase(self):
        parse_list = [Namespace(argname='rlPhaseStartTest', lineno=3),
                      Namespace(argname='rlPhaseEnd', lineno=4)]
        expected_errors = [err('E1502', 'style', LWithinPhase.EMPTY_PHASE, 4)]
        self.analyse_with_rule_(LWithinPhase, parse_list, expected_errors)

    def test_metric_name(self):
        parse_list = [Namespace(argname='rlPhaseStartTest', lineno=0),
                      Namespace(argname='rlLogMetricLow', name='a', lineno=1),
                      Namespace(argname='UNKNOWN', lineno=2),
                      Namespace(argname='rlLogMetricHigh', name='a', lineno=3)]
        expected_errors = [err('E1501', 'error', "{} ({})".format(LWithinPhase.METRICNAME, 'a'), 3)]
        self.analyse_with_rule_(LWithinPhase, parse_list, expected_errors)


if __name__ == '__main__':
    unittest.main()
