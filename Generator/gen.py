#!/usr/bin/python
# author Jiri Kulda

import sys
import argparse
import subprocess


"""Class to parse from script file data and save them to list"""


class Gener(object):
    fileString = ""
    inputfile = ""
    fail = True
    skip = False
    BlockComm = False
    NextLine = False
    filename = ""

    # List of comments
    comments = []

    # Helpfull list
    block = []

    # String of Author of a test
    author = "None"

    # String of Description of a test
    description = "None"

    #Strin of Keywords of a test
    keywords = ""

    #@ Konstructor of class Gener
    #@ @param file_in is filepath to input file
    def __init__(self, file_in):
        self.comments = []
        self.block = []
        if file_in[(len(file_in) - 3):len(file_in)] == ".sh":

            try:
                #subprocess.Popen(file_in + ' >& ahoj.txt', shell=True)
                #subprocess.Popen( 'rm ahoj.txt', shell=True)
                self.filename = file_in
                with open(file_in, "r") as inputfile:
                    #inputfile = open(File ,"r",errors='strict')
                    self.fileString = inputfile.read()

            except IOError:
                self.fail = False
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)

        else:
            print "ERROR: Not a script file. (.sh)"
            sys.exit(1)


    #@ method to parse tags from file
    def parse_tags(self):
        pom = []
        func = False

        for line in self.fileString.split('\n'):
            line = line.strip()
            #print("............." + line)
            #print( self.BlockComm)
            #print( self.NextLine)
            if (len(line) >= 2) and (line[0] == "#"):
                self.parse_line(line[1:len(line)].strip())

            elif self.NextLine:
                if not (not ('phasestart' in line.lower()) and not (line[0:2].lower() == 'if')) or (
                            line[0:3].lower() == 'for'):
                    self.block.insert(0, line)

                elif line[0:len('function')].lower() == 'function':
                    self.block.insert(0, line)
                    func = True

                else:
                    #print(self.block)
                    self.block.append(line)

                self.comments.append(self.block)
                #print (self.comments)
                self.block = []
                #print("---------------------")
                #print(self.comments)
                self.NextLine = False
                self.BlockComm = False

            else:
                self.BlockComm = False
                if line[len(line) - 2:len(line)] == "#@":
                    pom.append(line)
                    self.comments.append(pom)
                    pom = []

                elif ('phasestart' in line.lower()) or \
                        (line[0:2].lower() == 'if') or (line[0:3].lower() == 'for'):
                    self.block.insert(0, line)
                    self.comments.append(self.block)
                    self.block = []

                elif 'phaseend' in line.lower():
                    pom.append("END")
                    self.comments.append(pom)
                    pom = []

                elif 'done' == line[0:4]:
                    pom.append("ENDLOOP")
                    self.comments.append(pom)
                    pom = []

                elif 'fi' == line[0:2]:
                    pom.append("ENDCOND")
                    self.comments.append(pom)
                    pom = []

                elif '}' == line[0:1] and func:
                    pom.append("ENDFUNC")
                    self.comments.append(pom)
                    pom = []

    #@ funciton to parse line with comments
    def parse_line(self, line_sec):
        line_sec = line_sec.strip()
        if (line_sec[0] == '@') and (not self.BlockComm):
            self.BlockComm = True
            self.NextLine = True
            self.block.append(line_sec)

        elif self.BlockComm:
            self.block.append("&" + line_sec)

        elif 'description' in line_sec[0:len('description')].lower():
            self.description = line_sec[len('description') + 1: len(line_sec)]

        elif 'author' in line_sec[0:len('author')].lower():
            self.author = line_sec[len('author') + 1: len(line_sec)]

        elif 'key' in line_sec[0:3].lower():
            pom_str = line_sec.split()
            self.keywords = line_sec[len(pom_str[0]): \
                len(line_sec)].strip() + ","


""" Class to recognize what data geting from previous class """


class NewTextDoc:
    description = ""
    author = ""
    keywords = ""
    phases = []
    additionalInfo = []
    filename = ""
    func = []
    loop = []
    cond = []
    outsidePhase = []
    pom_list = []
    action_list = []
    listAdd = []
    listPomAdd = []
    parseInfo = ""

    # @ Constructor of class NewTextDoc
    # @ @param parse_info contains  parsed informations from file
    def __init__(self, parse_info):
        self.filename = parse_info.filename
        self.parseInfo = parse_info
        self.phases = []
        self.func = []
        self.loop = []
        self.cond = []
        self.pom_list = []
        self.action_list = []
        self.outsidePhase = []
        self.listAdd = []
        self.listPomAdd = []

    # function to recognize all data from test
    # and set them to proper list
    def parse_data(self):

        start_phase = False
        start_cond = False
        start_func = False
        start_loop = False
        start_pom = False

        for doc in self.parseInfo.comments:

            for line in doc:
                #print(self.listPomAdd)
                #print(self.listAdd)
                #print(line)
                #print(start_cond)
                #print(start_loop)
                #print("---------------------------------------------")
                #print(start_cond)
                if 'phasestart' in line.lower():
                    pom_str = line.strip()
                    self.pom_list.insert(0, '\040\040' + \
                                         pom_str[len('rlphasestart'):len(pom_str)] + "\n")
                    start_phase = True
                    start_pom = True

                    if len(self.outsidePhase) != 0:
                        self.phases.append(self.outsidePhase)
                        self.outsidePhase = []

                #Test of tag description in test
                elif '@description' in line.lower():
                    pom_desc_str = line[1:len(line)].strip()
                    if self.description != "":
                        self.description += ", " + \
                                            pom_desc_str[len('@description'): len(line)].strip()
                    else:
                        self.description = \
                            pom_desc_str[len('@description') + 1: len(line)].strip()

                #test of authors in test
                elif '@author' in line.lower():
                    pom_aut_str = line[1:len(line)].strip()
                    if self.author != "":
                        self.author += ", " + \
                                       pom_aut_str[len('@author'): len(line)].strip()
                    else:
                        self.author = \
                            pom_aut_str[len('@author'): len(line)].strip()

                #Test of keywords in test
                elif ('@keywords' in line.lower()) or ('@key' in line.lower()):
                    pom_key = line[1:len(line)].split()
                    pom_key_str = line[1:len(line)].strip()

                    if len(pom_key[0]) == 1:
                        del pom_key[0]
                        pom_key_str = pom_key_str[1:len(pom_key_str)].strip()

                    self.keywords += pom_key_str[len(pom_key[0]): \
                        len(line)].strip() + ", "

                #test of coments and block comments
                elif ('@' == line[0:1]) or ('&' == line[0:1]):
                    pom_list = line[1:len(line)].split()
                    pom_str = line[1:len(line)].strip()

                    if len(pom_list[0]) == 1:
                        del pom_list[0]
                        pom_str = pom_str[1:len(pom_str)].strip()

                    #geting multiple of tags
                    if '@' == pom_str[0][0:1]:
                        pom_str = ""
                        if start_loop:
                            pom_str += "\040\040\040\040\040\040loop"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, True)

                        elif start_cond:
                            pom_str += "\040\040\040\040\040\040condition"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, True)

                        elif start_phase:
                            pom_str += "\040\040\040\040\040\040"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, False)

                    #When start_phase(Phase) is activated, 
                    #then saves according to cond etc... data
                    elif start_phase:
                        pom_str = ""
                        if start_loop:
                            pom_str += "\040\040\040\040\040\040loop"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, True)

                        elif start_cond:
                            pom_str += "\040\040\040\040\040\040condition"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, True)

                        elif not start_pom:
                            pom_str += "\040\040\040\040\040\040action"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, True, False)

                        else:
                            pom_str += "\040\040\040\040"
                            self.parse_multiple_tags \
                                (pom_list, pom_str, False, False)

                    #saves data of function to func list
                    elif start_func:
                        self.func.append('\040\040\040\040\040\040' + pom_str + "\n")

                    #saving out of phase data
                    elif not start_phase:
                        if len(self.outsidePhase) != 0:
                            self.outsidePhase.append('\040\040\040\040' + \
                                                     line[1:len(line)].strip() + "\n")
                        else:
                            self.outsidePhase.append('\040\040' + 'Outside Phase:\n')
                            self.outsidePhase.append('\040\040\040\040' + \
                                                     line[1:len(line)].strip() + "\n")

                #Test of loops and end of loops and multiple cond or loops
                elif ('for' == line[0:3]) or \
                        ('ENDLOOP' == line[0:len('ENDLOOP')]):

                    if 'ENDLOOP' == line[0:len('ENDLOOP')]:
                        self.loop += self.listPomAdd
                        self.listPomAdd = []
                        if len(self.listAdd) != 0:
                            self.listPomAdd = self.listAdd[-1]
                            del self.listAdd[-1]
                            if self.listPomAdd[0][0:len('\040\040\040\040for')].strip() == 'for':
                                start_loop = True
                                start_cond = False
                            else:
                                start_loop = False
                                start_cond = True
                        else:
                            start_loop = False

                    else:
                        start_loop = True
                        start_cond = False
                        if len(self.listPomAdd) != 0:
                            self.listAdd.append(self.listPomAdd)
                            self.listPomAdd = []
                        self.listPomAdd.append('\040\040\040\040' + line + "\n")

                #Test of condition and end of 
                #condition and multiple cond or loops
                elif ('if' == line[0:2]) or ('ENDCOND' == line):
                    if 'ENDCOND' in line:
                        self.cond += self.listPomAdd
                        self.listPomAdd = []
                        if len(self.listAdd) != 0:
                            self.listPomAdd = self.listAdd[-1]
                            del self.listAdd[-1]
                            if self.listPomAdd[0][0:len('\040\040\040\040for')].strip() == 'for':
                                start_loop = True
                                start_cond = False
                            else:
                                start_loop = False
                                start_cond = True
                        else:
                            start_cond = False

                    else:
                        start_cond = True
                        start_loop = False
                        if len(self.listPomAdd) != 0:
                            self.listAdd.append(self.listPomAdd)
                            self.listPomAdd = []
                        self.listPomAdd.append('\040\040\040\040' + line + "\n")

                        #Test of function and end of function
                elif ('function' == line[0:len('function')].lower()) or \
                        ('ENDFUNC' == line):
                    if 'ENDFUNC' == line:
                        start_func = False
                    else:
                        start_func = True
                        self.func.append('\040\040\040\040' + line + "\n")

                #Test of END phase
                elif 'END' in line[0:3]:
                    self.pom_list = self.pom_list + self.action_list
                    self.phases.append(self.pom_list)
                    self.pom_list = []
                    self.action_list = []
                    start_phase = False

                #Adding to phases code: It's a test
                # when #@ is on the end of line
                elif '#@' == line[len(line) - 2:len(line)]:
                    self.pom_list.append('\040\040\040\040\040\040code: ' + \
                                         line[0:len(line) - 2] + '\n')

            start_pom = False

        #appedn to list outside Phases in the back of phases
        if len(self.outsidePhase) != 0:
            self.phases.append(self.outsidePhase)
            self.outsidePhase = []

        #adding authors from head
        if self.parseInfo.author != "None":
            if self.author != "":
                self.author += ", " + self.parseInfo.author
            else:
                self.author += self.parseInfo.author
        #adding description from head
        if self.parseInfo.description != "None":
            if self.description != "":
                self.description += ', ' + self.parseInfo.description
            else:
                self.description += self.parseInfo.description

        #adding keywords from head
        if self.parseInfo.keywords != "":
            self.keywords += self.parseInfo.keywords

    #method that parse multiple tags from line
    def parse_multiple_tags \
                    (self, list_of_words, begin_str, action_in, pom_add):
        out_str = begin_str
        sec_str = "\040\040\040\040\040\040"
        text_bool = False
        last_bool = True
        for word in list_of_words:
            if word[0:1] == '@':
                if len(out_str.strip()) == 0:
                    out_str += word[1:len(word)]

                elif text_bool:
                    out_str += "\n"
                    sec_str += "\n"
                    if action_in and pom_add:
                        self.action_list.append(out_str)
                        self.listPomAdd.append(sec_str)

                    elif action_in and not pom_add:
                        self.action_list.append(out_str)

                    elif not action_in and pom_add:
                        self.listPomAdd.append(sec_str)

                    elif not action_in and not pom_add:
                        self.pom_list.append(out_str)
                        action_in = True

                    last_bool = True
                    if len(begin_str.strip()) == 0:
                        out_str = "\040\040\040\040\040\040" + word[1:len(word)]
                    else:
                        out_str = begin_str + ', ' + word[1:len(word)]
                    sec_str = "\040\040\040\040\040\040"
                    text_bool = False

                else:
                    out_str += ', ' + word[1:len(word)]

            else:
                text_bool = True
                if last_bool and (len(out_str.strip()) != 0):
                    out_str += ': '
                    last_bool = False
                elif len(out_str.strip()) == 0:
                    last_bool = False

                sec_str += word + ' '
                out_str += word + ' '

        out_str += "\n"
        sec_str += "\n"
        if action_in and pom_add:
            self.action_list.append(out_str)
            self.listPomAdd.append(sec_str)

        elif action_in and not pom_add:
            self.action_list.append(out_str)

        elif not action_in and pom_add:
            self.listPomAdd.append(sec_str)

        elif not action_in and not pom_add:
            self.pom_list.append(out_str)

    """Method that tranfer file data to .txt documentattion """

    def text_output(self, out_bool):
        output_str = ""
        output_str += "Description: " + self.description + "\n"
        output_str += "Author: " + self.author + "\n"
        output_str += "Keywords: " + self.keywords + "\n\n"
        output_str += "Phases: \n"
        #print(self.phases)
        for i in self.phases:
            if len(i) != 0:
                for k in i:
                    output_str += k
                output_str += "\n"

        output_str += "Expected result: \n\n"
        output_str += "Additional information: \n"
        if len(self.loop) != 0:
            output_str += "\040\040 Loops:"
            print(self.loop)
            for loops in self.loop:
                if loops[0:len("\40\40\40\40for")] == "\40\40\40\40for":
                    output_str += "\n"
                output_str += loops

        if len(self.func) != 0:
            output_str += "\n\040\040 Functions:"
            for functions in self.func:
                if functions[0:len("\40\40\40\40function")] == "\40\40\40\40function":
                    output_str += "\n"
                output_str += functions

        if len(self.cond) != 0:
            output_str += "\n\040\040 Conditions:"
            for conditions in self.cond:
                if conditions[0:len("\40\40\40\40if")] == "\40\40\40\40if":
                    output_str += "\n"
                output_str += conditions

        if out_bool:
            file_out = open(self.filename[0: \
                len(self.filename) - 3] + "-DOC.txt", "w")
            file_out.write(output_str)
        else:
            sys.stdout.write(output_str)

    """method that creates moinmoin output of file"""

    def moin_output(self, out_bool):
        output_str = ""
        output_str += " .'''Description:''' " + self.description + "\n"
        output_str += " .'''Author:''' " + self.author + "\n"
        output_str += " .'''Keywords:''' " + self.keywords + "\n\n"
        output_str += "=== Phases: ===\n"
        for lists in self.phases:
            if len(lists) != 0:
                for block in lists:
                    if 'Outside Phase:' in block:
                        output_str += "\040\040'''''" + block.strip() + "'''''\n"

                    elif 'phasestart' in block.lower():
                        pom = block.strip().split()
                        if len(pom) > 1:
                            output_str += \
                                "\040\040'''" + pom[0] + "'''" + " ''" + block \
                                    [len(pom[0]) + 1:len(block)].strip() + "''\n"
                        else:
                            output_str += "\040\040'''" + block.strip() + "'''\n"

                    else:
                        pom = block.strip().split()
                        mark_bool = False
                        for sign in pom:
                            if ':' == sign[-1].strip():
                                #print(sign)
                                mark_bool = True

                        #need to claryfie where is tag or its 
                        #just specification of the block
                        if not mark_bool:
                            output_str += "\040\040\040\040 ." + block.strip() \
                                          + "\n"

                        else:
                            output_str += "\040\040\040\040\040\040 *" + \
                                          block.strip() + "\n"
                output_str += "\n"

        output_str += "=== Expected result: ===\n\n"
        output_str += "=== Additional information: ===\n"
        if len(self.loop) != 0:
            output_str += "\040\040 '''Loops:''' \n"
            for loops in self.loop:
                if loops[0:len('\040\040\040\040for')] == \
                        '\040\040\040\040for':
                    output_str += "\040\040\040\040''" + loops.strip() + "''\n"
                else:
                    output_str += "\040\040\040\040\040\040 *" + loops.strip() \
                                  + "\n"

        if len(self.func) != 0:
            output_str += "\n\040\040 '''Functions:''' \n"
            for functions in self.func:
                if functions[0:len('\040\040\040\040function')] == \
                        '\040\040\040\040function':
                    output_str += "\040\040\040\040''" + functions.strip() \
                                  + "''\n"
                else:
                    output_str += "\040\040\040\040\040\040 *" + \
                                  functions.strip() + "\n"

        if len(self.cond) != 0:
            output_str += "\n\040\040 '''Conditions:''' \n"
            for conditions in self.cond:
                if conditions[0:len('\040\040\040\040if')] == \
                        '\040\040\040\040if':
                    output_str += "\040\040\040\040''" + conditions.strip() \
                                  + "''\n"
                else:
                    output_str += "\040\040\040\040\040\040 *" + \
                                  conditions.strip() + "\n"

        if out_bool:
            file_out = open(self.filename[0: \
                len(self.filename) - 3] + "-MoinDOC.txt", "w")
            file_out.write(output_str)
        else:
            sys.stdout.write(output_str)

            #!!!!!!!!!!MAIN!!!!!!!!!!!!!!!!!!!

# Parse of arguments
parser = argparse.ArgumentParser(description= \
                                     'Parse arguments in cmd line for generator')
group = parser.add_mutually_exclusive_group()
parser.add_argument('files', metavar='file', type=str, nargs='+',
                    help='script file')
group.add_argument('--txt', '--TXT', dest='text_in', action='store_true',
                   default=False, help='argument to make txt doc file output')
group.add_argument('--moin', '--MOIN', dest='moin_in', action='store_true',
                   default=False, help='argument to make moinmoin doc file output')
parser.add_argument('-o', '--output', dest='out_in', action='store_true',
                    default=False, help='argument to save documentation to ouptut file')
parser_arg = parser.parse_args()

# cycle of script files to be transformed to documentation
for file_in_cmd in parser_arg.files:
    part = Gener(file_in_cmd)
    part.parse_tags()
    foo = NewTextDoc(part)
    foo.parse_data()
    if (not parser_arg.text_in and not parser_arg.moin_in) or \
            parser_arg.text_in:
        foo.text_output(parser_arg.out_in)
    elif parser_arg.moin_in:
        foo.moin_output(parser_arg.out_in)
