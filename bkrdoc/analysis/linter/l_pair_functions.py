__author__ = 'Zuzana Baranova'

import copy
from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser


class Match(object):
    """
    Class defining a matching pair of commands.

    :param func: Opening command
    :param pair: Closing command
    :param before: List of commands (if any) which should be preceded by a Closing command if the Opening one was present,
                   i.e. Start -> Stop -> Restore;  Restore should not appear before Stop
    :param each_needs_match: Bool value stating whether each Opening command needs a Closing one or
                             a single Closing command closes all Opening commands (with matching flag)
    :param flag_source: String defining an attribute value of Namespace where the flag/name is located, can be None
    :param flag: Concrete flag of a command whose pair with matching flag is searched for
    :param restores_all: a flagless Closing command closes everything regardless of flag
    """
    def __init__(self, func, pair, before=[], each=False, flag_source=None, restores_all=False):
        self.func = func
        self.pair = pair
        self.before = before
        self.each_needs_match = each
        self.restores_all = restores_all
        self.flag_source = flag_source
        self.flag = None

    def set_flag(self, flag):
        self.flag = flag


class LinterPairFunctions(common.LinterRule):
    """Does the logical analysis of matching paired commands."""

    start_phase_names = bkrdoc_parser.Parser.start_phase_names

    pairs = {'rlPhaseStart': Match('rlPhaseStart', 'rlPhaseEnd', before=start_phase_names, each=True),
             'rlPhaseStartTest': Match('rlPhaseStartTest', 'rlPhaseEnd', before=start_phase_names, each=True),
             'rlPhaseStartSetup': Match('rlPhaseStartSetup', 'rlPhaseEnd', before=start_phase_names, each=True),
             'rlPhaseStartCleanup': Match('rlPhaseStartCleanup', 'rlPhaseEnd', before=start_phase_names, each=True),
             'rlFileBackup': Match('rlFileBackup', 'rlFileRestore', flag_source='namespace'),
             'rlVirtualXStart': Match('rlVirtualXStart', 'rlVirtualXStop', flag_source='name'),
             'rlServiceStart': Match('rlServiceStart', 'rlServiceStop', before=['rlServiceRestore'], flag_source='service'),
             'rlSEBooleanOn': Match('rlSEBooleanOn', 'rlSEBooleanRestore', flag_source='boolean', restores_all=True),
             'rlSEBooleanOff': Match('rlSEBooleanOff', 'rlSEBooleanRestore', flag_source='boolean', restores_all=True)}

    currently_unmatched = []

    def __init__(self, _list):
        self.currently_unmatched = []
        self.errors = []
        self._list = _list

    def analyse(self):

        for line in self._list:
            match = self.get_relevant_match(line.argname)
            line_flags = self.get_flag(line, match)
            if isinstance(line_flags, list):
                if not line_flags:
                    line_flags = [None]       # analyse commands with empty optional argument lists
                for _flag in line_flags:
                    setattr(line, match.flag_source, _flag)
                    self.analyse_single_line(line)
            else:
                self.analyse_single_line(line)

        for elem in self.currently_unmatched:
            self.add_error(elem.func + " without a matching " + elem.pair, flag=elem.flag)

    def analyse_single_line(self, line):

        for elem in self.currently_unmatched:
                if self.command_is_before_end_function(line, elem):
                    self.add_error(line.argname + " before matching " + elem.pair)

        if self.is_end_function_that_restores_all(line):
            size_before_filter = len(self.currently_unmatched)
            self.currently_unmatched = [x for x in self.currently_unmatched if x.pair != line.argname]
            if size_before_filter > len(self.currently_unmatched):
                return   # would mess looking for Ends without Begins

        for elem in self.currently_unmatched:
            if self.matches_opposite(line, elem):
                self.currently_unmatched.remove(elem)
                return

        if line.argname in self.pairs.keys() and (self.pairs[line.argname].each_needs_match or not self.already_present(line)):
            match = copy.deepcopy(self.pairs[line.argname])
            match.set_flag(self.get_flag(line, match))
            self.currently_unmatched.insert(0, match)

        elif line.argname in [x.pair for x in self.pairs.values()]:
            flag = self.get_flag(line, self.get_relevant_match(line.argname))
            self.add_error(line.argname + " without a previous begin", flag=flag)

    def get_relevant_match(self, command):
        """Fetches the Match instance from 'pairs' map associated with 'command'
        (is the command, its pair or in 'before' of the command)."""
        if command in self.pairs.keys():
            return self.pairs[command]
        for entry in self.pairs.values():
            if command == entry.pair or command in entry.before:
                return entry

    def command_is_before_end_function(self, line, elem):
        """Checks whether analysed line consists of a command that is
        (and should not happen) before elem's ending pair."""
        return elem.before is not None \
               and line.argname in elem.before \
               and elem.flag == self.get_flag(line, elem)

    def is_end_function_that_restores_all(self, line):
        match = self.get_relevant_match(line.argname)
        return match is not None \
               and line.argname == match.pair \
               and match.restores_all \
               and not self.get_flag(line, match)

    def matches_opposite(self, line, elem):
        return line.argname == elem.pair \
               and (not elem.flag_source or elem.flag == self.get_flag(line, elem))

    def already_present(self, line):
        match = self.pairs[line.argname]
        line_flag = self.get_flag(line, match)
        return (match.pair, line_flag) in [(x.pair, x.flag) for x in self.currently_unmatched]

    @staticmethod
    def get_flag(line, elem):
        if not elem or not elem.flag_source:
            return None
        return getattr(line, elem.flag_source)

