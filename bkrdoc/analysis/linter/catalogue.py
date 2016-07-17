__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter.common import Severity

catalogue = {

    # pair functions - begin without end
    '1000' : { 'rlPhaseStart': ('E1001', Severity.error),
             'rlPhaseStartTest': ('E1001', Severity.error),
             'rlPhaseStartSetup': ('E1001', Severity.error),
             'rlPhaseStartCleanup': ('E1001', Severity.error),
             'rlFileBackup': ('E1002', Severity.error),
             'rlVirtualXStart': ('E1003', Severity.warning),
             'rlServiceStart': ('E1004', Severity.warning),
             'rlSEBooleanOn': ('E1005', Severity.error),
             'rlSEBooleanOff': ('E1005', Severity.error) },
    # pair functions - end before `before`
    '1100' : { 'rlPhaseEnd': ('E1101', Severity.warning),
             'rlServiceStop': ('E1102', Severity.warning) },
    # pair functions - ends without begins
    '1200' : { 'rlPhaseEnd': ('E1201', Severity.error),
             'rlFileRestore': ('E1202', Severity.error),
             'rlVirtualXStop': ('E1203', Severity.error),
             'rlServiceStop': ('E1204', Severity.error),
             'rlSEBooleanRestore': ('E1205', Severity.error) },

    # deprecated commands
    '2000' : { 'rlGetArch': ('E2001', Severity.error) },

    '2400' : { 'beaker_env': ('E2401', Severity.error), # beakerlib environment not set
             'journal_beg': ('E2402', Severity.warning), # journal not started
             'journal_end': ('E2403', Severity.warning) }, # journal end followed by a command

    # argument errors (parsing/type)
    '3000' : { 'parse_err': ('E3001', Severity.error) }

}
