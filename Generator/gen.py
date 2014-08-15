#!/usr/bin/python
#author Jiri Kulda 
    
import sys


class gener(object):
    fileString = ""
    inputfile = ""
    fail = True
    skip = False
    BlockComm = False
    NextLine = False
    filename = ""
	


	#List of comments
    comments = []
	
	#Helpfull list
    block = []

	#String of Author of a test
    author = "None"

	#String of Description of a test
    description = "None"

	#Strin of Keywords of a test
    keywords = ""

    def __init__(self, File):
        self.comments = []
        self.block = []
        if (File[(len(File)-3):len(File)] == ".sh"):

            try:
                self.filename = File
                with open(File,"r") as inputfile:
				#inputfile = open(File ,"r",errors='strict')
                    self.fileString = inputfile.read()
                                                
            except IOError:
                self.fail = False
                sys.stderr.write("ERROR: Fail to open file: " + File + "\n")
                sys.exit(1)

        else:
            print("ERROR: Not a script file. (.sh)")
			#TODO ... osetrit zadani ne scrip file. Aby nepokracoval dal ...


    def parseTags(self):
        POM = []
        FUNCTION = False

        for line in self.fileString.split('\n'):
            line = line.strip()
			#print("............." + line)
			#print( self.BlockComm)
			#print( self.NextLine)
            if((len(line) >= 2) and (line[0] == "#")):
                self.parseLine(line[1:len(line)].strip())


            elif(self.NextLine == True):
                if (('phasestart' in line.lower()) or (line[0:2].lower() == 'if') or (line[0:3].lower() == 'for') ):
                    self.block.insert(0,line)

                elif((line[0:len('function')].lower() == 'function')):
                    self.block.insert(0,line)
                    FUNCTION = True

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
                if (line[len(line)-2:len(line)] == "#@"):
                    POM.append(line)
                    self.comments.append(POM)
                    POM = []
					
                elif (('phasestart' in line.lower()) or (line[0:2].lower() == 'if') or (line[0:3].lower() == 'for') ):
                    self.block.insert(0,line)
                    self.comments.append(self.block)
                    self.block = []    

                elif ('phaseend' in line.lower()):
                    POM.append("END")
                    self.comments.append(POM)
                    POM = []

                elif('done' == line[0:4]):
                    POM.append("ENDLOOP")
                    self.comments.append(POM)
                    POM = []

                elif('fi' == line[0:2]):
                    POM.append("ENDCOND")
                    self.comments.append(POM)
                    POM = []

                elif('}' == line[0:1] and FUNCTION == True):
                    POM.append("ENDFUNC")
                    self.comments.append(POM)
                    POM = []

	#funciton to parse line with comments
    def parseLine(self,Line):
        Line = Line.strip()
        POM = []
        if((Line[0] == '@') and (self.BlockComm == False)):
            self.BlockComm = True
            self.NextLine = True
            self.block.append(Line)

        elif(self.BlockComm == True):
            self.block.append("&" + Line)

        elif(('description' in Line[0:len('description')].lower())):
            self.description = Line[len('description')+1: len(Line)]

        elif(('author' in Line[0:len('author')].lower())):
            self.author = Line[len('author')+1: len(Line)]

        elif('key' in Line[0:3].lower()):
            pom_str = Line.split()
            self.keywords = Line[len(pom_str[0]):len(Line)].strip() + ","
		

# Class to make document
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
    def __init__(self,parseInfoo):
        self.filename = parseInfoo.filename
        self.parseInfo = parseInfoo
        self.phases = []
        self.func = []
        self.loop = []
        self.cond = []
        self.pom_list = []
        self.action_list = []
        self.outsidePhase = []
        self.listAdd = []
        self.listPomAdd = []

	#function to parse all data from test
    def parseData(self):
		
        STARTP = False
        STARTC = False
        STARTF = False
        STARTL = False
        STARTB = False
		
        for doc in self.parseInfo.comments:

            for line in doc:
				#print(self.listPomAdd)
				#print(self.listAdd)
                #print(line)
				#print(STARTC)
				#print(STARTL)
				#print("---------------------------------------------")
				#print(STARTC)
                if ('phasestart' in line.lower()):
                    self.pom_list.insert(0,'\t' + line.strip() + "\n")

                    STARTP = True
                    STARTB = True

                    if (len(self.outsidePhase) != 0):
                        self.phases.append(self.outsidePhase)
                        self.outsidePhase = []

				#Test of tag description in test
                elif('@description' in line.lower()):
                    pom_desc_str = line[1:len(line)].strip()
                    if (self.description != ""):
                        self.description += ", " + pom_desc_str[len('@description'): len(line)].strip()
                    else: 
                        self.description = pom_desc_str[len('@description'): len(line)].strip()

				#test of authors in test
                elif ('@author' in line.lower()):
                    pom_aut_str = line[1:len(line)].strip()
                    if (self.author != ""):
                        self.author += ", " + pom_aut_str[len('@author'): len(line)].strip()
                    else: 
                        self.author = pom_aut_str[len('@author'): len(line)].strip()

				#Test of keywords in test
                elif (('@keywords' in line.lower()) or ('@key' in line.lower()) ):
                    pom_key = line[1:len(line)].split()
                    pom_key_str = line[1:len(line)].strip()
					
                    if (len(pom_key[0]) == 1):
                        del pom_key[0]
                        pom_key_str = pom_key_str[1:len(pom_key_str)].strip()

                    self.keywords += pom_key_str[len(pom_key[0]):len(line)].strip() + ", "

				#test of coments and block comments
                elif ((('@' == line[0:1]) or ('&' == line[0:1]) )):
                    pom_list = line[1:len(line)].split()
                    pom_str = line[1:len(line)].strip()

                    if (len(pom_list[0]) == 1):
                        del pom_list[0]
                        pom_str = pom_str[1:len(pom_str)].strip()

					#geting multiple of tags
                    if ('@' == pom_str[0][0:1]):
                        pom_str = ""
                        if (STARTL == True):
                            pom_str += "\t\t\tloop"
                            self.parseMultipleTags(pom_list,pom_str,True,True)
							#self.listPomAdd.append('\t\t\t' + pom_str[len(pom_list[0]) :len(line)].strip() + "\n" )

                        elif(STARTC == True):
                            pom_str += "\t\t\tcondition"
                            self.parseMultipleTags(pom_list,pom_str,True,True)
							#self.listPomAdd.append('\t\t\t' + pom_str[len(pom_list[0]) :len(line)].strip() + "\n" )

                        elif(STARTP == True):
                            pom_str += "\t\t\t"
                            self.parseMultipleTags(pom_list,pom_str,True,False)

					#When STARTP(Phase) is activated, then saves according to cond etc... data
                    elif (STARTP == True):
                        pom_str = ""
                        if(STARTL == True):
                            pom_str += "\t\t\tloop"
                            self.parseMultipleTags(pom_list,pom_str,True,True)

                        elif(STARTC == True):
                            pom_str += "\t\t\tcondition"
                            self.parseMultipleTags(pom_list,pom_str,True,True)

                        elif(STARTB == False):
                            pom_str += "\t\t\taction"
                            self.parseMultipleTags(pom_list,pom_str,True,False)

                        else:
                            pom_str += "\t\t"
                            self.parseMultipleTags(pom_list,pom_str,False,False)

				
					#saves data of function to func list
                    elif(STARTF == True):
                        self.func.append('\t\t\t' + pom_str + "\n" )

					#saving out of phase data
                    elif(STARTP == False):
                        if (len(self.outsidePhase) != 0):
                            self.outsidePhase.append('\t\t' + line[1:len(line)].strip() + "\n")
                        else:
                            self.outsidePhase.append('\t' + 'Outside Phase:\n')
                            self.outsidePhase.append('\t\t' + line[1:len(line)].strip() + "\n")

				#Test of loops and end of loops and multiple cond or loops
                elif(('for' == line[0:3]) or ('ENDLOOP' == line[0:len('ENDLOOP')]) ):

                    if (('ENDLOOP' == line[0:len('ENDLOOP')])):
                        self.loop += self.listPomAdd
                        self.listPomAdd = []
                        if (len(self.listAdd) != 0):
                            self.listPomAdd = self.listAdd[-1]
                            del self.listAdd[-1]
                            if (self.listPomAdd[0][0:5].strip() == 'for'):
                                STARTL = True
                                STARTC = False
                            else:
                                STARTL = False
                                STARTC = True
                        else:
                            STARTL = False

                    else:
                        STARTL = True
                        STARTC = False
                        if (len(self.listPomAdd) != 0 ):
                            self.listAdd.append(self.listPomAdd)
                            self.listPomAdd = []
                        self.listPomAdd.append('\t\t' + line + "\n")


				#Test of condition and end of condition and multiple cond or loops
                elif(('if' == line[0:2]) or ('ENDCOND' == line)):
                    if ('ENDCOND' in line):
                        self.cond += self.listPomAdd
                        self.listPomAdd = []
                        if (len(self.listAdd) != 0):
                            self.listPomAdd = self.listAdd[-1]
                            del self.listAdd[-1]
                            if (self.listPomAdd[0][0:5].strip() == 'for'):
                                STARTL = True
                                STARTC = False
                            else:
                                STARTL = False
                                STARTC = True
                        else:
                            STARTC = False

                    else:
                        STARTC = True
                        STARTL = False
                        if (len(self.listPomAdd) != 0 ):
                            self.listAdd.append(self.listPomAdd)
                            self.listPomAdd = []
                        self.listPomAdd.append('\t\t' + line + "\n") 

				#Test of function and end of function
                elif(('function' == line[0:len('function')].lower()) or ('ENDFUNC' == line)):
                    if ('ENDFUNC' == line):
                        STARTF = False
                    else:
                        STARTF = True
                        self.func.append('\t\t' + line + "\n")
				
				#Test of END phase
                elif ('END' in  line[0:3]):
                    self.pom_list = self.pom_list + self.action_list
                    self.phases.append(self.pom_list)
                    self.pom_list = []
                    self.action_list =[]
                    STARTP = False

				#Adding to phases code: It's a test when #@ is on the end of line
                elif ('#@' == line[len(line)-2:len(line)]):
                    self.pom_list.append('\t\t\tcode: ' + line[0:len(line)-2] + '\n')

            STARTB = False

		#appedn to list outside Phases in the back of phases
        if (len(self.outsidePhase) != 0):
            self.phases.append(self.outsidePhase)
            self.outsidePhase = []

		#adding authors from head
        if (self.parseInfo.author != "None"):
            if (self.author != ""):
                self.author += ", " + self.parseInfo.author
            else:
                self.author += self.parseInfo.author
		#adding description from head
        if(self.parseInfo.description != "None"):
            if (self.description != ""):
                self.description += ', ' + self.parseInfo.description
            else:
                self.description += self.parseInfo.description

		#adding keywords from head
        if(self.parseInfo.keywords != ""):
            self.keywords += self.parseInfo.keywords

	#method that parse multiple tags from line
    def parseMultipleTags(self,listOfWords,beginStr,ACTION,POMADD):
        outStr = beginStr
        secStr = "\t\t\t"
        TEXT = False
        LAST = True
        for word in listOfWords:
            if (word[0:1] == '@'):
                if (len(outStr.strip()) == 0):
                    outStr += word[1:len(word)]

                elif(TEXT == True):
                    outStr += "\n"
                    secStr += "\n"
                    if((ACTION == True) and (POMADD == True)):
                        self.action_list.append(outStr)
                        self.listPomAdd.append(secStr)

                    elif((ACTION == True) and (POMADD == False)):
                        self.action_list.append(outStr)

                    elif((ACTION == False) and (POMADD == True)):
                        self.listPomAdd.append(secStr)

                    elif((ACTION == False) and (POMADD == False)):
                        self.pom_list.append(outStr)
                        ACTION = True
					

                    LAST = True
                    if (len(beginStr.strip()) == 0):
                        outStr = "\t\t\t" + word[1:len(word)]
                    else:
                        outStr = beginStr + ', ' + word[1:len(word)]
                    secStr = "\t\t\t"
                    TEXT = False
				
                else:
                    outStr += ', ' + word[1:len(word)]

            else:
                TEXT = True
                if ((LAST == True) and (len(outStr.strip()) != 0) ):
                    outStr += ': '
                    LAST = False
                elif((len(outStr.strip()) == 0)):
                    LAST = False

                secStr += word + ' '	
                outStr += word + ' '

        outStr += "\n"
        secStr += "\n"
        if((ACTION == True) and (POMADD == True)):
            self.action_list.append(outStr)
            self.listPomAdd.append(secStr)

        elif((ACTION == True) and (POMADD == False)):
            self.action_list.append(outStr)

        elif((ACTION == False) and (POMADD == True)):
            self.listPomAdd.append(secStr)

        elif((ACTION == False) and (POMADD == False)):
            self.pom_list.append(outStr)

        outStr = ""
        secStr = ""

    """Method that tranfer file data to .txt documentattion """
    def textOutput(self):
        fileOut = open(self.filename[0:len(self.filename) - 3] + "-DOC.txt", "w")
        fileOut.write("Description: " + self.description + "\n")
        fileOut.write("Author: " + self.author + "\n")
        fileOut.write("Keywords: " + self.keywords + "\n\n")
        fileOut.write("Phases: \n")
        #print(self.phases)
        for i in self.phases:
            if (len(i) != 0):
                for k in i:
                    fileOut.write(k)
                fileOut.write("\n")

        fileOut.write("Expected result: \n\n")
        fileOut.write("Additional information: \n")
        if (len(self.loop) != 0):
            fileOut.write("\t Loops: \n")
            for loops in self.loop:
                fileOut.write(loops)

        if (len(self.func) != 0):
            fileOut.write("\n\t Functions: \n")
            for functions in self.func:
                fileOut.write(functions)

        if (len(self.cond) != 0):
            fileOut.write("\n\t Conditions: \n")
            for conditions in self.cond:
                fileOut.write(conditions) 
				
    def moinOutput(self):
        fileOut = open(self.filename[0:len(self.filename) - 3] + "-MoinDOC.txt", "w")
        fileOut.write(" .'''Description:''' " + self.description + "\n")
        fileOut.write(" .'''Author:''' " + self.author + "\n")
        fileOut.write(" .'''Keywords:''' " + self.keywords + "\n\n")
        fileOut.write("=== Phases: ===\n")
        for lists in self.phases:
            if (len(lists) != 0):
                for block in lists:
                    if ('Outside Phase:' in block):
                        fileOut.write("\t'''''" + block.strip() + "'''''\n" )
                    
                    elif('phasestart' in block.lower()):
                        pom = block.strip().split()
                        if (len(pom) > 1):
                            fileOut.write("\t'''" + pom[0] + "'''" + " ''" + block[len(pom[0]) + 1:len(block)].strip() + "''\n")
                        else:
                            fileOut.write("\t'''" + block.strip() + "'''\n")
                    
                    else:
                        pom = block.strip().split()
                        MARK = False
                        for sign in pom:
                            if (':' == sign[-1].strip()):
                                #print(sign)
                                MARK = True
                        
                        #need to claryfie where is tag or its just specification of the block
                        if (MARK == False):
                            fileOut.write("\t\t ." + block.strip() + "\n")

                        else:
                            fileOut.write("\t\t\t *" + block.strip() + "\n")
                fileOut.write("\n")

        fileOut.write("=== Expected result: ===\n\n")
        fileOut.write("=== Additional information: ===\n")  
        if (len(self.loop) != 0):
            fileOut.write("\t '''Loops:''' \n")
            for loops in self.loop:
                if (loops[0:len('\t\tfor')] == '\t\tfor'):
                    fileOut.write("\t\t''" + loops.strip() + "''\n")
                else:
                    fileOut.write("\t\t\t *" + loops.strip() + "\n")

        if (len(self.func) != 0):
            fileOut.write("\n\t '''Functions:''' \n")
            for functions in self.func:
                if (functions[0:len('\t\tfunction')] == '\t\tfunction'):
                    fileOut.write("\t\t''" + functions.strip() + "''\n")
                else:
                    fileOut.write("\t\t\t *" + functions.strip() + "\n")

        if (len(self.cond) != 0):
            fileOut.write("\n\t '''Conditions:''' \n")
            for conditions in self.cond:
                if (conditions[0:len('\t\tif')] == '\t\tif'):
                    fileOut.write("\t\t''" + conditions.strip() + "''\n")
                else:
                    fileOut.write("\t\t\t *" + conditions.strip() + "\n")       


#!!!!!!!!!!MAIN!!!!!!!!!!!!!!!!!!!
#List of references on class gener
parts = []

#Options of output doc file
TXT = False
MOIN = False
LATEX = False
"""
parser = optparse.OptionParser()
parser.add_option('-t', '--txt', '--TXT', 
                  dest="check_text", 
                  default=False,action="store_true",
                  )
parser.add_option('-m', '--moin','--MOIN',
                  dest="check_moin",
                  default=False,
                  action="store_true",
                  )
option = parser.parse_args()
print(option.check_text())
print(option.check_moin())
print(option)
"""
""" Cycle for parse arguments """
for arguments in sys.argv[1:sys.argv.__len__()]:
    if(arguments == "--txt"):
        TXT = True

    elif(arguments == "--moin"):
        MOIN = True

    else:
        myGener = ""
        myGener = gener(arguments)
        parts.append(myGener)

#Test of formats. It could be different
if ((TXT == True and MOIN == True) or (TXT == True and LATEX == True) or (MOIN == True and LATEX == True)):
    sys.stderr.write("ERROR: Too many types of output format \n")
    sys.exit(1)

#cycle of cript files to be transformed to documentation
for part in parts:
    part.parseTags()
    #print(part.comments)
    foo = NewTextDoc(part)
    foo.parseData()
    if (((MOIN == False) and (TXT == False)) or (TXT == True)):
        foo.textOutput()
    elif(MOIN == True):
        foo.moinOutput()