__author__ = 'Zuzana Baranova'

import sys
from enum import Enum
from argparse import Namespace


class Severity(Enum):
    error = 1
    warning = 2
    info = 3
    style = 4


class Catalogue:

    pair_ends = {
        'rlPhaseStart': 'rlPhaseEnd',
        'rlPhaseStartTest': 'rlPhaseEnd',
        'rlPhaseStartSetup': 'rlPhaseEnd',
        'rlPhaseStartCleanup': 'rlPhaseEnd',
        'rlFileBackup': 'rlFileRestore',
        'rlVirtualXStart': 'rlVirtualXStop',
        'rlServiceStart': 'rlServiceRestore',
        'rlServiceStop': 'rlServiceRestore',
        'rlSEBooleanOn': 'rlSEBooleanRestore',
        'rlSEBooleanOff': 'rlSEBooleanRestore'
    }

    deprecated_commands = {
        'rlGetArch': ['rlGetPrimaryArch', 'rlGetSecondaryArch'],
        'rlLogLowMetric': ['rlLogMetricLow'],
        'rlLogHighMetric': ['rlLogMetricHigh'],
        'rlShowPkgVersion': ['rlShowPackageVersion']
    }

    table = {

        '1000': Namespace(
            description="Pair commands -- begin without end\n"
                        "Each opening pair command needs a corresponding closing command, "
                        "which is mostly needed for matching phase begins with ends.",
            description_function='get_pair_end_description',
            value={'rlPhaseStart': ('E1001', Severity.error),
                   'rlPhaseStartTest': ('E1001', Severity.error),
                   'rlPhaseStartSetup': ('E1001', Severity.error),
                   'rlPhaseStartCleanup': ('E1001', Severity.error),
                   'rlFileBackup': ('E1002', Severity.error),
                   'rlVirtualXStart': ('E1003', Severity.warning),
                   'rlServiceStart': ('E1004', Severity.error),
                   'rlServiceStop': ('E1005', Severity.error),
                   'rlSEBooleanOn': ('E1006', Severity.error),
                   'rlSEBooleanOff': ('E1007', Severity.error)}),

        '1100': Namespace(
            description="Pair commands -- end before 'before'\n"
                        "A command can have a `before` specified - a list of commands "
                        "which should not appear before its ending counterpart "
                        "has been encountered.",
            value={'rlPhaseEnd': ('E1101', Severity.warning, "rlPhaseEnd, before: PhaseStartX"),
                   'rlServiceStop': ('E1102', Severity.warning, "rlServiceStop, before: rlServiceRestore")}),

        '1200': Namespace(
            description="Pair commands -- end without begin\n"
                        "Similarly to begins without ends, an ending without a begin has "
                        "been found. This is especially useful for commands differing by some label "
                        "or flag where they have to match for each pair.",
            description_function='get_pair_begin_description',
            value={'rlPhaseEnd': ('E1201', Severity.error),
                   'rlFileRestore': ('E1202', Severity.error),
                   'rlVirtualXStop': ('E1203', Severity.error),
                   'rlSEBooleanRestore': ('E1204', Severity.error)}),

        '1500': Namespace(
            description="Within phase functionality\n"
                        "Error class uniting problems that are related to phase composition "
                        "of tests.",
            value={'rlLogMetric': ('E1501', Severity.error, "metric name has to be unique within a single phase"),
                   'empty_phase': ('E1502', Severity.style, "empty phase found"),
                   'out_of_phase': ('E1503', Severity.style, "out of phase command")}),

        '2000': Namespace(
            description="Deprecated commands\n"
                        "The following commands are deprecated and should no longer be used:",
            description_function='get_deprecated_alternative',
            value={'rlGetArch': ('E2001', Severity.error),
                   'rlLogLowMetric': ('E2002', Severity.error),
                   'rlLogHighMetric': ('E2002', Severity.error),
                   'rlShowPkgVersion': ('E2003', Severity.error)}),

        '2400': Namespace(
            description="Standalone rules",
            value={'beaker_env': ('E2401', Severity.error, "beakerlib environment not set"),
                   'journal_beg': ('E2402', Severity.warning, "journal not started"),
                   'journal_end': ('E2403', Severity.warning, "journal end followed by a command other than journal print")}),

        '3000': Namespace(
            description="Argument errors\n"
                        "A number of commands require specific type of arguments. "
                        "The simple ones (int/float..) are checked at command parsing, "
                        "while the more complex ones are checked individually. "
                        "This includes passing unknown options to commands or "
                        "using one too many arguments.",
            value={'parse_err': ('E3001', Severity.error, "invalid command argument"),
                   'too_many_args': ('E3002', Severity.warning, "too many arguments / unrecognized options"),
                   'rlRun_type': ('E3010', Severity.error, "rlRun status not a float(int)"),
                   'rlRun_bounds': ('E3011', Severity.error, "rlRun range status a-b : a>b"),
                   'rlWatchdog_signal': ('E3012', Severity.info, "rlWatchdog signal not a common one"),
                   'rlWait_signal': ('E3013', Severity.info, "rlWait signal not a common one"),
                   'rlReport': ('E3014', Severity.warning, "rlReport result not in (PASS,WARN,FAIL)"),
                   'rhel_fedora': ('E3015', Severity.error, "rlIsRHEL/Fedora invalid format of type"),
                   'hash_algo': ('E3016', Severity.error, "rlHash/rlUnhash invalid hash algorithm"),
                   'time': ('E3017', Severity.error, "rlWaitForX time not a non-negative integer"),
                   'pid': ('E3018', Severity.error, "rlWaitForX PID not a non-negative integer"),
                   'count': ('E3019', Severity.error, 'rlWaitForCmd count not a non-negative integer'),
                   'retval': ('E3020', Severity.error, 'rlWaitForCmd return value not an int within range (0,255)'),
                   'library': ('E3021', Severity.warning, 'rlImport library has to be in X/Y format')}),

        '4000': Namespace(
            description="Command typos\n"
                        "Class checking for the most common typos that "
                        "users tend to make, case-sensitivity related errors and "
                        "not ending the command with 's' where one should "
                        "(such as Equal vs. Equals).",
            value={'letter_case': ('E4001', Severity.error, "command differs by upper/lowercase"),
                   'end_s': ('E4002', Severity.error, "Equals vs. Equal"),
                   'rl_command': ('E4003', Severity.info, "rlUppercase command unrecognized")})
    }

    @staticmethod
    def get_pair_end_description(command):
        return "{} >> {}".format(command, Catalogue.pair_ends[command])

    @staticmethod
    def get_pair_begin_description(command):
        relevant_begins = []
        for pair_begin in Catalogue.pair_ends:
            if Catalogue.pair_ends[pair_begin] == command:
                relevant_begins.append(pair_begin)
        return "{}, begins: {}".format(command, ', '.join(sorted(relevant_begins)))

    @staticmethod
    def get_deprecated_alternative(command):
        return "{}, use: {}".format(command, ', '.join(Catalogue.deprecated_commands[command]))

    def output_as_markdown_file(self):
        output = []
        for error_class in sorted(self.table):

            table_entry = self.table[error_class]

            output.append(table_entry.description.split('\n'))
            output[-1][0] = "{} EC{}: {}".format('#'*3, error_class, output[-1][0])

            error_msgs = []
            for error_label in table_entry.value:
                if hasattr(table_entry, 'description_function'):
                    description = getattr(Catalogue, table_entry.description_function)(error_label)
                    id, severity = table_entry.value[error_label]
                else:
                    id, severity, description = table_entry.value[error_label]
                msg = "- [{}][{}] {}".format(id, severity.name, description)
                error_msgs.append(msg)
            error_msgs.sort()

            for err in error_msgs:
                output[-1].append(err)
            output[-1].append('\n')

        try:
            with open('catalogue.md', "w") as input_file:
                for item in output:
                    for line in item:
                        input_file.write(line + '\n')
                    input_file.write('')
        except IOError:
            sys.stderr.write("ERROR: Failed to write to catalogue.md\n")
