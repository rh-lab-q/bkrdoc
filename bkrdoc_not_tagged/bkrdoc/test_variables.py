#!/usr/bin/python
__author__ = 'Jiri_Kulda'

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
