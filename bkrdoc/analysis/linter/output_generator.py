#!/usr/bin/python
from __future__ import print_function
import sys
import argparse
import bashlex
from bkrdoc.analysis.parser import bkrdoc_parser
from bkrdoc.analysis.linter import linter, common, catalogue

__author__ = 'Zuzana Baranova'

Severity = catalogue.Severity
CATALOGUE = catalogue.Catalogue.table


class OutputGenerator(object):

    VERSION = '1.0.0'

    NOERRORS = "Static analysis revealed no errors."
    BASHLEX_ERR = "bashlex parse error: cannot continue~\n" \
                  "traceback follows:\n"

    def __init__(self, arguments):
        self.main_linter = linter.Linter()
        self.parser_ref = bkrdoc_parser.Parser(arguments.file_in)
        self.options = self.Options(arguments)
        self.main_linter.errors += self.options.unrecognized_options

    def analyse(self):
        try:
            self.parser_ref.parse_data()
        except bashlex.errors.ParsingError:
            print(self.BASHLEX_ERR, file=sys.stderr)
            raise
        self.main_linter.errors += self.parser_ref.get_errors()
        self.main_linter.analyse(self.parser_ref.argparse_data_list)

    def print_to_stdout(self):
        #for elem in self.parser_ref.argparse_data_list:
        #    print(elem)

        error_was_printed = False
        sorted_err_list = iter(sorted(self.main_linter.errors))
        for error in sorted_err_list:
            if error.err_id != 'UNK_FLAG':
                if not error.severity or error.severity and self.is_enabled_error(error):
                    print("")
                    print(self.pretty_format(error))
                    error_was_printed = True
                break
            print(self.pretty_format(error))

        if not error_was_printed:
            print("")
        for err in sorted_err_list:
            if not err.severity or err.severity and self.is_enabled_error(err):
                print(self.pretty_format(err))
                error_was_printed = True
        if not error_was_printed:
            print(self.NOERRORS)

    def is_enabled_error(self, error):
        return (self.is_enabled_severity(error.severity) and error.err_id not in self.options.suppressed_by_id) \
               or (not self.is_enabled_severity(error.severity) and error.err_id in self.options.enabled_by_id)

    def is_enabled_severity(self, severity):
        return self.options.enabled[severity]

    @staticmethod
    def pretty_format(error):
        if error.err_id and error.err_id is not 'UNK_FLAG':
            result = '{} [{}]'.format(error.message, error.err_id)
        else:
            result = error.message
        if error.lineno != 0:
            return '{}: {}'.format(str(error.lineno), result)
        return result

    @staticmethod
    def print_info():
        print("bkrlint :: version {}".format(OutputGenerator.VERSION))

    class Options(object):

        def __init__(self, options):
            self.enabled = {Severity.error: True,
                            Severity.warning: False,
                            Severity.info: False,
                            Severity.style: False}
            self.enabled_by_id = []
            self.suppressed_by_id = []
            self.unrecognized_options = []
            self.known_errors = self.get_known_errors()

            self.resolve_enabled_options(options)

        def resolve_enabled_options(self, options):

            if options.suppress_first:
                option_order = [options.suppressed, options.enabled]
            else:
                option_order = [options.enabled, options.suppressed]

            for option_list in option_order:
                if option_list:
                    is_enabled = True if option_list == options.enabled else False
                    for opt in option_list:
                        self.set_opt_list(opt, is_enabled=is_enabled)

        def set_opt_list(self, opt_data, is_enabled):
            set_severity_to, related_list = self.get_related_member_list(is_enabled)
            severities = self.enabled.keys()

            if opt_data == "all":
                for severity in severities:
                    self.enabled[severity] = set_severity_to
                    if is_enabled:
                        self.suppressed_by_id = []  # if enable=all, clear suppress_by_id list & vice versa
                    else:
                        self.enabled_by_id = []
            else:
                for single_opt in opt_data.split(','):

                    if single_opt in [sev.name for sev in Severity]:
                        self.enabled[Severity[single_opt]] = set_severity_to
                    elif single_opt in self.known_errors:
                        related_list.append(single_opt)
                    elif single_opt in CATALOGUE.keys():
                        related_list += (CATALOGUE[single_opt].value[key][0] for key in CATALOGUE[single_opt].value)
                    else:
                        msg = '{} not recognized, continuing anyway--'.format(single_opt)
                        self.unrecognized_options.append(common.Error(err_id='UNK_FLAG', message=msg))

        def get_related_member_list(self, is_enabled):
            if is_enabled:
                return True, self.enabled_by_id
            else:
                return False, self.suppressed_by_id

        @staticmethod
        def get_known_errors():
            known_errs = []
            for err_class in CATALOGUE:
                known_errs += (CATALOGUE[err_class].value[key][0] for key in CATALOGUE[err_class].value)
            return known_errs


def set_args():
    argp = argparse.ArgumentParser(description='Linter for BeakerLib-specific mistakes in BeakerLib tests.')
    argp.add_argument('file_in', type=str, help='input file', nargs='?')
    argp.add_argument('-s', dest='suppress_first', action='store_true', default=False, help='suppress first')
    argp.add_argument('--enable', type=str, dest='enabled', action='append')
    argp.add_argument('--suppress', type=str, dest='suppressed', action='append')
    argp.add_argument('--catalogue', dest='catalogue', action='store_true', default=False, help='generate catalogue.md')
    parsed_args = argp.parse_args()
    return parsed_args


# ***************** MAIN ******************
if __name__ == "__main__":
    args = set_args()

    OutputGenerator.print_info()
    if args.catalogue:
        catalogue.Catalogue().output_as_markdown_file()
    if args.file_in:
        gener = OutputGenerator(args)
        gener.analyse()
        gener.print_to_stdout()
    elif not args.catalogue:
        print("Input file must be specified.\n")
        sys.argv.append("--help")
        set_args()
