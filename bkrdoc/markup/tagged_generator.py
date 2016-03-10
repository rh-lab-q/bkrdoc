__author__ = 'jkulda'

import argparse
import sys
from bkrdoc.markup.tagged_parser import Parser
from bkrdoc.markup.data_containers import TaggedCommentContainer


class Generator(object):

    phases = []

    def __init__(self, file_in):
        if file_in[(len(file_in) - 3):len(file_in)] == ".sh":
            try:
                self.filename = file_in
                with open(file_in, "r") as input_file:
                    self.file_string = input_file.read()
                    self.parser_ref = ""
                    self.phases = []

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)
        else:
            print ("ERROR: Not a script file. (.sh)")
            sys.exit(1)

    def parse_file(self):
        self.parser_ref = Parser()
        self.parser_ref.parse_file_by_lines(self.file_string)
        self.phases = self.parser_ref.get_phases()

    def comments_set_up(self):
        for phase in self.phases:
            phase.comments_set_up()

    def get_title_data(self):
        self.phases[0].search_for_title_data()

    def erase_title_data(self):
        help_comment = TaggedCommentContainer("")
        help_comment.erase_known_tags()
        self.phases[0].comments_list.pop(0)

    def get_purpose_title_data(self):
        output_purpose_doc = ""
        for comment_container in self.phases[0].purpose_comments:
            for comment in comment_container.documentation_comments:
                output_purpose_doc += "{0}{1}\n".format("         ", comment)
        return output_purpose_doc.strip()

    def get_documentation_title_doc(self):
        self.get_title_data()
        title_data = self.phases[0].comments_list[0].get_title_data().copy()
        self.erase_title_data()
        documentation = "Description: {0}\n".format(self.get_adapted_header_line(title_data["description"]))
        documentation += "Author: {0}\n".format(self.get_adapted_header_line(title_data["author"]))
        # get purpose data
        if self.is_outside_phase_container(self.phases[0]):
            self.phases[0].get_and_set_purpose_comments(self.file_string)
        documentation += "Purpose: {0}\n".format(self.get_adapted_header_line(self.get_purpose_title_data()))

        if title_data["key"] and title_data["keywords"]:
            documentation += "Keywords: {0}, {1}".format(title_data["keywords"], title_data["key"])
        elif title_data["key"]:
            documentation += "Keywords: {0}".format(title_data["key"])
        elif title_data["keywords"]:
            documentation += "Keywords: {0}".format(title_data["keywords"])
        else:
            documentation += "Keywords: -"
        return documentation

    @staticmethod
    def get_adapted_header_line(string):
        return "-" if not string else string

    def get_phase_data_documentation(self, parsed_arg):
        documentation = ""
        if parsed_arg.additional_info:
            documentation += "Phases:\n"
        pom_doc = ""
        for phase in self.phases:
            pom_doc += phase.print_documentation()
            phases_doc_split = pom_doc.strip().split("\n")
            if len(phases_doc_split) > 1:
                if self.is_outside_phase_documentation(phases_doc_split):
                    pom_doc = self.erase_outside_phase_settings(phases_doc_split)
                    pom_doc += "\n"
                elif not parsed_arg.additional_info:
                    pom_doc = self.erase_spaces(phases_doc_split)
                    pom_doc += "\n"
                documentation += pom_doc
            pom_doc = ""
        return documentation

    # This method erases two spaces at the beginning of line.
    def erase_spaces(self, splitted_lines, spaces="  "):
        pom_line = "{0}{1}".format(splitted_lines[0], "\n")
        for line in splitted_lines[1:]:
            pom_line += "{0}{1}".format(line[len(spaces):], "\n")
        return pom_line

    def erase_outside_phase_settings(self, splitted_lines, spaces="    "):
        pom_line = ""
        for line in splitted_lines[1:]:
            pom_line += "{0}{1}".format(line[len(spaces):], "\n")
        return pom_line

    def is_outside_phase_documentation(self, splitted_lines):
        return splitted_lines[0] == "Outside Phase"

    def is_outside_phase_container(self, container):
        return type(container).__name__ == "PhaseOutsideContainer"

    def print_additional_container_data(self, name, additional_containers):
        documentation = ""
        if len(additional_containers):
            documentation += "  {0}:\n".format(name)
            for container in additional_containers:
                documentation += container.get_additional_phase_data()
                if self.is_condition_container(container):
                    for elif_member in container.elif_parts:
                        documentation += elif_member.get_additional_phase_data()
                    documentation += "{0}fi\n".format("    ")
                if len(additional_containers) > 1:
                    documentation += "\n"
            documentation += "\n"
        return documentation

    @staticmethod
    def is_condition_container(container):
        return type(container).__name__ == "ConditionContainer"

    def generate_additional_info(self):
        documentation = "Additional information:\n"
        func = []
        loop = []
        cond = []
        for phase in self.phases:
            func, loop, cond = phase.get_additional_containers(func, loop, cond)

        documentation += self.print_additional_container_data("Functions", func)
        documentation += self.print_additional_container_data("Loops", loop)
        documentation += self.print_additional_container_data("Conditions", cond)
        return documentation

    def get_documentation(self, parsed_arg):
        documentation = self.get_documentation_title_doc()
        documentation += "\n\n"
        documentation += self.get_phase_data_documentation(parsed_arg)
        if parsed_arg.additional_info:
            documentation += "\n"
            documentation += self.generate_additional_info()
        return documentation

    def show_documentation_data(self, parsed_arg):
        documentation = self.get_documentation(parsed_arg)
        if parsed_arg.FILE_NAME:
            file_out = open(parsed_arg.FILE_NAME, "w")
            file_out.write(documentation)
        else:
            sys.stdout.write(documentation)


# !!!!!!!!!!MAIN!!!!!!!!!!!!!!!!!!!
def set_cmd_arguments():
    # Parse of arguments
    parser = argparse.ArgumentParser(description='Documentation generator which creates documentation from tagged '
                                                 'documentation comments')
    parser.add_argument('files',
                        metavar='file',
                        type=str,
                        nargs='+',
                        help='script file')

    parser.add_argument('-o', '--output',
                        dest='FILE_NAME',
                        type=str,
                        default=False,
                        help='Save documentation into file with specified name.')
    parser.add_argument('--additional',
                        dest='additional_info',
                        default=False,
                        action='store_true',
                        help='This option shows additional information section in test documentation')
    return parser.parse_args()


def run_markup_doc_generator(parsed_arg):
    # cycle of script files to be transformed to documentation
    for file_in_cmd in parsed_arg.files:
        part = Generator(file_in_cmd)
        part.parse_file()
        part.comments_set_up()
        part.show_documentation_data(parsed_arg)


if __name__ == "__main__":
    CMD_args = set_cmd_arguments()
    run_markup_doc_generator(CMD_args)
