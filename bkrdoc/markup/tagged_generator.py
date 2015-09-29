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

    def get_documentation_title_doc(self):
        self.get_title_data()
        title_data = self.phases[0].comments_list[0].get_title_data()
        documentation = "Description: {0}\n".format(title_data["description"])
        documentation += "Author: {0}\n".format(title_data["author"])
        if title_data["key"]:
            documentation += "Keywords: {0}, {1}".format(title_data["keywords"], title_data["key"])
        else:
            documentation += "Keywords: {0}".format(title_data["keywords"])
        # need to erase shared title data
        self.erase_title_data()
        return documentation

    def get_phase_data_documentation(self):
        documentation = "Phases:\n"
        for phase in self.phases:
            documentation += phase.print_documentation()
        return documentation

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

    def is_condition_container(self, container):
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

    def get_documentation(self):
        documentation = self.get_documentation_title_doc()
        documentation += "\n\n"
        documentation += self.get_phase_data_documentation()
        documentation += "Expected results:\n"
        documentation += "\n"
        documentation += self.generate_additional_info()
        return documentation

    def show_documentation_data(self, parsed_arg):
        documentation = self.get_documentation()
        if parsed_arg:
            file_out = open(parsed_arg, "w")
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
    return parser.parse_args()


def run_doc_generator(parsed_arg):
    # cycle of script files to be transformed to documentation
    for file_in_cmd in parsed_arg.files:
        part = Generator(file_in_cmd)
        part.parse_file()
        part.comments_set_up()
        part.show_documentation_data(parsed_arg.FILE_NAME)


if __name__ == "__main__":
    CMD_args = set_cmd_arguments()
    run_doc_generator(CMD_args)

