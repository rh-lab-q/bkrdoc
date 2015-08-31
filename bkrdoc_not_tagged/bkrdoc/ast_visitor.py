#!/usr/bin/python

__author__ = 'Jiri_Kulda'

from bashlex import ast
from bkrdoc import data_containers
import shlex
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
        return _dump(self, indent)

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
        elif k == 'compound':
            dochild = self._visitnode(n, n.list, n.redirects)
            if dochild is None or dochild:
                for child in n.list:
                    self.visit(child)
                for child in n.redirects:
                    self.visit(child)
        elif k in ('if', 'for', 'while', 'until'):
            dochild = self._visitnode(n, n.parts)
            if dochild is None or dochild:
                for child in n.parts:
                    self.visit(child)
        elif k == 'command':
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

    def visitnodeend(self, n):
        #print("++++++++++++++++++++END++++++++++++++++++++++")
        #print(n.kind)
        #print("")
        #if self.is_function_container() and self.is_command_node(n) and not self.is_parsing_subject_empty():
        #    if n == self.get_parsing_subject_ast():
        #        self._function_ref.add_command(self._parsing_subject)
        #        self.erase_parsing_subject_variable()
        #elif self.is_command_substitution_node(n):
        if self.is_command_substitution_node(n):
            if n == self._parsing_subject.get_last_member_of_command_subst_ast_list():
                self._parsing_subject.set_empty_spot_for_cmd_subst_ast_list()

    def visitoperator(self, n, op):
        if not op == "\n":
            print("visitoperator NOT IMPLEMENTED")
            print(n)
            print(op)

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
        # self._function_ref = data_containers.FunctionContainer(body)
        # self._function_ref.set_function_name(name.word)
        # print("n: " + str(n))
        # print("Name: " + str(name))
        # print("Body: " + str(body))
        # print (parts[4]).list[1].kind
        pom_variables = self._variables
        self._variables = copy.deepcopy(self._variables)
        function = data_containers.FunctionContainer(body)
        function.set_function_name(name.word)
        if self.is_list_node((parts[4]).list[1]):
            for member in (parts[4]).list[1].parts:
                self.visit(member)
                # print(self._parsing_subject)
                if not self.is_parsing_subject_empty():
                    # TODO future check for condition and loop container
                    function.add_command(self.get_parsed_container())
                self.erase_parsing_subject_variable()
        else:
            self.visit((parts[4]).list[1].parts)
            function.add_command(self.get_parsed_data())
            self.erase_parsing_subject_variable()
        function.set_variables(self._variables)
        self._variables = pom_variables
        self._parsing_subject = function

    def visitword(self, n, word):
        # print("word!")
        # print(word)
        #if self.is_function_container() and not self.is_parsing_subject_empty():
        #    self._parsing_subject.set_argparse_list(word)
        #elif not self.is_function_container():
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
        # print("PARAMETR VISIT")
        if self._variables.is_existing_variable(value):
            pom_member = self._parsing_subject.get_last_member_of_argparse_list()
            pom_member = self._variables.replace_variable_in_string_with_specified_variable(pom_member, value)
            self._parsing_subject.set_last_member_in_argparse_list(pom_member)
        else:
            self._variables.set_unknown_variable(value)

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

    def is_list_node(self, n):
        return n.kind == "list"

    def get_parsing_subject_ast(self):
        return self._parsing_subject.get_ast()


def _dump(tree, indent='  '):
    def _format(n, level=0):
        if isinstance(n, node):
            d = dict(n.__dict__)
            kind = d.pop('kind')
            if kind == 'list' and level > 0:
                level = level + 1
            fields = []
            v = d.pop('s', None)
            if v:
                fields.append(('s', _format(v, level)))
            for k, v in sorted(d.items()):
                if not v or k == 'parts':
                    continue
                llevel = level
                if isinstance(v, node):
                    llevel += 1
                    fields.append((k, '\n' + (indent * llevel) + _format(v, llevel)))
                else:
                    fields.append((k, _format(v, level)))
            if kind == 'function':
                fields = [f for f in fields if f[0] not in ('name', 'body')]
            v = d.pop('parts', None)
            if v:
                fields.append(('parts', _format(v, level)))
            return ''.join([
                '%sNode' % kind.title(),
                '(',
                ', '.join(('%s=%s' % field for field in fields)),
                ')'])
        elif isinstance(n, list):
            lines = ['[']
            lines.extend((indent * (level + 1) + _format(x, level + 1) + ','
                         for x in n))
            if len(lines) > 1:
                lines.append(indent * (level) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(n)

    if not isinstance(tree, node):
        raise TypeError('expected node, got %r' % tree.__class__.__name__)
    return _format(tree)