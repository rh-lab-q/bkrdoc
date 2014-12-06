#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib test

import sys
import shlex          
            
class parser(object):
    
    lexer = shlex
    
    file_test = ""
    
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
        
        try:                
            with open(file_in, "r") as inputfile:
                inputfile = open(file_in ,"r")
                self.file_test = inputfile.read()
                self.parse_data()

        except IOError:
            sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
            sys.exit(1)
            
    
    def parse_data(self):
        journal = False
        self.outside = phase_outside(self)
        
        for line in self.file_test.split('\n'):
            line = line.strip()
            
            if line[0:len("rljournalstart")].lower() == "rljournalstart":
                journal = True
                
            elif line[0:len("rljournalend")].lower() == "rljournalend":
                journal = False
            
            elif journal and line[0:1] != '#' and len(line) > 1 and \
            line[0:len("rlphaseend")].lower() != "rlphaseend":
                print line
                
                if line[0:len("rlphasestartsetup")].lower() == "rlphasestartsetup":
                    self.phases.insert(0, phase_setup(line[len("rlphasestart"):-1], self))
                    
                elif line[0:len("rlphasestarttest")].lower() == "rlphasestarttest":
                    self.phases.insert(0, phase_test(line[len("rlphasestart"):-1], self))
                
                elif line[0:len("rlphasestartclean")].lower() == "rlphasestartclean":
                    self.phases.insert(0, phase_clean(line[len("rlphasestart"):-1], self))
                
                elif len(self.phases) > 0:
                    self.phases[0].setup_statement(line)
            
            elif line[0:1] != '#' and len(line) > 1 and \
            line[0:len("rlphaseend")].lower() != "rlphaseend":
                self.outside.setup_statement(line)
        
        
class phase_outside:
    
    parse_ref = ""
    statement_list = []
    
    def __init__(self,parse_cmd):
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        self.statement_list.insert(-1,line)

class phase_clean:
    
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        print "++++++++++++++++++++++++++++++++" + line


class phase_test:
    
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        print "-+++++++++-------------------" + line


class phase_setup:
    
    phase_name = ""
    parse_ref = ""
    statement_list = []
    
    def __init__(self,name,parse_cmd):
        self.phase_name = name
        self.parse_ref = parse_cmd
        self.statement_list = []
        
    def setup_statement(self,line):
        print "--------------------" + line
        

#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    parser(arg)
