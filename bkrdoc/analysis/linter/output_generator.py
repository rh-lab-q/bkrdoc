#!/usr/bin/python
from __future__ import print_function
import argparse, bashlex
import sys
from bkrdoc.analysis.parser import bkrdoc_parser
from bkrdoc.analysis.linter import linter, common
from bkrdoc.analysis.linter.catalogue import catalogue

__author__ = 'Zuzana Baranova'

Severity = common.Severity

class OutputGenerator(object):

    def __init__(self, args):
        self.main_linter = linter.Linter()
        self.parser_ref = bkrdoc_parser.Parser(args.file_in)
        self.options = self.Options(args)
        self.main_linter.errors += self.options.unrecognized_options

    def analyse(self):
        try:
            self.parser_ref.parse_data()
        except bashlex.errors.ParsingError:
            print("bashlex parse error: cannot continue~\ntraceback follows:\n", file=sys.stderr)
            raise
        self.main_linter.errors += self.parser_ref.get_errors()
        self.main_linter.analyse(self.parser_ref.argparse_data_list)

    def print_to_stdout(self):
        #for elem in self.parser_ref.argparse_data_list:
        #    print(elem)
        err_list = self.main_linter.errors

        if not err_list or all([err.id == 'UNK_FLAG' for err in err_list]):
            print("Static analysis revealed no errors.")
        else:
            for elem in err_list:
                if not elem.severity or elem.severity and self.is_enabled_error(elem):
                    print(self.pretty_format(elem))


    def is_enabled_error(self, error):
        return (self.is_enabled_severity(error.severity) and error.id not in self.options.suppressed_by_id) \
               or (not self.is_enabled_severity(error.severity) and error.id in self.options.enabled_by_id)

    def is_enabled_severity(self, severity):
        return self.options.enabled[severity]

    @staticmethod
    def pretty_format(err):
        if err.id and err.id is not 'UNK_FLAG' :
            return '{} [{}]'.format(err.message, err.id)
        else:
            return err.message


    class Options(object):

        def __init__(self, options):
            self.enabled = {Severity.error: True,
                            Severity.warning: False,
                            Severity.info: False}
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

            for error_list in option_order:
                if error_list:
                    is_enabled = True if error_list == options.enabled else False
                    for err in error_list:
                        self.set_err_list(err, is_enabled=is_enabled)

        def set_err_list(self, err_data, is_enabled):
            set_severity_to, related_list = self.get_related_member_list(is_enabled)
            severities = self.enabled.keys()

            if err_data == "all":
                for severity in severities:
                    self.enabled[severity] = set_severity_to
                    if is_enabled:
                        self.suppressed_by_id = []  # if enable=all, clear suppress_by_id list & vice versa
                    else:
                        self.enabled_by_id = []
            else:
                for single_err in err_data.split(','):

                    if single_err in [sev.name for sev in Severity]:
                        self.enabled[Severity[single_err]] = set_severity_to
                    elif single_err in self.known_errors:
                        related_list.append(single_err)
                    elif single_err in catalogue.keys():
                        related_list += (catalogue[single_err][key][0] for key in catalogue[single_err])
                    else:
                        msg = '{} not recognized, continuing anyway--'.format(single_err)
                        self.unrecognized_options.append(common.Error(id='UNK_FLAG',message=msg))

        def get_related_member_list(self, is_enabled):
            if is_enabled:
                return True, self.enabled_by_id
            else:
                return False, self.suppressed_by_id

        @staticmethod
        def get_known_errors():
            known_errs = []
            for err_class in catalogue:
                known_errs += (catalogue[err_class][key][0] for key in catalogue[err_class])
            return known_errs


def set_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('file_in', type=str)
    argp.add_argument('-s', dest='suppress_first', action='store_true', default=False)
    argp.add_argument('--enable', type=str, dest='enabled', action='append')
    argp.add_argument('--suppress', type=str, dest='suppressed', action='append')
    parsed_args = argp.parse_args()
    return parsed_args


# ***************** MAIN ******************
if __name__ == "__main__":
    args = set_args()
    gener = OutputGenerator(args)
    gener.analyse()
    gener.print_to_stdout()