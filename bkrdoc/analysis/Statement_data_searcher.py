#!/usr/bin/python
import argparse
import re
import shlex
import bkrdoc.analysis

__author__ = 'Jiri_Kulda'

class StatementDataSearcher:
    """
    This class is responsible for parsing data from statement lines. This parsing is done by
    setting argparse modules for every BeakerLib command. These setting we can see under
    big switch.
    :param generator_ref: parser reference
    :param phase_ref: reference to phase where was StatementDataSearcher instance made.
    """
    parsed_param_ref = ""
    generator_ref = ""
    phase_ref = ""

    minimum_variable_size = 4

    def __init__(self, generator_ref, phase_ref):
        self.generator_ref = generator_ref
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
        condition = bkrdoc.analysis.ConditionsForCommands()

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
            self.generator_ref.set_test_launch(match.group(3))

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
                    self.generator_ref.set_environmental_variable_information(word)

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

        if bkrdoc.analysis.ConditionsForCommands().is_rlwaitforcmd_command(command):
            parser_arg.add_argument("command", type=str)
            parser_arg.add_argument("-m", type=str, help="count")
            parser_arg.add_argument("-r", type=str, help="retrval", default="0")

        elif bkrdoc.analysis.ConditionsForCommands().is_rlwaitforfile_command(command):
            parser_arg.add_argument("path", type=str)

        elif bkrdoc.analysis.ConditionsForCommands().is_rlwaitforsocket_command(command):
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