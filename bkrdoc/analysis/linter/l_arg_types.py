__author__ = 'Zuzana Baranova'

import re
from bkrdoc.analysis.linter import common


class LinterArgTypes(common.LinterRule):
    """Class that checks for specific type errors of beakerlib arguments,
    such as: a status (bash command return code) must be an integer within range 0-255 etc.
    Some are of info type for it is unclear whether the input is invalid for certain."""

    # err_label, message
    NONNEGATIVE = "has to be a non-negative integer"
    TIMEOUT = 'time', "timeout in seconds"
    PID = 'pid', "PID number"
    COUNT = 'count', "max. number of executions"
    DELAY = 'delay', 'delay between executions'

    STATUS_NOT_INT = "status must be an enumeration (1,2), a range (2-5) or a combination of the two (of integral type)"
    SIGNAL = "is not recognized as one of the most common signals - make sure it's valid"
    RESULT = "is not one of (PASS,WARN,FAIL), WARN will be reported"
    OS_TYPE_INVALID = "OS type checked for must be in format >=5.0 where '>=' can be any of >=,>,<=,<,= or nothing"
    HASH_ALGO = "hash algorithm has to be one of: "
    RETVAL = "return value should be an integer within range (0,255)"

    # command: (namespace variable name, function to call, message ^)
    commands_to_check = {'rlRun': [('status', 'check_status', 'STATUS_NOT_INT')],
                         'rlWatchdog': [('signal', 'check_signal', 'SIGNAL')],
                         'rlReport': [('result', 'check_result', 'RESULT')],
                         'rlIsRHEL': [('type', 'check_os_type', 'OS_TYPE_INVALID')],
                         'rlIsFedora': [('type', 'check_os_type', 'OS_TYPE_INVALID')],
                         'rlHash': [('algorithm', 'check_hash_algo', 'HASH_ALGO')],
                         'rlUnhash': [('algorithm', 'check_hash_algo', 'HASH_ALGO')],
                         'rlWaitForCmd': [('time', 'check_nonnegative', 'TIMEOUT'),
                                          ('pid', 'check_nonnegative', 'PID'),
                                          ('count', 'check_nonnegative', 'COUNT'),
                                          ('delay', 'check_nonnegative', 'DELAY'),
                                          ('retval', 'check_retval', 'RETVAL')],
                         'rlWaitForFile': [('time', 'check_nonnegative', 'TIMEOUT'),
                                           ('pid', 'check_nonnegative', 'PID'),
                                           ('delay', 'check_nonnegative', 'DELAY')],
                         'rlWaitForSocket': [('time', 'check_nonnegative', 'TIMEOUT'),
                                          ('pid', 'check_nonnegative', 'PID'),
                                          ('delay', 'check_nonnegative', 'DELAY')],
                         'rlWait': [('signal', 'check_signal', 'SIGNAL'),
                                    ('time', 'check_nonnegative', 'TIMEOUT'),
                                    ('pids', 'check_pids', 'PID')]}

    common_signals = ['KILL', 'TERM', 'QUIT', 'INT', 'STOP', 'HUP', 'ILL', 'TRAP',
                      'ABRT', 'BUS', 'FPE', 'USR1', 'USR2', 'SEGV', 'PIPE', 'ALRM',
                      'CHLD', 'CONT', 'TTIN', 'TTOU', 'IO', 'SYS', 'TSTP']

    valid_hash_algorithms = ['base64', 'base64_', 'hex']

    def __init__(self):
        super(LinterArgTypes, self).__init__()
        self.lineno = 0
        self.argname = ""

    def analyse(self, line):
        args_to_check = self.commands_to_check.get(line.argname)
        self.argname = line.argname
        self.lineno = line.lineno
        if not args_to_check:
            return
        for (arg, func, msg) in args_to_check:
            attr = getattr(line, arg)
            func = getattr(self, func)
            msg  = getattr(self, msg)
            func(attr, msg)

    def check_status(self, statuses, msg):
        for single_range in [n for n in statuses.split(',')]:
            numbers = single_range.split('-')
            if len(numbers) > 2 or any(not self.is_valid_status(number) for number in numbers):
                self.add_error('3000', 'rlRun_type',
                               "{}, {} in `{}`".format(self.argname, msg, single_range),
                               self.lineno)
                return
            if len(numbers) == 2 and self.int_(numbers[0]) > self.int_(numbers[1]):
                msg2 = "first bound has to be smaller in `{}`".format(single_range)
                self.add_error('3000', 'rlRun_bounds',
                               self.argname + ", " + msg2,
                               self.lineno)

    def check_signal(self, tested_signal, msg):
        for signal in self.common_signals:
            if tested_signal.upper() in [signal, "SIG"+signal]:
                return
        self.add_error('3000', self.argname + "_signal",
                       "{}, `{}` {}".format(self.argname, tested_signal, msg),
                       self.lineno)

    def check_result(self, result, msg):
        if result.upper() not in ['PASS', 'WARN', 'FAIL']:
            self.add_error('3000', 'rlReport',
                           "{}, `{}` {}".format(self.argname, result, msg),
                           self.lineno)

    def check_os_type(self, types, msg):
        valid_prefixes = ['<=','<','>=','>','','=']
        for type_ in types:
            split_string = re.split('(\d)', type_, 1)  # split on first number
            numeric_part = ''.join(split_string[1:3])

            if split_string[0] in valid_prefixes and self.can_cast_to_type(numeric_part, float):
                continue
            self.add_error('3000', 'rhel_fedora',
                           "{}, `{}` - {}".format(self.argname, type_, msg),
                           self.lineno)

    def check_hash_algo(self, algo, msg):
        if algo not in self.valid_hash_algorithms:
            self.add_error('3000', 'hash_algo',
                           "{}, {} {} (was `{}`)".format(self.argname, msg, ', '.join(self.valid_hash_algorithms), algo),
                           self.lineno)

    def check_nonnegative(self, value, info):
        err_label, msg = info
        if not self.is_nonnegative_int(value):
            self.add_error('3000', err_label,
                           "{}, `{}` - {}, {}".format(self.argname, value, msg, self.NONNEGATIVE), self.lineno)

    def check_pids(self, pids, info):
        for pid in pids:
            self.check_nonnegative(pid, info)

    def check_retval(self, retval, msg):
        if not self.is_valid_status(retval):
            self.add_error('3000', 'retval',
                           "{}, `{}` - {}".format(self.argname, retval, msg),
                           self.lineno)

    def is_valid_status(self, num):
            return self.can_cast_to_type(num, float) and self.is_within_range(num, 0, 256)

    def is_nonnegative_int(self, val):
        return val is None or (self.can_cast_to_type(val, int) and int(val) >= 0)

    @staticmethod
    def can_cast_to_type(argument, type):
        try:
            type(argument)
        except ValueError:
            return False
        return True

    def is_within_range(self, num, min, max):
        num = self.int_(num)
        return min <= num < max

    @staticmethod
    def int_(num):
        return int(float(num))
