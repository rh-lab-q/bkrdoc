#!/usr/bin/python
__author__ = 'Jiri_Kulda'


class TestVariables:
    """Class contains variables from BeakerLib test"""
    variable_names_list = []
    variable_values_list = []

    test_launch_variables = 0
    test_environmental_variables_list = []

    keywords = []

    def __init__(self):
        self.variable_names_list = []
        self.variable_values_list = []
        self.test_launch_variables = 0
        self.test_environmental_variables_list = []

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

    def is_variable_in_environmental_list(self, variable):
        return variable in self.test_environmental_variables_list

    def get_variable_value(self, name):
        pos = self.get_variable_position(name)
        return self.variable_values_list[pos]

    def set_environmental_variable(self, variable):
        if not self.is_variable_in_environmental_list(variable):
            self.test_environmental_variables_list.append(variable)

    def set_unknown_variable(self, variable):
        if variable.isdigit() and self.test_launch_variables < int(variable):
            self.test_launch_variables = int(variable)
        elif not variable.isdigit():
            self.set_environmental_variable(variable)

    def get_test_launch(self):
        return self.test_launch_variables

    def get_test_environmental_variables_list(self):
        return self.test_environmental_variables_list

    def get_variable_position(self, name):
        i = 0
        for element in self.variable_names_list:
            if element == name:
                return i
            i += 1
        return -1

    def get_variable_names(self):
        return self.variable_names_list

    def copy_variables_from_variable_class(self, variable_container):
        second_variables_names = variable_container.get_variable_names()
        for sec_name in second_variables_names:
            self.add_variable(sec_name, variable_container.get_variable_value(sec_name))

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

    def replace_variable_in_string_with_specified_variable(self, string, spec_variable):
        original_string = string
        pom_str = string
        if len(self.variable_names_list) and self.is_existing_variable(spec_variable):
            pom_str = pom_str.replace("$" + spec_variable, self.get_variable_value(spec_variable))
            # Below while solves replacing variables in replaced variable value
            i = 0
            while pom_str is not string:
                string = pom_str
                pom_str = self.replace_variable_in_string(pom_str)
                i += 1
                if i >= 100:
                    print("ERROR: Too many variable replacement in line: " + original_string)
                    pom_str = original_string
                    break
            return pom_str
        else:
            return string

