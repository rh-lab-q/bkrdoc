__author__ = 'jkulda'

import argparse
import sys
from tagged_parser import Parser


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
                self.fail = False
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)
        else:
            print "ERROR: Not a script file. (.sh)"
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

    def generate_documentation_title(self):
        self.get_title_data()
        title_data = self.phases[0].comments_list[0].get_title_data()
        print "Description: {0}".format(title_data["description"])
        print "Author: {0}".format(title_data["author"])
        if title_data["key"]:
            print "Keywords: {0}, {1}".format(title_data["keywords"], title_data["key"])
        else:
            print "Keywords: {0}".format(title_data["keywords"])

    def generate_phase_data(self):
        print "Phases:"
        for phase in self.phases:
            phase.print_documentation()

    def print_additional_container_data(self, name, additional_containers):
        if len(additional_containers):
            print "  {0}:".format(name)
            for container in additional_containers:
                container.print_additional_phase_data()
                if len(additional_containers) > 1:
                    print ""
            print("")

    def generate_additional_info(self):
        print "Additional information:"
        func = []
        loop = []
        cond = []
        for phase in self.phases:
            func, loop, cond = phase.get_additional_containers(func, loop, cond)

        self.print_additional_container_data("Functions", func)
        self.print_additional_container_data("Loops", loop)
        self.print_additional_container_data("Conditions", cond)

    def generate_documentation(self):
        self.generate_documentation_title()
        print ""
        self.generate_phase_data()
        print ""
        print "Expected results:"
        print ""
        self.generate_additional_info()


# !!!!!!!!!!MAIN!!!!!!!!!!!!!!!!!!!
def set_cmd_arguments():
    # Parse of arguments
    parser = argparse.ArgumentParser(description='Parse arguments in cmd line for generator')
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('files',
                        metavar='file',
                        type=str,
                        nargs='+',
                        help='script file')

    group.add_argument('--txt', '--TXT',
                       dest='text_in',
                       action='store_true',
                       default=False,
                       help='argument to make txt doc file output')

    group.add_argument('--moin', '--MOIN',
                       dest='moin_in',
                       action='store_true',
                       default=False,
                       help='argument to make moinmoin doc file output')

    parser.add_argument('-o', '--output',
                        dest='out_in',
                        action='store_true',
                        default=False,
                        help='argument to save documentation to ouptut file')
    return parser.parse_args()


def run_doc_generator(parsed_arg):
    # cycle of script files to be transformed to documentation
    for file_in_cmd in parsed_arg.files:
        part = Generator(file_in_cmd)
        part.parse_file()
        part.comments_set_up()
        part.generate_documentation()
        #part.parse_tags()
        #foo = NewTextDoc(part)
        #foo.parse_data()
        #if (not parser_arg.text_in and not parser_arg.moin_in) or \
        #        parser_arg.text_in:
        #    foo.text_output(parser_arg.out_in)
        #elif parser_arg.moin_in:
        #    foo.moin_output(parser_arg.out_in)


if __name__ == "__main__":
    CMD_args = set_cmd_arguments()
    run_doc_generator(CMD_args)

