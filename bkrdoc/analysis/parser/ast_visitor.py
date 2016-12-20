#!/usr/bin/python

__author__ = 'Jiri_Kulda'

from bashlex import ast
from bkrdoc.analysis.parser import data_containers
import shlex
import sys
import copy


class node(object):
    """
    This class represents a node in the AST built while parsing command lines.
    It's basically an object container for various attributes, with a slightly
    specialised representation to make it a little easier to debug the parser.
    """

    def __init__(self, **kwargs):
        assert 'kind' in kwargs
        self.__dict__.update(kwargs)

    def dump(self, indent='  '):
        return ast._dump(self, indent)

    def __repr__(self):
        chunks = []
        d = dict(self.__dict__)
        kind = d.pop('kind')
        for k, v in sorted(d.items()):
            chunks.append('%s=%r' % (k, v))
        return '%sNode(%s)' % (kind.title(), ' '.join(chunks))

    def __eq__(self, other):
        if not isinstance(other, node):
            return False
        return self.__dict__ == other.__dict__


class NodeVisitor(ast.nodevisitor):
    _parsing_subject = data_containers.DataContainer
    _variables = ""

    def __init__(self, variables):
        self._parsing_subject = ""
        self._variables = variables

    def visit(self, n):
        k = n.kind
        if k == 'operator':
            self._visitnode(n, n.op)
        elif k == 'pattern':
            self._visitnode(n, n.actions, n.pattern)

        elif k == 'list':
            dochild = self._visitnode(n, n.parts)
            if dochild is None or dochild:
                for child in n.parts:
                    self.visit(child)
        elif k == 'reservedword':
            self._visitnode(n, n.word)
        elif k == 'pipe':
            self._visitnode(n, n.pipe)
        elif k == 'pipeline':
            dochild = self._visitnode(n, n.parts)
            if dochild is None or dochild:
                for child in n.parts:
                    self.visit(child)
        elif k == 'case':
            self._visitnode(n, n.parts)
            # if dochild is None or dochild:
            #    for child in n.parts:
            #       self.visit(child)
        elif k == 'compound':
            # print("compound")
            dochild = self._visitnode(n, n.list, n.redirects)
            if dochild is None or dochild:
                for child in n.list:
                    self.visit(child)
                for child in n.redirects:
                    self.visit(child)
        elif k in ('if', 'for', 'while', 'until'):
            dochild = self._visitnode(n, n.parts)
            # if dochild is None or dochild:
                # for child in n.parts:
                    # self.visit(child)
        elif k == 'command':
            # print("COMMAND")
            # print(n)
            dochild = self._visitnode(n, n.parts)
            if dochild is None or dochild:
                for child in n.parts:
                    self.visit(child)
        elif k == 'function':
            dochild = self._visitnode(n, n.name, n.body, n.parts)
            #if dochild is None or dochild:
            #    for child in n.parts:
            #        print(child)
            #        self.visit(child)
        elif k == 'redirect':
            dochild = self._visitnode(n, n.input, n.type, n.output, n.heredoc)
            if dochild is None or dochild:
                if isinstance(n.output, node):
                    self.visit(n.output)
                if n.heredoc:
                    self.visit(n.heredoc)
        elif k in ('word', 'assignment'):
            dochild = self._visitnode(n, n.word)
            if dochild is None or dochild:
                for child in n.parts:
                    self.visit(child)
        elif k in ('parameter', 'tilde', 'heredoc'):
            self._visitnode(n, n.value)
        elif k in ('commandsubstitution', 'processsubstitution'):
            dochild = self._visitnode(n, n.command)
            if dochild is None or dochild:
                self.visit(n.command)
        else:
            raise ValueError('unknown node kind %r' % k)
        self.visitnodeend(n)

    def visitnode(self, n):
        #print(n)
        pass

    def visitpattern(self, n, actions, parts):
        # TODO rewrite it to a condition similar container
        # self.visit(parts.actions)
        case_condition = data_containers.ConditionContainer(n)
        for child in actions:
            if child is not None:
                if not self.is_end_of_line(child):
                    self.visit(child)
                    case_condition.add_command(self._parsing_subject)
                    self.erase_parsing_subject_variable()
        self._parsing_subject = case_condition

    def visitnodeend(self, n):
        #print("++++++++++++++++++++END++++++++++++++++++++++")
        #print(n.kind)
        #print("")
        if self.is_command_substitution_node(n):
            if n == self._parsing_subject.get_last_member_of_command_subst_ast_list():
                self._parsing_subject.set_empty_spot_for_cmd_subst_ast_list()

    def visitoperator(self, n, op):
        pass

    def visitlist(self, n, parts):
        # for part in parts
        #   print part
        pass

    def visitpipe(self, n, pipe):
        # print("VISIT PIIIIIIIIIIIIPE NOT IMPLEMENTED")
        # print("PIPE: " + str(pipe))
        if self._parsing_subject:
            self._parsing_subject.set_argparse_list(pipe)

    def visitpipeline(self, n, parts):
        # print("VISIT PIIIIIIIIIIIIPEEEEELIIIIIIIIINEEEE NOT IMPLEMENTED")
        # print("PARTS: " + str(parts))
        pass

    def visitcompound(self, n, list, redirects):
        # compounds are visited on a more specific level (if/while/..)
        pass

    def visitif(self, node, parts):
        # print("IF ******************************** NOT IMPLEMENTED")
        # print("NODE: " + str(node))
        #  print("PARTS: " + str(parts))
        # print(self.get_condition_body_position(parts))
        condition = data_containers.ConditionContainer(parts)
        self.visit(parts[1]) #condition after 'if'
        condition.add_command(self.get_parsed_container())
        self.erase_parsing_subject_variable()
        condition_body = self.get_condition_body_position(parts)
        keys = condition_body.keys()
        # keys need to be sorted to be in right position.
        for key in sorted(keys):
            if self.is_list_node(parts[condition_body[key]]):
                for member in parts[condition_body[key]].parts:
                    self.visit(member)
                    if not self.is_parsing_subject_empty():
                        condition.add_command(self.get_parsed_container())
                    self.erase_parsing_subject_variable()
            else:
                self.visit(parts[condition_body[key]])
                condition.add_command(self.get_parsed_container())
                self.erase_parsing_subject_variable()
        self._parsing_subject = condition

    def visitfor(self, node, parts):
        # print("for ******************************** NOT IMPLEMENTED")
        loop = data_containers.LoopContainer(node, "for")
        self.set_for_loop_variable_settings(parts)
        self.visit_loops(loop, parts)
        pass

    def visitwhile(self, node, parts):
        # print("While ******************************** NOT IMPLEMENTED")
        loop = data_containers.LoopContainer(node, "while")
        self.visit_loops(loop, parts)

    def visituntil(self, node, parts):
        # print("Until ******************************** NOT IMPLEMENTED")
        loop = data_containers.LoopContainer(node, "until")
        self.visit_loops(loop, parts)

    def visitcommand(self, n, parts):
        #print("command ********************************")
        #print(n)
        if self._parsing_subject is "":
            self._parsing_subject = data_containers.CommandContainer(n)
        else:
            if not self.get_parsed_data():
                self._parsing_subject = data_containers.CommandContainer(n)

    def visitcase(self, node, parts):
        pom_variables = self._variables
        self._variables = copy.deepcopy(self._variables)
        case_container = data_containers.CaseContainer(node)
        # print("Velikost {0}".format(len(parts)))
        for pattern in parts[3:-1]:
            self.visit(pattern)
            case_container.add_condition(self._parsing_subject)
            self.erase_parsing_subject_variable()
        case_container.set_variables(self._variables)
        self._variables = pom_variables
        self._parsing_subject = case_container

    def visitfunction(self, n, name, body, parts):
        def inner_visit(part):
            self.visit(part)
            if not self.is_parsing_subject_empty():
                function.add_command(self.get_parsed_container())
            self.erase_parsing_subject_variable()

        def inner_visit_list(parts):
            for part in parts:
                inner_visit(part)

        pom_variables = self._variables
        self._variables = copy.deepcopy(self._variables)
        function = data_containers.FunctionContainer(body)
        function.set_function_name(name.word)

        compound = self.get_compound_from_function(parts)
        if self.is_list_node(compound.list[1]):
            inner_visit_list(compound.list[1].parts)
        elif hasattr(compound.list[1], 'parts') and isinstance(compound.list[1].parts, list):
            if compound.list[1].kind == 'command':
                inner_visit(compound.list[1])
            elif compound.list[1].kind == 'pipeline':
                inner_visit_list(compound.list[1].parts)
            else:
                sys.stderr.writelines("Function parsing not a command\n")
        elif compound.list[1].kind == "compound":
            parts = compound.list[1].list[0].parts
            inner_visit_list(parts)
        else:
            inner_visit(compound.list[1].parts)

        function.set_variables(self._variables)
        self._variables = pom_variables
        self._parsing_subject = function

    def visitword(self, n, word):
        self._parsing_subject.set_argparse_list(word)

    def visitassignment(self, n, word):
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
        pass

    def visitparameter(self, n, value):
        if self._variables.is_existing_variable(value):
            pom_member = self._parsing_subject.get_last_member_of_argparse_list()
            pom_member = self._variables.replace_variable_in_string_with_specified_variable(pom_member, value)
            self._parsing_subject.set_last_member_in_argparse_list(pom_member)
        else:
            self._variables.set_unknown_variable(value)

    def visittilde(self, n, value):
        pass

    def visitredirect(self, n, input, type, output, heredoc):
        pass

    def visitheredoc(self, n, value):
        pass

    def visitprocesssubstitution(self, n, command):
        sys.stderr.writelines("------------------------------------------SUBSTITUTION process NOT IMPLEMENTED\n")
        pass

    def visitcommandsubstitution(self, n, command):
        self._parsing_subject.set_command_substitution_ast(n)

    def erase_parsing_subject_variable(self):
        self._parsing_subject = ""

    def search_data(self):
        pass

    def visit_loops(self, loop_ref, parts):
        pom_variables = self._variables
        self._variables = copy.deepcopy(self._variables)
        if self.is_list_node(parts[self.get_loop_body_position(parts)]):
            for member in parts[self.get_loop_body_position(parts)].parts:
                self.visit(member)
                if not self.is_parsing_subject_empty():
                    loop_ref.add_command(self.get_parsed_container())
                self.erase_parsing_subject_variable()
        else:
            self.visit(parts[self.get_loop_body_position(parts)])
            loop_ref.add_command(self.get_parsed_container())
            self.erase_parsing_subject_variable()
        loop_ref.set_variables(self._variables)
        self._variables = pom_variables
        self._parsing_subject = loop_ref

    def get_loop_body_position(self, node):
        i = 0
        for member in node:
            if self.is_reservedword_node(member) and member.word == "do":
                i += 1
                return i
            i += 1
        return -1

    def get_condition_body_position(self, n):
        body_position = {}
        i = 0
        for member in n:
            if self.is_reservedword_node(member) and member.word == "then":
                i += 1
                body_position[str(i) + "then"] = i

            # elif self.is_reservedword_node(member) and member.word == "elif":
            #    i += 1
            #    body_position[str(i) + "elif"] = i

            elif self.is_reservedword_node(member) and member.word == "else":
                i += 1
                body_position[str(i) + "else"] = i

            elif self.is_reservedword_node(member) and member.word == "fi":
                i += 1
                return body_position
            else:
                i += 1
        return -1

    def get_parsed_data(self):
        return self._parsing_subject.get_argparse_list()

    def get_parsed_container(self):
        return self._parsing_subject

    def is_command_container(self):
        return type(self._parsing_subject).__name__ == "CommandContainer"

    def is_assignment_container(self):
        return type(self._parsing_subject).__name__ == "AssignmentContainer"

    def is_function_container(self):
        return type(self._function_ref).__name__ == "FunctionContainer"

    def is_function_word(self, word):
        return word == "function"

    def is_parsing_subject_empty(self):
        return self._parsing_subject == ""

    def is_end_of_function(self, word):
        return word == "}"

    def is_command_substitution_node(self, n):
        return n.kind == "commandsubstitution"

    def is_command_node(self, n):
        return n.kind == "command"

    def is_parametr_node(self, n):
        return n.kind == "parametr"

    def is_reservedword_node(self, n):
        return n.kind == "reservedword"

    def is_list_node(self, n):
        return n.kind == "list"

    def is_end_of_line(self, node):
        return node.kind == "operator" and node.op == '\n'

    def set_for_loop_variable_settings(self, node):
        for_variable = node[1].word
        for_variable_value = ""
        for value in node[3:]:
            if value.word == "do":
                break
            else:
                for_variable_value += value.word + " "
        # Erasing last empty space.
        for_variable_value = for_variable_value.strip()
        self._variables.add_variable(for_variable, for_variable_value)

    def get_parsing_subject_ast(self):
        return self._parsing_subject.get_ast()

    @staticmethod
    def get_compound_from_function(parts):
        if parts[2].kind == 'compound':
            return parts[2]
        else:
            return parts[4]
