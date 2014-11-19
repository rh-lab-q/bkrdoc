#!/usr/bin/python
# author Jiri Kulda
# description: Simple parser for BeakerLib
#            - Parser is using shlex which is lexical analysator.

import sys
import shlex          
            
class parser(object):
    
    lexer = shlex
    
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
    
    def __init__(self, file_in):
        try:                
            with open(file_in, "r") as inputfile:
                #print("open\n")
                inputfile = open(file_in ,"r")
                #self.fileString = inputfile.read()
                self.lexer = shlex.shlex(inputfile.read(), posix=False)
                self.parse_data()

        except IOError:
            #self.fail = False
            sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
            sys.exit(1)
            
    
    def parse_data(self):
        pom_phase = []
        important_tags = ["rlPhaseStart","rlPhaseStartSetup", "rlPhaseStartTest", \
        "rlPhaseStartCleanup"]
        
        try:
            for token in self.lexer:
                if (token[0:len("rlPhaseStart")] == "rlPhaseStart"):
                    pom_token = token[len("rlPhaseStart"):len(token)]
                    token = self.lexer.get_token()
                    if (token[0:2] != "rl"):
                        pom_token += " " + token 
                    else:
                        self.lexer.push_token(token)
                    self.parse_phase_data(pom_token)
            print self.phases
            
        except ValueError, err:
            first_line_of_error = lexer.token.splitlines()[0]
            print 'ERROR:', lexer.error_leader(), str(err), 'following "' + first_line_of_error + '"'

    
    def parse_phase_data(self, phase_type):
        pom_phase = []
        pom_phase.append(phase_type)
        try:
            important_tags = ["rlFileBackup", "rlFileRestore", "rlServiceStart", \
            "rlWaitForCmd", "rlWaitForFile", "rlWaitForSocket", "rlWait"]
            for token in self.lexer:
                #In importatnt tags
                if (token in important_tags):
                    print token
                    
                #it is in rlRun    
                elif (token == "rlRun"):
                    token = self.lexer.get_token()
                    pom_token = token.split()
                    
                    if pom_token[0][-1] == '"':
                        pom_token[0] = pom_token[0][0:-1]
                        
                    #testing if firt token is in important_tags
                    if (pom_token[0][1:len(pom_token[0])] in important_tags):
                        pom_phase.append(pom_token[0]) #ZDE je ulozeni tokenu
                        pom_command = pom_token[-1]
                        for command in self.lexer:
                            #testing if "command" is any command 
                            if (command[0:2] == "rl"):
                                self.lexer.push_token(command)
                                if (pom_command != ""):
                                    pom_phase.append(pom_command)
                                break
                            pom_command = command
                    """else:
                        pom_phase.append(token) #ZDE je ulozeni tokenu
                        pom_command = ""
                        for command in self.lexer:
                            #testing if "command" is any command 
                            if (command[0:2] == "rl"):
                                self.lexer.push_token(command)
                                if (pom_command != ""):
                                    pom_phase.append(pom_command)
                                break
                            pom_command = command
                     """   
                
                #testing of phase end
                if (token[0:len("rlPhaseEnd")] == "rlPhaseEnd"):
                    self.phases.append(pom_phase)
                    return 0
    
        except ValueError, err:
            first_line_of_error = lexer.token.splitlines()[0]
            print 'ERROR:', lexer.error_leader(), str(err), 'following "' + first_line_of_error + '"'


#***************** MAIN ******************
for arg in sys.argv[1:len(sys.argv)]:
    parser(arg)


