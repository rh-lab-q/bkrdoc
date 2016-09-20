__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import common
from bkrdoc.analysis.parser import bkrdoc_parser, conditions_for_commands


class LinterWithinPhase(common.LinterRule):
    """
    Class that checks for violations of rules that are specific within a single phase,
    e.g. a name has to be unique within a phase.
    Also checks for presence of empty phases.
    """

    METRICNAME = "rlLogMetric name has to be unique within a phase"
    EMPTY_PHASE = "Useless empty phase found."
    OUTSIDE_PHASE = "Command outside of phase found."

    def __init__(self):
        super(LinterWithinPhase, self).__init__()
        self.depth_of_nesting = 0
        self.last_command = None

        # list of lists of used metric names for each depth level
        # 0 is outside phase
        self.log_metric_names = [[]]

    def analyse(self, line):
        cond = conditions_for_commands.ConditionsForCommands()

        if self.is_phase_begin(line.argname):
            self.depth_of_nesting += 1
            self.log_metric_names.append([])

        elif cond.is_phase_end(line.argname):
            # empty phases
            if self.is_phase_begin(self.last_command):
                self.add_error('1500', 'empty_phase',
                               self.EMPTY_PHASE,
                               line.lineno)
            if self.depth_of_nesting > 0:
                self.depth_of_nesting -= 1
                del self.log_metric_names[-1]
        else:
            if self.depth_of_nesting == 0 and line.argname in bkrdoc_parser.Parser.beakerlib_commands:
                if not self.is_allowed_outside_phase(line):
                    self.add_error('1500', 'out_of_phase',
                                   "{} ({})".format(self.OUTSIDE_PHASE, line.argname),
                                   line.lineno)

            if cond.is_rllogmetric_command(line.argname):
                if line.name in self.get_used_metric_names():
                    self.add_error('1500', 'rlLogMetric',
                                   "{} ({})".format(self.METRICNAME, line.name),
                                   line.lineno)
                else:
                    self.log_metric_names[-1].append(line.name)

        self.last_command = line.argname


    @staticmethod
    def is_phase_begin(command):
        return command in bkrdoc_parser.Parser.start_phase_names

    def get_used_metric_names(self):
        return [name for namelist in self.log_metric_names for name in namelist]

    @staticmethod
    def is_allowed_outside_phase(command):
        common_ = common.LinterRule
        cond = conditions_for_commands.ConditionsForCommands()
        return any([cond.is_journal_start(command),
                   cond.is_journal_end(command),
                   common_.is_allowed_outside_journal(command)])
