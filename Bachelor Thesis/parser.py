#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex
import re
import argparse


class Parser(object):
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
                with open(file_in, "r") as inputfile:
                    self.file_name = file_in
                    self.description = file_in[0:(len(file_in) - 3)]
                    self.file_test = inputfile.read()
                    self.parse_data()

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)

        else:
            print("ERROR: Not a script file. (*.sh)")
            sys.exit(1)

    def parse_data(self):
        self.phases.append(phase_outside())

        pom_line = ""
        for line in self.file_test.split('\n'):
            line = line.strip()

            if line[0:1] != '#' and len(line) >= 1 and \
                    not self.is_phase_journal_end(line):

                if self.is_phase(line):
                    self.phases.append(phase_container(line[len("rlphasestart"):]))

                elif self.is_end_back_slash(line):
                    pom_line += line[0:-1]

                elif len(self.phases) > 0:
                    if pom_line != "":
                        self.phases[-1].setup_statement(pom_line + line)
                        pom_line = ""
                    else:
                        self.phases[-1].setup_statement(line)

            elif self.is_phase_journal_end(line):
                self.phases.append(phase_outside())

    def print_statement(self):
        for i in self.phases:
            print(i.statement_list)
            print("\n")

    def is_end_back_slash(self, line):
        return line[-1:] == '\\'

    def set_test_launch(self, number_of_variables):
        if number_of_variables > self.test_launch:
            self.test_launch = number_of_variables

    def set_environmental_variable_information(self, variable):
        if not variable in self.environmental_variable:
            self.environmental_variable.append(variable)

    def get_doc_data(self):
        pom_var = test_variables()
        pom_func = []
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.search_data(self, pom_var, pom_func)
                pom_var = test_variables()

            else:
                member.search_data(pom_var, pom_func)
                pom_var = test_variables()

            # copying variables to new variable instance
            for var in member.variables.variable_names_list:
                pom_value = member.variables.get_variable_value(var)
                pom_var.add_variable(var, pom_value)

            # copying keywords to new variable instance
            for key in member.variables.keywords:
                pom_var.add_keyword(key)

            #copying functions to new function list
            for function in member.func_list:
                pom_f = []
                pom_f.append(function)
                pom_func = pom_f

    def get_documentation_information(self):
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.translate_data(self)

    def generate_documentation(self):
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.generate_documentation()

    def get_test_weigh(self):
        weigh = 0
        for member in self.phases:
            if not self.is_phase_outside(member):
                weigh += member.get_phase_weigh()
        return weigh

    def setup_phases_lists_for_knapsack(self):
        phases_list = self.get_phases_information_lists()
        whole_setuped_list =[]
        for element in phases_list:
            pom_list = []
            pom_list.append(element)
            pom_list.append(element.get_information_weigh())
            pom_list.append(element.get_information_value())
            whole_setuped_list.append(pom_list)
        return whole_setuped_list

    def get_phases_information_lists(self):
        phases_lists = []
        for member in self.phases:
            if not self.is_phase_outside(member):
                phases_lists += member.get_information_list()
        return phases_lists

    def set_phases_information_lists(self, finished_knapsack_list):
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
        inf = "Test launch: " + self.file_name
        i = 0
        while(int(i) < int(self.test_launch)):
            inf += " [VARIABLE]"
            i += 1
        #inf += " with " + str(self.test_launch) + " command line arguments"
        print(inf)

    def print_test_environmental_variables_information(self):
        inf = "Test environmental variables: "
        if len(self.environmental_variable):
            for env in self.environmental_variable:
                inf += env + ", "
            inf = inf[0:-2]
        else:
            inf += "-"
        print(inf)

    def print_documentation(self, cmd_options):
        self.print_test_launch()
        self.print_test_environmental_variables_information()
        print("")
        test_weigh  = self.get_test_weigh()
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

    def is_beakerLib_command(self, testing_command):
        return testing_command in self.all_commands

    # items in [["information", weigh, value], ...] format
    def solve_knapsack_dp(self, items, limit):
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


class test_variables:
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


class test_function:
    """Class for working with functions from the BeakerLib test"""

    statement_list = []

    name = ""

    def __init__(self, fname):
        self.statement_list = []
        self.name = fname

    def add_line(self, line):
        self.statement_list.append(line)


class phase_outside:
    """Class for searching data outside of phases"""
    phase_name = ""
    statement_list = []
    variables = ""
    func_list = []

    def __init__(self):
        # self.parse_ref = parse_cmd
        self.phase_name = "Outside phase"
        self.statement_list = []
        self.variables = test_variables()
        self.func_list = []

    def setup_statement(self, line):
        self.statement_list.append(line)

    def search_data(self, variable_copy, function_copy):
        self.variables = variable_copy
        self.func_list = function_copy
        func = False
        for statement in self.statement_list:

            # This three conditions are here because of getting further
            # information from functions.
            if self.is_function(statement):
                func = True
                self.func_list.append(test_function(statement[len("function")+1:]))

            elif func and not self.is_function_end(statement):
                self.func_list[-1].add_line(statement)

            elif func and self.is_function_end(statement):
                self.func_list[-1].add_line(statement)
                func = False

            else:
                # searching variables in statement line
                try:
                    readed = shlex.shlex(statement)
                    member = readed.get_token()
                    equal_to = readed.get_token()

                    while(equal_to):

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
                        equal_to = readed.get_token()
                except ValueError as detail:
                    print("ERROR in line: " + str(statement))
                    print("With message: " + str(detail))

    def is_function(self, line):
        return line[0:len("function")] == "function"

    def is_function_end(self, line):
        if line[0:1] == "}":
            return True
        else:
            # This split for erasing comments on the end of line
            pom_list = shlex.split(line, True, True)
            if pom_list[-1][-1] == "}":
                return True
            else:
                return False


class phase_container:
    """Class for store information in test phase"""
    phase_name = ""
    statement_list = []
    doc_ref = ""
    variables = ""
    statement_classes = []
    documentation_units = []
    phase_documentation_information = []
    func_list = []

    def __init__(self, name):
        self.phase_name = name
        self.statement_list = []
        self.doc = []
        self.variables = test_variables()
        self.statement_classes = []
        self.documentation_units = []
        self.phase_documentation_information = []
        self.func_list = []

    def setup_statement(self, line):
        self.statement_list.append(line)

    def search_data(self, parser_ref, variable_copy, function_copy):
        self.function_list = function_copy
        self.variables = variable_copy
        command_translator = statement_automata(parser_ref, self)
        for statement in self.statement_list:
            try:
                self.statement_classes.append(command_translator.parse_command(statement))
            except ValueError:
                print("ERROR in line: " + str(statement))
                print(ValueError)
            except SystemExit:
                print("ERROR in line: " + str(statement))
                print("Can be problem with variables substitutions")

    def translate_data(self, parser_ref):
        data_translator = documentation_translator(parser_ref)
        for data in self.statement_classes:
            if data.argname != "UNKNOWN":
                self.documentation_units.append(data_translator.translate_data(data))

    def generate_documentation(self):
        information_translator = get_information()
        for information in self.documentation_units:
            if information:
                self.phase_documentation_information.append(information_translator.get_information_from_facts(information))

    def print_phase_documentation(self, cmd_options):
        self.print_phase_name_with_documentation_credibility()
        conditions = conditions_for_commands()

        for information in self.phase_documentation_information:
            if cmd_options.log_in:
                information.print_information()
            elif not conditions.is_rlLog(information.get_command_name()):
                information.print_information()

    def print_phase_name_with_documentation_credibility(self):
        credibility = len(self.statement_list) - len(self.phase_documentation_information)
        inf = self.phase_name + " [ Unknown commands: " + str(credibility) + ", Total: " + str(len(self.statement_list)) + " ]"
        print(inf)

    def get_information_list(self):
        return self.phase_documentation_information

    def set_information_list(self, inf_list):
        self.phase_documentation_information = inf_list

    def get_phase_weigh(self):
        phase_weigh = 0
        for inf in self.phase_documentation_information:
            phase_weigh += inf.get_information_weigh()
        return phase_weigh



class statement_automata:
    parsed_param_ref = ""
    parser_ref = ""
    phase_ref = ""

    minimum_variable_size = 4

    def __init__(self, parser_ref, phase_ref):
        self.parser_ref = parser_ref
        self.phase_ref = phase_ref
        self.minimum_variable_size = 4

    def parse_command(self, statement_line):
        # Spliting statement using shlex lexicator
        pom_statement_line = self.phase_ref.variables.replace_variable_in_string(statement_line)
        self.get_cmd_line_params(pom_statement_line)
        self.get_environmental_variable(pom_statement_line)
        pom_list = shlex.split(pom_statement_line, True, posix=True)
        first = pom_list[0]

        # if self.is_beakerLib_command(first, self.parser_ref):
        condition = conditions_for_commands()

        if condition.is_rlrun_command(first):
            self.rlRun(pom_list)

        elif condition.is_Rpm_command(first):
            self.rpm_command(pom_list)

        elif condition.is_check_or_assert_mount(first):
            self.check_or_assert_mount(pom_list)

        elif condition.is_assert_command(first):

            if condition.is_assert_grep(first):
                self.assert_grep(pom_list)

            elif condition.is_rlPass_or_rlFail(first):
                self.rlPass_or_rlFail(pom_list)

            elif condition.is_assert0(first):
                self.assert0(pom_list)

            elif condition.is_assert_comparasion(first):
                self.assert_comparison(pom_list)

            elif condition.is_assert_exists(first):
                self.assert_exits(pom_list)

            elif condition.is_assert_differ(first):
                self.assert_differ(pom_list)

            elif condition.is_assert_binary_origin(first):
                self.assert_binary_origin(pom_list)

        elif condition.is_rlFileBackup(first):
            self.rlFileBackup(pom_list)

        elif condition.is_rlFileRestore(first):
            self.rlFile_Restore(pom_list)

        elif condition.is_rlIsRHEL_or_rlISFedora(first):
            self.IsRHEL_or_Is_Fedora(pom_list)

        elif condition.is_rlmount(first):
            self.rl_mount(pom_list)

        elif condition.is_rlHash_or_rlUnhash(first):
            self.rlHash_or_rlUnhash(pom_list)

        elif condition.is_rlLog(first):
            self.rlLog(pom_list)

        elif condition.is_rlDie(first):
            self.rlDie(pom_list)

        elif condition.is_rlGet_x_Arch(first):
            self.rlGet_command(pom_list)

        elif condition.is_rlGetDistro(first):
            self.rlGet_command(pom_list)

        elif condition.is_rlGetPhase_or_Test_State(first):
            self.rlGet_command(pom_list)

        elif condition.is_rlReport(first):
            self.rlReport(pom_list)

        elif condition.is_rlWatchdog(first):
            self.rlWatchdog(pom_list)

        elif condition.is_rlBundleLogs(first):
            self.rlBundleLogs(pom_list)

        elif condition.is_rlservicexxx(first):
            self.rlServicexxx(pom_list)

        elif condition.is_SEBooleanxxx(first):
            self.SEBooleanxxx(pom_list)

        elif condition.is_rlShowRunningKernel(first):
            self.rlShowRunningKernel(pom_list)

        elif condition.is_get_or_check_makefile_requires(first):
            self.rlGet_or_rlCheck_MakefileRequeries(pom_list)

        elif condition.is_rlCleanup_Apend_or_Prepend(first):
            self.rlCleanup_Apend_or_Prepend(pom_list)

        elif condition.is_rlFileSubmit(first):
            self.rlFileSubmit(pom_list)

        elif condition.is_rlPerfTime_RunsInTime(first):
            self.rlPerfTime_RunsInTime(pom_list)

        elif condition.is_rlPerfTime_AvgFromRuns(first):
            self.rlPerfTime_AvgFromRuns(pom_list)

        elif condition.is_rlShowPackageVersion(first):
            self.rlShowPackageVersion(pom_list)

        elif condition.is_rlJournalPrint(first):
            self.rlJournalPrint(pom_list)

        elif condition.is_rlImport(first):
            self.rlImport(pom_list)

        elif condition.is_rlWaitForxxx(first):
            self.rlWaitForxxx(pom_list, first)

        elif condition.is_rlWaitFor(first):
            self.rlWaitFor(pom_list)

        elif condition.is_VirtualXxxx(first):
            self.rlVirtualX_xxx(pom_list)

        else:
            self.unknown_command(pom_list, pom_statement_line)

        return self.parsed_param_ref

    def find_and_replace_variable(self, statement):
        pass

    def get_cmd_line_params(self, line):
        # This method searches for command line variables in code represented as $1 $2 ...
        regular = re.compile("(.*)(\$(\d+))(.*)")
        match = regular.match(line)
        if match:
            self.parser_ref.set_test_launch(match.group(3))

    def get_environmental_variable(self,line):
        lexer = shlex.shlex(line)
        word = lexer.get_token()
        while(word):
            if word == "$":
                word = lexer.get_token()
                if not self.phase_ref.variables.is_existing_variable(word) and len(word) > self.minimum_variable_size:
                    self.parser_ref.set_environmental_variable_information(word)

            elif word[0:1] == '"':  # shelx doesn't returns whole string so for searching in strings I'm using recursion
                self.get_environmental_variable(word[1:-1])
            word = lexer.get_token()


    def is_variable_assignment(self, statement):
        # searching variables in statement line
        readed = shlex.shlex(statement)
        member = readed.get_token()
        equal_to = readed.get_token()

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

        return

    def rlJournalPrint(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("type", type=str, nargs="?")
        parser_arg.add_argument('--full-journal', dest='full_journal',
                                action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlShowPackageVersion(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlFileSubmit(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-s", type=str, help="sets separator")
        parser_arg.add_argument("path_to_file", type=str)
        parser_arg.add_argument("required_name", type=str, nargs="?")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlBundleLogs(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str)
        parser_arg.add_argument("file", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlDie(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("file", type=str, nargs="*")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlLog(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("logfile", type=str, nargs="?")
        parser_arg.add_argument("priority", type=str, nargs="?")
        parser_arg.add_argument('--prio-label', dest='prio_label',
                                action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlShowRunningKernel(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlGet_or_rlCheck_MakefileRequeries(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlGet_command(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def unknown_command(self, pom_param_list, statement_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref = parser_arg.parse_args(["UNKNOWN"])
        # Trying to find variable assignment in statement line
        self.is_variable_assignment(statement_list)

    def rlWatchdog(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("timeout", type=str)
        parser_arg.add_argument("signal", type=str, nargs='?', default="KILL")
        parser_arg.add_argument("callback", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlReport(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        parser_arg.add_argument("result", type=str)
        parser_arg.add_argument("score", type=str, nargs='?')
        parser_arg.add_argument("log", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlRun(self, pom_param_list):
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
        self.parse_command(self.parsed_param_ref.command) # for getting variables from command
        self.parsed_param_ref = ref

    def rlVirtualX_xxx(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlWaitFor(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('n', type=str, nargs='*')
        parser_arg.add_argument("-t", type=int, help="time")
        parser_arg.add_argument("-s", type=str, help="SIGNAL", default="SIGTERM")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlWaitForxxx(self, pom_param_list, command):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-p", type=str, help="PID")
        parser_arg.add_argument("-t", type=str, help="time")
        parser_arg.add_argument("-d", type=int, help="delay", default=1)

        if conditions_for_commands().is_rlWaitForCmd(command):
            parser_arg.add_argument("command", type=str)
            parser_arg.add_argument("-m", type=str, help="count")
            parser_arg.add_argument("-r", type=str, help="retrval", default="0")

        elif conditions_for_commands().is_rlWaitForFile(command):
            parser_arg.add_argument("path", type=str)

        elif conditions_for_commands().is_rlWaitForSocket(command):
            parser_arg.add_argument("port_path", type=str)
            parser_arg.add_argument('--close', dest='close', action='store_true',
                                    default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlImport(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("LIBRARY", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlPerfTime_RunsInTime(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("time", type=int, nargs='?', default=30)
        parser_arg.add_argument("runs", type=int, nargs='?', default=3)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlPerfTime_AvgFromRuns(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("count", type=int, nargs='?', default=3)
        parser_arg.add_argument("warmup", type=str, nargs='?', default="warmup")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlCleanup_Apend_or_Prepend(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("string", type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def SEBooleanxxx(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("boolean", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlServicexxx(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("service", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlFile_Restore(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlFileBackup(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--clean', dest='clean', action='store_true',
                                default=False)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        parser_arg.add_argument('file', type=str, nargs='+')
        parser_arg.add_argument('status', type=str, nargs='?', default="-")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlHash_or_rlUnhash(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--decode', dest='decode', action='store_true',
                                default=False, help='unhash given string')
        parser_arg.add_argument("--algorithm", type=str,
                                help="given hash algorithm")
        parser_arg.add_argument("STRING", type=str, nargs='?')
        parser_arg.add_argument('--stdin', action='store_true', default=False)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def check_or_assert_mount(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str, nargs='?')
        parser_arg.add_argument('share', type=str, nargs='?')
        parser_arg.add_argument('mountpoint', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rl_mount(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str)
        parser_arg.add_argument('share', type=str)
        parser_arg.add_argument('mountpoint', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert_binary_origin(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('binary', type=str)
        parser_arg.add_argument('package', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rpm_command(self, pom_param_list):
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

    def IsRHEL_or_Is_Fedora(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('type', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert_differ(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file1', type=str)
        parser_arg.add_argument('file2', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert_exits(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file_directory', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert_comparison(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument('value1', type=str)
        parser_arg.add_argument('value2', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert0(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument('value', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def rlPass_or_rlFail(self, pom_param_list):
        parser_arg = argparse.ArgumentParser()
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def assert_grep(self, pom_param_list):
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

    def is_beakerLib_command(self, testing_command, parser_ref):
        return parser_ref.is_beakerLib_command(testing_command)


class documentation_translator:
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
        self.inf_ref = ""

        argname = argparse_data.argname
        condition = conditions_for_commands()

        if condition.is_rlrun_command(argname):
            self.rlRun(argparse_data)

        elif condition.is_Rpm_command(argname):
            self.rpm_command(argparse_data)

        elif condition.is_check_or_assert_mount(argname):
            self.check_or_assert_mount(argparse_data)

        elif condition.is_assert_command(argname):

            if condition.is_assert_grep(argname):
                self.assert_grep(argparse_data)

            elif condition.is_rlPass_or_rlFail(argname):
                self.rlPass_or_rlFail(argparse_data)

            elif condition.is_assert0(argname):
                self.assert0(argparse_data)

            elif condition.is_assert_comparasion(argname):
                self.assert_comparison(argparse_data)

            elif condition.is_assert_exists(argname):
                self.assert_exits(argparse_data)

            elif condition.is_assert_differ(argname):
                self.assert_differ(argparse_data)

            elif condition.is_assert_binary_origin(argname):
                self.assert_binary_origin(argparse_data)

        elif condition.is_rlFileBackup(argname):
            self.rlFileBackup(argparse_data)

        elif condition.is_rlFileRestore(argname):
            self.rlFile_Restore(argparse_data)

        elif condition.is_rlIsRHEL_or_rlISFedora(argname):
            self.IsRHEL_or_Is_Fedora(argparse_data)

        elif condition.is_rlmount(argname):
            self.rl_mount(argparse_data)

        elif condition.is_rlHash_or_rlUnhash(argname):
            self.rlHash_or_rlUnhash(argparse_data)

        elif condition.is_rlLog(argname):
            self.rlLog(argparse_data)

        elif condition.is_rlDie(argname):
            self.rlDie(argparse_data)

        elif condition.is_rlGet_x_Arch(argname):
            self.rlGet_command(argparse_data)

        elif condition.is_rlGetDistro(argname):
            self.rlGet_command(argparse_data)

        elif condition.is_rlGetPhase_or_Test_State(argname):
            self.rlGet_command(argparse_data)

        elif condition.is_rlReport(argname):
            self.rlReport(argparse_data)

        elif condition.is_rlWatchdog(argname):
            self.rlWatchdog(argparse_data)

        elif condition.is_rlBundleLogs(argname):
            self.rlBundleLogs(argparse_data)

        elif condition.is_rlservicexxx(argname):
            self.rlServicexxx(argparse_data)

        elif condition.is_SEBooleanxxx(argname):
            self.SEBooleanxxx(argparse_data)

        elif condition.is_rlShowRunningKernel(argname):
            self.rlShowRunningKernel()

        elif condition.is_get_or_check_makefile_requires(argname):
            self.rlGet_or_rlCheck_MakefileRequeries(argparse_data)

        elif condition.is_rlCleanup_Apend_or_Prepend(argname):
            self.rlCleanup_Apend_or_Prepend(argparse_data)

        elif condition.is_rlFileSubmit(argname):
            self.rlFileSubmit(argparse_data)

        elif condition.is_rlPerfTime_RunsInTime(argname):
            self.rlPerfTime_RunsInTime(argparse_data)

        elif condition.is_rlPerfTime_AvgFromRuns(argname):
            self.rlPerfTime_AvgFromRuns(argparse_data)

        elif condition.is_rlShowPackageVersion(argname):
            self.rlShowPackageVersion(argparse_data)

        elif condition.is_rlJournalPrint(argname):
            self.rlJournalPrint(argparse_data)

        elif condition.is_rlImport(argname):
            self.rlImport(argparse_data)

        elif condition.is_rlWaitFor(argname):
            self.rlWaitFor(argparse_data)

        elif condition.is_rlWaitForCmd(argname):
            self.rlWaitForCmd(argparse_data)

        elif condition.is_rlWaitForFile(argname):
            self.rlWaitForFile(argparse_data)

        elif condition.is_rlWaitForSocket(argname):
            self.rlWaitForSocket(argparse_data)

        elif condition.is_VirtualXxxx(argname):
            self.rlVirtualX_xxx(argparse_data)

        return self.inf_ref

    def rlJournalPrint(self, argparse_data):
        importance = self.low
        subject = []
        paramOption = []
        if argparse_data.argname == "rlJournalPrint":
            if len(argparse_data.type):
                subject.append(argparse_data.type)
            else:
                subject.append("xml")
        else:
            subject.append("text")
            if argparse_data.full_journal:
                paramOption.append("additional information")

        topic_obj = topic("JOURNAL", subject)
        action = ["print"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlShowPackageVersion(self, argparse_data):
        importance = self.lowMedium
        action = ["print"]
        subject = argparse_data.package
        topic_obj = topic("PACKAGE", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlFileSubmit(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.path_to_file]
        if not len(argparse_data.s) and not len(argparse_data.required_name):
            subject.append('-')

        elif len(argparse_data.s) and not len(argparse_data.required_name):
            subject.append(argparse_data.s)

        elif len(argparse_data.s) and len(argparse_data.required_name):
            subject.append(argparse_data.s)
            subject.append(argparse_data.required_name)
        topic_obj = topic("FILE", subject)
        action = ["resolve"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlBundleLogs(self, argparse_data):
        importance = self.low
        subject = argparse_data.file
        topic_obj = topic("FILE", subject)
        action = ["create"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlDie(self, argparse_data):
        importance = self.low
        subject = [argparse_data.message]
        subject += argparse_data.file
        topic_obj = topic("MESSAGE", subject)
        action = ["create"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlLog(self, argparse_data):
        importance = self.low
        subject = [argparse_data.message]
        topic_obj = topic("MESSAGE", subject)
        action = ["create"]
        paramOption = []
        if argparse_data.logfile:
            paramOption.append(argparse_data.logfile)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlShowRunningKernel(self):
        importance = self.lowMedium
        topic_obj = topic("MESSAGE", ["kernel"])
        action = ["create"]
        self.inf_ref = documentation_information("rlShowRunningKernel", topic_obj, action, importance)

    def rlGet_or_rlCheck_MakefileRequeries(self, argparse_data):

        importance = self.lowMedium
        topic_obj = topic("FILE", ["makefile"])
        action = []
        if argparse_data.argname == "rlGetMakefileRequires":
            action.append("print")
        else:
            action.append("check")
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlGet_command(self, argparse_data):
        importance = self.medium
        subject = []
        action = []
        if conditions_for_commands().is_rlGetPhase_or_Test_State(argparse_data.argname):
            if argparse_data.argname == "rlGetTestState":
                subject.append("test")
            else:
                subject.append("phase")
        elif conditions_for_commands().is_rlGetDistro(argparse_data.argname):
            if argparse_data.argname == "rlGetDistroRelease":
                subject.append("release")
            else:
                subject.append("variant")
        elif argparse_data.argname == "rlGetPrimaryArch":
            subject.append("primary")
        else:
            subject.append("secondary")
        topic_obj = topic("JOURNAL", subject)
        action.append("return")
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlWatchdog(self, argparse_data):
        importance = self.highest
        subject = ["watchdog", argparse_data.command, argparse_data.timeout]
        paramOption = []
        if argparse_data.signal:
            paramOption.append(argparse_data.signal)
        topic_obj = topic("COMMAND", subject)
        action = ["run"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlReport(self, argparse_data):
        importance = self.high
        subject = [argparse_data.name, argparse_data.result]
        topic_obj = topic("JOURNAL", subject)
        action = ["report"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlRun(self, argparse_data):
        importance = self.highest
        subject = [argparse_data.command, argparse_data.status]
        possibleBeakerLibCommand = self.Get_argparse_of_command(argparse_data.command)

        if possibleBeakerLibCommand.argname == "UNKNOWN":
            paramOption = []
            if argparse_data.l:
                paramOption.append("l")
            elif argparse_data.c:
                paramOption.append("c")
            elif argparse_data.t and argparse_data.s:
                paramOption.append("s")
                paramOption.append("t")
            elif argparse_data.t:
                paramOption.append("t")
            elif argparse_data.s:
                paramOption.append("s")
            topic_obj = topic("COMMAND", subject)
            action = ["run"]
            self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

        else:
            beakerLibInformationUnit = self.translate_data(possibleBeakerLibCommand)
            beakerLibInformationUnit.set_status(argparse_data.status)

    def Get_argparse_of_command(self, command):
        pomPhase = phase_container("Helpful phase")
        return statement_automata(self.parser_ref,pomPhase).parse_command(command)

    def rlVirtualX_xxx(self, argparse_data):
        importance = self.medium
        subject = [argparse_data.name]
        action = []
        if argparse_data.argname == "rlVirtualXStop":
            action.append("kill")
        elif argparse_data.argname == "rlVirtualXStart":
            action.append("run")
        else:
            action.append("return")
        topic_obj = topic("SERVER", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlWaitFor(self, argparse_data):
        importance = self.lowMedium
        subject = []
        if len(argparse_data.n):
            subject = argparse_data.n
        topic_obj = topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlWaitForSocket(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.port_path]
        paramOption = []
        if argparse_data.close:
            paramOption.append("close")
        elif argparse_data.p:
            paramOption.append("p")

        topic_obj = topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlWaitForFile(self, argparse_data):
        importance = self.lowMedium
        subject = ["file", argparse_data.path]
        paramOption = []
        if argparse_data.p:
            paramOption.append(argparse_data.p)
        topic_obj = topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlWaitForCmd(self, argparse_data):
        importance = self.lowMedium
        subject = ["cmd", argparse_data.command]
        paramOption = ["",""]
        if argparse_data.r:
            paramOption[0] = argparse_data.r

        if argparse_data.p:
            paramOption[1] = argparse_data.p

        topic_obj = topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlImport(self, argparse_data):
        importance = self.medium
        subject = argparse_data.LIBRARY
        topic_obj = topic("PACKAGE", subject)
        action = ["import"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlPerfTime_RunsInTime(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.command]
        paramOption = [argparse_data.time]
        topic_obj = topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlPerfTime_AvgFromRuns(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.command]
        topic_obj = topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlCleanup_Apend_or_Prepend(self, argparse_data):
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlCleanupAppend":
            subject.append("append")
        subject.append(argparse_data.string)
        topic_obj = topic("STRING", subject)
        action = ["create"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def SEBooleanxxx(self, argparse_data):
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlSEBooleanOn":
            subject.append("on")
        elif argparse_data.argname == "rlSEBooleanOff":
            subject.append("off")
        subject += argparse_data.boolean
        topic_obj = topic("BOOLEAN", subject)
        action = ["set"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlServicexxx(self, argparse_data):
        importance = self.medium
        subject = argparse_data.service
        action = []
        if argparse_data.argname == "rlServiceStart":
            action.append("run")
        elif argparse_data.argname == "rlServiceStop":
            action.append("kill")
        else:
            action.append("restore")
        topic_obj = topic("SERVICE", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlFile_Restore(self, argparse_data):
        importance = self.high
        paramOption = []
        if argparse_data.namespace:
            paramOption.append(argparse_data.namespace)
        topic_obj = topic("FILE", [""])
        action = ["restore"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlFileBackup(self, argparse_data):
        importance = self.medium
        paramOption = []
        subject = argparse_data.file
        if argparse_data.namespace:
            paramOption.append(argparse_data.namespace)

        topic_obj = topic("FILE", subject)
        action = ["backup"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def rlHash_or_rlUnhash(self, argparse_data):
        importance = self.medium
        paramOption = []
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
            paramOption.append(argparse_data.algorithm)
        topic_obj = topic("STRING", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def check_or_assert_mount(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.mountpoint]
        action = []
        if argparse_data.argname == "rlCheckMount":
            action.append("check")
        else:
            action.append("exists")
        if argparse_data.server and argparse_data.mountpoint:
            subject.append(argparse_data.server)
        topic_obj = topic("MOUNTPOINT", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rl_mount(self, argparse_data):
        importance = self.lowMedium
        subject = [argparse_data.mountpoint, argparse_data.server]
        topic_obj = topic("MOUNTPOINT", subject)
        action = ["create"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def assert_binary_origin(self, argparse_data):
        importance = self.medium
        subject = [argparse_data.binary]
        subject += argparse_data.package
        topic_obj = topic("PACKAGE", subject)
        action = ["owned by"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rpm_command(self, argparse_data):
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
        topic_obj = topic("PACKAGE", subject)
        paramOption = []
        if argparse_data.version or argparse_data.release or \
                argparse_data.arch:
            if argparse_data.version:
                paramOption.append(argparse_data.version)

            if argparse_data.release:
                paramOption.append(argparse_data.release)

            if argparse_data.arch:
                paramOption.append(argparse_data.arch)

        # TODO test correction of generation of information unit for this commands
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))

    def IsRHEL_or_Is_Fedora(self, argparse_data):
        importance = self.medium
        action = []
        subject = []
        if argparse_data.argname == "rlIsRHEL":
            action.append("RHEL")
        else:
            action.append("Fedora")
        if len(argparse_data.type):
            subject = argparse_data.type
        topic_obj = topic("SYSTEM", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def assert_differ(self, argparse_data):
        importance = self.high
        action = []
        if argparse_data.argname == "rlAssertDiffer":
            action.append("differ")
        else:
            action.append("not differ")
        subject = [argparse_data.file1, argparse_data.file2]
        topic_obj = topic("FILE", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def assert_exits(self, argparse_data):
        importance = self.high
        subject = [argparse_data.file_directory]
        topic_obj = topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertExists":
            action.append("exists")
        else:
            action.append("not exists")
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def assert_comparison(self, argparse_data):
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
        topic_obj = topic("VALUE", subject)
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def assert0(self, argparse_data):
        importance = self.high
        topic_obj = topic("VALUE", [argparse_data.value])
        action = ["check"]
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance)

    def rlPass_or_rlFail(self, argparse_data):
        pass

    def assert_grep(self, argparse_data):
        importance = self.high
        name = argparse_data.argname
        subject = [argparse_data.file, argparse_data.pattern]
        topic_obj = topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertGrep":
            action.append("contain")
        else:
            action.append("not contain")
        paramOption = []
        if argparse_data.text_in:
            paramOption.append("text_in")
        elif argparse_data.moin_in:
            paramOption.append("moin_in")
        elif argparse_data.out_in:
            paramOption.append("out_in")
        self.inf_ref = documentation_information(argparse_data.argname, topic_obj, action, importance, option(paramOption))


class topic(object):
    topic = ""

    subject = []

    def __init__(self, Topic, subject):
        self.topic = Topic
        self.subject = subject

    def get_topic(self):
        return self.topic

    def get_subject(self):
        return self.subject


class option(object):
    option = []

    status = []

    def __init__(self, Option = None, Status = "-"):
        if Option is None:
            self.option = []
        else:
            self.option = Option
        self.status = Status

    def get_option(self):
        return self.option

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status


class documentation_information(object):
    command_name = ""

    topic = ""

    options = option

    action = []

    importance = ""

    def __init__(self,cmd_name, Topic, action, importance, options=None ):
        if options is None:
            self.options = option()
        else:
            self.options = options
        self.command_name = cmd_name
        self.topic = Topic
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


class information_unit(object):
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
        line_size = 60  # char per line
        weigh = (len(self.information)//line_size)
        mod_weigh = (len(self.information)%line_size)
        if weigh == 0:
            return 1
        elif mod_weigh >= 20:  # tolerance
            return weigh + 1
        else:
            return weigh

    def get_information_value(self):
        return self.information_obj.get_importance()

    def is_list_empty(self, tested_list):
        return len(tested_list) == 0

    def check_status_and_add_information(self, status):
        if not status == "-":
            if status == "1":
                self.information += " and must finished unsuccessfully"
            elif not status == "0":
                self.information += " and must finished with return code matching: " + status

    def set_correct_singulars_or_plurals(self, word, number_of_subject, ending="s", verb=False):
        pom_word = word
        if number_of_subject >= 2:
            if pom_word[-1] == "y" and ending == "ies":
                pom_word = word[:-1] + ending
            else:
                pom_word += ending

            if  verb:
                pom_word += " are"
        elif verb:
            pom_word += " is"

        if not verb:
            pom_word += " "
        return pom_word



class information_FILE_exists(information_unit):
    def set_information(self):
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must exist"
        self.check_status_and_add_information( self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_FILE_not_exists(information_unit):
    def set_information(self):
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must not exist"
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_FILE_contain(information_unit):
    def set_information(self):
        self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                           + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                             + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                             + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_FILE_not_contain(information_unit):
    def set_information(self):
        self.information = "File " + self.information_obj.get_topic_subject()[0] \
                           + " must not contain pattern " + self.information_obj.get_topic_subject()[1]
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                             + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                             + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_JOURNAL_print(information_unit):
    def set_information(self):
        self.information = "Prints the content of the journal in pretty " + self.information_obj.get_topic_subject()[0]
        self.information += " format"
        if len(self.information_obj.get_option()):
            self.information += " with additional information"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_PACKAGE_print(information_unit):
    def set_information(self):
        self.information = "Shows information about "
        self.information += self.connect_multiple_facts(self.information_obj.get_topic_subject(), 4)
        self.information += " version"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_resolve(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Resolves absolute path " + subjects[0]
        if len(subjects) == 3:
            self.information += ", replaces / for " + subjects[1]
            self.information += " and rename file to " + subjects[2]
        else:
            self.information += " and replaces / for " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_create(information_unit):
    def set_information(self):
        subject = self.information_obj.get_topic_subject()
        self.information = "Creates a tarball of " + self.set_correct_singulars_or_plurals("file",len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.information += " and attached it/them to test result"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_MESSAGE_create(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if subjects[0] == "kernel":  # rlShowRunningKernel
            self.information = "Log a message with version of the currently running kernel"
        else:  # rlDie & rlLog
            self.information = "Message \"" + subjects[0]
            if len(subjects) > 1:
                self.information += "\" is created in to log and "
                self.information += self.set_correct_singulars_or_plurals("file",len(subjects[1:]))
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


class information_FILE_print(information_unit):
    def set_information(self):
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Prints comma separated list of requirements defined in Makefile"
        else:
            self.information = "Prints file content"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_check(information_unit):
    def set_information(self):
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Checks requirements in Makefile and returns number of compliance"
        else:
            self.information = "Checks file " + self.information_obj.get_topic_subject()[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_JOURNAL_return(information_unit):
    def set_information(self):
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


class information_COMMAND_run(information_unit):
    def set_information(self):
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


class information_SERVER_run(information_unit):
    def set_information(self):
        self.information = "Starts virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " server on a first free display"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_SERVER_kill(information_unit):
    def set_information(self):
        self.information = "Kills virtual X " + self.information_obj.get_topic_subject()[0] + " server"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_SERVER_return(information_unit):
    def set_information(self):
        self.information = "Shows number of displays where virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " is running"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_JOURNAL_report(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Reports test \"" + subjects[0]
        self.information += "\" with result " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_COMMAND_wait(information_unit):
    def set_information(self):
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


class information_FILE_wait(information_unit):
    def set_information(self):
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


class information_PACKAGE_import(information_unit):
    def set_information(self):
        subject = self.information_obj.get_topic_subject()
        self.information = "Imports code provided by "
        self.information += self.connect_multiple_facts(subject, 2)
        self.information += self.set_correct_singulars_or_plurals(" library",len(subject), "ies")
        self.information += "  library(ies) into the test namespace"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_COMMAND_measures(information_unit):
    def set_information(self):
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


class information_STRING_create(information_unit):
    def set_information(self):
        if self.information_obj.get_topic_subject()[0] == "append":
            self.information = "Appends string: " + self.information_obj.get_topic_subject()[1]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        else:
            self.information = "Prepends string: " + self.information_obj.get_topic_subject()[0]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_BOOLEAN_set(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "on":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean",len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to true"
        elif subjects[0] == "off":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean",len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to false"
        else:
            self.information = "Restore "
            self.information += self.set_correct_singulars_or_plurals("boolean",len(subjects))
            self.information += self.connect_multiple_facts(subjects, 3)
            self.information += " into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_SERVICE_run(information_unit):
    def set_information(self):
        subject = self.information_obj.get_topic_subject()
        self.information = "Starts "
        self.information += self.set_correct_singulars_or_plurals("service",len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""
        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service",len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(subject, 3) + \
                                " must be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service",len(subject))
            self.information = self.information[:-1] +  ": " + self.connect_multiple_facts(subject, 3) + \
                                " must not be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_SERVICE_kill(information_unit):
    def set_information(self):
        subject = self.information_obj.get_topic_subject()
        self.information = "Kills "
        self.information += self.set_correct_singulars_or_plurals("service",len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""
        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service",len(subject))
            self.information= self.information[:-1] +  ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                                " must not be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service",len(subject))
            self.information = self.information[:-1] +  ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                                " must be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class information_SERVICE_restore(information_unit):
    def set_information(self):
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("Service",len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        if len(subject) > 1:
            self.information += " are restored into original state"
        else:
            self.information += " is restored into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_restore(information_unit):
    def set_information(self):
        option = self.information_obj.get_option()
        if not self.is_list_empty(option):
            self.information = "Restores backed up file with namespace: "
            self.information += option[0]
            self.information += "to original state"
        else:
            self.information = "Restores backed up files to their "
            self.information += "original location"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_backup(information_unit):
    def set_information(self):
        option = self.information_obj.get_option()
        status = self.information_obj.get_status()
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("File",len(subject))
        self.information += "or " + self.set_correct_singulars_or_plurals("directory",len(subject), "ies")
        self.information += self.connect_multiple_facts(subject, 2)
        if len(subject) >= 2:
            self.information += " are backed up"
        else:
            self.information += " is backed up"
        if not self.is_list_empty(option):
            self.information += "with namespace " + option[0]
        self.check_status_and_add_information(status)


class information_STRING_hash(information_unit):
    def set_information(self):
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


class information_STRING_unhash(information_unit):
    def set_information(self):
        option = self.information_obj.get_option()
        subjects = self.information_obj.get_topic_subject()
        self.information = "Unhashes string "
        if subjects[0] == True:
            self.information += "from input"
        else:
            self.information += subjects[0]

        if not self.is_list_empty(option):
            self.information += " with hashing algorithm "
            self.information += option[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_MOUNTPOINT_exists(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Directory "
        self.information += subjects[0]
        self.information += "must be a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_MOUNTPOINT_create(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Creates mount point " + subjects[0]
        if subjects[1]:
            self.information += " and mount NFS " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_MOUNTPOINT_check(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Checks if directory "
        self.information += subjects[0]
        self.information += "is a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_PACKAGE_owned_by(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Binary " + subjects[0] + "must be"
        self.information += " owned by "
        self.information += self.set_correct_singulars_or_plurals("package",len(subjects[1:]))
        self.information += self.connect_multiple_facts(subjects[1:], 4)
        self.check_status_and_add_information(self.information_obj.get_status())


class information_SYSTEM_is_RHEL(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " RHEL "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class information_SYSTEM_is_Fedora(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " Fedora "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_differ(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be different"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_FILE_not_differ(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be identical"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_VALUE_equal(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_VALUE_not_equal(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must not be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_VALUE_greater(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater than value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_VALUE_greater_or_equal(information_unit):
    def set_information(self):
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater or equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class information_VALUE_check(information_unit):
    def set_information(self):
        self.information = "Value " + self.information_obj.get_topic_subject()[0] + " must be 0"
        self.check_status_and_add_information(self.information_obj.get_status())


class information_PACKAGE_check(information_unit):
    def set_information(self):
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


class information_PACKAGE_exists(information_unit):
    def set_information(self):
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


class information_PACKAGE_not_exists(information_unit):
    def set_information(self):
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


class get_information(object):
    array = [
        # topic: FILE(DIRECTORY),           STRING                   PACKAGE          JOURNAL,PHASE,TEST       MESSAGE         COMMAND                SERVER              BOOLEAN              SERVICE            MOUNTPOINT              SYSTEM                 VALUE  # ACTIONS
        [information_FILE_exists,           0,           information_PACKAGE_exists,              0,              0,              0,                     0,                  0,                  0,  information_MOUNTPOINT_exists,         0,                     0],  # exists
        [information_FILE_not_exists,       0,           information_PACKAGE_not_exists,          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not exists
        [information_FILE_contain,          0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # contain
        [information_FILE_not_contain,      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not contain
        [information_FILE_print,            0,           information_PACKAGE_print,   information_JOURNAL_print,  0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # print(show)
        [information_FILE_resolve,          0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # resolve
        [information_FILE_create, information_STRING_create,        0,                            0, information_MESSAGE_create,  0,                     0,                  0,                  0,  information_MOUNTPOINT_create,         0,                     0],  # create
        [information_FILE_check,            0,           information_PACKAGE_check,               0,              0,              0,                     0,                  0,                  0,  information_MOUNTPOINT_check,          0,         information_VALUE_check],  # check
        [           0,                      0,                      0,                information_JOURNAL_return, 0,              0,         information_SERVER_return,      0,                  0,                   0,                    0,                     0],  # return
        [           0,                      0,                      0,                            0,              0,  information_COMMAND_run, information_SERVER_run,       0,       information_SERVICE_run,        0,                    0,                     0],  # run
        [           0,                      0,                      0,                information_JOURNAL_report, 0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # report
        [           0,                      0,                      0,                            0,              0,              0,          information_SERVER_kill,       0,       information_SERVICE_kill,       0,                    0,                     0],  # kill
        [information_FILE_wait,             0,                      0,                            0,              0,  information_COMMAND_wait,          0,                  0,                  0,                   0,                    0,                     0],  # wait
        [           0,                      0,           information_PACKAGE_import,              0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # import
        [           0,                      0,                      0,                            0,              0,  information_COMMAND_measures,      0,                  0,                  0,                   0,                    0,                     0],  # measures
        [           0,                      0,                      0,                            0,              0,              0,                     0,     information_BOOLEAN_set,         0,                   0,                    0,                     0],  # set
        [information_FILE_restore,          0,                      0,                            0,              0,              0,                     0,                  0,      information_SERVICE_restore,     0,                    0,                     0],  # restore
        [information_FILE_backup,           0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # backup
        [           0,          information_STRING_hash,            0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # hash
        [           0,          information_STRING_unhash,          0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # unhash
        [           0,                      0,           information_PACKAGE_owned_by,            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # owned by
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,    information_SYSTEM_is_RHEL,            0],  # is RHEL
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,   information_SYSTEM_is_Fedora,           0],  # is Fedora
        [information_FILE_differ,           0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # differ
        [information_FILE_not_differ,       0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not differ
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,         information_VALUE_equal],  # equal
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,       information_VALUE_not_equal],  # not equal
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,        information_VALUE_greater],  # greater
        [           0,                      0,                      0,                            0,              0,              0,                     0,                  0,                  0,                   0,                    0,   information_VALUE_greater_or_equal],  # greater or equal
    ]

    def get_information_from_facts(self, information_obj):
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
        elif self.is_action_is_RHEL(action):
            return 21
        elif self.is_action_is_Fedora(action):
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
        if self.is_topic_FILE(topic):
            return 0
        elif self.is_topic_STRING(topic):
            return 1
        elif self.is_topic_PACKAGE(topic):
            return 2
        elif self.is_topic_JOURNAL(topic):
            return 3
        elif self.is_topic_MESSAGE(topic):
            return 4
        elif self.is_topic_COMMAND(topic):
            return 5
        elif self.is_topic_SERVER(topic):
            return 6
        elif self.is_topic_BOOLEAN(topic):
            return 7
        elif self.is_topic_SERVICE(topic):
            return 8
        elif self.is_topic_MOUNTPOINT(topic):
            return 9
        elif self.is_topic_SYSTEM(topic):
            return 10
        elif self.is_topic_VALUE(topic):
            return 11

    def is_topic_FILE(self, topic):
        return topic == "FILE"

    def is_topic_STRING(self, topic):
        return topic == "STRING"

    def is_topic_PACKAGE(self, topic):
        return topic == "PACKAGE"

    def is_topic_JOURNAL(self, topic):
        return topic == "JOURNAL"

    def is_topic_MESSAGE(self, topic):
        return topic == "MESSAGE"

    def is_topic_COMMAND(self, topic):
        return topic == "COMMAND"

    def is_topic_SERVER(self, topic):
        return topic == "SERVER"

    def is_topic_BOOLEAN(self, topic):
        return topic == "BOOLEAN"

    def is_topic_SERVICE(self, topic):
        return topic == "SERVICE"

    def is_topic_MOUNTPOINT(self, topic):
        return topic == "MOUNTPOINT"

    def is_topic_SYSTEM(self, topic):
        return topic == "SYSTEM"

    def is_topic_VALUE(self, topic):
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

    def is_action_is_RHEL(self, action):
        return action == "RHEL"

    def is_action_is_Fedora(self, action):
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


class conditions_for_commands:
    """ Class consists of conditions for testing commands used in
    parser_automata and documentation translator """

    def is_rlWatchdog(self, command):
        return command == "rlWatchdog"

    def is_rlReport(self, command):
        return command == "rlReport"

    def is_VirtualXxxx(self, command):
        pom_list = ["rlVirtualXStop", "rlVirtualXStart", "rlVirtualXGetDisplay"]
        return command in pom_list

    def is_rlWaitFor(self, command):
        return command == "rlWaitFor"

    def is_rlWaitForSocket(self, command):
        return command == "rlWaitForSocket"

    def is_rlWaitForFile(self, command):
        return command == "rlWaitForFile"

    def is_rlWaitForCmd(self, command):
        return command == "rlWaitForCmd"

    def is_rlWaitForxxx(self, command):
        pom_list = ["rlWaitForCmd", "rlWaitForFile", "rlWaitForSocket"]
        return command in pom_list

    def is_rlImport(self, command):
        return command == "rlImport"

    def is_rlPerfTime_RunsInTime(self, command):
        return command == "rlPerfTime_RunsInTime"

    def is_rlPerfTime_AvgFromRuns(self, command):
        return command == "rlPerfTime_AvgFromRuns"

    def is_rlCleanup_Apend_or_Prepend(self, command):
        return command == "rlCleanupAppend" or command == "rlCleanupPrepend"

    def is_SEBooleanxxx(self, command):
        pom_list = ["rlSEBooleanOn", "rlSEBooleanOff", "rlSEBooleanRestore"]
        return command in pom_list

    def is_rlservicexxx(self, command):
        pom_list = ["rlServiceStart", "rlServiceStop", "rlServiceRestore"]
        return command in pom_list

    def is_rlFileBackup(self, command):
        return command == "rlFileBackup"

    def is_rlFileRestore(self, command):
        return command == "rlFileRestore"

    def is_rlHash_or_rlUnhash(self, command):
        return command == "rlHash" or command == "rlUnhash"

    def is_check_or_assert_mount(self, command):
        return command == "rlCheckMount" or command == "rlAssertMount"

    def is_get_or_check_makefile_requires(self, command):
        return command == "rlCheckMakefileRequires" or \
               command == "rlGetMakefileRequires"

    def is_rlmount(self, command):
        return command == "rlMount"

    def is_assert_binary_origin(self, command):
        return command == "rlAssertBinaryOrigin"

    def is_rlIsRHEL_or_rlISFedora(self, command):
        return command == "rlIsRHEL" or command == "rlIsFedora"

    def is_assert_differ(self, command):
        return command == "rlAssertDiffer" or command == "rlAssertNotDiffer"

    def is_assert_exists(self, command):
        return command == "rlAssertExists" or command == "rlAssertNotExists"

    def is_assert_comparasion(self, command):
        pom_list = ["rlAssertEquals", "rlAssertNotEquals", "rlAssertGreater",
                    "rlAssertGreaterOrEqual"]
        return command in pom_list

    def is_rlPass_or_rlFail(self, command):
        return command == "rlPass" or command == "rlFail"

    def is_assert_grep(self, command):
        return command == "rlAssertGrep" or command == "rlAssertNotGrep"

    def is_assert0(self, command):
        return command == "rlAssert0"

    def is_assert_command(self, line):
        return line[0:len("rlAssert")] == "rlAssert"

    def is_Rpm_command(self, command):
        return command[-3:] == "Rpm"

    def is_rlrun_command(self, line):
        return line[0:len("rlRun")] == "rlRun"

    def is_rlJournalPrint(self, command):
        pom_list = ["rlJournalPrint", "rlJournalPrintText"]
        return command in pom_list

    def is_rlGetPhase_or_Test_State(self, command):
        pom_list = ["rlGetPhaseState", "rlGetTestState"]
        return command in pom_list

    def is_rlLog(self, command):
        pom_list = ["rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo",
                    "rlLogDebug", "rlLog"]
        return command in pom_list

    def is_rlLogMetric(self, command):
        pom_list = ["rlLogMetricLow", "rlLogMetricHigh"]
        return command in pom_list

    def is_rlDie(self, command):
        return command[0:len("rlDie")] == "rlDie"

    def is_rlBundleLogs(self, command):
        return command[0:len("rlBundleLogs")] == "rlBundleLogs"

    def is_rlFileSubmit(self, command):
        return command[0:len("rlFileSubmit")] == "rlFileSubmit"

    def is_rlShowPackageVersion(self, command):
        return command[0:len("rlShowPackageVersion")] == "rlShowPackageVersion"

    def is_rlGet_x_Arch(self, command):
        pom_list = ["rlGetArch", "rlGetPrimaryArch", "rlGetSecondaryArch"]
        return command in pom_list

    def is_rlGetDistro(self, command):
        pom_list = ["rlGetDistroRelease", "rlGetDistroVariant"]
        return command in pom_list

    def is_rlShowRunningKernel(self, command):
        return command[0:len("rlShowRunningKernel")] == "rlShowRunningKernel"


#  ***************** MAIN ******************
def set_cmd_arguments():
    pom_parser = argparse.ArgumentParser(description= \
                                     'Parse arguments in cmd line for generator')
    pom_parser.add_argument('files', metavar='file', type=str, nargs='+',
                    help='script file')
    pom_parser.add_argument('-l', '--log', dest='log_in', action='store_true',
                   default=False, help='Show log data if they are possible')
    pom_parser.add_argument('-s', '--size', type=int, help="Size of output documentation in lines, default is 32 lines(A4) per documentation", default=32)
    parser_arg = pom_parser.parse_args()
    return parser_arg


def run_doc_generator(parser_arg):
    for file in parser_arg.files:
        pom = Parser(file)
        pom.get_doc_data()
        pom.get_documentation_information()
        pom.generate_documentation()
        pom.print_documentation(parser_arg)

if __name__ == "__main__":
    cmd_args = set_cmd_arguments()
    run_doc_generator(cmd_args)
