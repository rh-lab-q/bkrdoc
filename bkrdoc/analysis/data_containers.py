#!/usr/bin/python
__author__ = 'Jiri_Kulda'

import shlex
import bkrdoc.analysis
import sys
from bkrdoc.analysis.credibility import DocumentationCredibility
from bkrdoc.analysis.bkrdoc_parser import Parser


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
        self.variables = bkrdoc.analysis.TestVariables()
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
        # TODO below lines should be fixed by new version of bashlex
        # after that uncomment these below lines!!!

        """
        self.variables = variable_copy
        self.func_list = function_copy
        func = False
        for statement in self.statement_list:

            # These three conditions are here because of getting further
            # information from functions.
            if self.is_function(statement):
                func = True
                self.func_list.append(bkrdoc.analysis.TestFunction(statement[len("function")+1:]))

            elif func and not self.is_function_end(statement):
                self.func_list[-1].add_line(statement)

            elif func and self.is_function_end(statement):
                self.func_list[-1].add_line(statement)
                func = False

            else:
            """

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
    """Class for storing information in test phase"""
    phase_name = ""
    statement_list = []
    doc_ref = ""
    variables = ""
    statement_classes = []
    documentation_units = []
    phase_documentation_information = []
    func_list = []
    generator_ref = ""

    def __init__(self, name):
        self.phase_name = name
        self.statement_list = []
        self.doc = []
        self.variables = bkrdoc.analysis.TestVariables()
        self.statement_classes = []
        self.documentation_units = []
        self.phase_documentation_information = []
        self.func_list = []
        self.generator_ref = ""

    def setup_statement(self, line):
        # sys.stderr.write("{0}\n".format(line))
        self.statement_list.append(line)

    def search_data(self, generator_ref, variable_copy, function_copy):
        """
        This method runs data searching in statement lines.
        :param generator_ref: parser object reference
        :param variable_copy: variable copy
        :param function_copy: function copy
        """
        self.func_list = function_copy
        self.variables = variable_copy
        self.generator_ref = generator_ref
        command_translator = bkrdoc.analysis.StatementDataSearcher()

        for statement in self.statement_list:
            try:
                replaced_statement_variables = self.variables.replace_variable_in_string(statement)
                # self.get_cmd_line_params(replaced_statement_variables)
                # self.get_environmental_variable(replaced_statement_variables)
                argparse_data, pom_variables = command_translator.parse_command(replaced_statement_variables)
                self.variables.copy_variables_from_variable_class(pom_variables)
                self.statement_classes.append(argparse_data)
            except ValueError:
                sys.stdout.write("********************************************")
                print("ERROR in line: " + str(statement))
                print(ValueError)
                print("********************************************")
            except SystemExit:
                sys.stdout.write("********************************************")
                print("ERROR in line: " + str(statement))
                print("Can be problem with variables substitutions")
                print("********************************************")

    def search_data_in_function(self, function):
        """
        Searching data in function object
        :param function: function object
        """

        command_translator = bkrdoc.analysis.StatementDataSearcher()
        function.data_list = []
        for statement in function.statement_list:
            try:
                function.add_data(command_translator.parse_command(statement))
            except ValueError:
                sys.stdout.write("********************************************")
                print("ERROR in line: " + str(statement))
                print(ValueError)
                print("********************************************")
            except SystemExit:
                sys.stdout.write("********************************************")
                print("ERROR in line: " + str(statement))
                print("Can be problem with variables substitutions")
                print("********************************************")

    def translate_data(self, parser_ref):
        """
        Translate data from argparse object to DocumentationInformation object
        :param parser_ref: parser reference
        """

        data_translator = bkrdoc.analysis.DocumentationTranslator(parser_ref)
        for data in self.statement_list:
            if data.argname != "UNKNOWN":
                self.documentation_units.append(data_translator.translate_data(data))

    def generate_documentation(self):
        """
        Transforms DocumentationInformation into small classes using GetInformation
        """
        information_translator = bkrdoc.analysis.GetInformation()
        for information in self.documentation_units:
            if information:
                self.phase_documentation_information.append(information_translator.get_information_from_facts(information))

    def print_phase_documentation(self, cmd_options):
        """
        Prints nature language information
        :param cmd_options: possible command line options
        """
        self.print_phase_name_with_documentation_credibility()
        conditions = bkrdoc.analysis.ConditionsForCommands()

        for information in self.phase_documentation_information:
            if cmd_options.log_in or cmd_options.print_all:
                information.print_information()
            elif not conditions.is_rllog_command(information.get_command_name()):
                information.print_information()

    def print_phase_name_with_documentation_credibility(self):
        inf = self.phase_name + " [Unknown commands: " + str(self.get_unknown_commands()) \
                              + ", Total: " + str(self.get_total_commands()) \
                              + ", Documentation credibility: " + self.get_phase_credibility().get_credibility() + "]"
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

    def get_cmd_line_params(self, line):
        """
        This method searches for command line variables in code represented as $1 $2 ...
        :param line: statement line of code
        """
        raise NotImplementedError("Method get_cmd_line_params should not be launched")
        # TODO lines below were commented due upper Exception. Whether it will be all right please uncomment below
        # TODO section
        # regular = re.compile("(.*)(\$(\d+))(.*)")
        # match = regular.match(line)
        # if match:
        #    self.generator_ref.set_test_launch(match.group(3))

    def get_environmental_variable(self, line):
        """
        Searches environmental variables in code line
        :param line: code line
        """
        minimum_variable_size = 4
        lexer = shlex.shlex(line)
        print("????? line {0}".format(line))
        word = lexer.get_token()
        while word:
            if word == "$":
                word = lexer.get_token()
                if not self.variables.is_existing_variable(word) and len(word) > minimum_variable_size:
                    self.generator_ref.set_environmental_variable_information(word)

            elif word[0:1] == '"':  # shlex doesn't returns whole string so for searching in strings I'm using recursion
                self.get_environmental_variable(word[1:-1])
            word = lexer.get_token()

    def get_function_list(self):
        """
        :return: list of functions
        """
        return self.func_list

    def get_phase_credibility(self):
        return DocumentationCredibility(self.get_unknown_commands(), self.get_total_commands())

    def get_total_commands(self):
        phase_length = 0
        for statement in self.statement_list:
            if self.is_simple_container_instance(statement):
                phase_length += statement.container_length()
            else:
                phase_length += 1
        return phase_length

    def get_unknown_commands(self):
        unknown = 0
        for statement in self.statement_list:
            if self.is_simple_container_instance(statement):
                unknown += statement.unknown_commands_num()
            elif statement.argname == "UNKNOWN":
                unknown += 1
        return unknown

    @staticmethod
    def is_simple_container_instance(container):
        pom_containers = ["FunctionContainer", "LoopContainer", "ConditionContainer", "CaseContainer"]
        return type(container).__name__ in pom_containers


class DataContainer(object):
    _argparse_list = []
    _command_substitution_ast_list = [""]

    def set_argparse_list(self, member):
        pass

    def get_argparse_list(self):
        pass

    def set_last_member_in_argparse_list(self, member):
        pass

    def get_last_member_of_argparse_list(self):
        pass

    def get_ast(self):
        pass

    def set_command_substitution_ast(self, ast):
        self._command_substitution_ast_list.append(ast)

    def is_command_substitution_list_empty(self):
        return self._command_substitution_ast_list[-1] is ""

    def get_last_member_of_command_subst_ast_list(self):
        return self._command_substitution_ast_list[-1]

    def set_empty_spot_for_cmd_subst_ast_list(self):
        self._command_substitution_ast_list.append("")


class CommandContainer(DataContainer):
    _command_ast = ""
    _command_substitution_ast_list = [""]
    _substitution_argparse_list = []

    def __init__(self, ast):
        self._command_ast = ast
        self._argparse_list = []
        self._substitution_argparse_list = []
        self._command_substitution_ast_list = [""]

    def set_argparse_list(self, command_member):
        if self.is_command_substitution_list_empty():
            self._argparse_list.append(command_member)
        else:
            self._substitution_argparse_list.append(command_member)

    def get_argparse_list(self):
        return self._argparse_list

    def set_last_member_in_argparse_list(self, member):
        self._argparse_list[-1] = member

    def get_last_member_of_argparse_list(self):
        return self._argparse_list[-1]

    def get_ast(self):
        return self._command_ast


class SimpleContainer(object):
    command_list = []
    statement_list = []
    _variables = ""

    def add_command(self, command):
        self.command_list.append(command)

    def get_last_command(self):
        return self.command_list[-1]

    def get_command_list(self):
        return self.command_list

    def set_member_of_statement_list(self, member):
        self.statement_list.append(member)

    def set_variables(self, variables):
        self._variables = variables

    def get_statement_list(self):
        pom_statement_list = []
        for line in self.statement_list:
            if self.is_container(line):
                pom_statement_list += line.get_statement_list()
            else:
                pom_statement_list.append(line)
        return pom_statement_list

    def is_container(self, data):
        pom_containers = ["FunctionContainer", "LoopContainer", "ConditionContainer", "CaseContainer"]
        return type(data).__name__ in pom_containers

    def search_data(self, parser_ref, nodevisitor):
        data_searcher = bkrdoc.analysis.StatementDataSearcher()
        conditions = bkrdoc.analysis.ConditionsForCommands()
        for command in self.command_list:
            if self.is_container(command):
                command.search_data(parser_ref, nodevisitor)
                self.statement_list.append(command)
            else:
                data_searcher.parse_command(command)
                data = data_searcher.parsed_param_ref
                if conditions.is_rlrun_command(data.argname):
                    data = parser_ref.search_for_beakerlib_command_in_rlrun(nodevisitor, data)
                self.statement_list.append(data)

    def container_length(self):
        pass

    def unknown_commands_num(self):
        pass


class FunctionContainer(SimpleContainer):
    _function_ast = ""
    function_name = ""

    def __init__(self, ast):
        self.command_list = []
        self._function_ast = ast
        self.function_name = ""
        self.statement_list = []
        self._variables = ""

    def set_function_name(self, fname):
        self.function_name = fname

    def get_function_name(self):
        return self.function_name

    def container_length(self):
        # function 1line; { 2nd line and } is a third line
        function_header = 3
        function_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                function_size += statement.container_length()
            else:
                function_size += 1
        return function_size + function_header

    def unknown_commands_num(self):
        # function 1line; { 2nd line and } is a third line
        function_header = 3
        unknown_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                unknown_size += statement.unknown_commands_num()
            elif statement.argname == "UNKNOWN":
                unknown_size += 1
        return unknown_size + function_header


class LoopContainer(SimpleContainer):
    _loop_ast = ""
    argname = "loop"

    def __init__(self, ast, name):
        self.argname = name + " " + self.argname
        self._loop_ast = ast
        self.command_list = []
        self.statement_list = []
        self._variables = ""

    def container_length(self):
        # loop 1line; do 2nd line and do is a third line
        loop_header = 3
        loop_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                loop_size += statement.container_length()
            else:
                loop_size += 1
        return loop_size + loop_header

    def unknown_commands_num(self):
        # loop 1line; do 2nd line and do is a third line
        loop_header = 3
        unknown_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                unknown_size += statement.unknown_commands_num()
            elif statement.argname == "UNKNOWN":
                unknown_size += 1
        return unknown_size + loop_header


class ConditionContainer(SimpleContainer):
    _condition_ast = ""
    argname = "condition"

    def __init__(self, ast):
        self._condition_ast = ast
        self.command_list = []
        self.statement_list = []
        self._variables = ""

    def container_length(self):
        # if 1line then; 2nd line ended with fi
        cond_header = 2
        cond_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                cond_size += statement.container_length()
            else:
                cond_size += 1
        return cond_size + cond_header

    def unknown_commands_num(self):
        # if 1line then; 2nd line ended with fi
        cond_header = 2
        unknown_size = 0
        for statement in self.statement_list:
            if self.is_container(statement):
                unknown_size += statement.unknown_commands_num()
            elif statement.argname == "UNKNOWN":
                unknown_size += 1
        return unknown_size + cond_header


class AssignmentContainer(DataContainer):
    _assign_ast = []
    _command_substitution_ast_list = [""]

    def __init__(self, ast):
        self._assign_ast = ast
        self._command_substitution_ast_list = [""]
        self._argparse_list = []

    def set_argparse_list(self, command_member):
        self._argparse_list.append(command_member)

    def get_argparse_list(self):
        return self._argparse_list

    def set_last_member_in_argparse_list(self, member):
        self._argparse_list[-1] = member

    def get_last_member_of_argparse_list(self):
        return self._argparse_list[-1]

    def get_ast(self):
        return self._assign_ast


class CaseContainer(SimpleContainer):
    _case_ast = ""
    argname = "case"

    def __init__(self, ast):
        self._case_ast = ast
        self.command_list = []
        self.statement_list = []
        self._variables = ""

    def container_length(self):
        case_header = 2
        case_size = 0
        for condition in self.statement_list:
            case_size += condition.container_length()
        return case_size + case_header

    def unknown_commands_num(self):
        # case 1line in; 2nd line ended with esac
        case_header = 2
        unknown_size = 0
        for condition in self.statement_list:
            unknown_size += condition.unknown_commands_num()
        return unknown_size + case_header

    def add_condition(self, condition):
        self.command_list.append(condition)
