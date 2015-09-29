__author__ = 'jkulda'

import shlex
from bkrdoc.markup.data_containers import *


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
            splitted_line = shlex.split(line, posix=False)

            if not self.is_empty_line(splitted_line):
                if self.is_phase_start_xxx(splitted_line[0]):
                    self.phases.append(TestPhaseContainer())

                elif self.is_phase_journal_end(splitted_line[0]) or self.is_journal_start(splitted_line[0]):
                    if self.is_tagged_comment_container(tagged_comment_container):
                        self.phases[-1].add_comment(tagged_comment_container)
                        tagged_comment_container = ""
                    self.phases.append(PhaseOutsideContainer())

            i, tagged_comment_container, container = self.comments_and_containers_parsing(splitted_line,
                                                                                          tagged_comment_container,
                                                                                          self.phases[-1],
                                                                                          splitted_file_string,
                                                                                          i, line)
            i += 1

    def comments_and_containers_parsing(self, splitted_line, tagged_comment_container, container, splitted_file_string,
                                        i, line):

        if not self.is_empty_line(splitted_line) and self.is_tagged_comment_start(splitted_line) and \
           not self.is_tagged_comment_container(tagged_comment_container):
                tagged_comment_container = TaggedCommentContainer(splitted_line)
        elif not self.is_empty_line(splitted_line) and self.is_common_comment_line(splitted_line):
            if self.is_tagged_comment_container(tagged_comment_container):
                # print splitted_line
                tagged_comment_container.add_comment(splitted_line)
            else:
                container.add_common_comment(splitted_line)
        else:
            if not self.is_empty_line(splitted_line):
                if self.is_condition_line(splitted_line):
                    i, condition = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                      ConditionContainer(), ["fi"],
                                                                      splitted_file_string)
                    container.add_statement_line(condition)
                    container.add_comment(condition)
                    tagged_comment_container = ""
                elif self.is_loop_line(splitted_line):
                    loop = LoopContainer()
                    i, loop = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                 loop, ["done"], splitted_file_string)
                    container.add_statement_line(loop)
                    container.add_comment(loop)
                    tagged_comment_container = ""

                elif self.is_function_line(splitted_line):
                    function = FunctionContainer()
                    i, function = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
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
            if not self.is_empty_line(splitted_line) and self.is_important_code_line(splitted_line):
                tagged_comment_container = TaggedCommentContainer([""])
                tagged_comment_container.add_condition_tag("code")
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

            if not self.is_empty_line(splitted_line) and self.is_seacher_keyword(searched_last_keyword, splitted_line):
                if self.is_tagged_comment_container(tagged_comment_container):
                    tagged_comment_container.add_tagged_line(splitted_line)
                    container.add_comment(tagged_comment_container)
                return i, container

            elif not self.is_empty_line(splitted_line) and self.is_seacher_keyword(["else", "elif", "fi"], splitted_line):
                i, condition = self.specific_container_parse_call(i, tagged_comment_container, splitted_line,
                                                                  ConditionContainer(), ["else", "elif", "fi"],
                                                                  splitted_file_string)
                container.add_elif_part(condition)
                line = splitted_file_string[i]
                line = line.strip()
                tagged_comment_container = ""
                splitted_line = shlex.split(line, posix=False)
                if not self.is_empty_line(splitted_line) and self.is_seacher_keyword(searched_last_keyword, splitted_line):
                    if self.is_tagged_comment_container(tagged_comment_container):
                        container.add_comment(tagged_comment_container)
                    return i, container
                is_elif_condition_part = True
                i -= 1

            if not is_elif_condition_part:
                i, tagged_comment_container, container = self.comments_and_containers_parsing(splitted_line,
                                                                                              tagged_comment_container,
                                                                                              container,
                                                                                              splitted_file_string,
                                                                                              i, line)
            if is_elif_condition_part:
                is_elif_condition_part = False
            i += 1
        return i, container

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

    def is_important_code_line(self, splitted_line):
        return splitted_line[-1].endswith("#@")

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


