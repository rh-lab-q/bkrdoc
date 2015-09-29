#!/usr/bin/python
__author__ = 'Jiri_Kulda'
# description: Simple parser for BeakerLib test

import shlex
import sys
import bkrdoc.analysis


class Parser(object):
    """
    Parser is main class. It contains methods for running analysis and nature language information creation.
    Also contains phases containers.
    :param file_in: is path with name to file from which the documentation will be created.
    """
    lexer = shlex

    file_test = ""

    description = ""

    all_commands = ["rlAssert0", "rlAssertEquals", "rlAssertNotEquals",
                    "rlAssertGreater", "rlAssertGreaterOrEqual", "rlAssertExists", "rlAssertNotExists",
                    "rlAssertGrep", "rlAssertNotGrep", "rlAssertDiffer", "rlAssertNotDiffer", "rlRun",
                    "rlWatchdog", "rlReport", "rlIsRHEL", "rlIsFedora", "rlCheckRpm", "rlAssertRpm",
                    "rlAssertNotRpm", "rlAssertBinaryOrigin", "rlGetMakefileRequires",
                    "rlCheckRequirements", "rlCheckMakefileRequires", "rlMount", "rlCheckMount",
                    "rlAssertMount", "rlHash", "rlUnhash", "rlFileBackup", "rlFileRestore",
                    "rlServiceStart", "rlServiceStop", "rlServiceRestore", "rlSEBooleanOn",
                    "rlSEBooleanOff", "rlSEBooleanRestore", "rlCleanupAppend", "rlCleanupPrepend",
                    "rlVirtualXStop", "rlVirtualXGetDisplay", "rlVirtualXStart", "rlWait", "rlWaitForSocket",
                    "rlWaitForFile", "rlWaitForCmd", "rlImport", "rlDejaSum", "rlPerfTime_AvgFromRuns",
                    "rlPerfTime_RunsinTime", "rlLogMetricLow", "rlLogMetricHigh", "rlShowRunningKernel",
                    "rlGetDistroVariant", "rlGetDistroRelease", "rlGetSecondaryArch", "rlGetPrimaryArch",
                    "rlGetArch", "rlShowPackageVersion", "rlFileSubmit", "rlBundleLogs", "rlDie",
                    "rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo", "rlLogDebug", "rlLog",
                    "rlGetTestState", "rlGetPhaseState", "rlJournalPrint", "rlJournalPrintText"]

    phases = []
    outside = ""
    file_name = ""

    test_launch = ""

    environmental_variable = []

    def __init__(self, file_in):
        self.phases = []
        self.test_launch = 0
        self.environmental_variable = []
        file_in = file_in.strip()
        if file_in[(len(file_in) - 3):len(file_in)] == ".sh":
            try:
                with open(file_in, "r") as input_file:
                    self.file_name = file_in
                    self.description = file_in[0:(len(file_in) - 3)]
                    self.file_test = input_file.read()
                    self.parse_data()

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)

        else:
            print("ERROR: Not a script file. (*.sh)")
            sys.exit(1)

    def parse_data(self):
        """
        Method which divides lines of code into phase containers.
        """
        self.phases.append(bkrdoc.analysis.PhaseOutside())

        pom_line = ""
        for line in self.file_test.split('\n'):
            line = line.strip()

            if line[0:1] != '#' and len(line) >= 1 and \
                    not self.is_phase_journal_end(line):

                if self.is_phase(line):
                    self.phases.append(bkrdoc.analysis.PhaseContainer(line[len("rlphasestart"):]))

                elif self.is_end_back_slash(line):
                    pom_line += line[0:-1]

                elif len(self.phases) > 0:
                    if pom_line != "":
                        self.phases[-1].setup_statement(pom_line + line)
                        pom_line = ""
                    else:
                        self.phases[-1].setup_statement(line)

            elif self.is_phase_journal_end(line):
                self.phases.append(bkrdoc.analysis.PhaseOutside())

    def print_statement(self):
        for i in self.phases:
            print(i.statement_list)
            print("\n")

    def is_end_back_slash(self, line):
        return line[-1:] == '\\'

    def is_phase(self, line):
        return line[0:len("rlphasestart")].lower() == "rlphasestart"

    def is_phase_clean(self, line):
        return line[0:len("rlphasestartclean")].lower() == "rlphasestartclean"

    def is_phase_test(self, line):
        return line[0:len("rlphasestarttest")].lower() == "rlphasestarttest"

    def is_phase_setup(self, line):
        return line[0:len("rlphasestartsetup")].lower() == "rlphasestartsetup"

    def is_phase_journal_end(self, line):
        if line[0:len("rlphaseend")].lower() == "rlphaseend":
            return True

        elif line[0:len("rljournalend")].lower() == "rljournalend":
            return True

        else:
            return False

    def is_journal_start(self, line):
        return line[0:len("rljournalstart")].lower() == "rljournalstart"

    def is_phase_outside(self, phase_ref):
        return phase_ref.phase_name == "Outside phase"

    def is_beakerlib_command(self, testing_command):
        return testing_command in self.all_commands

    def get_phases(self):
        return self.phases

    def get_environmental_variables(self):
        return self.environmental_variable

    def get_file_name(self):
        return self.file_name

    def get_test_launch(self):
        return self.test_launch

    def set_test_launch(self, number_of_variable):
        self.test_launch = number_of_variable