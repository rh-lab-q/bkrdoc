#!/usr/bin/python
__author__ = 'Jiri_Kulda'

from bashlex import ast
from bkrdoc import data_containers
import shlex


class NodeVisitor(ast.nodevisitor):
    _parsing_subject = data_containers.DataContainer
    _variables = ""

    def __init__(self, variables):
        self._parsing_subject = ""
        self._variables = variables

    def visitnode(self, n):
        #print(n)
        pass

    def visitnodeend(self, n):
        if self.is_command_container():
            if not self._parsing_subject.is_command_substitution_list_empty():
                if n == self._parsing_subject.get_last_member_of_command_subst_ast_list():
                    self._parsing_subject.set_empty_spot_for_cmd_subst_ast_list()

    def visitoperator(self, n, op):
        print("visitoperator NOT IMPLEMENTED")
        print(n)
        print(op)
        pass

    def visitlist(self, n, parts):
        print("visitlist NOT IMPLEMENTED")
        print(n)
        print(parts)
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
        if self._parsing_subject is "":
            self._parsing_subject = data_containers.CommandContainer(n)
        else:
            if not self.get_parsed_data():
                self._parsing_subject = data_containers.CommandContainer(n)

    def visitfunction(self, n, name, body, parts):
        print("function ******************************** NOT IMPLEMENTED")
        pass
    def visitword(self, n, word):
        #print("word!")
        #print(word)
        self._parsing_subject.set_argparse_list(word)

    def visitassignment(self, n, word):
        #print("AssingmentTTTTTTTT NOT IMPLEMENTED")
        #print(word)
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
        print(n)
        print(word)
        pass

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

    def search_data(self):
        pass

    def get_parsed_data(self):
        return self._parsing_subject.get_argparse_list()

    def get_parsed_container(self):
        return self._parsing_subject

    def is_command_container(self):
        return type(self._parsing_subject).__name__ == "CommandContainer"
