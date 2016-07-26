__author__ = 'Zuzana Baranova'

import re
from bkrdoc.analysis.linter import common
from bkrdoc.analysis.linter.catalogue import catalogue


class LinterArgTypes(common.LinterRule):

    STATUS_NOT_INT = "status must be an enumeration (1,2), a range (2-5) or a combination of the two (of integral type)"
    SIGNAL = "is not recognized as one of the most common signals - make sure it's valid"
    RESULT = "is not one of (PASS,WARN,FAIL), WARN will be reported"
    OS_TYPE_INVALID = "OS type checked for must be in format >=5.0 where '>=' can be any of >=,>,<=,<,= or nothing"

    commands_to_check = {'rlRun': [('status', 'check_status', 'STATUS_NOT_INT')],
                         'rlWatchdog': [('signal', 'check_signal', 'SIGNAL')],
                         'rlReport': [('result', 'check_result', 'RESULT')],
                         'rlIsRHEL': [('type', 'check_os_type', 'OS_TYPE_INVALID')],
                         'rlIsFedora': [('type', 'check_os_type', 'OS_TYPE_INVALID')]}

    common_signals = ['KILL', 'TERM', 'QUIT', 'INT', 'STOP', 'HUP', 'ILL', 'TRAP',
                      'ABRT', 'BUS', 'FPE', 'USR1', 'USR2', 'SEGV', 'PIPE', 'ALRM',
                      'CHLD', 'CONT', 'TTIN', 'TTOU', 'IO', 'SYS', 'TSTP']

    def __init__(self, parsed_input_list):
        super(LinterArgTypes, self).__init__()
        self.parsed_input_list = parsed_input_list
        self.lineno = 0
        self.argname = ""

    def analyse(self):
        for line in self.parsed_input_list:
            args_to_check = self.commands_to_check.get(line.argname)
            self.argname = line.argname
            self.lineno = line.lineno
            if not args_to_check:
                continue
            for (arg,func,msg) in args_to_check:
                attr = getattr(line, arg)
                func = getattr(self, func)
                msg  = getattr(self, msg)
                func(attr, msg)

    def check_status(self, statuses, msg):
        def is_valid_status(num):
            return self.can_cast_to_type(num, float) and self.is_within_range(num, 0, 256)

        for single_range in [n for n in statuses.split(',')]:
            numbers = single_range.split('-')
            if len(numbers) > 2 or any(not is_valid_status(number) for number in numbers):
                id, severity = catalogue['3000']['rlRun']
                self.add_error(id, severity, self.argname + ", " + msg, self.lineno)
                return

    def check_signal(self, tested_signal, msg):
        for signal in self.common_signals:
            if tested_signal in [signal, "SIG"+signal]:
                return
        id, severity = catalogue['3000']['rlWatchdog']
        self.add_error(id, severity, "{}, `{}` {}".format(self.argname,tested_signal,msg), self.lineno)

    def check_result(self, result, msg):
        if result not in ['PASS', 'WARN', 'FAIL']:
            id, severity = catalogue['3000']['rlReport']
            self.add_error(id, severity, "{}, `{}` {}".format(self.argname,result,msg), self.lineno)

    def check_os_type(self, types, msg):
        for type in types:
            split_string = re.split('(\d)', type, 1) # split on first number
            numeric_part = ('').join(split_string[1:3])
            if split_string[0] in ['<=','<','>=','>','','='] and self.can_cast_to_type(numeric_part, float):
                continue
            id, severity = catalogue['3000']['rhel_fedora']
            self.add_error(id, severity, "{}, `{}` - {}".format(self.argname,type,msg), self.lineno)

    @staticmethod
    def can_cast_to_type(argument, type):
        try:
            type(argument)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_within_range(num, min, max):
        num = int(num)
        return min <= num < max
