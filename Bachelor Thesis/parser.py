#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex
import re          
import DFA
            
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
    "rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo", "rlLogDebug", "rlLog"
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
                    pom_line = line[0:-1].strip()
                
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
        for statement in self.statement_list:
            self.statement_classes.append(statement_automata(statement,parser_ref))


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
        for statement in self.statement_list:
            self.statement_classes.append(statement_automata(statement,parser_ref))


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
        for statement in self.statement_list:
            self.statement_classes.append(statement_automata(statement,parser_ref))

class statement_automata:
    
    command_name = ""
    first_param = ""
    second_param = ""
    third_param = ""
    options_list = []
    
    
    def __init__(self,statement_line,parser_ref):
        self.command_name = ""
        self.first_param = ""
        self.second_param = ""
        self.third_param = ""
        self.options_list = []
        
        readed = shlex.shlex(statement_line)
        
        first = readed.get_token()
        if self.is_beakerLib_command(first,parser_ref):
            print "ANO " + first + " is BeakerLib command"
            
            
             
        else:
            self.command_name = "UNKNOWN"
        
        #print readed.get_token()
    
    
    def is_assert_command(self,line):
        return line[0:len("rlAssert")] == "rlAssert"
        
    def is_rlrun_command(self,line):
        return line[0:len("rlRun")] == "rlRun"
        
    def is_beakerLib_command(self,testing_command,parser_ref):
        return parser_ref.is_beakerLib_command(testing_command)
    
    """
    def __init__(self,phase_ref,parser_ref):
        
        self.parser_ref = parser_ref
        self.documentation = []
        self.phase_ref = phase_ref
        
        for line in phase_ref.statement_list:
            
            if self.is_assert_command(line):
                self.assert_command(line)
            
            elif self.is_rlrun_command(line):
                print "Not implemented rlRun"
        
        print self.documentation    
            
    def is_assert_command(self,line):
        return line[0:len("rlAssert")] == "rlAssert"
        
    def is_rlrun_command(self,line):
        return line[0:len("rlRun")] == "rlRun"
        
    def assert_command(self,line):
        pom = line.split()
        
        if pom[0] == "rlAssertRpm":
            self.documentation.append("Package " + pom[1][1:-1] + " must be installed")
        
        elif pom[0] == "rlAssertGrep":
            readed = shlex.shlex(line)
            readed.get_token() #erase first element with name "rlAssertGrep"
            pattern = readed.get_token()
            search_file = readed.get_token()
            
            #searching for variable in file string
            if self.is_variable_in_string(search_file):
                #regular expression for parsing file data and variables
                regular = re.compile("\"(.*)\$(.*)(\/.*)\"")
                match = regular.match(search_file)
                if match:
                    self.documentation.append("File " + match.group(1) + \
                    self.get_variable(match.group(2)) + match.group(3)\
                    + " must contain string " + pattern)
            
            else:
                self.documentation.append("File " + search_file[1:-1]\
                 + " must contain string " + pattern)
        
        
                    
    def is_variable_in_string(self,string_file):
        return string_file.find('$') >= 0
            
    def get_variable(self,variable_string):
        return self.parser_ref.search_variable(self.phase_ref,variable_string)
    """
            
#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    pom = parser(arg)
    #pom.print_statement()
    pom.get_doc_data()
