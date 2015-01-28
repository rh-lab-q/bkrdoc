#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex
import re          
import argparse
            
class parser(object):
    
    lexer = shlex
    
    file_test = ""
    
    description = ""
    
    all_commands = ["rlAssert0", "rlAssertEquals", "rlAssertNotEquals",\
    "rlAssertGreater", "rlAssertGreaterOrEqual", "rlAssertExists", "rlAssertNotExists",\
    "rlAssertGrep", "rlAssertNotGrep", "rlAssertDiffer", "rlAssertNotDiffer", "rlRun",\
    "rlWatchdog", "rlReport", "rlIsRHEL", "rlIsFedora", "rlCheckRpm", "rlAssertRpm", \
    "rlAssertNotRpm", "rlAssertBinaryOrigin", "rlGetMakefileRequires", \
    "rlCheckRequirements", "rlCheckMakefileRequires", "rlMount", "rlCheckMount", \
    "rlAssertMount", "rlHash", "rlUnhash", "rlFileBackup", "rlFileRestore", \
    "rlServiceStart", "rlServiceStop", "rlServiceRestore", "rlSEBooleanOn",\
    "rlSEBooleanOff", "rlSEBooleanRestore", "rlCleanupAppend", "rlCleanupPrepend",\
    "rlVirtualXStop", "rlVirtualXGetDisplay", "rlVirtualXStart", "rlWait", "rlWaitForSocket",\
    "rlWaitForFile", "rlWaitForCmd", "rlImport", "rlDejaSum", "rlPerfTime_AvgFromRuns",\
    "rlPerfTime_RunsinTime", "rlLogMetricLow", "rlLogMetricHigh", "rlShowRunningKernel", \
    "rlGetDistroVariant", "rlGetDistroRelease", "rlGetSecondaryArch", "rlGetPrimaryArch", \
    "rlGetArch", "rlShowPackageVersion", "rlFileSubmit", "rlBundleLogs", "rlDie", \
    "rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo", "rlLogDebug", "rlLog",\
    "rlGetTestState", "rlGetPhaseState"
    ]
    
    commands_with_no_options = ["rlGetTestState", "rlGetPhaseState", "rlGetArch", \
    "rlGetPrimaryArch", "rlGetSecondaryArch", "rlGetDistroRelease", "rlGetDistroVariant",\
    "rlShowRunningKernel", "rlPass", "rlFail", "rlAssert0", "rlAssertEquals",\
    "rlAssertNotEquals", "rlAssertGreater", "rlAssertGreaterOrEqual", "rlAssertExists",\
    "rlAssertNotExists", "rlAssertDiffer", "rlAssertNotDiffer","rlGetMakefileRequires",\
    "rlCheckRequirements", "rlCheckMakefileRequires", "rlMount", "rlCheckMount", \
    "rlAssertMount", "rlCleanupAppend", "rlCleanupPrepend", "rlDejaSum",\
    "rlVirtualXStart", "rlVirtualXGetDisplay", "rlVirtualXStop" ]
    
    
    phases = []
    outside = ""
    
    def __init__(self, file_in):
        self.phases = []
        
        if file_in[(len(file_in) - 3):len(file_in)] == ".sh":
            try:                
                with open(file_in, "r") as inputfile:
                    inputfile = open(file_in ,"r")
                    self.description = file_in[0:(len(file_in) - 3)]
                    self.file_test = inputfile.read()
                    self.parse_data()

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)
                
        else:
            print "ERROR: Not a script file. (.sh)"
            sys.exit(1)
            
            
    def parse_data(self):
        journal = False
        self.phases.append(phase_outside())
        
        pom_line = ""
        for line in self.file_test.split('\n'):
            line = line.strip()
            
            if line[0:1] != '#' and len(line) > 1 and \
            not self.is_phase_journal_end(line) :
                
                if self.is_phase_setup(line):
                    self.phases.append(phase_setup(line[len("rlphasestart"):]))
                    
                elif self.is_phase_test(line):
                    self.phases.append(phase_test(line[len("rlphasestart"):]))
                
                elif self.is_phase_clean(line):
                    self.phases.append(phase_clean(line[len("rlphasestart"):]))
                    
                elif self.is_end_back_slash(line):
                    pom_line = line[0:-1]
                
                elif len(self.phases) > 0:
                    if pom_line != "":
                        self.phases[-1].setup_statement(pom_line + line)
                        pom_line = ""
                    else:
                        self.phases[-1].setup_statement(line)
            
            elif self.is_phase_journal_end(line):
                self.phases.append(phase_outside())

        
    def print_statement(self):
        #self.outside.search_data()
        for i in self.phases:
            print i.statement_list
            print "\n"
        
    def is_end_back_slash(self, line):
        return line[-1:] == '\\'
    
    def get_doc_data(self):
        for member in self.phases:
            member.search_data(self)
    
    def is_no_option_command(self, command):
        return command in self.commands_with_no_options
        
    def is_phase_clean(self, line):
        return line[0:len("rlphasestartclean")].lower() == "rlphasestartclean"
        
    def is_phase_test(self, line):
        return line[0:len("rlphasestarttest")].lower() == "rlphasestarttest"
        
    def is_phase_setup(self, line):
        return line[0:len("rlphasestartsetup")].lower() == "rlphasestartsetup"
        
    def is_phase_journal_end(self, line):
        if line[0:len("rlphaseend")].lower() == "rlphaseend":
            return True
        
        elif line[0:len("rljournalend")].lower() == "rljournalend":
            return True
        
        else:
            return False
        
    def is_journal_start(self, line):
        return line[0:len("rljournalstart")].lower() == "rljournalstart"
        
    def is_phase_outside(self,phase_ref):
        return phase_ref.phase_name == "Outside phase"
        
    def is_beakerLib_command(self,testing_command):
        return testing_command in self.all_commands
        
    def search_variable(self, phase_ref, searching_variable):
        pom_pos = 0
        pom_variable = ""
        
        for member in self.phases:
            if self.is_phase_outside(member):
                pom_pos = member.get_variable_position(searching_variable)
                if pom_pos >= 0:
                    pom_variable = member.variable_values_list[pom_pos] 
    
            elif member == phase_ref:
                if pom_variable == "":
                    print "UNKNOWN VARIABLE !!!"
                return pom_variable
                
        
        
        
class phase_outside:
    """Class for searching data ourside of phases"""
    #parse_ref = ""
    phase_name = ""
    statement_list = []
    variable_list = []
    variable_values_list = []
    keywords_list = []
    
    def __init__(self):
        #self.parse_ref = parse_cmd
        self.phase_name = "Outside phase"
        self.statement_list = []
        self.variable_list = []
        self.variable_values_list = []
        self.keywords_list = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self,parser_ref):
        for statement in self.statement_list:
            readed = shlex.shlex(statement)
            member = readed.get_token()
            pom = readed.get_token()
            
            # condition to handle assign to random value
            # setting variable list
            if pom == '=':
                pom = readed.get_token()
                self.variable_list.append(member)
                regular = re.compile("\"(\/.*\/)(.*)\"")
                match = regular.match(pom)
                if match:
                    self.variable_values_list.append(match.group(1) + match.group(2))
                    self.keywords_list.append(match.group(2))
                else:
                    self.variable_values_list.append(pom[1:-1])
        #print self.variable_list
        #print self.variable_values_list
        #print self.keywords_list
        
    def get_variable_position(self,searching_variable):
        i = -1
        for member in self.variable_list:
            if member == searching_variable:
                i += 1
                return i
            else:
                i += 1
        
        return -1

class phase_clean:
    """Class for store informations in test phase"""
    phase_name = ""
    #parse_ref = ""
    statement_list = []
    doc_ref = ""
    statement_classes = []
    new_line = False
    
    def __init__(self,name):
        self.phase_name = name
        #self.parse_ref = parse_cmd
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        self.new_line = False
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))


class phase_test:
    """Class for store informations in test phase"""
    phase_name = ""
    #parse_ref = ""
    statement_list = []
    doc_ref = ""
    statement_classes = []
    
    def __init__(self,name):
        self.phase_name = name
        #self.parse_ref = parse_cmd
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
    
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))


class phase_setup:
    """Class for store informations in setup phase"""
    phase_name = ""
    #parse_ref = ""
    doc_ref = ""
    statement_list = []
    statement_classes = []
    
    def __init__(self,name):
        self.phase_name = name
        #self.parse_ref = parse_cmd
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))


class statement_automata:
    parsed_param_ref = ""
    parser_ref = ""
    
    def __init__(self,parser_ref):
        self.parser_ref = parser_ref
        
    def parse_command(self,statement_line):
        #Reading statement using shlex lexicator
        readed = shlex.shlex(statement_line)
        pom_list = []
    
        first = readed.get_token()
        if self.is_beakerLib_command(first,self.parser_ref):
            self.command_name = first 
            pom_list.append(first)
            element = readed.get_token()
            
            while (element != ""):
                #This condition is here because shlex splits "-" or "--" from options
                #so there is no chance to match it after using argparse 
                if element == '-' or element == '--' or element == '$':
                    element += readed.get_token()
                    
                    #Important for status in rlrun command
                    if self.is_rlrun_command(first):
                        pom_list[-1] = pom_list[-1] + element
                        element = readed.get_token()
                        
                #Important for status in rlrun command
                elif element == ',' and self.is_rlrun_command(first):
                    element += readed.get_token()
                    pom_list[-1] = pom_list[-1] + element
                    element = readed.get_token()
                
                else:
                    pom_list.append(element)
                    element = readed.get_token()
                    
            if self.is_rlrun_command(first):
                self.rlRun(pom_list)
            
            elif self.is_Rpm_command(first):
                self.rpm_command(pom_list)
            
            elif self.is_check_or_assert_mount(first):
                self.check_or_assert_mount(pom_list)
                
            elif self.is_assert_command(first):
                
                if self.is_assert_grep(first):
                    self.assert_grep(pom_list)
                
                elif self.is_rlPass_or_rlFail(first):
                    self.rlPass_or_rlFail(pom_list)
                    
                elif self.is_assert0(first):
                    self.assert0(pom_list)
                    
                elif self.is_assert_comparasion(first):
                    self.assert_comparasion(pom_list)
                    
                elif self.is_assert_exists(first):
                    self.assert_exits(pom_list)
                
                elif self.is_assert_differ(first):
                    self.assert_differ(pom_list)
                    
                elif self.is_assert_binary_origin(first):
                    self.assert_binary_origin(pom_list)
            
            elif self.is_rlFileBackup(first):
                self.rlFileBackup(pom_list)
                
            elif self.is_rlFileRestore(first):
                self.rlFile_Restore(pom_list)
            
            elif self.is_rlIsRHEL_or_rlISFedora(first):
                self.IsRHEL_or_Is_Fedora(pom_list)
                
            elif self.is_rlmount(first):
                self.rl_mount(pom_list)
                
            elif self.is_rlHash_or_rlUnhash(first):
                self.rlHash_or_rlUnhash(pom_list)
                
            elif self.is_rlReport(first):
                self.rlReport(pom_list)
                
            elif self.is_rlWatchdog(first):
                self.rlWatchdog(pom_list)
                
            elif self.is_rlservicexxx(first):
                self.rlServicexxx(pom_list)
                
            elif self.is_SEBooleanxxx(first):
                self.SEBooleanxxx(pom_list)
                
            elif self.is_rlCleanup_Apend_or_Prepend(first):
                self.rlCleanup_Apend_or_Prepend(pom_list)
                
            elif self.is_rlPerfTime_RunsInTime(first):
                self.rlPerfTime_RunsInTime(pom_list)
            
            elif self.is_rlPerfTime_AvgFromRuns(first):
                self.rlPerfTime_AvgFromRuns(pom_list)
                
            elif self.is_rlImport(first):
                self.rlImport(pom_list)
                
            elif self.is_rlWaitForxxx(first):
                self.rlWaitForxxx(pom_list,first)
                
            elif self.is_rlWaitFor(first):
                self.rlWaitFor(pom_list)
                
            elif self.is_VirtualXxxx(first):
                self.rlVirtualX_xxx(pom_list)
            
        else:
            self.unknown_command(pom_list)
        
        return self.parsed_param_ref;    
        
    def unknown_command(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        self.parsed_param_ref = parser.parse_args(["UNKNOWN"])
        
    def rlWatchdog(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("command", type=str)
        parser.add_argument("timeout", type=str)
        parser.add_argument("signal", type=str, nargs = '?', default = "KILL")
        parser.add_argument("callback", type=str, nargs = '?')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlReport(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("name", type=str)
        parser.add_argument("result", type=str)
        parser.add_argument("score", type=str, nargs = '?')
        parser.add_argument("log", type=str, nargs = '?')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
            
    def rlRun(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('-t', dest='t', action='store_true', default=False)
        parser.add_argument('-l', dest='l', action='store_true', default=False)
        parser.add_argument('-c', dest='c', action='store_true', default=False)
        parser.add_argument('-s', dest='s', action='store_true', default=False)
        parser.add_argument("command", type=str)
        parser.add_argument("status", type=str, nargs = '?', default = 0)
        parser.add_argument("comment", type=self.string_type, nargs = '?')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
    
    def rlVirtualX_xxx(self, pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("name", type=str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlWaitFor(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('n', type = str, nargs = '*')
        parser.add_argument("-t", type=int, help="time")
        parser.add_argument("-s", type=str, help="SIGNAL", default = "SIGTERM")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    
    def rlWaitForxxx(self,pom_param_list,command):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("-p", type=str, help="PID")
        parser.add_argument("-t", type=str, help="time")
        parser.add_argument("-d", type=int, help="delay", default = 1)
        
        if is_rlWaitForCmd(command):
            parser.add_argument("command", type=str)
            parser.add_argument("-m", type=int, help="count")
            parser.add_argument("-r", type=int, help="retrval")
        
        elif is_rlWaitForFile(command):
            parser.add_argument("path", type=str)
            
        elif is_rlWaitForSocket(command):
            parser.add_argument("port_path", type=str)
            parser.add_argument('--close', dest='close', action='store_true',
                   default=False)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlImport(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("LIBRARY", type=str, nargs = '+')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlPerfTime_RunsInTime(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("command", type=str)
        parser.add_argument("time", type=int, nargs = '?', default = 30)
        parser.add_argument("runs", type=int, nargs = '?', default = 3)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlPerfTime_AvgFromRuns(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("command", type=str)
        parser.add_argument("count", type=int, nargs = '?', default = 3)
        parser.add_argument("warmup", type=str, nargs = '?', default = "warmup")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlCleanup_Apend_or_Prepend(self, pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("string", type=str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def SEBooleanxxx(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("boolean", type=str, nargs = '+')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlServicexxx(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("service", type=str, nargs = '+')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rlFileRestore(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("--namespace", type=str,
                    help="specified namespace to use")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
            
    def rlFileBackup(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('--clean', dest='clean', action='store_true',
                   default=False)
        parser.add_argument("--namespace", type=str,
                    help="specified namespace to use")
        parser.add_argument('file', type = str, nargs = '+')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
            
    def rlHash_or_rlUnhash(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('--decode', dest='decode', action='store_true',
                   default=False, help='unhash given string')
        parser.add_argument("--algorithm", type=str,
                    help="given hash algorithm")
        parser.add_argument('stdin_STRING', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
            
    def check_or_assert_mount(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('server', type = str, nargs = '?')
        parser.add_argument('share', type = str, nargs = '?')
        parser.add_argument('mountpoint', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rl_mount(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('server', type = str)
        parser.add_argument('share', type = str)
        parser.add_argument('mountpoint', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def assert_binary_origin(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('binary', type = str)
        parser.add_argument('package', type = str, nargs = '*')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def rpm_command(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        if len(pom_param_list) == 1 and pom_param_list[0] == "--all":
            parser.add_argument('--all', dest='all', action='store_true',
                   default=False, help='assert all packages')
            self.parsed_param_ref = parser.parse_args(pom_param_list)
        else:
            parser.add_argument('name', type = str)
            parser.add_argument('version', type = str, nargs = '?')
            parser.add_argument('release', type = str, nargs = '?')
            parser.add_argument('arch', type = str, nargs = '?')
            self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def IsRHEL_or_Is_Fedora(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('type', type = str, nargs = '*')
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def assert_differ(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('file1', type = self.string_type)
        parser.add_argument('file2', type = self.string_type)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def assert_exits(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('file|directory', type = self.string_type)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def assert_comparasion(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('comment', type = self.string_type)
        parser.add_argument('value1', type = int)
        parser.add_argument('value2', type = int)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
    
    def assert0(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('comment', type = str)
        parser.add_argument('value', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
    
    def rlPass_or_rlFail(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('comment', type = self.string_type)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
    
    
    def assert_grep(self,pom_param_list):        
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('pattern', type = str)
        parser.add_argument('file', type = str)
        parser.add_argument('-i', '-I', dest='text_in', action='store_true',
                   default=False, help='insensitive matches')
        parser.add_argument('-e', '-E', dest='moin_in', action='store_true',
                   default=False, help='Extended grep')
        parser.add_argument('-p', '-P', dest='out_in', action='store_true',
                    default=False, help='perl regular expression')        
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    
    def string_type(self,command):
        if command[0:1] != '"':
            raise argparse.ArgumentTypeError("Not type string")
        return command
        
    def is_rlWatchdog(self,command):
        return command == "rlWatchdog"
        
    def is_rlReport(self,command):
        return command == "rlReport"
        
    def is_VirtualXxxx(self, command):
        pom_list = ["rlVirtualXStop", "rlVirtualXStart", "rlVirtualXGetDisplay"]
        return command in pom_list
        
    def is_rlWaitFor(self, command):
        return command == "rlWaitFor"
        
    def is_rlWaitForSocket(self, command):
        return command == "rlWaitForSocket"
        
    def is_rlWaitForFile(self, command):
        return command == "rlWaitForFile"
        
    def is_rlWaitForCmd(self, command):
        return command == "rlWaitForCmd"
        
    def is_rlWaitForxxx(self,command):
        pom_list = ["rlWaitForCmd", "rlWaitForFile", "rlWaitForSocket"]
        return command in pom_list
        
    def is_rlImport(self,command):
        return command == "rlImport"
        
    def is_rlPerfTime_RunsInTime(self, command):
        return command == "rlPerfTime_RunsInTime"
        
    def is_rlPerfTime_AvgFromRuns(self, command):
        return command == "rlPerfTime_AvgFromRuns"
        
    def is_rlCleanup_Apend_or_Prepend(self,command):
        return command == "rlCleanupAppend" or command == "rlCleanupPrepend"
        
    def is_SEBooleanxxx(self,command):
        pom_list = ["rlSEBooleanOn", "rlSEBooleanOff", "rlSEBooleanRestore"]
        return command in pom_list
        
    def is_rlservicexxx(self,command):
        pom_list = ["rlServiceStart", "rlServiceStop", "rlServiceRestore"]
        return command in pom_list
        
    def is_rlFileBackup(self,command):
        return command == "rlFileBackup"
        
    def is_rlFileRestore(self,command):
        return command == "rlFileRestore"
        
    def is_rlHash_or_rlUnhash(self,command):
        return command == "rlHash" or command == "rlUnhash"
        
    def is_check_or_assert_mount(self,command):
        return command == "rlCheckMount" or command == "rlAssertMount"
        
    def is_get_or_check_makefile_requires(self,command):
        return command == "rlCheckMakefileRequires" or command == \
        "rlGetMakefileRequires"
        
    def is_rlmount(self,command):
        return command == "rlMount"    
    
    def is_assert_binary_origin(self,command):
        return command == "rlAssertBinaryOrigin"
        
    def is_rlIsRHEL_or_rlISFedora(self,command):
        return command == "rlIsRHEL" or command == "rlIsFedora"
        
    def is_assert_differ(self,command):
        return command == "rlAssertDiffer" or command == "rlAssertNotDiffer"
        
    def is_assert_exists(self,command):
        return command == "rlAssertExists" or command == "rlAssertNotExists"
    
    def is_assert_comparasion(self,command):
        pom = ["rlAssertEquals", "rlAssertNotEquals", "rlAssertGreater",\
        "rlAssertGreaterOrEqual"]
        return command in pom
        
    def is_rlPass_or_rlFail(self,command):
        return command == "rlPass" or command == "rlFail"
        
    def is_assert_grep(self,command):
        return command == "rlAssertGrep" or command == "rlAssertNotGrep"
        
    def is_assert0(self,command):
        return command == "rlAssert0"
    
    def is_command_with_max_two_params(self, command, parser_ref):
        parser_ref.is_in_two_command_list(command)
    
    def is_assert_command(self,line):
        return line[0:len("rlAssert")] == "rlAssert"
        
    def is_Rpm_command(self,command):
        return command[-3:] == "Rpm"
        
    def is_rlrun_command(self,line):
        return line[0:len("rlRun")] == "rlRun"
    
    def is_no_option_command(self,command,parser_ref):
        return parser_ref.is_no_option_command(command)
        
    def is_beakerLib_command(self,testing_command,parser_ref):
        return parser_ref.is_beakerLib_command(testing_command)
    

    
class documentation_translator:
        
    def __init__(self, command_ref):
        print "ahoj"
    
            
#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    pom = parser(arg)
    #pom.print_statement()
    pom.get_doc_data()
