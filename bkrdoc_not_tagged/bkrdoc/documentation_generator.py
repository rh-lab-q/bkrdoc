#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex
import re
import argparse


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
        self.phases.append(PhaseOutside())

        pom_line = ""
        for line in self.file_test.split('\n'):
            line = line.strip()

            if line[0:1] != '#' and len(line) >= 1 and \
                    not self.is_phase_journal_end(line):

                if self.is_phase(line):
                    self.phases.append(PhaseContainer(line[len("rlphasestart"):]))

                elif self.is_end_back_slash(line):
                    pom_line += line[0:-1]

                elif len(self.phases) > 0:
                    if pom_line != "":
                        self.phases[-1].setup_statement(pom_line + line)
                        pom_line = ""
                    else:
                        self.phases[-1].setup_statement(line)

            elif self.is_phase_journal_end(line):
                self.phases.append(PhaseOutside())

    def print_statement(self):
        for i in self.phases:
            print(i.statement_list)
            print("\n")

    def is_end_back_slash(self, line):
        return line[-1:] == '\\'

    def set_test_launch(self, number_of_variables):
        """
        This method sets up test launch variable, which indicates number of variables.
        :param number_of_variables: number of command line variables in test
        """
        if int(number_of_variables) > int(self.test_launch):
            self.test_launch = number_of_variables

    def set_environmental_variable_information(self, variable):
        """
        This method sets up test environmental variable information command. This command
        contains names of environmental variables in test.
        :param variable: founded environmental variable in test.
        """
        if variable not in self.environmental_variable:
            self.environmental_variable.append(variable)

    def get_doc_data(self):
        """
        Method which is responsible for starting the first analysis of code lines.
        After this method finishes all phase containers will have argparse object
        with parsed data.
        """
        pom_var = TestVariables()
        pom_func = []
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.search_data(self, pom_var, pom_func)
                pom_var = TestVariables()

            else:
                member.search_data(pom_var, pom_func)
                pom_var = TestVariables()

            # copying variables to new variable instance
            for var in member.variables.variable_names_list:
                pom_value = member.variables.get_variable_value(var)
                pom_var.add_variable(var, pom_value)

            # copying keywords to new variable instance
            for key in member.variables.keywords:
                pom_var.add_keyword(key)

            # copying functions to new function list
            copy_func_list = member.func_list
            pom_func = copy_func_list

    def get_documentation_information(self):
        """
        This method is responsible for starting of replacement of argparse object to
        DocumentationInformation object.
        """
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.translate_data(self)

    def generate_documentation(self):
        """
        This method starts transformation from DocumentationInformation objects
        to small object with nature language information
        """
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.generate_documentation()

    def get_test_weigh(self):
        """
        This method calculates number of lines in test.

        :return: number of lines where information will be placed.
        """
        weigh = 0
        for member in self.phases:
            if not self.is_phase_outside(member):
                weigh += member.get_phase_weigh()
        return weigh

    def setup_phases_lists_for_knapsack(self):
        """
        This method sets up list for knapsack algorithm.

        :return: Set up list.
        """
        phases_list = self.get_phases_information_lists()
        whole_set_uped_list = []
        for element in phases_list:
            pom_list = [element, element.get_information_weigh(), element.get_information_value()]
            whole_set_uped_list.append(pom_list)
        return whole_set_uped_list

    def get_phases_information_lists(self):
        """
        This method gathers all information lists in phase containers into big one

        :return: one big information list
        """
        phases_lists = []
        for member in self.phases:
            if not self.is_phase_outside(member):
                phases_lists += member.get_information_list()
        return phases_lists

    def set_phases_information_lists(self, finished_knapsack_list):
        """
        This method checks number of lines in phases containers. If the lines are
        bigger then this method will run prepared knapsack algorithm.
        :param finished_knapsack_list: final list with information
        """
        pom_phases_lists = []
        for member in self.phases:
            if not self.is_phase_outside(member):
                pom = member.get_information_list()
                for element in finished_knapsack_list:
                    if element[0] in pom:
                        pom_phases_lists.insert(0, element[0])
                member.set_information_list(pom_phases_lists)
                pom_phases_lists = []

    def print_test_launch(self):
        """
        This method prints test launch information
        """
        inf = "Test launch: " + self.file_name
        i = 0
        while int(i) < int(self.test_launch):
            inf += " [VARIABLE]"
            i += 1
        print(inf)

    def print_test_environmental_variables_information(self):
        """
        This method prints environmental variables information
        """
        inf = "Test environmental variables: "
        if len(self.environmental_variable):
            for env in self.environmental_variable:
                inf += env + ", "
            inf = inf[0:-2]
        else:
            inf += "-"
        print(inf)

    def print_documentation(self, cmd_options):
        """
        This method is responsible for printing the final documentation to stdout
        :param cmd_options: possible command line options
        """
        self.print_test_launch()
        self.print_test_environmental_variables_information()
        print("")
        test_weigh = self.get_test_weigh()
        if test_weigh > cmd_options.size:
            knapsack_list = self.setup_phases_lists_for_knapsack()
            finished_knapsack = self.solve_knapsack_dp(knapsack_list, cmd_options.size)
            self.set_phases_information_lists(finished_knapsack)

        for member in self.phases:
            if not self.is_phase_outside(member):
                member.print_phase_documentation(cmd_options)
                print("")

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

    # items in [["information", weigh, value], ...] format
    def solve_knapsack_dp(self, items, limit):
        """
        Algorithm for solving the knapsack problem
        :param items: set up list of information
        :param limit: specified size limit
        :return: final list with information with best value
        """
        global xrange
        try:
            xrange
        except NameError:
            xrange = range

        table = [[0 for w in range(limit + 1)] for j in xrange(len(items) + 1)]  # initialization of table
        for j in xrange(1, len(items) + 1):
            item, wt, val = items[j-1]
            for w in xrange(1, limit + 1):
                if wt > w:
                    table[j][w] = table[j-1][w]
                else:
                    table[j][w] = max(table[j-1][w],
                                      table[j-1][w-wt] + val)

        result = []
        w = limit
        for j in range(len(items), 0, -1):
            was_added = table[j][w] != table[j-1][w]

            if was_added:
                item, wt, val = items[j-1]
                result.append(items[j-1])
                w -= wt
        return result

    def search_variable(self, phase_ref, searching_variable):
        """
        this method searches specified test variable
        :param phase_ref: reference to phase container
        :param searching_variable: <-
        """
        pom_variable = ""

        for member in self.phases:
            if self.is_phase_outside(member):
                pom_pos = member.get_variable_position(searching_variable)
                if pom_pos >= 0:
                    pom_variable = member.variable_values_list[pom_pos]

            elif member == phase_ref:
                if pom_variable == "":
                    print("UNKNOWN VARIABLE !!!")
                return pom_variable


class TestVariables:
    """Class contain variables from BeakerLib test"""
    variable_names_list = []
    variable_values_list = []

    keywords = []

    def __init__(self):
        self.variable_names_list = []
        self.variable_values_list = []

    def add_variable(self, name, value):
        if self.is_existing_variable(name):
            pom_pos = self.get_variable_position(name)
            self.variable_values_list[pom_pos] = value
        else:
            self.variable_names_list.append(name)
            self.variable_values_list.append(value)

    def add_keyword(self, keyword):
        if not self.is_existing_keyword(keyword):
            self.keywords.append(keyword)

    def is_existing_keyword(self, keyword):
        return keyword in self.keywords

    def is_existing_variable(self, name):
        return name in self.variable_names_list

    def get_variable_value(self, name):
        pos = self.get_variable_position(name)
        return self.variable_values_list[pos]

    def get_variable_position(self, name):
        i = 0
        for element in self.variable_names_list:
            if element == name:
                return i
            i += 1
        return -1

    def replace_variable_in_string(self, string):
        i = 0
        pom_str = string
        if len(self.variable_names_list):
            for element in self.variable_names_list:
                pom_str = pom_str.replace("$" + element, self.variable_values_list[i])
                i += 1
            return pom_str
        else:
            return string


class TestFunction:
    """Class for working with functions from the BeakerLib test"""

    statement_list = []

    data_list = []

    name = ""

    def __init__(self, fname):
        self.statement_list = []
        lex = shlex.shlex(fname)
        self.name = lex.get_token()
        self.data_list = []

    def add_line(self, line):
        self.statement_list.append(line)

    def add_data(self, data):
        self.data_list.append(data)

    def is_function_data_empty(self):
        return len(self.data_list) == 0


class PhaseOutside:
    """Class for searching data outside of phases"""
    phase_name = ""
    statement_list = []
    variables = ""
    func_list = []

    def __init__(self):
        # self.parse_ref = parse_cmd
        self.phase_name = "Outside phase"
        self.statement_list = []
        self.variables = TestVariables()
        self.func_list = []

    def setup_statement(self, line):
        self.statement_list.append(line)

    def search_data(self, variable_copy, function_copy):
        """
        This method searches variables in statements. Also when it finds function then this method
        created TestFunction object with function data.
        :param variable_copy: Copy of variables
        :param function_copy: Copy of functions
        """
        self.variables = variable_copy
        self.func_list = function_copy
        func = False
        for statement in self.statement_list:

            # This three conditions are here because of getting further
            # information from functions.
            if self.is_function(statement):
                func = True
                self.func_list.append(TestFunction(statement[len("function")+1:]))

            elif func and not self.is_function_end(statement):
                self.func_list[-1].add_line(statement)

            elif func and self.is_function_end(statement):
                self.func_list[-1].add_line(statement)
                func = False

            else:
                # searching variables in statement line
                try:
                    read = shlex.shlex(statement)
                    member = read.get_token()
                    equal_to = read.get_token()

                    while equal_to:
                    # condition to handle assign to random value
                    # setting variable list
                        if equal_to == '=':
                        # This 7 lines are here for erasing comments and for reading whole line
                            pom_i = statement.find("=", len(member)) + 1
                            list_of_statement = shlex.split(statement[pom_i:], True, True)
                            value = ""
                            for value_member in list_of_statement:
                                if not value == "":
                                    value += " "
                                value += value_member

                            regular = re.compile("\"(/.*/)(.*)\"")
                            match = regular.match(value)
                            if match:
                                self.variables.add_variable(member, match.group(1) + match.group(2))
                                self.variables.add_keyword(match.group(2))
                            else:
                                self.variables.add_variable(member, value)

                        member = equal_to
                        equal_to = read.get_token()
                except ValueError as detail:
                    print("ERROR in line: " + str(statement))
                    print("With message: " + str(detail))

    def is_function(self, line):
        return line[0:len("function")] == "function"

    def is_function_end(self, line):
        """
        Test end of line of function in statement line
        :param line: statement line
        :return: true or false
        """
        if line[0:1] == "}":
            return True
        else:
            # This split for erasing comments on the end of line
            pom_list = shlex.split(line, True, True)
            if pom_list[-1][-1] == "}":
                return True
            else:
                return False


class PhaseContainer:
    """Class for store information in test phase"""
    phase_name = ""
    statement_list = []
    doc_ref = ""
    variables = ""
    statement_classes = []
    documentation_units = []
    phase_documentation_information = []
    func_list = []
    parser_ref = ""

    def __init__(self, name):
        self.phase_name = name
        self.statement_list = []
        self.doc = []
        self.variables = TestVariables()
        self.statement_classes = []
        self.documentation_units = []
        self.phase_documentation_information = []
        self.func_list = []
        self.parser_ref = ""

    def setup_statement(self, line):
        self.statement_list.append(line)

    def search_data(self, parser_ref, variable_copy, function_copy):
        """
        This method runs data searching in statement lines.
        :param parser_ref: parser object reference
        :param variable_copy: variable copy
        :param function_copy: function copy
        """
        self.func_list = function_copy
        self.variables = variable_copy
        self.parser_ref = parser_ref
        command_translator = StatementDataSearcher(parser_ref, self)
        for statement in self.statement_list:
            try:
                self.statement_classes.append(command_translator.parse_command(statement))
            except ValueError:
                print("ERROR in line: " + str(statement))
                print(ValueError)
            except SystemExit:
                print("ERROR in line: " + str(statement))
                print("Can be problem with variables substitutions")

    def search_data_in_function(self, function):
        """
        Searching data in function object
        :param function: function object
        """
        command_translator = StatementDataSearcher(self.parser_ref, self)
        function.data_list = []
        for statement in function.statement_list:
            try:
                function.add_data(command_translator.parse_command(statement))
            except ValueError:
                print("ERROR in line: " + str(statement))
                print(ValueError)
            except SystemExit:
                print("ERROR in line: " + str(statement))
                print("Can be problem with variables substitutions")

    def translate_data(self, parser_ref):
        """
        Translate data from argparse object to DocumentationInformation object
        :param parser_ref: parser reference
        """
        data_translator = DocumentationTranslator(parser_ref)
        for data in self.statement_classes:
            if data.argname != "UNKNOWN":
                self.documentation_units.append(data_translator.translate_data(data))

    def generate_documentation(self):
        """
        Transforms DocumentationInformation into small classes using GetInformation
        """
        information_translator = GetInformation()
        for information in self.documentation_units:
            if information:
                self.phase_documentation_information.append(information_translator.get_information_from_facts(information))

    def print_phase_documentation(self, cmd_options):
        """
        Prints nature language information
        :param cmd_options: possible command line options
        """
        self.print_phase_name_with_documentation_credibility()
        conditions = ConditionsForCommands()

        for information in self.phase_documentation_information:
            if cmd_options.log_in:
                information.print_information()
            elif not conditions.is_rllog_command(information.get_command_name()):
                information.print_information()

    def print_phase_name_with_documentation_credibility(self):
        credibility = len(self.statement_list) - len(self.phase_documentation_information)
        inf = self.phase_name + " [ Unknown commands: " + str(credibility) + ", Total: " + str(len(self.statement_list)) + " ]"
        print(inf)

    def get_information_list(self):
        return self.phase_documentation_information

    def set_information_list(self, inf_list):
        """
        Sets whole information list. This method is called after solving knapsack problem.
        :param inf_list: list of information from finished knapsack algorithm
        """
        self.phase_documentation_information = inf_list

    def get_phase_weigh(self):
        """
        this method returns number of lines on which information will be printed

        :return: -//-
        """
        phase_weigh = 0
        for inf in self.phase_documentation_information:
            phase_weigh += inf.get_information_weigh()
        return phase_weigh

    def get_function_list(self):
        """
        :return: list of functions
        """
        return self.func_list


class StatementDataSearcher:
    """
    This class is responsible for parsing data from statement lines. This parsing is done by
    setting argparse modules for every BeakerLib command. These setting we can see under
    big switch.
    :param parser_ref: parser reference
    :param phase_ref: reference to phase where was StatementDataSearcher instance made.
    """
    parsed_param_ref = ""
    parser_ref = ""
    phase_ref = ""

    minimum_variable_size = 4

    def __init__(self, parser_ref, phase_ref):
        self.parser_ref = parser_ref
        self.phase_ref = phase_ref
        self.minimum_variable_size = 4

    def parse_command(self, statement_line):
        # Splitting statement using shlex lexicator
        """
        Method contains big switch for division of statement line
        :param statement_line: singe line of code from test
        :return: argparse object with parsed data
        """
        pom_statement_line = self.phase_ref.variables.replace_variable_in_string(statement_line)
        self.get_cmd_line_params(pom_statement_line)
        self.get_environmental_variable(pom_statement_line)
        pom_list = shlex.split(pom_statement_line, True, posix=True)
        first = pom_list[0]

        # if self.is_beakerLib_command(first, self.parser_ref):
        condition = ConditionsForCommands()

        if condition.is_rlrun_command(first):
            self.get_rlrun_data(pom_list)

        elif condition.is_rpm_command(first):
            self.get_rpmcommand_data(pom_list)

        elif condition.is_check_or_assert_mount(first):
            self.get_check_or_assert_mount_data(pom_list)

        elif condition.is_assert_command(first):

            if condition.is_assert_grep(first):
                self.get_assert_grep_data(pom_list)

            elif condition.is_rlpass_or_rlfail_command(first):
                self.get_rlpass_or_rlfail_data(pom_list)

            elif condition.is_assert0(first):
                self.get_assert0_data(pom_list)

            elif condition.is_assert_comparasion(first):
                self.get_assert_comparison_data(pom_list)

            elif condition.is_assert_exists(first):
                self.get_assert_exits_data(pom_list)

            elif condition.is_assert_differ(first):
                self.get_assert_differ_data(pom_list)

            elif condition.is_assert_binary_origin(first):
                self.get_assertbinaryorigin_data(pom_list)

        elif condition.is_rlfilebackup_command(first):
            self.get_rlfilebackup_data(pom_list)

        elif condition.is_rlfilerestore_command(first):
            self.get_rlfile_restore_data(pom_list)

        elif condition.is_rlisrhel_or_rlisfedora_command(first):
            self.get_isrhel_or_isfedora_data(pom_list)

        elif condition.is_rlmount(first):
            self.get_rlmount_data(pom_list)

        elif condition.is_rlhash_or_rlunhash_command(first):
            self.get_rlhash_or_rlunhash_data(pom_list)

        elif condition.is_rllog_command(first):
            self.get_rllog_data(pom_list)

        elif condition.is_rldie_command(first):
            self.get_rldie_data(pom_list)

        elif condition.is_rlget_x_arch_command(first):
            self.get_rlget_commands_data(pom_list)

        elif condition.is_rlgetdistro_command(first):
            self.get_rlget_commands_data(pom_list)

        elif condition.is_rlgetphase_or_test_state_command(first):
            self.get_rlget_commands_data(pom_list)

        elif condition.is_rlreport_command(first):
            self.get_rlreport_data(pom_list)

        elif condition.is_rlwatchdog_command(first):
            self.get_rlwatchdog_data(pom_list)

        elif condition.is_rlbundlelogs_command(first):
            self.get_rlbundlelogs_data(pom_list)

        elif condition.is_rlservicexxx(first):
            self.get_rlservicexxx_data(pom_list)

        elif condition.is_sebooleanxxx_command(first):
            self.get_sebooleanxxx_data(pom_list)

        elif condition.is_rlshowrunningkernel_command(first):
            self.get_rlshowrunningkernel_data(pom_list)

        elif condition.is_get_or_check_makefile_requires(first):
            self.get_rlget_or_rlcheck_makefilerequeries_data(pom_list)

        elif condition.is_rlcleanup_apend_or_prepend_command(first):
            self.get_rlcleanup_apend_or_prepend_data(pom_list)

        elif condition.is_rlfilesubmit_command(first):
            self.get_rlfilesubmit_data(pom_list)

        elif condition.is_rlperftime_runsintime_command(first):
            self.get_rlperftime_runsintime_data(pom_list)

        elif condition.is_rlperftime_avgfromruns_command(first):
            self.get_rlperftime_avgfromruns_data(pom_list)

        elif condition.is_rlshowpackageversion_command(first):
            self.get_rlshowpackageversion_data(pom_list)

        elif condition.is_rljournalprint_command(first):
            self.get_rljournalprint_data(pom_list)

        elif condition.is_rlimport_command(first):
            self.get_rlimport_data(pom_list)

        elif condition.is_rlwaitforxxx_command(first):
            self.get_rlwaitforxxx_data(pom_list, first)

        elif condition.is_rlwaitfor_command(first):
            self.get_rlwaitfor_data(pom_list)

        elif condition.is_virtualxxx_command(first):
            self.get_rlvirtualx_xxx_data(pom_list)

        else:
            self.unknown_command(pom_list, pom_statement_line)

        return self.parsed_param_ref

    def find_and_replace_variable(self, statement):
        pass

    def get_cmd_line_params(self, line):
        """
        This method searches for command line variables in code represented as $1 $2 ...
        :param line: statement line of code
        """
        regular = re.compile("(.*)(\$(\d+))(.*)")
        match = regular.match(line)
        if match:
            self.parser_ref.set_test_launch(match.group(3))

    def get_environmental_variable(self, line):
        """
        Searches environmental variables in code line
        :param line: code line
        """
        lexer = shlex.shlex(line)
        word = lexer.get_token()
        while word:
            if word == "$":
                word = lexer.get_token()
                if not self.phase_ref.variables.is_existing_variable(word) and len(word) > self.minimum_variable_size:
                    self.parser_ref.set_environmental_variable_information(word)

            elif word[0:1] == '"':  # shlex doesn't returns whole string so for searching in strings I'm using recursion
                self.get_environmental_variable(word[1:-1])
            word = lexer.get_token()

    def is_variable_assignment(self, statement):
        """
        searching variables in statement line
        :param statement: code line
        :return: returns nothing
        """
        read = shlex.shlex(statement)
        member = read.get_token()
        equal_to = read.get_token()
        while equal_to:
            # condition to handle assign to random value
            # setting variable list
            if equal_to == '=':
                # This 7 lines are here for erasing comments and for reading whole line
                pom_i = statement.find("=", len(member)) + 1
                list_of_statement = shlex.split(statement[pom_i:], True, True)
                value = ""
                for value_member in list_of_statement:
                    if not value == "":
                        value += " "
                    value += value_member

                regular = re.compile("\"(/.*/)(.*)\"")
                match = regular.match(value)
                if match:
                    self.phase_ref.variables.add_variable(member, match.group(1) + match.group(2))
                    # TODO keywords from not outside phases
                    # self.keywords_list.append(match.group(2))
                else:
                    self.phase_ref.variables.add_variable(member, value)

            member = equal_to
            equal_to = read.get_token()

        return

    def get_rljournalprint_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("type", type=str, nargs="?")
        parser_arg.add_argument('--full-journal', dest='full_journal',
                                action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlshowpackageversion_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlfilesubmit_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-s", type=str, help="sets separator")
        parser_arg.add_argument("path_to_file", type=str)
        parser_arg.add_argument("required_name", type=str, nargs="?")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlbundlelogs_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str)
        parser_arg.add_argument("file", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rldie_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("file", type=str, nargs="*")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rllog_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("logfile", type=str, nargs="?")
        parser_arg.add_argument("priority", type=str, nargs="?")
        parser_arg.add_argument('--prio-label', dest='prio_label',
                                action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlshowrunningkernel_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlget_or_rlcheck_makefilerequeries_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlget_commands_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def unknown_command(self, pom_param_list, statement_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(["UNKNOWN"])
        # Trying to find variable assignment in statement line
        self.is_variable_assignment(statement_list)
        self.is_function_name_in_statement(statement_list)

    def is_function_name_in_statement(self, line):
        for function in self.phase_ref.get_function_list():
            if function.name in line and function.is_function_data_empty():
                self.phase_ref.search_data_in_function(function)

    def get_rlwatchdog_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("timeout", type=str)
        parser_arg.add_argument("signal", type=str, nargs='?', default="KILL")
        parser_arg.add_argument("callback", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlreport_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        parser_arg.add_argument("result", type=str)
        parser_arg.add_argument("score", type=str, nargs='?')
        parser_arg.add_argument("log", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlrun_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('-t', dest='t', action='store_true', default=False)
        parser_arg.add_argument('-l', dest='l', action='store_true', default=False)
        parser_arg.add_argument('-c', dest='c', action='store_true', default=False)
        parser_arg.add_argument('-s', dest='s', action='store_true', default=False)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("status", type=str, nargs='?', default="0")
        parser_arg.add_argument("comment", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)
        ref = self.parsed_param_ref
        self.parse_command(self.parsed_param_ref.command)  # for getting variables from command
        self.parsed_param_ref = ref

    def get_rlvirtualx_xxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlwaitfor_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('n', type=str, nargs='*')
        parser_arg.add_argument("-t", type=int, help="time")
        parser_arg.add_argument("-s", type=str, help="SIGNAL", default="SIGTERM")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlwaitforxxx_data(self, pom_param_list, command):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        :param command: command name
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-p", type=str, help="PID")
        parser_arg.add_argument("-t", type=str, help="time")
        parser_arg.add_argument("-d", type=int, help="delay", default=1)

        if ConditionsForCommands().is_rlwaitforcmd_command(command):
            parser_arg.add_argument("command", type=str)
            parser_arg.add_argument("-m", type=str, help="count")
            parser_arg.add_argument("-r", type=str, help="retrval", default="0")

        elif ConditionsForCommands().is_rlwaitforfile_command(command):
            parser_arg.add_argument("path", type=str)

        elif ConditionsForCommands().is_rlwaitforsocket_command(command):
            parser_arg.add_argument("port_path", type=str)
            parser_arg.add_argument('--close', dest='close', action='store_true',
                                    default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlimport_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("LIBRARY", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlperftime_runsintime_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("time", type=int, nargs='?', default=30)
        parser_arg.add_argument("runs", type=int, nargs='?', default=3)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlperftime_avgfromruns_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("count", type=int, nargs='?', default=3)
        parser_arg.add_argument("warmup", type=str, nargs='?', default="warmup")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlcleanup_apend_or_prepend_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("string", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_sebooleanxxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("boolean", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlservicexxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("service", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlfile_restore_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlfilebackup_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--clean', dest='clean', action='store_true',
                                default=False)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        parser_arg.add_argument('file', type=str, nargs='+')
        parser_arg.add_argument('status', type=str, nargs='?', default="-")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlhash_or_rlunhash_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--decode', dest='decode', action='store_true',
                                default=False, help='unhash given string')
        parser_arg.add_argument("--algorithm", type=str,
                                help="given hash algorithm")
        parser_arg.add_argument("STRING", type=str, nargs='?')
        parser_arg.add_argument('--stdin', action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_check_or_assert_mount_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str, nargs='?')
        parser_arg.add_argument('share', type=str, nargs='?')
        parser_arg.add_argument('mountpoint', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlmount_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str)
        parser_arg.add_argument('share', type=str)
        parser_arg.add_argument('mountpoint', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assertbinaryorigin_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('binary', type=str)
        parser_arg.add_argument('package', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rpmcommand_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        if len(pom_param_list) == 2 and pom_param_list[1] == "--all":
            parser_arg.add_argument('--all', dest='all', action='store_true',
                                    default=False, help='assert all packages')
            self.parsed_param_ref = parser_arg.parse_args(pom_param_list)
        else:
            parser_arg.add_argument('name', type=str)
            parser_arg.add_argument('version', type=str, nargs='?')
            parser_arg.add_argument('release', type=str, nargs='?')
            parser_arg.add_argument('arch', type=str, nargs='?')
            # this line is for information translator
            parser_arg.add_argument('--all', dest='all', action='store_true',
                                    default=False, help='assert all packages')
            self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_isrhel_or_isfedora_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('type', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_differ_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file1', type=str)
        parser_arg.add_argument('file2', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_exits_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file_directory', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_comparison_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument('value1', type=str)
        parser_arg.add_argument('value2', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert0_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument('value', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlpass_or_rlfail_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_grep_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('pattern', type=str)
        parser_arg.add_argument('file', type=str)
        parser_arg.add_argument('-i', '-I', dest='text_in', action='store_true',
                                default=False, help='insensitive matches')
        parser_arg.add_argument('-e', '-E', dest='moin_in', action='store_true',
                                default=False, help='Extended grep')
        parser_arg.add_argument('-p', '-P', dest='out_in', action='store_true',
                                default=False, help='perl regular expression')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def is_beakerlib_command(self, testing_command, parser_ref):
        return parser_ref.is_beakerlib_command(testing_command)


class DocumentationTranslator:
    """Class making documentation information from argparse data. 
    Generated information are focused on BeakerLib commands"""
    inf_ref = ""

    low = 1
    lowMedium = 2
    medium = 3
    high = 4
    highest = 5

    def __init__(self, parser_ref):
        self.parser_ref = parser_ref
        self.inf_ref = ""

    def translate_data(self, argparse_data):
        """
        This method translate argparse object into DocumentationInformation object
        :param argparse_data: argparse object
        :return: DocumentationInformation object
        """
        self.inf_ref = ""

        argname = argparse_data.argname
        condition = ConditionsForCommands()

        if condition.is_rlrun_command(argname):
            self.set_rlrun_data(argparse_data)

        elif condition.is_rpm_command(argname):
            self.set_rpmcommand_data(argparse_data)

        elif condition.is_check_or_assert_mount(argname):
            self.set_check_or_assert_mount_data(argparse_data)

        elif condition.is_assert_command(argname):

            if condition.is_assert_grep(argname):
                self.set_assert_grep_data(argparse_data)

            elif condition.is_rlpass_or_rlfail_command(argname):
                self.set_rlpass_or_rlfail_data(argparse_data)

            elif condition.is_assert0(argname):
                self.set_rlassert0_data(argparse_data)

            elif condition.is_assert_comparasion(argname):
                self.set_assert_comparison_data(argparse_data)

            elif condition.is_assert_exists(argname):
                self.set_assert_exits_data(argparse_data)

            elif condition.is_assert_differ(argname):
                self.set_assert_differ_data(argparse_data)

            elif condition.is_assert_binary_origin(argname):
                self.set_assertbinaryorigin_data(argparse_data)

        elif condition.is_rlfilebackup_command(argname):
            self.set_rlfilebackup_data(argparse_data)

        elif condition.is_rlfilerestore_command(argname):
            self.set_rlfile_restore_data(argparse_data)

        elif condition.is_rlisrhel_or_rlisfedora_command(argname):
            self.set_isrhel_or_isfedora_data(argparse_data)

        elif condition.is_rlmount(argname):
            self.set_rlmount_data(argparse_data)

        elif condition.is_rlhash_or_rlunhash_command(argname):
            self.set_rlhash_or_rlunhash_data(argparse_data)

        elif condition.is_rllog_command(argname):
            self.set_rllog_data(argparse_data)

        elif condition.is_rldie_command(argname):
            self.set_rldie_data(argparse_data)

        elif condition.is_rlget_x_arch_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlgetdistro_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlgetphase_or_test_state_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlreport_command(argname):
            self.set_rlreport_data(argparse_data)

        elif condition.is_rlwatchdog_command(argname):
            self.set_rlwatchdog_data(argparse_data)

        elif condition.is_rlbundlelogs_command(argname):
            self.set_rlbundlelogs_data(argparse_data)

        elif condition.is_rlservicexxx(argname):
            self.set_rlservicexxx_data(argparse_data)

        elif condition.is_sebooleanxxx_command(argname):
            self.set_sebooleanxxx_data(argparse_data)

        elif condition.is_rlshowrunningkernel_command(argname):
            self.set_rlshowrunningkernel_data()

        elif condition.is_get_or_check_makefile_requires(argname):
            self.set_rlget_or_rlcheck_makefilerequeries_data(argparse_data)

        elif condition.is_rlcleanup_apend_or_prepend_command(argname):
            self.set_rlcleanup_apend_or_prepend_data(argparse_data)

        elif condition.is_rlfilesubmit_command(argname):
            self.set_rlfilesubmit_data(argparse_data)

        elif condition.is_rlperftime_runsintime_command(argname):
            self.set_rlperftime_runsintime_data(argparse_data)

        elif condition.is_rlperftime_avgfromruns_command(argname):
            self.set_rlperftime_avgfromruns_data(argparse_data)

        elif condition.is_rlshowpackageversion_command(argname):
            self.set_rlshowpackageversion_data(argparse_data)

        elif condition.is_rljournalprint_command(argname):
            self.set_rljournalprint_data(argparse_data)

        elif condition.is_rlimport_command(argname):
            self.set_rlimport_data(argparse_data)

        elif condition.is_rlwaitfor_command(argname):
            self.set_rlwaitfor_data(argparse_data)

        elif condition.is_rlwaitforcmd_command(argname):
            self.set_rlwaitforcmd_data(argparse_data)

        elif condition.is_rlwaitforfile_command(argname):
            self.set_rlwaitforfile_data(argparse_data)

        elif condition.is_rlwaitforsocket_command(argname):
            self.set_rlwaitforsocket_data(argparse_data)

        elif condition.is_virtualxxx_command(argname):
            self.set_rlvirtualx_xxx_data(argparse_data)

        return self.inf_ref

    def set_rljournalprint_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = []
        param_option = []
        if argparse_data.argname == "rlJournalPrint":
            if len(argparse_data.type):
                subject.append(argparse_data.type)
            else:
                subject.append("xml")
        else:
            subject.append("text")
            if argparse_data.full_journal:
                param_option.append("additional information")

        topic_obj = Topic("JOURNAL", subject)
        action = ["print"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlshowpackageversion_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        action = ["print"]
        subject = argparse_data.package
        topic_obj = Topic("PACKAGE", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlfilesubmit_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.path_to_file]
        if not len(argparse_data.s) and not len(argparse_data.required_name):
            subject.append('-')

        elif len(argparse_data.s) and not len(argparse_data.required_name):
            subject.append(argparse_data.s)

        elif len(argparse_data.s) and len(argparse_data.required_name):
            subject.append(argparse_data.s)
            subject.append(argparse_data.required_name)
        topic_obj = Topic("FILE", subject)
        action = ["resolve"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlbundlelogs_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = argparse_data.file
        topic_obj = Topic("FILE", subject)
        action = ["create"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rldie_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = [argparse_data.message]
        subject += argparse_data.file
        topic_obj = Topic("MESSAGE", subject)
        action = ["create"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rllog_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = [argparse_data.message]
        topic_obj = Topic("MESSAGE", subject)
        action = ["create"]
        param_option = []
        if argparse_data.logfile:
            param_option.append(argparse_data.logfile)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlshowrunningkernel_data(self):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        """
        importance = self.lowMedium
        topic_obj = Topic("MESSAGE", ["kernel"])
        action = ["create"]
        self.inf_ref = DocumentationInformation("rlShowRunningKernel", topic_obj, action, importance)

    def set_rlget_or_rlcheck_makefilerequeries_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        topic_obj = Topic("FILE", ["makefile"])
        action = []
        if argparse_data.argname == "rlGetMakefileRequires":
            action.append("print")
        else:
            action.append("check")
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlget_commands_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        action = []
        if ConditionsForCommands().is_rlgetphase_or_test_state_command(argparse_data.argname):
            if argparse_data.argname == "rlGetTestState":
                subject.append("test")
            else:
                subject.append("phase")
        elif ConditionsForCommands().is_rlgetdistro_command(argparse_data.argname):
            if argparse_data.argname == "rlGetDistroRelease":
                subject.append("release")
            else:
                subject.append("variant")
        elif argparse_data.argname == "rlGetPrimaryArch":
            subject.append("primary")
        else:
            subject.append("secondary")
        topic_obj = Topic("JOURNAL", subject)
        action.append("return")
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwatchdog_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.highest
        subject = ["watchdog", argparse_data.command, argparse_data.timeout]
        param_option = []
        if argparse_data.signal:
            param_option.append(argparse_data.signal)
        topic_obj = Topic("COMMAND", subject)
        action = ["run"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlreport_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.name, argparse_data.result]
        topic_obj = Topic("JOURNAL", subject)
        action = ["report"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlrun_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.highest
        subject = [argparse_data.command, argparse_data.status]
        possible_beakerlib_command = self.get_argparse_of_command(argparse_data.command)

        if possible_beakerlib_command.argname == "UNKNOWN":
            param_option = []
            if argparse_data.l:
                param_option.append("l")
            elif argparse_data.c:
                param_option.append("c")
            elif argparse_data.t and argparse_data.s:
                param_option.append("s")
                param_option.append("t")
            elif argparse_data.t:
                param_option.append("t")
            elif argparse_data.s:
                param_option.append("s")
            topic_obj = Topic("COMMAND", subject)
            action = ["run"]
            self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

        else:
            beakerlib_information_unit = self.translate_data(possible_beakerlib_command)
            beakerlib_information_unit.set_status(argparse_data.status)

    def get_argparse_of_command(self, command):
        """
        Gets argparse from command. This method is called in few methods. It depends
        on BeakerLib commands. If argparse of BeakerLib command contain command data,
        then this method will be used.
        :param command: command line
        :return: argparse object
        """
        pom_phase = PhaseContainer("Helpful phase")
        return StatementDataSearcher(self.parser_ref, pom_phase).parse_command(command)

    def set_rlvirtualx_xxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = [argparse_data.name]
        action = []
        if argparse_data.argname == "rlVirtualXStop":
            action.append("kill")
        elif argparse_data.argname == "rlVirtualXStart":
            action.append("run")
        else:
            action.append("return")
        topic_obj = Topic("SERVER", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwaitfor_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = []
        if len(argparse_data.n):
            subject = argparse_data.n
        topic_obj = Topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwaitforsocket_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.port_path]
        param_option = []
        if argparse_data.close:
            param_option.append("close")
        elif argparse_data.p:
            param_option.append("p")

        topic_obj = Topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlwaitforfile_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = ["file", argparse_data.path]
        param_option = []
        if argparse_data.p:
            param_option.append(argparse_data.p)
        topic_obj = Topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlwaitforcmd_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = ["cmd", argparse_data.command]
        param_option = ["", ""]
        if argparse_data.r:
            param_option[0] = argparse_data.r

        if argparse_data.p:
            param_option[1] = argparse_data.p

        topic_obj = Topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlimport_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = argparse_data.LIBRARY
        topic_obj = Topic("PACKAGE", subject)
        action = ["import"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlperftime_runsintime_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.command]
        param_option = [argparse_data.time]
        topic_obj = Topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlperftime_avgfromruns_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.command]
        topic_obj = Topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlcleanup_apend_or_prepend_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlCleanupAppend":
            subject.append("append")
        subject.append(argparse_data.string)
        topic_obj = Topic("STRING", subject)
        action = ["create"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_sebooleanxxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlSEBooleanOn":
            subject.append("on")
        elif argparse_data.argname == "rlSEBooleanOff":
            subject.append("off")
        subject += argparse_data.boolean
        topic_obj = Topic("BOOLEAN", subject)
        action = ["set"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlservicexxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = argparse_data.service
        action = []
        if argparse_data.argname == "rlServiceStart":
            action.append("run")
        elif argparse_data.argname == "rlServiceStop":
            action.append("kill")
        else:
            action.append("restore")
        topic_obj = Topic("SERVICE", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlfile_restore_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        param_option = []
        if argparse_data.namespace:
            param_option.append(argparse_data.namespace)
        topic_obj = Topic("FILE", [""])
        action = ["restore"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlfilebackup_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        param_option = []
        subject = argparse_data.file
        if argparse_data.namespace:
            param_option.append(argparse_data.namespace)

        topic_obj = Topic("FILE", subject)
        action = ["backup"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_rlhash_or_rlunhash_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        param_option = []
        subject = []
        if argparse_data.stdin:
            subject.append(argparse_data.stdin)
        else:
            subject.append(argparse_data.STRING)
        action = []
        if argparse_data.argname == "rlUnhash" or argparse_data.decode:
            action.append("unhash")
        else:
            action.append("hash")
        if argparse_data.algorithm:
            param_option.append(argparse_data.algorithm)
        topic_obj = Topic("STRING", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_check_or_assert_mount_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.mountpoint]
        action = []
        if argparse_data.argname == "rlCheckMount":
            action.append("check")
        else:
            action.append("exists")
        if argparse_data.server and argparse_data.mountpoint:
            subject.append(argparse_data.server)
        topic_obj = Topic("MOUNTPOINT", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlmount_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.mountpoint, argparse_data.server]
        topic_obj = Topic("MOUNTPOINT", subject)
        action = ["create"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assertbinaryorigin_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = [argparse_data.binary]
        subject += argparse_data.package
        topic_obj = Topic("PACKAGE", subject)
        action = ["owned by"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rpmcommand_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = []
        action = []
        subject.append(argparse_data.name)
        if argparse_data.argname == "rlCheckRpm":
            action.append("check")
        elif argparse_data.argname == "rlAssertRpm":
            action.append("exists")
            if argparse_data.all:
                subject.append("all")
        else:
            action.append("not exists")
        topic_obj = Topic("PACKAGE", subject)
        param_option = []
        if argparse_data.version or argparse_data.release or \
                argparse_data.arch:
            if argparse_data.version:
                param_option.append(argparse_data.version)

            if argparse_data.release:
                param_option.append(argparse_data.release)

            if argparse_data.arch:
                param_option.append(argparse_data.arch)

        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))

    def set_isrhel_or_isfedora_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        action = []
        subject = []
        if argparse_data.argname == "rlIsRHEL":
            action.append("RHEL")
        else:
            action.append("Fedora")
        if len(argparse_data.type):
            subject = argparse_data.type
        topic_obj = Topic("SYSTEM", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_differ_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        action = []
        if argparse_data.argname == "rlAssertDiffer":
            action.append("differ")
        else:
            action.append("not differ")
        subject = [argparse_data.file1, argparse_data.file2]
        topic_obj = Topic("FILE", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_exits_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.file_directory]
        topic_obj = Topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertExists":
            action.append("exists")
        else:
            action.append("not exists")
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_comparison_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        action = []
        subject = [argparse_data.value1, argparse_data.value2]
        if argparse_data.argname == "rlAssertEquals":
            action.append("equal")
        elif argparse_data.argname == "rlAssertNotEquals":
            action.append("not equal")
        elif argparse_data.argname == "rlAssertGreater":
            action.append("greater")
        else:
            action.append("greater or equal")
        topic_obj = Topic("VALUE", subject)
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlassert0_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        topic_obj = Topic("VALUE", [argparse_data.value])
        action = ["check"]
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlpass_or_rlfail_data(self, argparse_data):
        pass

    def set_assert_grep_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.file, argparse_data.pattern]
        topic_obj = Topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertGrep":
            action.append("contain")
        else:
            action.append("not contain")
        param_option = []
        if argparse_data.text_in:
            param_option.append("text_in")
        elif argparse_data.moin_in:
            param_option.append("moin_in")
        elif argparse_data.out_in:
            param_option.append("out_in")
        self.inf_ref = DocumentationInformation(argparse_data.argname, topic_obj, action, importance, Option(param_option))


class Topic(object):
    """
    Class which is consist of information topic data.
    For example for BeakerLib command rlRun is topic command.

    :param topic_data: topic data (Facts)
    :param subject: Subject data which are "connected" to topic_data
    """
    topic = ""

    subject = []

    def __init__(self, topic_data, subject):
        self.topic = topic_data
        self.subject = subject

    def get_topic(self):
        return self.topic

    def get_subject(self):
        return self.subject


class Option(object):
    """
    Option class which is consist of option and status of BeakerLib command
    :param option_data: BeakerLib command options data
    :param status_data: BeakerLib command future exit status
    """
    option = []

    status = []

    def __init__(self, option_data=None, status_data="-"):
        if option_data is None:
            self.option = []
        else:
            self.option = option_data
        self.status = status_data

    def get_option(self):
        return self.option

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status


class DocumentationInformation(object):
    """
    This class contains data to describe every BeakerLib command
    :param cmd_name: Command name
    :param topic_object: Instance of Topic class
    :param action: BeakerLib command action
    :param importance: BeakerLib command importance
    :param options: Instance of Option class
    """
    command_name = ""

    topic = ""

    options = Option

    action = []

    importance = ""

    def __init__(self, cmd_name, topic_object, action, importance, options=None):
        if options is None:
            self.options = Option()
        else:
            self.options = options
        self.command_name = cmd_name
        self.topic = topic_object
        self.action = action
        self.importance = importance

    def get_topic(self):
        return self.topic.get_topic()

    def get_topic_subject(self):
        return self.topic.get_subject()

    def get_action(self):
        return self.action

    def get_importance(self):
        return self.importance

    def get_status(self):
        return self.options.get_status()

    def get_option(self):
        return self.options.get_option()

    def set_status(self, status):
        self.options.set_status(status)

    def get_command_name(self):
        return self.command_name


class InformationUnit(object):
    """
    This is main class containing nature language information
    :param inf: DocumentationInformation object with data
    """
    information = ""
    information_obj = ""

    def __init__(self, inf):
        self.information = ""
        self.information_obj = inf

    def set_information(self):
        pass

    def get_command_name(self):
        return self.information_obj.get_command_name()

    def connect_multiple_facts(self, facts, max_size=5):
        """
        This method makes more human language sentences by
        correct representing of word enumeration
        :param facts: list of words to enumerate
        :param max_size: Maximum size of words to be shown.
                         Default is 5.
        :return: set upped string line with enumerated words
        """
        pom_inf = ""
        if len(facts) == 1:
            pom_inf = facts[0]
        elif len(facts) == 2:
            pom_inf = facts[0] + " and " + facts[1]
        else:
            i = 0
            while i < max_size:
                pom_inf += facts[i]
                if len(facts) > (i + 2) and (i + 2) < max_size:
                    pom_inf += ", "
                elif (i + 1) == len(facts):
                    return pom_inf
                elif (i + 1) == max_size:
                    pom_inf += "..."
                    return pom_inf
                else:
                    pom_inf += " and "
                i += 1
            pom_inf += "..."
        return pom_inf

    def print_information(self):
        print("   " + self.information)

    def get_information_weigh(self):
        """
        This method calculates information weight.
        The weight is amount of lines on which information
        will be displayed

        :return: information weight
        """
        line_size = 60  # char per line
        weigh = (len(self.information)//line_size)
        mod_weigh = (len(self.information) % line_size)
        if weigh == 0:
            return 1
        elif mod_weigh >= 20:  # tolerance
            return weigh + 1
        else:
            return weigh

    def get_information_value(self):
        """
        :return: Return information importance
        """
        return self.information_obj.get_importance()

    def is_list_empty(self, tested_list):
        return len(tested_list) == 0

    def check_status_and_add_information(self, status):
        """
        This method replaces status number for better information string.
        :param status: command status
        """
        if not status == "-":
            if status == "1":
                self.information += " and must finished unsuccessfully"
            elif not status == "0":
                self.information += " and must finished with return code matching: " + status

    def set_correct_singulars_or_plurals(self, word, number_of_subject, ending="s", verb=False):
        """
        This method correctly represent singulars or plurals in word.
        :param word: word to set up
        :param number_of_subject: count of subjects in sentence
        :param ending: word ending in plural. default is "s"
        :param verb: possible verb after word
        :return: Correctly set upped word
        """
        pom_word = word
        if number_of_subject >= 2:
            if pom_word[-1] == "y" and ending == "ies":
                pom_word = word[:-1] + ending
            else:
                pom_word += ending

            if verb:
                pom_word += " are"
        elif verb:
            pom_word += " is"

        if not verb:
            pom_word += " "
        return pom_word


class InformationFileExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must exist"
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileNotExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must not exist"
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileContain(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                           + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileNotContain(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File " + self.information_obj.get_topic_subject()[0] \
                           + " must not contain pattern " + self.information_obj.get_topic_subject()[1]
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationJournalPrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Prints the content of the journal in pretty " + self.information_obj.get_topic_subject()[0]
        self.information += " format"
        if len(self.information_obj.get_option()):
            self.information += " with additional information"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackagePrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Shows information about "
        self.information += self.connect_multiple_facts(self.information_obj.get_topic_subject(), 4)
        self.information += " version"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileResolve(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Resolves absolute path " + subjects[0]
        if len(subjects) == 3:
            self.information += ", replaces / for " + subjects[1]
            self.information += " and rename file to " + subjects[2]
        else:
            self.information += " and replaces / for " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Creates a tarball of " + self.set_correct_singulars_or_plurals("file", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.information += " and attached it/them to test result"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMessageCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if subjects[0] == "kernel":  # rlShowRunningKernel
            self.information = "Log a message with version of the currently running kernel"
        else:  # rlDie & rlLog
            self.information = "Message \"" + subjects[0]
            if len(subjects) > 1:
                self.information += "\" is created in to log and "
                self.information += self.set_correct_singulars_or_plurals("file", len(subjects[1:]))
                self.information += self.connect_multiple_facts(subjects[1:], 3)
                if len(subjects[1:]) > 1:
                    self.information += "\" are uploaded"
                else:
                    self.information += "\" is uploaded"
            else:
                if not self.is_list_empty(option):
                    self.information += "\" is created in to logfile "
                    self.information += option[0]
                else:
                    self.information += "\" is created in to log"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFilePrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Prints comma separated list of requirements defined in Makefile"
        else:
            self.information = "Prints file content"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Checks requirements in Makefile and returns number of compliance"
        else:
            self.information = "Checks file " + self.information_obj.get_topic_subject()[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationJournalReturn(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "phase":
            self.information = "Returns number of failed asserts in current phase"
        elif subjects[0] == "test":
            self.information = "Returns number of failed asserts"
        elif subjects[0] == "variant":
            self.information = "Returns variant of the distribution on the system"
        elif subjects[0] == "release":
            self.information = "Returns release of the distribution on the system"
        elif subjects[0] == "primary":
            self.information = "Returns primary arch for the current system"
        elif subjects[0] == "secondary":
            self.information = "Returns base arch for the current system"
        else:
            self.information = "Returns data from Journal"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "watchdog":
            self.information = "Runs command " + subjects[1]
            self.information += " for " + subjects[2]
            self.information += " seconds"
            if not self.is_list_empty(self.information_obj.get_option()):
                self.information += " and killed with signal "
                self.information += self.information_obj.get_option()[0]

        else:  # rlRun
            self.information = "Command \"" + subjects[0]
            if subjects[1] == "0":
                self.information += "\" must run successfully"
            elif subjects[1] == "1":
                self.information += "\" must run unsuccessfully"
            else:
                self.information += "\" exit code must match: " + subjects[1]

            option = self.information_obj.get_option()
            if not self.is_list_empty(option):
                if option[0] == "l":
                    self.information += " and output is stored in to log"
                elif option[0] == "c":
                    self.information += " and failed output is stored in to log"
                elif len(option) > 1:
                    self.information += " and stdout and stderr are tagged and stored"
                elif option[0] == "t":
                    self.information += " and stdout and stderr are tagged"
                elif option[0] == "s":
                    self.information += " and stdout and stderr are stored"


class InformationServerRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Starts virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " server on a first free display"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServerKill(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Kills virtual X " + self.information_obj.get_topic_subject()[0] + " server"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServerReturn(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Shows number of displays where virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " is running"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationJournalReport(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Reports test \"" + subjects[0]
        self.information += "\" with result " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandWait(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "cmd":
            # rlWaitForCmd
            option = self.information_obj.get_option()
            self.information = "Pauses script execution until command " + subjects[1]
            if option[0] == "0":
                self.information += " exit status is successful"
            elif option[0] == "1":
                self.information += " exit status is unsuccessful"
            else:
                self.information += " exit status match " + option[0]

            if option[1]:
                self.information += "\n and process with this PID " + option[1]
                self.information += " must be running"
        else:  # rlWait
            if subjects:
                self.information = "Wait for " + self.connect_multiple_facts(subjects, 3)
            else:
                self.information = "All currently active child processes are"
                self.information += " waited for, and the return status is zero"
            self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileWait(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        if self.information_obj.get_topic_subject()[0] == "file":  # rlWaitForFile
            if not self.is_list_empty(option):
                self.information = "Pauses script until file or directory with this path "
                self.information += self.information_obj.get_topic_subject()[1] + " starts existing"
                self.information += "\n and process with this PID " + option[0]
                self.information += " must be running"
            else:
                self.information = "Pauses script until file or directory with this path "
                self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
        else:  # rlWaitForScript
            if not self.is_list_empty(option):
                if option[0] == "close":
                    self.information = "Waits for the socket with this path"
                    self.information += self.information_obj.get_topic_subject()[1] + "to stop listening"
                elif option[0] == "p":
                    self.information = "Pauses script until socket with this path or port "
                    self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
                    self.information += "\n and process with this PID " + option[0]
                    self.information += " must be running"
            else:
                self.information = "Pauses script until socket with this path or port "
                self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageImport(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Imports code provided by "
        self.information += self.connect_multiple_facts(subject, 2)
        self.information += self.set_correct_singulars_or_plurals(" library", len(subject), "ies")
        self.information += "  library(ies) into the test namespace"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandMeasures(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if not self.is_list_empty(option):
            self.information = "Measures, how many runs of command "
            self.information += subjects[0] + " in "
            self.information += option[0] + " second(s)"
        else:
            self.information = "Measures the average time of running command "
            self.information += subjects[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationStringCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "append":
            self.information = "Appends string: " + self.information_obj.get_topic_subject()[1]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        else:
            self.information = "Prepends string: " + self.information_obj.get_topic_subject()[0]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationBooleanSet(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "on":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to true"
        elif subjects[0] == "off":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to false"
        else:
            self.information = "Restore "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects))
            self.information += self.connect_multiple_facts(subjects, 3)
            self.information += " into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServiceRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Starts "
        self.information += self.set_correct_singulars_or_plurals("service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""

        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(subject, 3) + \
                               " must be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(subject, 3) + \
                               " must not be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationServiceKill(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Kills "
        self.information += self.set_correct_singulars_or_plurals("service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""
        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                               " must not be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                               " must be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationServiceRestore(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        if len(subject) > 1:
            self.information += " are restored into original state"
        else:
            self.information += " is restored into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileRestore(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        if not self.is_list_empty(option):
            self.information = "Restores backed up file with namespace: "
            self.information += option[0]
            self.information += "to original state"
        else:
            self.information = "Restores backed up files to their "
            self.information += "original location"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileBackup(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        status = self.information_obj.get_status()
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("File", len(subject))
        self.information += "or " + self.set_correct_singulars_or_plurals("directory", len(subject), "ies")
        self.information += self.connect_multiple_facts(subject, 2)
        if len(subject) >= 2:
            self.information += " are backed up"
        else:
            self.information += " is backed up"
        if not self.is_list_empty(option):
            self.information += "with namespace " + option[0]
        self.check_status_and_add_information(status)


class InformationStringHash(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        self.information = "Hashes string "
        if subjects[0] == True:
            self.information += "from input"
        else:
            self.information += subjects[0]
        if not self.is_list_empty(option):
            self.information += " with hashing algorithm "
            self.information += option[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationStringUnHash(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        subjects = self.information_obj.get_topic_subject()
        self.information = "Unhashes string "
        if subjects[0] ==  True:
            self.information += "from input"
        else:
            self.information += subjects[0]

        if not self.is_list_empty(option):
            self.information += " with hashing algorithm "
            self.information += option[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Directory "
        self.information += subjects[0]
        self.information += "must be a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Creates mount point " + subjects[0]
        if subjects[1]:
            self.information += " and mount NFS " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Checks if directory "
        self.information += subjects[0]
        self.information += "is a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageOwnedBy(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Binary " + subjects[0] + "must be"
        self.information += " owned by "
        self.information += self.set_correct_singulars_or_plurals("package", len(subjects[1:]))
        self.information += self.connect_multiple_facts(subjects[1:], 4)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationSystemIsRHEL(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " RHEL "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationSystemIsFedora(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " Fedora "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileDiffer(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be different"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileNotDiffer(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be identical"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueNotEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must not be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueGreater(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater than value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueGreaterOrEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater or equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Value " + self.information_obj.get_topic_subject()[0] + " must be 0"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        self.information = "Package " + self.information_obj.get_topic_subject()[0]
        self.information += " must be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if subjects[0] == "all":
            self.information = "Packages in $PACKAGES, $REQUIRES"
            self.information += " and $COLLECTIONS must be installed"
        else:
            self.information = "Package " + subjects[0]
            self.information += " must be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageNotExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        self.information = "Package " + self.information_obj.get_topic_subject()[0]
        self.information += " must not be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())


class GetInformation(object):
    """
    This class is responsible for transformation from DocumentationInformation class
    to small InformationUnit class. This class contain big 2D array with reference to
    small InformationUnit classes.
    """
    array = [
        # topic: FILE(DIRECTORY),           STRING                   PACKAGE          JOURNAL,PHASE,TEST   MESSAGE         COMMAND                SERVER              BOOLEAN              SERVICE            MOUNTPOINT              SYSTEM                 VALUE  # ACTIONS
        [InformationFileExists,           0,           InformationPackageExists,              0,              0,              0,                     0,                  0,                  0,  InformationMountpointExists,           0,                     0],  # exists
        [InformationFileNotExists,        0,           InformationPackageNotExists,           0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not exists
        [InformationFileContain,          0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # contain
        [InformationFileNotContain,       0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not contain
        [InformationFilePrint,            0,           InformationPackagePrint,   InformationJournalPrint,    0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # print(show)
        [InformationFileResolve,          0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # resolve
        [InformationFileCreate, InformationStringCreate,          0,                          0, InformationMessageCreate,    0,                     0,                  0,                  0,  InformationMountpointCreate,           0,                     0],  # create
        [InformationFileCheck,            0,           InformationPackageCheck,               0,              0,              0,                     0,                  0,                  0,  InformationMountpointCheck,            0,         InformationValueCheck],  # check
        [           0,                    0,                      0,                InformationJournalReturn, 0,              0,         InformationServerReturn,        0,                  0,                   0,                    0,                     0],  # return
        [           0,                    0,                      0,                          0,              0,  InformationCommandRun, InformationServerRun,           0,       InformationServiceRun,          0,                    0,                     0],  # run
        [           0,                    0,                      0,                InformationJournalReport, 0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # report
        [           0,                    0,                      0,                          0,              0,              0,          InformationServerKill,         0,       InformationServiceKill,         0,                    0,                     0],  # kill
        [InformationFileWait,             0,                      0,                          0,              0,  InformationCommandWait,            0,                  0,                  0,                   0,                    0,                     0],  # wait
        [           0,                    0,           InformationPackageImport,              0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # import
        [           0,                    0,                      0,                          0,              0,  InformationCommandMeasures,        0,                  0,                  0,                   0,                    0,                     0],  # measures
        [           0,                    0,                      0,                          0,              0,              0,                     0,     InformationBooleanSet,           0,                   0,                    0,                     0],  # set
        [InformationFileRestore,          0,                      0,                          0,              0,              0,                     0,                  0,      InformationServiceRestore,       0,                    0,                     0],  # restore
        [InformationFileBackup,           0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # backup
        [           0,          InformationStringHash,            0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # hash
        [           0,          InformationStringUnHash,          0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # unhash
        [           0,                    0,           InformationPackageOwnedBy,             0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # owned by
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,    InformationSystemIsRHEL,               0],  # is RHEL
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,   InformationSystemIsFedora,              0],  # is Fedora
        [InformationFileDiffer,           0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # differ
        [InformationFileNotDiffer,        0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not differ
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,         InformationValueEqual],  # equal
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,       InformationValueNotEqual],  # not equal
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,        InformationValueGreater],  # greater
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,   InformationValueGreaterOrEqual],  # greater or equal
    ]

    def get_information_from_facts(self, information_obj):
        """
        Method responsible for the transformation
        :param information_obj: DocumentationInformation instanse to be transformed
        :return: InformationUnit class or empty string.
        """
        information = ""
        topic = information_obj.get_topic()
        for action in information_obj.get_action():
            column = self.get_topic_number(topic)
            row = self.get_action_number(action)
            information_class = self.array[row][column]
            if information_class:
                information = information_class(information_obj)
                information.set_information()
        return information

    def get_action_number(self, action):
        """
        method responsible for returning the right row number
        :param action: action word
        :return: row number
        """
        if self.is_action_exists(action):
            return 0
        elif self.is_action_not_exists(action):
            return 1
        elif self.is_action_contain(action):
            return 2
        elif self.is_action_not_contain(action):
            return 3
        elif self.is_action_print(action):
            return 4
        elif self.is_action_resolve(action):
            return 5
        elif self.is_action_create(action):
            return 6
        elif self.is_action_check(action):
            return 7
        elif self.is_action_return(action):
            return 8
        elif self.is_action_run(action):
            return 9
        elif self.is_action_report(action):
            return 10
        elif self.is_action_kill(action):
            return 11
        elif self.is_action_wait(action):
            return 12
        elif self.is_action_import(action):
            return 13
        elif self.is_action_measures(action):
            return 14
        elif self.is_action_set(action):
            return 15
        elif self.is_action_restore(action):
            return 16
        elif self.is_action_backup(action):
            return 17
        elif self.is_action_hash(action):
            return 18
        elif self.is_action_unhash(action):
            return 19
        elif self.is_action_owned_by(action):
            return 20
        elif self.is_action_is_rhel(action):
            return 21
        elif self.is_action_is_fedora(action):
            return 22
        elif self.is_action_differ(action):
            return 23
        elif self.is_action_not_differ(action):
            return 24
        elif self.is_action_equal(action):
            return 25
        elif self.is_action_not_equal(action):
            return 26
        elif self.is_action_greater(action):
            return 27
        elif self.is_action_greater_or_equal(action):
            return 28

    def get_topic_number(self, topic):
        """
        method responsible for returning the right topic column number
        :param topic: Topic word
        :return: column
        """
        if self.is_topic_file(topic):
            return 0
        elif self.is_topic_string(topic):
            return 1
        elif self.is_topic_package(topic):
            return 2
        elif self.is_topic_journal(topic):
            return 3
        elif self.is_topic_message(topic):
            return 4
        elif self.is_topic_command(topic):
            return 5
        elif self.is_topic_server(topic):
            return 6
        elif self.is_topic_boolean(topic):
            return 7
        elif self.is_topic_service(topic):
            return 8
        elif self.is_topic_mountpoint(topic):
            return 9
        elif self.is_topic_system(topic):
            return 10
        elif self.is_topic_value(topic):
            return 11

    def is_topic_file(self, topic):
        return topic == "FILE"

    def is_topic_string(self, topic):
        return topic == "STRING"

    def is_topic_package(self, topic):
        return topic == "PACKAGE"

    def is_topic_journal(self, topic):
        return topic == "JOURNAL"

    def is_topic_message(self, topic):
        return topic == "MESSAGE"

    def is_topic_command(self, topic):
        return topic == "COMMAND"

    def is_topic_server(self, topic):
        return topic == "SERVER"

    def is_topic_boolean(self, topic):
        return topic == "BOOLEAN"

    def is_topic_service(self, topic):
        return topic == "SERVICE"

    def is_topic_mountpoint(self, topic):
        return topic == "MOUNTPOINT"

    def is_topic_system(self, topic):
        return topic == "SYSTEM"

    def is_topic_value(self, topic):
        return topic == "VALUE"

    def is_action_exists(self, action):
        return action == "exists"

    def is_action_not_exists(self, action):
        return action == "not exists"

    def is_action_contain(self, action):
        return action == "contain"

    def is_action_not_contain(self, action):
        return action == "not contain"

    def is_action_print(self, action):
        return action == "print"

    def is_action_resolve(self, action):
        return action == "resolve"

    def is_action_create(self, action):
        return action == "create"

    def is_action_check(self, action):
        return action == "check"

    def is_action_return(self, action):
        return action == "return"

    def is_action_run(self, action):
        return action == "run"

    def is_action_report(self, action):
        return action == "report"

    def is_action_kill(self, action):
        return action == "kill"

    def is_action_wait(self, action):
        return action == "wait"

    def is_action_import(self, action):
        return action == "import"

    def is_action_measures(self, action):
        return action == "measures"

    def is_action_set(self, action):
        return action == "set"

    def is_action_restore(self, action):
        return action == "restore"

    def is_action_backup(self, action):
        return action == "backup"

    def is_action_hash(self, action):
        return action == "hash"

    def is_action_unhash(self, action):
        return action == "unhash"

    def is_action_owned_by(self, action):
        return action == "owned_by"

    def is_action_is_rhel(self, action):
        return action == "RHEL"

    def is_action_is_fedora(self, action):
        return action == "Fedora"

    def is_action_differ(self, action):
        return action == "differ"

    def is_action_not_differ(self, action):
        return action == "not differ"

    def is_action_equal(self, action):
        return action == "equal"

    def is_action_not_equal(self, action):
        return action == "not equal"

    def is_action_greater(self, action):
        return action == "greater"

    def is_action_greater_or_equal(self, action):
        return action == "greater or equal"


class ConditionsForCommands:
    """ Class consists of conditions for testing commands used in
    StatementDataSearcher and DocumentationTranslator """

    def is_rlwatchdog_command(self, command):
        return command == "rlWatchdog"

    def is_rlreport_command(self, command):
        return command == "rlReport"

    def is_virtualxxx_command(self, command):
        pom_list = ["rlVirtualXStop", "rlVirtualXStart", "rlVirtualXGetDisplay"]
        return command in pom_list

    def is_rlwaitfor_command(self, command):
        return command == "rlWaitFor"

    def is_rlwaitforsocket_command(self, command):
        return command == "rlWaitForSocket"

    def is_rlwaitforfile_command(self, command):
        return command == "rlWaitForFile"

    def is_rlwaitforcmd_command(self, command):
        return command == "rlWaitForCmd"

    def is_rlwaitforxxx_command(self, command):
        pom_list = ["rlWaitForCmd", "rlWaitForFile", "rlWaitForSocket"]
        return command in pom_list

    def is_rlimport_command(self, command):
        return command == "rlImport"

    def is_rlperftime_runsintime_command(self, command):
        return command == "rlPerfTime_RunsInTime"

    def is_rlperftime_avgfromruns_command(self, command):
        return command == "rlPerfTime_AvgFromRuns"

    def is_rlcleanup_apend_or_prepend_command(self, command):
        return command == "rlCleanupAppend" or command == "rlCleanupPrepend"

    def is_sebooleanxxx_command(self, command):
        pom_list = ["rlSEBooleanOn", "rlSEBooleanOff", "rlSEBooleanRestore"]
        return command in pom_list

    def is_rlservicexxx(self, command):
        pom_list = ["rlServiceStart", "rlServiceStop", "rlServiceRestore"]
        return command in pom_list

    def is_rlfilebackup_command(self, command):
        return command == "rlFileBackup"

    def is_rlfilerestore_command(self, command):
        return command == "rlFileRestore"

    def is_rlhash_or_rlunhash_command(self, command):
        return command == "rlHash" or command == "rlUnhash"

    def is_check_or_assert_mount(self, command):
        return command == "rlCheckMount" or command == "rlAssertMount"

    def is_get_or_check_makefile_requires(self, command):
        return command == "rlCheckMakefileRequires" or command == "rlGetMakefileRequires"

    def is_rlmount(self, command):
        return command == "rlMount"

    def is_assert_binary_origin(self, command):
        return command == "rlAssertBinaryOrigin"

    def is_rlisrhel_or_rlisfedora_command(self, command):
        return command == "rlIsRHEL" or command == "rlIsFedora"

    def is_assert_differ(self, command):
        return command == "rlAssertDiffer" or command == "rlAssertNotDiffer"

    def is_assert_exists(self, command):
        return command == "rlAssertExists" or command == "rlAssertNotExists"

    def is_assert_comparasion(self, command):
        pom_list = ["rlAssertEquals", "rlAssertNotEquals", "rlAssertGreater",
                    "rlAssertGreaterOrEqual"]
        return command in pom_list

    def is_rlpass_or_rlfail_command(self, command):
        return command == "rlPass" or command == "rlFail"

    def is_assert_grep(self, command):
        return command == "rlAssertGrep" or command == "rlAssertNotGrep"

    def is_assert0(self, command):
        return command == "rlAssert0"

    def is_assert_command(self, line):
        return line[0:len("rlAssert")] == "rlAssert"

    def is_rpm_command(self, command):
        return command[-3:] == "Rpm"

    def is_rlrun_command(self, line):
        return line[0:len("rlRun")] == "rlRun"

    def is_rljournalprint_command(self, command):
        pom_list = ["rlJournalPrint", "rlJournalPrintText"]
        return command in pom_list

    def is_rlgetphase_or_test_state_command(self, command):
        pom_list = ["rlGetPhaseState", "rlGetTestState"]
        return command in pom_list

    def is_rllog_command(self, command):
        pom_list = ["rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo",
                    "rlLogDebug", "rlLog"]
        return command in pom_list

    def is_rllogmetric_command(self, command):
        pom_list = ["rlLogMetricLow", "rlLogMetricHigh"]
        return command in pom_list

    def is_rldie_command(self, command):
        return command[0:len("rlDie")] == "rlDie"

    def is_rlbundlelogs_command(self, command):
        return command[0:len("rlBundleLogs")] == "rlBundleLogs"

    def is_rlfilesubmit_command(self, command):
        return command[0:len("rlFileSubmit")] == "rlFileSubmit"

    def is_rlshowpackageversion_command(self, command):
        return command[0:len("rlShowPackageVersion")] == "rlShowPackageVersion"

    def is_rlget_x_arch_command(self, command):
        pom_list = ["rlGetArch", "rlGetPrimaryArch", "rlGetSecondaryArch"]
        return command in pom_list

    def is_rlgetdistro_command(self, command):
        pom_list = ["rlGetDistroRelease", "rlGetDistroVariant"]
        return command in pom_list

    def is_rlshowrunningkernel_command(self, command):
        return command[0:len("rlShowRunningKernel")] == "rlShowRunningKernel"


#  ***************** MAIN ******************
def set_cmd_arguments():
    """
    This method contains set upped argparse object to parse
    command line options and files

    :return: argparse object
    """
    pom_parser = argparse.ArgumentParser(description='Parse arguments in cmd line for generator')
    pom_parser.add_argument('files', metavar='file', type=str, nargs='+', help='script file')
    pom_parser.add_argument('-l', '--log', dest='log_in', action='store_true',
                            default=False, help='Show log data if they are possible')
    pom_parser.add_argument('-s', '--size', type=int, help="Size of output documentation in lines,"
                                                           " default is 32 lines(A4) per documentation", default=32)
    parser_arg = pom_parser.parse_args()
    return parser_arg


def run_doc_generator(parser_arg):
    """
    This method runs documentation generator
    :param parser_arg: argparse object
    """
    for file in parser_arg.files:
        pom = Parser(file)
        pom.get_doc_data()
        pom.get_documentation_information()
        pom.generate_documentation()
        pom.print_documentation(parser_arg)

if __name__ == "__main__":
    CMD_args = set_cmd_arguments()
    run_doc_generator(CMD_args)
