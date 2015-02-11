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
    "rlGetTestState", "rlGetPhaseState", "rlJournalPrint", "rlJournalPrintText"
    ]
    
    
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
            
    def get_documentation_information(self):
        for member in self.phases:
            if not self.is_phase_outside(member):
                member.translate_data(self)
        
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
    documentation_information = []
    
    def __init__(self,name):
        self.phase_name = name
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        self.new_line = False
        self.documentation_information = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))
            
    def translate_data(self,parser_ref):
        data_translator = documentation_translator(parser_ref)
        for data in self.statement_classes:
            if data.argname != "UNKNOWN":
                self.documentation_information.append(data_translator.translate_data(data))


class phase_test:
    """Class for store informations in test phase"""
    phase_name = ""
    #parse_ref = ""
    statement_list = []
    doc_ref = ""
    statement_classes = []
    documentation_information = []
    
    def __init__(self,name):
        self.phase_name = name
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        self.documentation_information = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
    
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))
            
    def translate_data(self,parser_ref):
        data_translator = documentation_translator(parser_ref)
        for data in self.statement_classes:
            if data.argname != "UNKNOWN":
                self.documentation_information.append(data_translator.translate_data(data))


class phase_setup:
    """Class for store informations in setup phase"""
    phase_name = ""
    #parse_ref = ""
    doc_ref = ""
    statement_list = []
    statement_classes = []
    documentation_information = []
    
    def __init__(self,name):
        self.phase_name = name
        #self.parse_ref = parse_cmd
        self.statement_list = []
        self.doc = []
        self.statement_classes = []
        self.documentation_information = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self,parser_ref):
        command_translator = statement_automata(parser_ref)
        for statement in self.statement_list:
            self.statement_classes.append(command_translator.parse_command(statement))
            
    def translate_data(self,parser_ref):
        data_translator = documentation_translator(parser_ref)
        for data in self.statement_classes:
            if data.argname != "UNKNOWN":
                self.documentation_information.append(data_translator.translate_data(data))


class statement_automata:
    parsed_param_ref = ""
    parser_ref = ""
    
    def __init__(self,parser_ref):
        self.parser_ref = parser_ref
        
    def parse_command(self,statement_line):
        #Spliting statement using shlex lexicator
        pom_list = []
        pom_list = shlex.split(statement_line,posix = True)
        first = pom_list[0]
    
        if self.is_beakerLib_command(first,self.parser_ref):
            self.command_name = first 
            condition = conditions_for_commands()

            
            """while (element != ""):
                #This condition is here because shlex splits "-" or "--" from options
                #so there is no chance to match it after using argparse 
                if element == '-' or element == '--' or element == '$':
                    element += readed.get_token()
                    
                    #Important for status in rlrun command
                    if condition.is_rlrun_command(first):
                        pom_list[-1] = pom_list[-1] + element
                        element = readed.get_token()
                        
                #Important for status in rlrun command
                elif element == ',' and condition.is_rlrun_command(first):
                    element += readed.get_token()
                    pom_list[-1] = pom_list[-1] + element
                    element = readed.get_token()
                
                else:
                    pom_list.append(element)
                    element = readed.get_token()"""
                    
                    
            if condition.is_rlrun_command(first):
                self.rlRun(pom_list)
            
            elif condition.is_Rpm_command(first):
                self.rpm_command(pom_list)
            
            elif condition.is_check_or_assert_mount(first):
                self.check_or_assert_mount(pom_list)
                
            elif condition.is_assert_command(first):
                
                if condition.is_assert_grep(first):
                    self.assert_grep(pom_list)
                
                elif condition.is_rlPass_or_rlFail(first):
                    self.rlPass_or_rlFail(pom_list)
                    
                elif condition.is_assert0(first):
                    self.assert0(pom_list)
                    
                elif condition.is_assert_comparasion(first):
                    self.assert_comparasion(pom_list)
                    
                elif condition.is_assert_exists(first):
                    self.assert_exits(pom_list)
                
                elif condition.is_assert_differ(first):
                    self.assert_differ(pom_list)
                    
                elif condition.is_assert_binary_origin(first):
                    self.assert_binary_origin(pom_list)
            
            elif condition.is_rlFileBackup(first):
                self.rlFileBackup(pom_list)
                
            elif condition.is_rlFileRestore(first):
                self.rlFile_Restore(pom_list)
            
            elif condition.is_rlIsRHEL_or_rlISFedora(first):
                self.IsRHEL_or_Is_Fedora(pom_list)
                
            elif condition.is_rlmount(first):
                self.rl_mount(pom_list)
                
            elif condition.is_rlHash_or_rlUnhash(first):
                self.rlHash_or_rlUnhash(pom_list)
            
            elif condition.is_rlLog(first):
                self.rlLog(pom_list)
                
            elif condition.is_rlDie(first):
                self.rlDie(pom_list)
                
            elif condition.is_rlGet_x_Arch(first):
                self.rlGet_command(pom_list)
                
            elif condition.is_rlGetDistro(first):
                self.rlGet_command(pom_list)
                
            elif condition.is_rlGetPhase_or_Test_State(first):
                self.rlGet_command(pom_list)
                
            elif condition.is_rlReport(first):
                self.rlReport(pom_list)
                
            elif condition.is_rlWatchdog(first):
                self.rlWatchdog(pom_list)
                
            elif condition.is_rlBundleLogs(first):
                self.rlBundleLogs(pom_list)
                
            elif condition.is_rlservicexxx(first):
                self.rlServicexxx(pom_list)
                
            elif condition.is_SEBooleanxxx(first):
                self.SEBooleanxxx(pom_list)
                
            elif condition.is_rlShowRunningKernel(first):
                self.rlShowRunningKernel(pom_list)
                
            elif condition.is_get_or_check_makefile_requires(first):
                self.rlGet_or_rlCheck_MakefileRequeries(pom_list)
            
            elif condition.is_rlCleanup_Apend_or_Prepend(first):
                self.rlCleanup_Apend_or_Prepend(pom_list)

            elif condition.is_rlFileSubmit(first):
                self.rlFileSubmit(pom_list)
                
            elif condition.is_rlPerfTime_RunsInTime(first):
                self.rlPerfTime_RunsInTime(pom_list)
            
            elif condition.is_rlPerfTime_AvgFromRuns(first):
                self.rlPerfTime_AvgFromRuns(pom_list)
                
            elif condition.is_rlShowPackageVersion(first):
                self.rlShowPackageVersion(pom_list)
            
            elif condition.is_rlJournalPrint(first):
                self.rlJournalPrint(pom_list)
                
            elif condition.is_rlImport(first):
                self.rlImport(pom_list)
                
            elif condition.is_rlWaitForxxx(first):
                self.rlWaitForxxx(pom_list,first)
                
            elif condition.is_rlWaitFor(first):
                self.rlWaitFor(pom_list)
                
            elif condition.is_VirtualXxxx(first):
                self.rlVirtualX_xxx(pom_list)
            
        else:
            self.unknown_command(pom_list)
        
        return self.parsed_param_ref;
        
    def rlJournalPrint(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("type", type=str,nargs = "?")
        parser.add_argument('--full-journal', dest='full_journal',\
         action='store_true', default=False)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlShowPackageVersion(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("package", type=str,nargs = "+")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlFileSubmit(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("-s", type=str, help="sets separator")
        parser.add_argument("path_to_file", type=str)
        parser.add_argument("required_name", type=str,nargs = "?")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlBundleLogs(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("package", type=str)
        parser.add_argument("file", type=str,nargs = "+")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlDie(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("message", type=str)
        parser.add_argument("file", type=str,nargs = "*")
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlLog(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument("message", type=str)
        parser.add_argument("logfile", type=str,nargs = "?")
        parser.add_argument("priority", type=str,nargs = "?")
        parser.add_argument('--prio-label', dest='prio_label',\
         action='store_true', default=False)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlShowRunningKernel(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlGet_or_rlCheck_MakefileRequeries(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
    def rlGet_command(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
        
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
        parser.add_argument("status", type=str, nargs = '?', default = "0")
        parser.add_argument("comment", type=str, nargs = '?')
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
        
        if conditions_for_commands().is_rlWaitForCmd(command):
            parser.add_argument("command", type=str)
            parser.add_argument("-m", type=str, help="count")
            parser.add_argument("-r", type=str, help="retrval", default = "0")
        
        elif conditions_for_commands().is_rlWaitForFile(command):
            parser.add_argument("path", type=str)
            
        elif conditions_for_commands().is_rlWaitForSocket(command):
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
        parser.add_argument('file1', type = str)
        parser.add_argument('file2', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def assert_exits(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('file|directory', type = str)
        self.parsed_param_ref = parser.parse_args(pom_param_list)
            
    def assert_comparasion(self,pom_param_list):
        parser = argparse.ArgumentParser()
        parser.add_argument("argname", type=str)
        parser.add_argument('comment', type = str)
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
        parser.add_argument('comment', type = str)
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
        
    
    def is_beakerLib_command(self,testing_command,parser_ref):
        return parser_ref.is_beakerLib_command(testing_command)
    

class documentation_translator:
    """Class making documentation information from argparse data. 
    Generated information are focused on BeakerLib commands"""
    inf_ref = ""
    
    low = 1
    medium = 2
    high = 3
    
    information = ""
    link_information = ""
    connection = []
    importance = 0
    
    def __init__(self,parser_ref):
        self.parser_ref = parser_ref
        self.inf_ref = ""
        self.information = ""
        self.link_information = ""
        self.connection = []
        self.importance = 0
        
    def translate_data(self,argparse_data):
        self.inf_ref = ""
        self.information = ""
        self.link_information = ""
        self.connection = []
        
        argname = argparse_data.argname
        condition = conditions_for_commands()
        
        if condition.is_rlrun_command(argname):
            self.rlRun(argparse_data)
        
        elif condition.is_Rpm_command(argname):
            self.rpm_command(argparse_data)
            
        elif condition.is_check_or_assert_mount(argname):
            self.check_or_assert_mount(argparse_data)
                
        elif condition.is_assert_command(argname):
                
            if condition.is_assert_grep(argname):
                self.assert_grep(argparse_data)
                
            elif condition.is_rlPass_or_rlFail(argname):
                self.rlPass_or_rlFail(argparse_data)
                    
            elif condition.is_assert0(argname):
                self.assert0(argparse_data)
                
            elif condition.is_assert_comparasion(argname):
                self.assert_comparasion(argparse_data)
                    
            elif condition.is_assert_exists(argname):
                self.assert_exits(argparse_data)
            
            elif condition.is_assert_differ(argname):
                self.assert_differ(argparse_data)
                
            elif condition.is_assert_binary_origin(argname):
                self.assert_binary_origin(argparse_data)
        
        elif condition.is_rlFileBackup(argname):
            self.rlFileBackup(argparse_data)
            
        elif condition.is_rlFileRestore(argname):
            self.rlFile_Restore(argparse_data)
        
        elif condition.is_rlIsRHEL_or_rlISFedora(argname):
            self.IsRHEL_or_Is_Fedora(argparse_data)
            
        elif condition.is_rlmount(argname):
            self.rl_mount(argparse_data)
            
        elif condition.is_rlHash_or_rlUnhash(argname):
            self.rlHash_or_rlUnhash(argparse_data)
        
        elif condition.is_rlLog(argname):
            self.rlLog(argparse_data)
            
        elif condition.is_rlDie(argname):
            self.rlDie(argparse_data)
                
        elif condition.is_rlGet_x_Arch(argname):
            self.rlGet_command(argparse_data)
            
        elif condition.is_rlGetDistro(argname):
            self.rlGet_command(argparse_data)
            
        elif condition.is_rlGetPhase_or_Test_State(argname):
            self.rlGet_command(argparse_data)
            
        elif condition.is_rlReport(argname):
            self.rlReport(argparse_data)
            
        elif condition.is_rlWatchdog(argname):
            self.rlWatchdog(argparse_data)
            
        elif condition.is_rlBundleLogs(argname):
            self.rlBundleLogs(argparse_data)
            
        elif condition.is_rlservicexxx(argname):
            self.rlServicexxx(argparse_data)
            
        elif condition.is_SEBooleanxxx(argname):
            self.SEBooleanxxx(argparse_data)
            
        elif condition.is_rlShowRunningKernel(argname):
            self.rlShowRunningKernel(argparse_data)
                
        elif condition.is_get_or_check_makefile_requires(argname):
            self.rlGet_or_rlCheck_MakefileRequeries(argparse_data)
        
        elif condition.is_rlCleanup_Apend_or_Prepend(argname):
            self.rlCleanup_Apend_or_Prepend(argparse_data)

        elif condition.is_rlFileSubmit(argname):
            self.rlFileSubmit(argparse_data)
                
        elif condition.is_rlPerfTime_RunsInTime(argname):
            self.rlPerfTime_RunsInTime(argparse_data)
            
        elif condition.is_rlPerfTime_AvgFromRuns(argname):
            self.rlPerfTime_AvgFromRuns(argparse_data)
                
        elif condition.is_rlShowPackageVersion(argname):
            self.rlShowPackageVersion(argparse_data)
        
        elif condition.is_rlJournalPrint(argname):
            self.rlJournalPrint(argparse_data)
            
        elif condition.is_rlImport(argname):
            self.rlImport(argparse_data)
                
        elif condition.is_rlWaitFor(argname):
            self.rlWaitFor(argparse_data)
            
        elif condition.is_rlWaitForCmd(argname):
            self.rlWaitForCmd(argparse_data)
            
        elif condition.is_rlWaitForFile(argname):
            self.rlWaitForFile(argparse_data)
            
        elif condition.is_rlWaitForSocket(argname):
            self.rlWaitForSocket(argparse_data)
                
        elif condition.is_VirtualXxxx(argname):
            self.rlVirtualX_xxx(argparse_data)
            
        return self.inf_ref
            
            
    def rlJournalPrint(self,argparse_data):
        self.importance = self.low
        if argparse_data.argname == "rlJournalPrint":
            if len(argparse_data.type):
                self.information = "Prints content of the journal in " + \
                argparse_data.type + " format"
            else:
                self.information = "Prints content of the journal in xml format"
        else:
            if argparse_data.full_journal:
                self.information = "Prints content of the journal in pretty text format" +\
                  " with additional information"
            else:
                self.information = "Prints content of the journal in pretty text format"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlShowPackageVersion(self,argparse_data):
        self.importance = self.low
        if len(argparse_data.package) == 1:
            self.information = "Shows information about " + argparse_data.package[0] +\
            " version"
            self.link_information = "shows information about this package version"
        else:
            self.information = "Shows information about "
            self.information += self.connect_multiple_facts(argparse_data.package,4)\
              + " version"
        self.connection = argparse_data.package        
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlFileSubmit(self,argparse_data):
        self.importance = self.low
        if not len(argparse_data.s) and not len(argparse_data.required_name):
            self.information = "Resolves absolute path " + argparse_data.path_to_file
            self.information += " and replaces \/ for -"
            
        elif len(argparse_data.s) and not len(argparse_data.required_name):
            self.information = "Resolves absolute path " + argparse_data.path_to_file
            self.information += " and replaces \/ for " + argpase_data.s
            
        elif len(argparse_data.s) and len(argparse_data.required_name):
            self.information = "Resolves absolute path " + argparse_data.path_to_file
            self.information += ", replaces \/ for " + argparse_data.s
            self.information += " and rename file to " + argparse_data.required_name
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlBundleLogs(self,argparse_data):
        self.importance = self.low
        if len(argparse_data.file) > 1:
            self.information = "Creates a tarball of files " + \
            self.connect_multiple_facts(argparse_data.file,3)
            self.information += " and attached them to test result" 
        else:
            self.information = "Creates a tarball of file " + argparse_data.file[0]
            self.information += " and attached it to test result"
            self.connection = argparse_data.file
            self.link_information = "creates a tarball of this file" 
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlDie(self,argparse_data):
        self.importance = self.low
        if len(argparse_data.file):
            self.information = "Message " + argparse_data.message
            if len(argparse_data.file) > 1:
                self.information += " will be created in to log and files "
            else:
                self.information += " will be created in to log and file "
            self.information += self.connect_multiple_facts(argparse_data.file,3)
            self.information += " will be uploaded"
        else:
            self.information = "Message " + argparse_data.message
            self.information += " will be created in to log"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlLog(self,argparse_data):
        self.importance = self.low
        self.information = "Message " + argparse_data.message
        if argparse_data.logfile:
            self.information += " will be created in to logfile "
            self.information += argparse_data.logfile
        else:
            self.information += " will be created in to log"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlShowRunningKernel(self,argparse_data):
        self.importance = self.low
        self.information = "Log a message with version of the currently running kernel"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlGet_or_rlCheck_MakefileRequeries(self,argparse_data):
        self.importance = self.low
        if argparse_data.argname == "rlGetMakefileRequires":
            self.importance = "Prints comma separated list of requirements defined in Makefile"
        else:
            self.importance = "Checking requirements in Makefile and returns number of compliance"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlGet_command(self,argparse_data):
        self.importance = self.low
        if conditions_for_commands().is_rlGetPhase_or_Test_State(argparse_data.argname):
            if argparse_data.argname == "rlGetTestState":
                self.information = "Returns number of failed asserts" 
            else:
                self.information = "Returns number of failed asserts in current phase"
        elif conditions_for_commands().is_rlGetDistro(argparse_data.argname):
            if argparse_data.argname == "rlGetDistroRelease":
                self.information = "Return release of the distribution on the system"
            else:
                self.information = "Return variant of the distribution on the system"
        
        elif argparse_data.argname == "rlGetPrimaryArch":
            self.information = "Return primary arch for the current system"
        
        else:
            self.information = "Return base arch for the current system"
                
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)        
        
    def rlWatchdog(self,argparse_data):
        self.importance = self.medium
        self.information = "Run command " + argparse_data.command
        self.information += " for " + argparse_data.timeout
        self.information += " seconds"
        if argparse_data.signal:
            self.information += " and killed with signal "
            self.information += argparse_data.signal
        
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def rlReport(self,argparse_data):
        #TODO Check if it is ALL 
        self.importance = self.medium
        self.information = argparse_data.name + " " + argparse_data.result
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlRun(self,argparse_data):
        self.importance = self.medium
        self.information = "Command " + argparse_data.command
        if argparse_data.status == "0":
            self.information += " must run successfully"
        elif argparse_data.status == "1":
            self.information += " must run unsuccessfully"
        else:
            self.information += " exit code must match " 
            self.information += argparse_data.status
        
        if argparse_data.l:
            self.information += " and output will be stored in to log"
        elif argparse_data.c:
            self.information += " and failed output will be stored in to log"
        elif argparse_data.t and argparse_data.s:
            self.information += " and stdout and stderr will be tagged and stored"
        elif argparse_data.t:
            self.information += " and stdout and stderr will be tagged"
        elif argparse_data.s:
            self.information += " and stdout and stderr will be stored" 
        
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
    
    def rlVirtualX_xxx(self, argparse_data):
        self.importance = self.medium
        if argparse_data.argname == "rlVirtualXStop":
            self.information = "Kills " + argparse_data.name
            self.information += " server"
        elif argparse_data.argname == "rlVirtualXStart":
            self.information = "Starts virtual X " + argparse_data.name
            self.information += " server on a first free display"
        else:
            self.information = "Shows number of display where virtual X "
            self.information += argparse_data.name + " is running"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)     
        
    def rlWaitFor(self,argparse_data):
        self.importance = self.low
        if len(argparse_data.n) == 1:
            self.information = "Wait for " + argparse_data.n[0] 
            self.information += " process"
        elif len(argparse_data.n) > 1:
            self.information = "Wait for " + connect_multiple_facts(argparse_data.n,3)
            self.information += " processes"
        else: 
            self.information = "All currently active child processes are" 
            self.information += " waited for, and the return status is zero"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection) 
        
    def rlWaitForSocket(self,argparse_data):
        self.importance = self.low
        if argparse_data.close:
            self.information = "Wait for the socket with this path" 
            self.information += argparse_data.port_path + "to stop listening"
        elif argparse_data.p:
            self.information = "Pauses script until socket with this path or port "
            self.information += argparse_data.port_path  + " starts listening"
            self.information += "\n and process with this PID " + argparse_data.p
            self.information += " must be running"
        else:
            self.information = "Pauses script until socket with this path or port "
            self.information += argparse_data.port_path  + " starts listening"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlWaitForFile(self,argparse_data):
        self.importance = self.low
        if argparse_data.p:
            self.information = "Pauses script until file or directory with this path "
            self.information += argparse_data.path  + " starts existing"
            self.information += "\n and process with this PID " + argparse_data.p
            self.information += " must be running"
        else:
            self.information = "Pauses script until file or directory with this path "
            self.information += argparse_data.path  + " starts listening"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
        
    def rlWaitForCmd(self,argparse_data):
        self.importance = self.low
        self.information = "Pauses script until command " 
        self.information += argparse_data.command 
        
        if argparse_data.r == "0":
            self.information +=  " exit status is successfully"
        elif argparse_data.r == "1":
            self.information +=  " exit status is unsuccessfully"
        else:
            self.information += " exit status is " + argparse_data.r
        if argparse_data.p:
            self.information += "\n and process with this PID " + argparse_data.p
            self.information += " must be running"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def rlImport(self,argparse_data):
        self.importance = self.medium
        self.information = "Imports code provided by "
        if len(argparse_data.LIBRARY) == 1:
            self.information += argparse_data.LIBRARY[0]
            self.information += "  library into the test namespace"
        else:
            self.information += connect_multiple_facts(argparse_data.LIBRARY,2)
            self.information += "  libraries into the test namespace"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def rlPerfTime_RunsInTime(self,argparse_data):
        self.importance = self.low
        self.information = "Measures, how many runs of command "
        self.information += argparse_data.command + " in " 
        self.information += argparse_data.time + " second(s)"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def rlPerfTime_AvgFromRuns(self,argparse_data):
        self.importance = self.low
        self.information = "Measures the average time of running command "
        self.information += argparse_data.command
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def rlCleanup_Apend_or_Prepend(self, argparse_data):
        self.importance = self.medium
        if argparse_data.argname == "rlCleanupAppend":
            self.information = "Appends string: " + argparse_data.string 
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script" 
        else:
            self.information = "Prepends string: " + argparse_data.string
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        self.inf_ref = documentation_information(self.information,\
        self.link_information,self.importance,self.connection)
            
    def SEBooleanxxx(self,argparse_data):
        pass
            
    def rlServicexxx(self,argparse_data):
        pass
            
    def rlFileRestore(self,argparse_data):
        pass
        
    def rlFileBackup(self,argparse_data):
        pass
        
    def rlHash_or_rlUnhash(self,argparse_data):
        pass
        
    def check_or_assert_mount(self,argparse_data):
        pass
            
    def rl_mount(self,argparse_data):
        pass
            
    def assert_binary_origin(self,argparse_data):
        pass
            
    def rpm_command(self,argparse_data):
        pass
            
    def IsRHEL_or_Is_Fedora(self,argparse_data):
        pass
        
    def assert_differ(self,argparse_data):
        pass
            
    def assert_exits(self,argparse_data):
        pass
            
    def assert_comparasion(self,argparse_data):
        pass
    
    def assert0(self,argparse_data):
        pass
    
    def rlPass_or_rlFail(self,argparse_data):
        pass
    
    def assert_grep(self,argparse_data):        
        pass
        
    def connect_multiple_facts(self,facts ,max_size = 5):
        pom_inf = ""
        if len(facts) == 1:
            pom_inf = facts[0]
        elif len(facts) == 2:
            pom_inf = facts[0] + " and " + facts[1]
        else:
            i = 0
            while(i < max_size):
                pom_inf += facts[i]
                if len(facts) > (i + 2) and (i + 2) < max_size:
                    pom_inf += ", "
                elif (i + 1) == len(facts):
                    return pom_inf
                elif (i + 1) == max_size:
                    pom_inf += "..."
                    return pom_inf
                else:
                    pom_inf += " and "
                i += 1
            pom_inf += "..."
        return pom_inf
        

class documentation_information:
    """ Class made as a output of class documentation translator """
    
    information = ""
    
    linker_inf = ""
    
    importance = 0
    
    connection_data = []
    
    def __init__(self,inf,link_inf,importance_of_inf, connection):
        self.information = inf
        self.linker_inf = link_inf
        self.importance = importance_of_inf
        self.connection_data = connection
    

class conditions_for_commands:
    """ Class consits of conditions for testing commands used in 
    parser_automata and documentation translator """        
        
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
    
    def is_assert_command(self,line):
        return line[0:len("rlAssert")] == "rlAssert"
        
    def is_Rpm_command(self,command):
        return command[-3:] == "Rpm"
        
    def is_rlrun_command(self,line):
        return line[0:len("rlRun")] == "rlRun"
        
    def is_rlJournalPrint(self,command):
        pom = ["rlJournalPrint", "rlJournalPrintText"]
        return command in pom
        
    def is_rlGetPhase_or_Test_State(self,command):
        pom = ["rlGetPhaseState", "rlGetTestState"]
        return command in pom
    
    def is_rlLog(self,command):
        pom = ["rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo",\
         "rlLogDebug", "rlLog"]
        return command in pom
        
    def is_rlLogMetric(self,command):
        pom = ["rlLogMetricLow", "rlLogMetricHigh"]
        return command in pom
        
    def is_rlDie(self,command):
        return command[0:len("rlDie")] == "rlDie"
        
    def is_rlBundleLogs(self,command):
        return command[0:len("rlBundleLogs")] == "rlBundleLogs"

    def is_rlFileSubmit(self,command):
        return command[0:len("rlFileSubmit")] == "rlFileSubmit"
        
    def is_rlShowPackageVersion (self,command):
        return command[0:len("rlShowPackageVersion")] == "rlShowPackageVersion"
        
    def is_rlGet_x_Arch(self,command):
        pom = ["rlGetArch","rlGetPrimaryArch","rlGetSecondaryArch"]
        return command in pom
        
    def is_rlGetDistro(self,command):
        pom = ["rlGetDistroRelease","rlGetDistroVariant"]
        return command in pom

    def is_rlShowRunningKernel(self,command):
        return command[0:len("rlShowRunningKernel")] == "rlShowRunningKernel"

            
#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    pom = parser(arg)
    #pom.print_statement()
    pom.get_doc_data()
    pom.get_documentation_information()
    
