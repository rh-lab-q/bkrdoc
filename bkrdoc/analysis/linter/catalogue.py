__author__ = 'Zuzana Baranova'

from enum import Enum


class Severity(Enum):
    error = 1
    warning = 2
    info = 3


catalogue = {

    # pair functions - begin without end
    '1000': {'rlPhaseStart': ('E1001', Severity.error),
             'rlPhaseStartTest': ('E1001', Severity.error),
             'rlPhaseStartSetup': ('E1001', Severity.error),
             'rlPhaseStartCleanup': ('E1001', Severity.error),
             'rlFileBackup': ('E1002', Severity.error),
             'rlVirtualXStart': ('E1003', Severity.warning),
             'rlServiceStart': ('E1004', Severity.warning),
             'rlSEBooleanOn': ('E1005', Severity.error),
             'rlSEBooleanOff': ('E1005', Severity.error)},
    # pair functions - end before `before`
    '1100': {'rlPhaseEnd': ('E1101', Severity.warning),
             'rlServiceStop': ('E1102', Severity.warning)},
    # pair functions - ends without begins
    '1200': {'rlPhaseEnd': ('E1201', Severity.error),
             'rlFileRestore': ('E1202', Severity.error),
             'rlVirtualXStop': ('E1203', Severity.error),
             'rlServiceStop': ('E1204', Severity.error),
             'rlSEBooleanRestore': ('E1205', Severity.error)},

    # within phase
    '1500': {'rlLogMetric': ('E1501', Severity.error),  # metric name has to be unique
             'empty_phase': ('E2404', Severity.warning)},  # empty phase

    # deprecated commands
    '2000': {'rlGetArch': ('E2001', Severity.error),
             'rlLogLowMetric': ('E2002', Severity.error),
             'rlLogHighMetric': ('E2002', Severity.error),
             'rlShowPkgVersion': ('E2003', Severity.error)},

    '2400': {'beaker_env': ('E2401', Severity.error),  # beakerlib environment not set
             'journal_beg': ('E2402', Severity.warning),  # journal not started
             'journal_end': ('E2403', Severity.warning)},  # journal end followed by a command

    # argument errors (parsing/type)
    '3000': {'parse_err': ('E3001', Severity.error),
             'rlRun_type': ('E3010', Severity.error),  # rlRun status not a float(int)
             'rlRun_bounds': ('E3011', Severity.error),  # rlRun range status a-b : a>b
             'rlWatchdog': ('E3012', Severity.info),  # rlWatchdog signal not a common one
             'rlReport': ('E3013', Severity.warning),  # rlReport result not in (PASS,WARN,FAIL)
             'rhel_fedora': ('E3014', Severity.error),  # rlIsRHEL/Fedora invalid type
             'rhel_fedora_neg': ('E3015', Severity.info)},  # rlIsRHEL/Fedora negative number

    # command typos
    '4000': {'letter_case': ('E4001', Severity.error),  # command differs by upper/lowercase
             'end_s': ('E4002', Severity.error)}  # Equals vs. Equal
}
