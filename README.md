The project targets BeakerLib based tests and is composed of two main parts: </br>
**bkrdoc** - a documentation generator </br>
**bkrlint** - a static analyser

Both tools are written purely in Python and support Python 2.7 and 3.2 - 3.5.

Note: *this is a development branch that is based on [bashlex](https://github.com/idank/bashlex) and is yet to be deployed*.

## BeakerLib
**BeakerLib** is a shell-level integration testing library, providing convenience functions which simplify writing, running and analysis of integration and blackbox tests.

https://fedorahosted.org/beakerlib/

## CI Status
The project is automatically tested by [Travis CI](https://travis-ci.org). Latest build status is: 
[![Build Status](https://travis-ci.org/rh-lab-q/bkrdoc.svg?branch=bkrdoc_with_bashlex)](https://travis-ci.org/rh-lab-q/bkrdoc)

## Prerequisites

Both tools require *bashlex* for parsing, specifically [our custom *devel* branch](https://github.com/blurrymoi/bashlex/tree/devel).
The current easiest way to get bashlex is fetching it from github using `git clone https://github.com/blurrymoi/bashlex.git` followed by a `python setup.py install` in the core directory (make sure you are on the *devel* branch when doing so).

## Package contents
After downloading the bkrdoc project from github, you will see the following directories:

_**bkrdoc/:**_
Folder containing the bkrdoc generator and the bkrlint linter.

_**bkrdoc/analysis/parser:**_
Folder with sources of the parser providing a common parsing logic for the two tools

_**bkrdoc/analysis/generator:**_
Folder with sources for automated documentation generator without documentation markup

_**bkrdoc/markup/:**_
Folder with sources for automated documentation generator with documentation markup

_**bkrdoc/analysis/linter:**_
Folder with sources for the static analyser

_**examples/:**_
This folder contains some **BeakerLib** tests and generated documentations

_**docs/:**_
Folder contains TODO options and first documentation format.

_**tests/:**_
Folder containing tests


bkrdoc
======

This project aims to provide tools for automated documentation generation for BeakerLib tests.

## 1. Introduction
### 1.1 What is bkrdoc?
**bkrdoc** is a documentation generator from tests written using the **BeakerLib** library. This generator makes documentation from test code with and also without any documentation markup.

### 1.2 What is it good for?
For fast, brief and reliable documentation creation. It's good for a quick start with an unknown **BeakerLib** test. Created documentation provides information about the documentation credibility. The documentation further shows environmental variables and helps the reader to run test script from which the documentation was created. 

### 1.3 How is bkrdoc licensed?
BSD license. See the LICENSE file in the distribution.

### 1.4 Contact details
Feel free to send me an email (Kulda12@seznam.cz) for any question you have on **bkrdoc** project.   

### 2 Installation process
Installation is very simple. You have two choices. First is to download rpm from [bkrdoc](https://pypi.python.org/pypi/bkrdoc) pypi and easily install it. Second choice is to download the whole project and after that run setup.py script in bkrdoc folder. For executing setup.py file you need to run this standard `python setup.py install` command. 

## 3. Using
### 3.1 Basic usage
After installation of bkrdoc rpm you can easily run bkrdoc by typing bkrdoc in command line. You can see on these examples:
```
for analysis:
bkrdoc analysis [analysis-options] [BeakerLib_test.sh]

for markup:
bkrdoc markup [markup-options] [BeakerLib_test.sh]
```

### 3.2 Documentation tags
First important thing is that all documentation comments **must** start with `#@`. For example this code comment `#@ Makes temporary directory and saves work in it` will create this documentation line: `Makes temporary directory and saves work in it`.

If a documentation comment is before BeakerLib phase, function, loop or condition this comment will be taken as a description. You can see what will happen on this example:
```bash
  #@ Various types of arguments will start this part
  rlPhaseStartTest "various argument types"
  
    #@ for every argument in selected word will do...
    for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
    do
        #@ Report argument
        rlRun "abrt-auto-reporting $arg"
    done
    #@ Reporting finished
  rlPhaseEnd
```
result:

```
  Test "various argument types"
    Various types of arguments will start this part
      loop: for every argument in selected word will do...
        Report argument
      Reporting finished
```

In the top of every generated documentation are three lines consisting of description, information about authors and keywords of the test. These three lines are generated from test template. But it can occur that the template is missing or you want to add more data and that you can do using these tags: `@keyword`, `@key`, `@author` and `@description`. For example: `#@ @key httpd` will add key into keywords line:
```
Description: Simple test
Author: Jan Kresla
Keywords: httpd
```

Also tagged generator supports block comments. Each block comment must start with `#@` as you can see on this example:

```bash
    #@ Somenthing in start of the test
    #@ Could be anything
    #@ Make temporary directory and saves work in it
    rlPhaseStartSetup
        TmpDir=$(mktemp -d)
        pushd $TmpDir
    rlPhaseEnd
```
will generate:

```
  Setup
    Somenthing in start of the test
    Could be anything
    Make temporary directory and saves work in it
```

useful feature is that bkrdoc generator could use existing BeakerLib command comment as you can see from below example:
```bash
rlPhaseStartSetup
  rlRun 'ps aux' 'ps command should not traceback' #@
  rlRun 'ps aux' 'ps command should not traceback' #@ check for traceback
rlPhaseEnd
```
will reproduce:

```
Setup
  ps command should not traceback
  check for traceback
```

Also markup version supports initial comment as a global whole test comment. This initial comment or block comment must be after shebang(also could be after test description made by beaker-wizard) and must start as usual with `#@`. You can see little example below:

```bash
#!/usr/bin/env bash

#@ This is the first line of initial documentation comment
#@ second line
#@ third line

PACKAGE="httpd"
HttpdPages="/var/www/html"
HttpdLogs="/var/log/httpd"
.
.
```
will reproduce:

```bash
Description: -
Author: -
Purpose: This is the first line of initial documentation comment
         second line
         third line
Keywords: -
.
.
```
