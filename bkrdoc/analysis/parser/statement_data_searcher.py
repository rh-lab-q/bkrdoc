#!/usr/bin/python
import argparse
import shlex
import re
from bkrdoc.analysis.parser import conditions_for_commands, custom_argparse
from bkrdoc.analysis.linter import common
from bkrdoc.analysis.linter.catalogue import catalogue


__author__ = 'Jiri_Kulda'


class StatementDataSearcher:
    """
    This class is responsible for parsing data from statement lines. This parsing is done by
    setting argparse modules for every BeakerLib command. The setting we can see under
    big switch.
    """
    parsed_param_ref = ""
    phase_ref = ""

    minimum_variable_size = 4

    def __init__(self):
        self.minimum_variable_size = 4
        self.errors = []
        self.lineno = 0

    def parse_command(self, data_container):
        # Splitting statement using shlex lexicator
        """
        Method contains big switch for division of statement line
        :param data_container: Container with set upped data for argparse
        :return: argparse object with parsed data
        """
        # pom_statement_line = self.phase_ref.variables.replace_variable_in_string(statement_line)
        # self.get_cmd_line_params(pom_statement_line)
        # self.get_environmental_variable(pom_statement_line)
        # pom_list = shlex.split(pom_statement_line, True, posix=True)
        pom_list = data_container.get_argparse_list()

        pom_list = self.erase_empty_list_mmebers(pom_list)
        first = pom_list[0]
        if type(data_container).__name__ == "CommandContainer":
            self.lineno = data_container._command_ast.lineno

        # if self.is_beakerLib_command(first, self.parser_ref):
        condition = conditions_for_commands.ConditionsForCommands()

        if condition.is_rlrun_command(first):
            self.check_err(self.get_rlrun_data, pom_list)

        elif condition.is_rpm_command(first):
            self.check_err(self.get_rpmcommand_data, pom_list)

        elif condition.is_check_or_assert_mount(first):
            self.check_err(self.get_check_or_assert_mount_data, pom_list)

        elif condition.is_assert_command(first):

            if condition.is_assert_grep(first):
                self.check_err(self.get_assert_grep_data, pom_list)

            elif condition.is_assert0(first):
                self.check_err(self.get_assert0_data, pom_list)

            elif condition.is_rlpass_or_rlfail_command(first):
                self.check_err(self.get_rlpass_or_rlfail_data, pom_list)

            elif condition.is_assert_comparison(first):
                self.check_err(self.get_assert_comparison_data, pom_list)

            elif condition.is_assert_exists(first):
                self.check_err(self.get_assert_exists_data, pom_list)

            elif condition.is_assert_differ(first):
                self.check_err(self.get_assert_differ_data, pom_list)

            elif condition.is_assert_binary_origin(first):
                self.check_err(self.get_assertbinaryorigin_data, pom_list)

            else:
                self.unknown_command(pom_list)

        elif condition.is_rlfilebackup_command(first):
            self.check_err(self.get_rlfilebackup_data, pom_list)

        elif condition.is_rlfilerestore_command(first):
            self.check_err(self.get_rlfile_restore_data, pom_list)

        elif condition.is_phase_start(first):
            self.check_err(self.get_rlphasestart_data, pom_list)

        elif condition.is_phase_startxxx(first):
            self.check_err(self.get_rlphasestartxxx_data, pom_list)

        elif condition.is_phase_journal_end(first):
            self.check_err(self.get_rljournal_phase_end_data, pom_list)

        elif condition.is_journal_start(first):
            self.check_err(self.get_rljournalstart_data, pom_list)

        elif condition.is_rlisrhel_or_rlisfedora_command(first):
            self.check_err(self.get_isrhel_or_isfedora_data, pom_list)

        elif condition.is_rlmount(first):
            self.check_err(self.get_rlmount_data, pom_list)

        elif condition.is_rlhash_or_rlunhash_command(first):
            self.check_err(self.get_rlhash_or_rlunhash_data, pom_list)

        elif condition.is_rllog_command(first):
            self.check_err(self.get_rllog_data, pom_list)

        elif condition.is_rldie_command(first):
            self.check_err(self.get_rldie_data, pom_list)

        elif condition.is_rlget_x_arch_command(first):
            self.check_err(self.get_rlget_commands_data, pom_list)

        elif condition.is_rlgetdistro_command(first):
            self.check_err(self.get_rlget_commands_data, pom_list)

        elif condition.is_rlgetphase_or_test_state_command(first):
            self.check_err(self.get_rlget_commands_data, pom_list)

        elif condition.is_rllogmetric_command(first):
            self.check_err(self.get_rllogmetric_data, pom_list)

        elif condition.is_rlreport_command(first):
            self.check_err(self.get_rlreport_data, pom_list)

        elif condition.is_rlwatchdog_command(first):
            self.check_err(self.get_rlwatchdog_data, pom_list)

        elif condition.is_rlbundlelogs_command(first):
            self.check_err(self.get_rlbundlelogs_data, pom_list)

        elif condition.is_rlservicexxx(first):
            self.check_err(self.get_rlservicexxx_data, pom_list)

        elif condition.is_seboolean_on_off_command(first):
            self.check_err(self.get_seboolean_on_off_data, pom_list)

        elif condition.is_sebooleanrestore_command(first):
            self.check_err(self.get_sebooleanrestore_data, pom_list)

        elif condition.is_rlshowrunningkernel_command(first):
            self.check_err(self.get_rlshowrunningkernel_data, pom_list)

        elif condition.is_get_or_check_makefile_requires(first):
            self.check_err(self.get_rlget_or_rlcheck_makefilerequeries_data, pom_list)

        elif condition.is_checkrequirements(first):
            self.check_err(self.get_checkrequirements_data, pom_list)

        elif condition.is_rlcleanup_append_or_prepend_command(first):
            self.check_err(self.get_rlcleanup_append_or_prepend_data, pom_list)

        elif condition.is_rlfilesubmit_command(first):
            self.check_err(self.get_rlfilesubmit_data, pom_list)

        elif condition.is_rlperftime_runsintime_command(first):
            self.check_err(self.get_rlperftime_runsintime_data, pom_list)

        elif condition.is_rlperftime_avgfromruns_command(first):
            self.check_err(self.get_rlperftime_avgfromruns_data, pom_list)

        elif condition.is_rlshowpackageversion_command(first):
            self.check_err(self.get_rlshowpackageversion_data, pom_list)

        elif condition.is_rljournalprint_command(first):
            self.check_err(self.get_rljournalprint_data, pom_list)

        elif condition.is_rlimport_command(first):
            self.check_err(self.get_rlimport_data, pom_list)

        elif condition.is_rlwaitforxxx_command(first):
            self.check_err(self.get_rlwaitforxxx_data, pom_list)

        elif condition.is_rlwaitfor_command(first):
            self.check_err(self.get_rlwaitfor_data, pom_list)

        elif condition.is_virtualxxx_command(first):
            self.check_err(self.get_rlvirtualx_xxx_data, pom_list)

        elif condition.is_deprecated_command(first):
            self.get_deprecated_data(pom_list)

        else:
            self.unknown_command(pom_list)

        return self.parsed_param_ref

    def find_and_replace_variable(self, statement):
        pass


    #TODO Commented because of the same searching in nodevisitor
    """def get_cmd_line_params(self, line):

        #This method searches for command line variables in code represented as $1 $2 ...
        #:param line: statement line of code

        regular = re.compile("(.*)(\$(\d+))(.*)")
        match = regular.match(line)
        if match:
            self.generator_ref.set_test_launch(match.group(3))

    def get_environmental_variable(self, line):

        #Searches environmental variables in code line
        #:param line: code line

        lexer = shlex.shlex(line)
        word = lexer.get_token()
        while word:
            if word == "$":
                word = lexer.get_token()
                if not self.phase_ref.variables.is_existing_variable(word) and len(word) > self.minimum_variable_size:
                    self.generator_ref.set_environmental_variable_information(word)

            elif word[0:1] == '"':  # shlex doesn't returns whole string so for searching in strings I'm using recursion
                self.get_environmental_variable(word[1:-1])
            word = lexer.get_token()"""

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
                    self.variables.add_variable(member, match.group(1) + match.group(2))
                    # TODO keywords from not outside phases
                    # self.keywords_list.append(match.group(2))
                else:
                    self.variables.add_variable(member, value)

            member = equal_to
            equal_to = read.get_token()

        return

    def get_rljournalstart_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rljournal_phase_end_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlphasestart_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("type", type=str)
        parser_arg.add_argument("name", type=str, nargs="?")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlphasestartxxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str, nargs="?")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rljournalprint_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        command = pom_param_list[0]
        parser_arg = custom_argparse.ArgumentParser(prog=command)
        parser_arg.add_argument("argname", type=str)
        if command.endswith("Text"):
            parser_arg.add_argument('--full-journal', dest='full_journal',
                                action='store_true', default=False)
        else:
            parser_arg.add_argument("type", type=str, nargs="?", choices=['raw', 'pretty'], default='pretty')
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlshowpackageversion_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlfilesubmit_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-s", type=str, help="sets separator")
        parser_arg.add_argument("path_to_file", type=str)
        parser_arg.add_argument("required_name", type=str, nargs="?")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlbundlelogs_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("package", type=str)
        parser_arg.add_argument("file", type=str, nargs="+")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rldie_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("file", type=str, nargs="*")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rllogmetric_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        parser_arg.add_argument("value", type=float)
        parser_arg.add_argument("tolerance", type=float, nargs="?")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rllog_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("message", type=str)
        parser_arg.add_argument("logfile", type=str, nargs="?")
        command_suffix = pom_param_list[0][len("rllog"):]
        if not command_suffix:
            parser_arg.add_argument("priority", type=str, nargs="?")
            parser_arg.add_argument('--prio-label', dest='prio_label',
                                    action='store_true', default=False)
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown
        if command_suffix:
            self.parsed_param_ref.priority = command_suffix.upper()
            self.parsed_param_ref.prio_label = True

    def get_rlshowrunningkernel_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlget_or_rlcheck_makefilerequeries_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_checkrequirements_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("requirement", type=str, nargs="*")
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlget_commands_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def unknown_command(self, pom_param_list):
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("data", type=str, nargs='?')
        self.parsed_param_ref = parser_arg.parse_args(["UNKNOWN"])

        # Added hack of data adding.
        self.parsed_param_ref.data = pom_param_list

        # Trying to find variable assignment in statement line
        statement_list = ""
        for member in pom_param_list:
            statement_list += " " + member
       #self.is_variable_assignment(statement_list)
       # self.is_function_name_in_statement(statement_list)

    # TODO
    # def is_function_name_in_statement(self, line):
    #    for function in self.phase_ref.get_function_list():
    #        if function.name in line and function.is_function_data_empty():
    #           self.phase_ref.search_data_in_function(function)

    def get_deprecated_data(self, pom_param_list):
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("data", type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlwatchdog_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("timeout", type=float)
        parser_arg.add_argument("signal", type=str, nargs='?', default="KILL")
        parser_arg.add_argument("callback", type=str, nargs='?')
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlreport_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        parser_arg.add_argument("result", type=str)
        parser_arg.add_argument("score", type=str, nargs='?')
        parser_arg.add_argument("log", type=str, nargs='?')
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlrun_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('-t', dest='t', action='store_true', default=False)
        parser_arg.add_argument('-l', dest='l', action='store_true', default=False)
        parser_arg.add_argument('-c', dest='c', action='store_true', default=False)
        parser_arg.add_argument('-s', dest='s', action='store_true', default=False)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("status", type=str, nargs='?', default="0")
        parser_arg.add_argument("comment", type=str, nargs='?')
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown
        ref = self.parsed_param_ref
        # TODO
        # self.parse_command(self.parsed_param_ref.command)  # for getting variables from command
        self.parsed_param_ref = ref

    def get_rlvirtualx_xxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("name", type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlwaitfor_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('n', type=str, nargs='*')
        parser_arg.add_argument("-t", type=int, help="time")
        parser_arg.add_argument("-s", type=str, help="SIGNAL", default="SIGTERM")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlwaitforxxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        :param command: command name
        """
        command = pom_param_list[0]
        parser_arg = custom_argparse.ArgumentParser(prog=command)
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("-p", type=str, help="PID")
        parser_arg.add_argument("-t", type=str, help="time")
        parser_arg.add_argument("-d", type=int, help="delay", default=1)

        if conditions_for_commands.ConditionsForCommands().is_rlwaitforcmd_command(command):
            parser_arg.add_argument("command", type=str)
            parser_arg.add_argument("-m", type=str, help="count")
            parser_arg.add_argument("-r", type=str, help="retrval", default="0")

        elif conditions_for_commands.ConditionsForCommands().is_rlwaitforfile_command(command):
            parser_arg.add_argument("path", type=str)

        elif conditions_for_commands.ConditionsForCommands().is_rlwaitforsocket_command(command):
            parser_arg.add_argument("port_path", type=str)
            parser_arg.add_argument('--close', dest='close', action='store_true',
                                    default=False)
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlimport_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("LIBRARY", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlperftime_runsintime_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("time", type=float, nargs='?', default=30)
        parser_arg.add_argument("runs", type=int, nargs='?', default=3)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlperftime_avgfromruns_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("command", type=str)
        parser_arg.add_argument("count", type=int, nargs='?', default=3)
        parser_arg.add_argument("warmup", type=str, nargs='?', default="warmup")
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlcleanup_append_or_prepend_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("string", type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_seboolean_on_off_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("boolean", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_sebooleanrestore_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("boolean", type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlservicexxx_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("service", type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlfile_restore_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_rlfilebackup_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--clean', dest='clean', action='store_true',
                                default=False)
        parser_arg.add_argument("--namespace", type=str,
                                help="specified namespace to use")
        parser_arg.add_argument('file', type=str, nargs='+')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlhash_or_rlunhash_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('--decode', dest='decode', action='store_true',
                                default=False, help='unhash given string')
        parser_arg.add_argument("--algorithm", type=str,
                                help="given hash algorithm")
        parser_arg.add_argument("STRING", type=str, nargs='?')
        parser_arg.add_argument('--stdin', action='store_true', default=False)
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def get_check_or_assert_mount_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str, nargs='?')
        parser_arg.add_argument('share', type=str, nargs='?')
        parser_arg.add_argument('mountpoint', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlmount_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('server', type=str)
        parser_arg.add_argument('share', type=str)
        parser_arg.add_argument('mountpoint', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assertbinaryorigin_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('binary', type=str)
        parser_arg.add_argument('package', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rpmcommand_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        if len(pom_param_list) == 2 and pom_param_list[1] == "--all":
            parser_arg.add_argument('--all', dest='all', action='store_true',
                                    default=False, help='assert all packages')
            self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
            self.parsed_param_ref.remainder = unknown
        else:
            parser_arg.add_argument('name', type=str)
            parser_arg.add_argument('version', type=str, nargs='?')
            parser_arg.add_argument('release', type=str, nargs='?')
            parser_arg.add_argument('arch', type=str, nargs='?')
            # this line is for information translator
            parser_arg.add_argument('--all', dest='all', action='store_true',
                                    default=False, help='assert all packages')
            self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
            self.parsed_param_ref.remainder = unknown

    def get_isrhel_or_isfedora_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('type', type=str, nargs='*')
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_differ_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file1', type=str)
        parser_arg.add_argument('file2', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_exists_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('file_directory', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_comparison_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)

        type_ = str if pom_param_list[0].endswith('Equals') else int
        parser_arg.add_argument('value1', type=type_)
        parser_arg.add_argument('value2', type=type_)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert0_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument('value', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_rlpass_or_rlfail_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('comment', type=str)
        parser_arg.add_argument("remainder", nargs=argparse.REMAINDER)
        self.parsed_param_ref = parser_arg.parse_args(pom_param_list)

    def get_assert_grep_data(self, pom_param_list):
        """
        Parsing data from statement line using set upped argparse module
        :param pom_param_list: code line
        """
        parser_arg = custom_argparse.ArgumentParser(prog=pom_param_list[0])
        parser_arg.add_argument("argname", type=str)
        parser_arg.add_argument('pattern', type=str)
        parser_arg.add_argument('file', type=str)
        parser_arg.add_argument('-i', '-I', dest='text_in', action='store_true',
                                default=False, help='insensitive matches')
        parser_arg.add_argument('-e', '-E', dest='moin_in', action='store_true',
                                default=False, help='Extended grep')
        parser_arg.add_argument('-p', '-P', dest='out_in', action='store_true',
                                default=False, help='perl regular expression')
        self.parsed_param_ref, unknown = parser_arg.parse_known_args(pom_param_list)
        self.parsed_param_ref.remainder = unknown

    def is_beakerlib_command(self, testing_command, parser_ref):
        return parser_ref.is_beakerlib_command(testing_command)

    def erase_empty_list_mmebers(self, input_list):
        return list(filter(None, input_list))

    def check_err(self, get_data_method, argument_list):
        def add_error(err_class, err_label, msg, lineno):
            id, severity = catalogue[err_class][err_label]
            self.errors.append(common.Error(id, severity, msg, lineno))

        try:
            get_data_method(argument_list)
            if hasattr(self.parsed_param_ref, 'remainder') and self.parsed_param_ref.remainder:
                msg = "{}, too many arguments (unrecognized args: {})".format(self.parsed_param_ref.argname,
                                                                       self.parsed_param_ref.remainder)
                add_error('3000', 'too_many_args', msg, self.lineno)
        except argparse.ArgumentError as exc:
            msg = self.strip_argparse_error_of_usage_info(exc.message, argument_list[0])
            add_error('3000', 'parse_err', msg, self.lineno)


    def get_errors(self):
        return self.errors

    @staticmethod
    def strip_argparse_error_of_usage_info(str, command):
        """Gets rid of '[-h]' for help, 'argname',
         prefixes command name and replaces the last newline with ||"""
        str = str.replace(' [-h]', '').replace(' argname', '')
        if not str.startswith(command):
            str = command + ", " + str
        str = str.rsplit('\n', 1)
        return ' || '.join(str)
