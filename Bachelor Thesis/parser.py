#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex
import re          
            
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
    ] # there is not every command od BeakerLib library
    
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
        self.phases.append(phase_outside(self))
        
        for line in self.file_test.split('\n'):
            line = line.strip()
            
            if line[0:1] != '#' and len(line) > 1 and \
            not self.is_phase_journal_end(line) :
                
                if self.is_phase_setup(line):
                    self.phases.append(phase_setup(line[len("rlphasestart"):-1], self))
                    
                elif self.is_phase_test(line):
                    self.phases.append(phase_test(line[len("rlphasestart"):-1], self))
                
                elif self.is_phase_clean(line):
                    self.phases.append(phase_clean(line[len("rlphasestart"):-1], self))
                
                elif len(self.phases) > 0:
                    self.phases[-1].setup_statement(line)
            
            elif self.is_phase_journal_end(line):
                self.phases.append(phase_outside(self))
            
            elif line[0:1] != '#' and len(line) > 1:
                self.phases[-1].setup_statement(line)

        
    def print_statement(self):
        #self.outside.search_data()
        for i in self.phases:
            print i.statement_list
            print "\n"
        
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
        
        
        
class phase_outside:
    """Class for searching data ourside of phases"""
    parse_ref = ""
    statement_list = []
    variable_list = []
    variable_values_list = []
    keywords_list = []
    
    def __init__(self,parse_cmd):
        self.parse_ref = parse_cmd
        self.statement_list = []
        self.variable_list = []
        self.variable_values_list = []
        self.keywords_list = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        
    def search_data(self):
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
                    self.variable_values_list.append(match.group(1))
                    self.keywords_list.append(match.group(2))
                else:
                    self.variable_values_list.append(pom[1:-1])
        
        #print self.variable_list
        #print self.variable_values_list
        #print self.keywords_list

class phase_clean:
    """Class for store informations in test phase"""
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)


class phase_test:
    """Class for store informations in test phase"""
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)


class phase_setup:
    """Class for store informations in setup phase"""
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        self.statement_list.append(line)
        

#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    pom = parser(arg)
    pom.print_statement()
