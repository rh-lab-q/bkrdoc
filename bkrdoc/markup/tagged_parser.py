__author__ = 'jkulda'

import shlex
from bkrdoc.markup.data_containers import *
from bkrdoc.analysis.Statement_data_searcher import StatementDataSearcher


class UnknownStatementDataParsingException(Exception):
        pass


class Parser(object):

    phases = []

    def __init__(self):
        self.phases = []

    def parse_file_by_lines(self, file_string):
        tagged_comment_container = ""
        self.phases.append(PhaseOutsideContainer())
        splitted_file_string = file_string.split("\n")
        max_len = len(splitted_file_string)
        i = 0
        while i < max_len:
            line = splitted_file_string[i]
            line = line.strip()
            try:
                splitted_line = shlex.split(line, posix=False)
            except ValueError as detail:
                self.print_value_error_msg(detail)

            if not self.is_empty_line(splitted_line):
                ''' for Description: / Author: / Keywords: spanning multiple lines '''
                if self.has_keyword(splitted_line):
                    i_temp = i
                    while True:
                        i_temp += 1
                        splitted_next = shlex.split(splitted_file_string[i_temp].strip(), posix=False)
                        if self.same_keyword_span(splitted_next):
                            splitted_line[-1] += self.comma_or_newline(splitted_line[1][:-1])
                            splitted_line += splitted_next[1:]
                            i += 1
                        else:
                            break

                if self.is_phase_start_xxx(splitted_line[0]):
                    self.phases.append(TestPhaseContainer())

                elif self.is_phase_journal_end(splitted_line[0]) or self.is_journal_start(splitted_line[0]):
                    if self.is_tagged_comment_container(tagged_comment_container):
                        self.phases[-1].add_comment(tagged_comment_container)
                        tagged_comment_container = ""
                    self.phases.append(PhaseOutsideContainer())
            try:
                i, tagged_comment_container, container = self.comments_and_containers_parsing(splitted_line,
                                                                                          tagged_comment_container,
                                                                                          self.phases[-1],
                                                                                          splitted_file_string,
                                                                                          i, line)
            except ValueError as detail:
                self.print_value_error_msg(detail)
            i += 1

    def comments_and_containers_parsing(self, splitted_line, tagged_comment_container, container, splitted_file_string,
                                        i, line):

        if not self.is_empty_line(splitted_line) and self.is_tagged_comment_start(splitted_line) and \
           not self.is_tagged_comment_container(tagged_comment_container):
                tagged_comment_container = TaggedCommentContainer(splitted_line)
        elif not self.is_empty_line(splitted_line) and self.is_common_comment_line(splitted_line):
            if self.is_tagged_comment_container(tagged_comment_container) and \
                    self.is_tagged_comment_start(splitted_line):
                # print "bbbb {0}".format(splitted_line)
                tagged_comment_container.add_comment(splitted_line)
            elif self.is_tagged_comment_container(tagged_comment_container):
                container.add_comment(tagged_comment_container)
                tagged_comment_container = ""
                container.add_common_comment(splitted_line)
            else:
                # print "aaaa {0}".format(splitted_line)
                container.add_common_comment(splitted_line)
        else:
            if not self.is_empty_line(splitted_line):
                if self.is_condition_line(splitted_line):
                    i, tagged_comment_container, condition = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                      ConditionContainer(), ["fi"],
                                                                      splitted_file_string)
                    container.add_statement_line(condition)
                    container.add_comment(condition)
                    tagged_comment_container = ""
                elif self.is_loop_line(splitted_line):
                    loop = LoopContainer()
                    i, tagged_comment_container, loop = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                 loop, ["done"], splitted_file_string)
                    container.add_statement_line(loop)
                    container.add_comment(loop)
                    tagged_comment_container = ""

                elif self.is_function_line(splitted_line):
                    function = FunctionContainer()
                    i, tagged_comment_container, function = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                     function, ["}"], splitted_file_string)
                    container.add_comment(function)
                    container.add_statement_line(function)
                    tagged_comment_container = ""

                else:
                    container.add_statement_line(line)
                if self.is_tagged_comment_container(tagged_comment_container):
                    tagged_comment_container.add_tagged_line(splitted_line)
                    container.add_comment(tagged_comment_container)
                    tagged_comment_container = ""
            else:
                if self.is_tagged_comment_container(tagged_comment_container):
                    container.add_comment(tagged_comment_container)
                    tagged_comment_container = ""
            if not self.is_empty_line(splitted_line) and self.is_after_code_doc_comment(splitted_line):
                tagged_comment_container = TaggedCommentContainer([""])
                data_searcher = StatementDataSearcher()
                argparse_data, var = data_searcher.parse_command(line)
                try:
                    if argparse_data.comment is not None:
                        after_line_comment = self.get_after_code_doc_commment(splitted_line)
                        if len(after_line_comment) > 0:
                            tagged_comment_container.add_condition_tag("after_code", after_line_comment)
                        else:
                            tagged_comment_container.add_condition_tag("after_code", argparse_data.comment)
                    else:
                        tagged_comment_container.add_condition_tag("after_code",
                                                                   self.get_after_code_doc_commment(splitted_line))
                except AttributeError:
                    tagged_comment_container.add_condition_tag("after_code",
                                                               self.get_after_code_doc_commment(splitted_line))
                except ValueError as detail:
                    self.print_value_error_msg(detail)
                except Exception as detail:
                    raise UnknownStatementDataParsingException("Unknown parsing exception. Please contact "
                                                               "jkulda@redhat, Kulda12@seznam.cz"
                                                               "Detail of exception: {0}".format(detail))
                tagged_comment_container.add_tagged_line(splitted_line)
                container.add_comment(tagged_comment_container)
                tagged_comment_container = ""

        return i, tagged_comment_container, container

    def parse_condition(self, i, splitted_file_string, searched_last_keyword, container):
        max_len = len(splitted_file_string)
        container.add_statement_line(splitted_file_string[i].strip())
        i += 1
        tagged_comment_container = ""
        is_elif_condition_part = False

        while i < max_len:
            line = splitted_file_string[i]
            line = line.strip()
            splitted_line = shlex.split(line, posix=False)
            # print splitted_line
            if not self.is_empty_line(splitted_line) and self.is_seacher_keyword(searched_last_keyword, splitted_line):
                if self.is_tagged_comment_container(tagged_comment_container):
                    tagged_comment_container.add_tagged_line(splitted_line)
                    # container.add_comment(tagged_comment_container)
                    # print "first {0}".format(tagged_comment_container.comments)
                return i, tagged_comment_container, container

            elif not self.is_empty_line(splitted_line) and self.is_seacher_keyword(["else", "elif", "fi"], splitted_line):
                i, tagged_comment_container, condition = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                  ConditionContainer(), ["else", "elif", "fi"],
                                                                  splitted_file_string)
                # if self.is_tagged_comment_container(tagged_comment_container):
                #   print "second {0}".format(tagged_comment_container.comments)
                container.add_elif_part(condition)
                line = splitted_file_string[i]
                line = line.strip()
                # print container.elif_parts
                #tagged_comment_container = ""
                splitted_line = shlex.split(line, posix=False)
                # print "splitted_line {0} last keywords {1}".format(splitted_line, searched_last_keyword)
                if not self.is_empty_line(splitted_line) and self.is_seacher_keyword(searched_last_keyword, splitted_line):
                    if self.is_tagged_comment_container(tagged_comment_container):
                        container.add_comment(tagged_comment_container)
                        # print "second {0}".format(tagged_comment_container.comments)
                    # print "AHOOOJ"
                    return i, tagged_comment_container, container
                # print "elif"
                is_elif_condition_part = True
                i -= 1

            # print "impossible"
            if not is_elif_condition_part:
                # print "ZDE {0} with container {1}".format(splitted_line, container)
                # print "with tagged_comment_container: {0}".format(tagged_comment_container)
                i, tagged_comment_container, container = self.comments_and_containers_parsing(splitted_line,
                                                                                              tagged_comment_container,
                                                                                              container,
                                                                                              splitted_file_string,
                                                                                              i, line)
                # print container.get_statement_list()
                # print container.comments_list
            if is_elif_condition_part:
                is_elif_condition_part = False
            i += 1
        return i, tagged_comment_container, container

    def specific_container_parse_call(self, i, tagged_comment_container, splitted_line, specific_container,
                                      end_list, splitted_file_string):
        if self.is_tagged_comment_container(tagged_comment_container):
            tagged_comment_container.add_tagged_line(splitted_line)
            specific_container.add_comment(tagged_comment_container)
            return self.parse_condition(i, splitted_file_string, end_list, specific_container)
        else:
            return self.parse_condition(i, splitted_file_string, end_list, specific_container)

    def get_phases(self):
        return self.phases

    def comments_set_up(self):
        for phase in self.phases:
            phase.comments_set_up()

    def is_after_code_doc_comment(self, splitted_line):
        if len(splitted_line) > 1 and not self.is_tagged_comment_start(splitted_line):
            for splitted in splitted_line[1:]:
                if splitted.endswith("#@"):
                    return True
        return False

    def get_after_code_doc_commment(self, splitted_line):
        pom_line = ""
        threshold = False
        if len(splitted_line) > 1:
            for splitted in splitted_line[1:]:
                if threshold:
                    if pom_line != "":
                        pom_line = "{0} {1}".format(pom_line, splitted)
                    else:
                        pom_line += splitted
                elif splitted.endswith("#@"):
                    threshold = True
        return pom_line


    def is_seacher_keyword(self, searched_keyword, line):
        return line[0] in searched_keyword

    def is_tagged_comment_start(self, splitted_line):
        if splitted_line[0].startswith("#@"):
            return True
        elif len(splitted_line) > 1 and splitted_line[0] == "#" and splitted_line[1] == "@":
            return True
        else:
            return False

    def is_function_line(self, splitted_line):
        return splitted_line[0] == "function"

    def is_common_comment_line(self, line):
        return line[0].startswith("#")

    def is_empty_line(self, line):
        return line == []

    def is_phase_start_xxx(self, word):
        phase_list = ["rlPhaseStartSetup", "rlPhaseStartCleanup", "rlPhaseStartTest"]
        return word in phase_list

    def is_journal_start(self, word):
        return word == "rlJournalStart"

    def is_phase_journal_end(self, line):
        if line[0:len("rlphaseend")].lower() == "rlphaseend":
            return True

        elif line[0:len("rljournalend")].lower() == "rljournalend":
            return True

        else:
            return False

    def is_condition_line(self, line):
        return line[0] == "if"

    def is_loop_line(self, line):
        loop_list = ["for", "while", "until"]
        return line[0] in loop_list

    def is_tagged_comment_container(self, tagged_container):
        return type(tagged_container).__name__ == "TaggedCommentContainer"

    def is_phase_outside_container(self, container):
        return type(container).__name__ == "PhaseOutsideContainer"

    def is_phase_startxxx_container(self, container):
        return type(container).__name__ == "TestPhaseContainer"

    def has_keyword(self, line):
        if len(line) <= 1:
            return False
        return line[1] in ["Description:", "Author:", "Keywords:"]

    def same_keyword_span(self, line):
        return (not self.is_empty_line(line)) and (not self.is_empty_line(line[1:])) \
                and (not self.has_keyword(line)) and (line[1][1] != '~')

    def comma_or_newline(self, word):
        table = {'Description': '\n' + ' ' * 12,
                 'Author': ',',
                 'Keywords': ','}
        return table.get(word, "")

    def print_value_error_msg(self, detail):
        print("****************************************")
        print("ValueError: This error is caused by missing closing quotation.")
        print("****************************************")

