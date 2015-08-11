__author__ = 'jkulda'

import codecs
import bashlex

try:
    with open('comments', "r") as input_file:
        test = input_file.read()
except:
    print("chyba!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

pokus = ""
pokus = test
'''append = False
for line in test.split('\n'):
    line = line.strip()

    if line[0:1] != '#' and len(line) >= 1:
        if line[-1:] == '\\':
            pokus += line[0:-1] + "\n"
            append = True
        elif append:
            pokus = pokus[0:-1] + " "
            pokus += line + "\n"
            append = False
        else:
            pokus += line + "\n"
'''

parts = bashlex.parse(pokus)
for ast in parts:
    print ast.dump()