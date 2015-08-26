#!/usr/bin/python
__author__ = 'Jiri_Kulda'

from bashlex import ast
from bkrdoc import data_containers
import shlex


class NodeVisitor(ast.nodevisitor):
    _parsing_subject = data_containers.DataContainer
    _variables = ""
    _function_ref = ""

    def __init__(self, variables):
        self._parsing_subject = ""
        self._variables = variables
        self._function_ref = ""

    def visitnode(self, n):
        #print(n)
        pass

    def visitnodeend(self, n):
        #print("++++++++++++++++++++END++++++++++++++++++++++")
        #print(n.kind)
        #print("")
        if self.is_function_container() and self.is_command_node(n) and not self.is_parsing_subject_empty():
            if n == self.get_parsing_subject_ast():
                self._function_ref.add_command(self._parsing_subject)
                self.erase_parsing_subject_variable()
        elif self.is_command_substitution_node(n):
            if n == self._parsing_subject.get_last_member_of_command_subst_ast_list():
                self._parsing_subject.set_empty_spot_for_cmd_subst_ast_list()

    def visitoperator(self, n, op):
        print("visitoperator NOT IMPLEMENTED")
        print(n)
        print(op)
        pass

    def visitlist(self, n, parts):
        print("visitlist NOT IMPLEMENTED")
        # print(n)
        # print(parts)
        pass

    def visitpipe(self, n, pipe):
        print("VISIT PIIIIIIIIIIIIPE NOT IMPLEMENTED")
        pass
    def visitpipeline(self, n, parts):
        print("VISIT PIIIIIIIIIIIIPEEEEELIIIIIIIIINEEEE NOT IMPLEMENTED")
        pass
    def visitcompound(self, n, list, redirects):
        print("VISIT COMPOUND NOT IMPLEMENTED")
        pass
    def visitif(self, node, parts):
        print("IF ******************************** NOT IMPLEMENTED")
        pass
    def visitfor(self, node, parts):
        print("for ******************************** NOT IMPLEMENTED")
        pass
    def visitwhile(self, node, parts):
        print("While ******************************** NOT IMPLEMENTED")
        pass
    def visituntil(self, node, parts):
        print("Until ******************************** NOT IMPLEMENTED")
        pass
    def visitcommand(self, n, parts):
        #print("command ********************************")
        #print(n)
        if self._parsing_subject is "":
            self._parsing_subject = data_containers.CommandContainer(n)
        else:
            if not self.get_parsed_data():
                self._parsing_subject = data_containers.CommandContainer(n)

    def visitfunction(self, n, name, body, parts):
        # print("function ******************************** NOT IMPLEMENTED")
        self._function_ref = data_containers.FunctionContainer(body)
        self._function_ref.set_function_name(name.word)
        # print("n: " + str(n))
        # print("Name: " + str(name))
        # print("Body: " + str(body))
        # print("Parts: " + str(parts))

    def visitword(self, n, word):
        # print("word!")
        # print(word)
        if self.is_function_container() and not self.is_parsing_subject_empty():
            self._parsing_subject.set_argparse_list(word)
        elif not self.is_function_container():
            self._parsing_subject.set_argparse_list(word)

    def visitassignment(self, n, word):
        # print("AssingmentTTTTTTTT NOT IMPLEMENTED")
        # print("ASSINGMENT")
        # print(word)
        # print(n)
        # print("")
        self._parsing_subject = data_containers.AssignmentContainer(n)
        read = shlex.shlex(word)
        member = read.get_token()
        equal_to = read.get_token()
        if equal_to == '=':
            # This 7 lines are here for erasing comments and for reading whole line
            pom_i = word.find("=", len(member)) + 1
            list_of_statement = shlex.split(word[pom_i:], True, True)
            value = ""
            for value_member in list_of_statement:
                if not value == "":
                    value += " "
                value += value_member

            self._parsing_subject.set_argparse_list(member)
            self._parsing_subject.set_argparse_list("=")
            self._parsing_subject.set_argparse_list(value)
            self._variables.add_variable(member, value)

    def visitreservedword(self, n, word):
        print("Reserved WOOOOOOOOOOOORD NOT IMPLEMENTED")
        print("Reserved word: " + str(word))
        # if self.is_end_of_function(word):
        #    print("SAve last command into function container")

    def visitparameter(self, n, value):
        #print("PARAMETR VISIT")
        #print(value)
        pom_member = self._parsing_subject.get_last_member_of_argparse_list()
        pom_member = self._variables.replace_variable_in_string_with_specified_variable(pom_member, value)
        self._parsing_subject.set_last_member_in_argparse_list(pom_member)

    def visittilde(self, n, value):
        print("TILDE NOT IMPLEMENTED")
        pass

    def visitredirect(self, n, input, type, output, heredoc):
        #print("REDIRECT NOT IMPLEMENTED")
        pass

    def visitheredoc(self, n, value):
        print("HEREDOC NOT IMPLEMENTED")
        pass

    def visitprocesssubstitution(self, n, command):
        print("------------------------------------------SUBSTITUTION process NOT IMPLEMENTED")
        pass

    def visitcommandsubstitution(self, n, command):
        #print("------------------------------------------SUBSTITUTION command NOT IMPLEMENTED")
        self._parsing_subject.set_command_substitution_ast(n)

    def erase_parsing_subject_variable(self):
        self._parsing_subject = ""

    def erase_function_reference_variable(self):
        self._function_ref = ""

    def search_data(self):
        pass

    def get_parsed_data(self):
        return self._parsing_subject.get_argparse_list()

    def get_parsed_container(self):
        if self.is_parsing_subject_empty():
            if self.is_function_container():
                return self._function_ref
        else:
            return self._parsing_subject

    def is_command_container(self):
        return type(self._parsing_subject).__name__ == "CommandContainer"

    def is_assignment_container(self):
        return type(self._parsing_subject).__name__ == "AssignmentContainer"

    def is_function_container(self):
        return type(self._function_ref).__name__ == "FunctionContainer"

    def is_function_word(self, word):
        return word == "function"

    def is_unnamed_function(self):
        return self._function_ref.get_function_name() == ""

    def is_parsing_subject_empty(self):
        return self._parsing_subject == ""

    def is_end_of_function(self, word):
        return word == "}"

    def is_command_substitution_node(self, n):
        return n.kind == "commandsubstitution"

    def is_command_node(self, n):
        return n.kind == "command"

    def get_parsing_subject_ast(self):
        return self._parsing_subject.get_ast()
