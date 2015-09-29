#!/usr/bin/python
# author Jiri Kulda

import argparse
import bkrdoc.analysis


class DocumentationGenerator:

    _parser_ref = ""
    _phases = ""

    def __init__(self):
        self._parser_ref = ""
        self._phases = ""

    def parse_given_file(self, file):
            self._parser_ref = bkrdoc.analysis.Parser(file)
            self._phases = self._parser_ref.get_phases()

    def set_test_launch(self, number_of_variables):
        """
        This method sets up test launch variable, which indicates number of variables.
        :param number_of_variables: number of command line variables in test
        """
        if int(number_of_variables) > int(self._parser_ref.get_test_launch()):
            self._parser_ref.set_test_launch(number_of_variables)

    def set_environmental_variable_information(self, variable):
        """
        This method sets up test environmental variable information command. This command
        contains names of environmental variables in test.
        :param variable: founded environmental variable in test.
        """
        if variable not in self._parser_ref.environmental_variable:
            self._parser_ref.environmental_variable.append(variable)

    def get_doc_data(self):
        """
        Method which is responsible for starting the first analysis of code lines.
        After this method finishes all phase containers will have argparse object
        with parsed data.
        """
        pom_var = bkrdoc.analysis.TestVariables()
        pom_func = []
        for member in self._phases:
            if not self.is_phase_outside(member):
                member.search_data(self, pom_var, pom_func)
                pom_var = bkrdoc.analysis.TestVariables()

            else:
                member.search_data(pom_var, pom_func)
                pom_var = bkrdoc.analysis.TestVariables()

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
        for member in self._phases:
            if not self.is_phase_outside(member):
                member.translate_data(self)

    def generate_documentation(self):
        """
        This method starts transformation from DocumentationInformation objects
        to small object with nature language information
        """
        for member in self._phases:
            if not self.is_phase_outside(member):
                member.generate_documentation()

    def get_test_weigh(self):
        """
        This method calculates number of lines in test.

        :return: number of lines where information will be placed.
        """
        weigh = 0
        for member in self._phases:
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
        for member in self._phases:
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
        for member in self._phases:
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
        inf = "Test launch: " + str(self._parser_ref.get_file_name())
        i = 0
        while int(i) < int(self._parser_ref.get_test_launch()):
            inf += " [VARIABLE]"
            i += 1
        print(inf)

    def print_test_environmental_variables_information(self):
        """
        This method prints environmental variables information
        """
        inf = "Test environmental variables: "
        if len(self._parser_ref.get_environmental_variables()):
            for env in self._parser_ref.get_environmental_variables():
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

        if not cmd_options.print_all and test_weigh > cmd_options.size:
            knapsack_list = self.setup_phases_lists_for_knapsack()
            finished_knapsack = self.solve_knapsack_dp(knapsack_list, cmd_options.size)
            self.set_phases_information_lists(finished_knapsack)

        for member in self._phases:
            if not self.is_phase_outside(member):
                member.print_phase_documentation(cmd_options)
                print("")

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

        for member in self._phases:
            if self.is_phase_outside(member):
                pom_pos = member.get_variable_position(searching_variable)
                if pom_pos >= 0:
                    pom_variable = member.variable_values_list[pom_pos]

            elif member == phase_ref:
                if pom_variable == "":
                    print("UNKNOWN VARIABLE !!!")
                return pom_variable

    def is_phase_outside(self, phase_ref):
        return phase_ref.phase_name == "Outside phase"

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
    pom_parser.add_argument('--all', '--print-all', dest='print_all', action='store_true',
                            default=False, help='Printing all possible data.')
    parser_arg = pom_parser.parse_args()
    return parser_arg


def run_doc_generator(parser_arg):
    """
    This method runs documentation generator
    :param parser_arg: argparse object
    """
    for one_file in parser_arg.files:
        doc_generator = DocumentationGenerator()
        doc_generator.parse_given_file(one_file)
        doc_generator.get_doc_data()
        doc_generator.get_documentation_information()
        doc_generator.generate_documentation()
        doc_generator.print_documentation(parser_arg)

if __name__ == "__main__":
    CMD_args = set_cmd_arguments()
    run_doc_generator(CMD_args)
