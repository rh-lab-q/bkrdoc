#author Jiri Kulda 

import sys , locale, re


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
		if (File[(len(File)-3):len(File)] == ".sh"):

			try:
				self.filename = File
				self.inputfile = open(File ,"r",errors='strict')
				self.fileString = self.inputfile.read()
                                                
			except IOError:
				self.fail = False
				sys.stderr.write("ERROR: Fail to open file: " + File + "\n")
				sys.exit(1)

			finally:
				if (self.fail != False):
					self.inputfile.close()
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
					self.block.append(line)
				
				self.comments.append(self.block)
				self.block = []
				self.NextLine = False
				self.BlockComm = False

			else:
				self.BlockComm = False
				if (line[len(line)-2:len(line)] == "#@"):
					POM.append(line)
					self.comments.append(POM)
					POM = []
					
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
	parseInfo = ""
	def __init__(self,parseInfoo):
		self.filename = parseInfoo.filename
		self.parseInfo = parseInfoo

	#function to parse all data from test
	def parseData(self):
		
		STARTP = False
		STARTC = False
		STARTF = False
		STARTL = False
		SWAP = False
		STARTB = False
		
		for doc in self.parseInfo.comments:

			for line in doc:
				#print(line)
				#print(STARTC)
				if ('phasestart' in line.lower()):
					self.pom_list.insert(0,'\t' + line.strip() + "\n")

					STARTP = True
					STARTB = True

					if (len(self.outsidePhase) != 0):
							self.phases.append(self.outsidePhase)
							self.outsidePhase = []

				elif ('@author' in line.lower()):
					pom_aut_str = line[1:len(line)].strip()
					if (self.author != ""):
						self.author += ", " + pom_aut_str[len('@author'): len(line)].strip()
					else: 
						self.author = pom_aut_str[len('@author'): len(line)].strip()

				elif (('@keywords' in line.lower()) or ('@key' in line.lower()) ):
					pom_key = line[1:len(line)].split()
					pom_key_str = line[1:len(line)].strip()
					
					if (len(pom_key[0]) == 1):
						del pom_key[0]
						pom_key_str = pom_key_str[1:len(pom_key_str)].strip()

					self.keywords += pom_key_str[len(pom_key[0]):len(line)].strip() + ", "

				elif ((('@' == line[0:1]) or ('&' == line[0:1]) )):
					pom_list = line[1:len(line)].split()
					pom_str = line[1:len(line)].strip()

					if (len(pom_list[0]) == 1):
						del pom_list[0]
						pom_str = pom_str[1:len(pom_str)].strip()


					if ('@' == pom_str[0][0:1]):
						#print("mmmmmm" + line)
						if (STARTL == True):
							self.action_list.append('\t\t\t' + "loop, "+ pom_list[0][1:len(pom_list[0])] + ": " + pom_str[len(pom_list[0]) :len(line)].strip() + "\n" )
							self.loop.append('\t\t\t' + pom_str[len(pom_list[0]) :len(line)].strip() + "\n" )

						elif(STARTC == True):
							self.action_list.append('\t\t\t' + "condition, " + pom_list[0][1:len(pom_list[0])]+ ": " + pom_str[len(pom_list[0]):len(pom_str)].strip() + "\n" )
							self.cond.append('\t\t\t' + pom_str[len(pom_list[0]) :len(line)].strip() + "\n" )

						elif(STARTP == True):
							self.action_list.append('\t\t\t' + pom_list[0][1:len(pom_list[0])]+ ": " + pom_str[len(pom_list[0]):len(pom_str)].strip() + "\n" )


					elif (STARTP == True):

						if(STARTL == True):
							self.action_list.append('\t\t\t' + "loop: " + line[1:len(line)].strip() + "\n" )
							self.loop.append('\t\t\t' + line[1:len(line)].strip() + "\n" )

						elif(STARTC == True):
							self.action_list.append('\t\t\t' + "condition: " + line[1:len(line)].strip() + "\n" )
							self.cond.append('\t\t\t' + line[1:len(line)].strip() + "\n" )

						elif(STARTB == False):
							self.action_list.append('\t\t\t' + "action: " + line[1:len(line)].strip() + "\n")

						else:
							self.pom_list.append('\t\t' + line[1:len(line)].strip() + "\n")

				

					elif(STARTF == True):
						self.func.append('\t\t\t' + pom_str + "\n" )

					elif(STARTP == False):
						if (len(self.outsidePhase) != 0):
							self.outsidePhase.append('\t\t' + line[1:len(line)].strip() + "\n")
						else:
							self.outsidePhase.append('\t' + 'Outside Phase:\n')
							self.outsidePhase.append('\t\t' + line[1:len(line)].strip() + "\n")


				elif(('for' == line[0:3]) or ('ENDLOOP' == line[0:len('ENDLOOP')]) ):
					if (('ENDLOOP' == line[0:len('ENDLOOP')])):
						STARTL = False
						if (SWAP == True):
							SWAP = False
							STARTC = True
					else:
						STARTL = True
						self.loop.append('\t\t' + line + "\n")
						if (STARTC == True):
							SWAP = True
							STARTC = False

				elif(('if' == line[0:2]) or ('ENDCOND' == line)):
					if ('ENDCOND' == line):
						STARTC = False
						if (SWAP == True):
							SWAP = False
							STARTL = True
					
					else:
						STARTC = True
						self.cond.append('\t\t' + line + "\n")
						if (STARTL == True):
							SWAP = True
							STARTL = False

				elif(('function' == line[0:len('function')].lower()) or ('ENDFUNC' == line)):
					if ('ENDFUNC' == line):
						STARTF = False
					else:
						STARTF = True
						self.func.append('\t\t' + line + "\n")

				elif ('END' in  line[0:3]):
					self.pom_list = self.pom_list + self.action_list
					self.phases.append(self.pom_list)
					self.pom_list = []
					self.action_list =[]
					STARTP = False

				elif ('#@' == line[len(line)-2:len(line)]):
					self.pom_list.append('\t\t\tcode: ' + line[0:len(line)-2] + '\n')

			STARTB = False

		if (len(self.outsidePhase) != 0):
			self.phases.append(self.outsidePhase)
			self.outsidePhase = []

		if (self.parseInfo.author != "None"):
			if (self.author != ""):
				self.author += ", " + self.parseInfo.author
			else:
				self.author += self.parseInfo.author
		
		if(self.parseInfo.description != "None"):
			self.description += self.parseInfo.description

		if(self.parseInfo.keywords != ""):
			self.keywords += self.parseInfo.keywords


	def textOutput(self):
		fileOut = open(self.filename[0:len(self.filename) - 3] + "-DOC.txt", "w")
		fileOut.write("Description: " + self.description + "\n")
		fileOut.write("Author: " + self.author + "\n")
		fileOut.write("Keywords: " + self.keywords + "\n\n")
		fileOut.write("Phases: \n")
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
				




#!!!!!!!!!!MAIN!!!!!!!!!!!!!!!!!!!
#List of references on class gener
parts = []

#Options of output doc file
TXT = False
PDF = False
LATEX = False

""" Cycle for parse arguments """
for arguments in sys.argv[1:sys.argv.__len__()]:
	if(arguments == "--txt"):
		print("TXT" + arguments)
		TXT = True

	elif(arguments == "--pdf"):
		print("PDF" + arguments)
		PDF = True

	elif(arguments == "--tex"):	
		print("LATEX " + arguments)
		LATEX = True

	else:
		myGener = ""
		myGener = gener(arguments)
		parts.append(myGener)


if ((TXT == True and PDF == True) or (TXT == True and LATEX == True) or (PDF == True and LATEX == True)):
	sys.stderr.write("ERROR: Too many types of output format \n")
	sys.exit(1)


for part in parts:
	part.comments = []
	part.block = []
	part.parseTags()
	#print(part.comments)
	#print("---------------------------------------------------")
	foo = NewTextDoc(part)
	foo.phases = []
	foo.func = []
	foo.loop = []
	foo.cond = []
	foo.pom_list = []
	foo.action_list = []
	foo.outsidePhase = []
	foo.parseData()
	foo.textOutput()


