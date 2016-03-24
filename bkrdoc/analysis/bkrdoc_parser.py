#!/usr/bin/python
__author__ = 'Jiri_Kulda'
# description: Simple parser for BeakerLib test

import shlex
import sys
import bashlex
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
                    "rlPerfTime_RunsInTime", "rlLogMetricLow", "rlLogMetricHigh", "rlShowRunningKernel",
                    "rlGetDistroVariant", "rlGetDistroRelease", "rlGetSecondaryArch", "rlGetPrimaryArch",
                    "rlGetArch", "rlShowPackageVersion", "rlFileSubmit", "rlBundleLogs", "rlDie",
                    "rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo", "rlLogDebug", "rlLog",
                    "rlGetTestState", "rlGetPhaseState", "rlJournalPrint", "rlJournalPrintText"]

    phases = []
    test_functions = []
    outside = ""
    file_name = ""
    variables = ""
    test_launch = ""
    argparse_data_list = []
    environmental_variable = []

    def __init__(self, file_in):
        self.phases = []
        self.test_launch = 0
        self.environmental_variable = []
        self.file_name = file_in.strip()
        self.argparse_data_list = []
        self.variables = ""
        self.test_functions = []

    def open_file(self):
        if self.file_name[(len(self.file_name) - 3):len(self.file_name)] == ".sh":
            try:
                with open(self.file_name, "r") as input_file:
                    self.file_name = self.file_name
                    self.description = self.file_name[0:(len(self.file_name) - 3)]
                    self.file_test = input_file.read()

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + self.file_name + "\n")
                sys.exit(1)

        else:
            print("ERROR: Not a script file. (*.sh)")
            sys.exit(1)

    def parse_data(self, input_line=""):
        """
        Method which divides lines of code into phase containers.
        :input_line short string to be parsed (optional). Primary for testing
        """
        # This condition is here for testing. Thanks to input_line I can test only one line without
        # of need use whole
        if len(input_line):
            self.file_test = input_line
        else:
            self.open_file()

        self.phases.append(bkrdoc.analysis.PhaseOutside())

        self.variables = bkrdoc.analysis.TestVariables()
        parsed_file = bashlex.parse(self.file_test)
        data_searcher = bkrdoc.analysis.StatementDataSearcher()
        nodevistor = bkrdoc.analysis.NodeVisitor(self.variables)
        conditions = bkrdoc.analysis.ConditionsForCommands()

        for command_line in parsed_file:
            # print(command_line)
            # print(command_line.kind)
            # print("")
            nodevistor.visit(command_line)
            container = nodevistor.get_parsed_container()
            if self.is_loop_function_or_condition_container(container):
                if self.is_function_container(container):
                    self.test_functions.append(container)
                    nodevistor.erase_parsing_subject_variable()
                else:
                    if self.is_loop_container(container) or self.is_condition_container(container):
                        self.argparse_data_list.append(container)
                    nodevistor.erase_parsing_subject_variable()
                    container.search_data(self, nodevistor)
            else:
                data_searcher.parse_command(nodevistor.get_parsed_container())
                nodevistor.erase_parsing_subject_variable()
                data_argparse = data_searcher.parsed_param_ref
                if conditions.is_rlrun_command(data_argparse.argname):
                    data_argparse = self.search_for_beakerlib_command_in_rlrun(nodevistor, data_argparse)
                self.argparse_data_list.append(data_argparse)

        # print("Started =======================================")
        # self.print_statement()

        # print(variables.variable_names_list)
        # print(variables.variable_values_list)

    def search_for_beakerlib_command_in_rlrun(self, nodevisitor, rlrun_argparse):
        # print("////////////////////////////////////")
        # print(nodevisitor)
        # print()
        # print(rlrun_argparse)
        # print("////////////////////////////////////")
        data_searcher = bkrdoc.analysis.StatementDataSearcher()
        command_parse = bashlex.parse(rlrun_argparse.command)
        nodevisitor.visit(command_parse[0])
        data_searcher.parse_command(nodevisitor.get_parsed_container())
        nodevisitor.erase_parsing_subject_variable()
        rlrun_argparse.command = data_searcher.parsed_param_ref
        return rlrun_argparse

    def divide_parsed_argparse_data_into_phase_conainers(self):
        cond = bkrdoc.analysis.ConditionsForCommands()
        for argparse_data in self.argparse_data_list:
            if not cond.is_journal_start(argparse_data.argname) and not cond.is_phase_journal_end(argparse_data.argname):
                if cond.is_phase(argparse_data.argname):
                    p_name = argparse_data.argname[len("rlPhaseStart"):]
                    if argparse_data.description is not None and argparse_data.description is not "":
                        self.phases.append(bkrdoc.analysis.PhaseContainer(p_name + ": " + argparse_data.description))
                    else:
                        self.phases.append(bkrdoc.analysis.PhaseContainer(p_name))
                else:
                    self.phases[-1].setup_statement(argparse_data)
            elif cond.is_phase_journal_end(argparse_data.argname) or cond.is_journal_start(argparse_data.argname):
                self.phases.append(bkrdoc.analysis.PhaseOutside())

        # print("Started =======================================")
        # self.print_statement()

    def print_statement(self):
        for i in self.phases:
            print(i.phase_name)
            print(i.statement_list)
            print("\n")

    def is_phase_outside(self, phase_ref):
        return phase_ref.phase_name == "Outside phase"

    def is_beakerlib_command(self, testing_command):
        return testing_command in self.all_commands

    def get_phases(self):
        return self.phases

    def get_environmental_variables(self):
        return self.variables.get_test_environmental_variables_list()

    def get_file_name(self):
        return self.file_name

    def get_test_launch(self):
        return self.variables.get_test_launch()

    def is_function_container(self, container):
        return type(container).__name__ == "FunctionContainer"

    def is_loop_container(self, container):
        return type(container).__name__ == "LoopContainer"

    def is_condition_container(self, container):
        return type(container).__name__ == "ConditionContainer"

    def is_loop_function_or_condition_container(self, container):
        pom_containers = ["FunctionContainer", "LoopContainer", "ConditionContainer"]
        return type(container).__name__ in pom_containers

    def set_test_launch(self, number_of_variable):
        self.test_launch = number_of_variable