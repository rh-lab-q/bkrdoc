bkrdoc
======

This project aims to provide tools for automated documentation generation for BeakerLib tests.

## 1. Introduction
### 1.1 What is bkrdoc?
**bkrdoc** is a documentation generator from tests written using **BeakerLib** library. This generator makes documentation from test code with and also without any documentation markup.

### 1.2 What it`s good for?
For fast, brief and reliable documentation creation. It`s good for quick start with unknown **BeakerLib** test. Created documentations provides information about the documentation credibility. Also created documentations shows environmental variables and helps reader to run test script from which was documentation created. 

**bkrdoc** is written in pure python.

### 1.3 What is BeakerLib?
**BeakerLib** is a shell-level integration testing library, providing convenience functions which simplify writing, running and analysis of integration and blackbox tests.

https://fedorahosted.org/beakerlib/

### 1.4 How is bkrdoc licensed?
BSD license. See the LICENSE file in the distribution.

### 1.5 Contact details
Feel free to send me an email (Kulda12@seznam.cz) for any question you have on **bkrdoc** project.   

## 2. Installing

### 2.1 Prerequisites
- **bkrdoc** was tested on Python 2.7 and 3.3 versions on Linux. 
- **bkrdoc** has no external dependencies.

### 2.2 Installation process
Installation is very simple. You have two choices. First is to download rpm from [bkrdoc](https://pypi.python.org/pypi/bkrdoc) pypi and easily install it. Second choice is to download whole project and after that run setup.py script in bkrdoc folder. For executing setup.py file you need to run this standard `python setup.py install` command. 

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

Also markup version supports initial comment as a global whole test comment. This initial comment or block comment must be after shebang(also could be after test description made by beaker-wizard) and must start as usuall with `#@`. You can see little example below:

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

## 4. Package contents
After downloading bkrdoc project, you will see following files and directories:

_**README.md:**_
This README file.

_**LICENSE:**_
File with bkrdoc license.

_**bkrdoc/:**_
Folder with bkrdoc generator which is creating documentations from **BeakerLib** tests with and without any documentation markup.

_**bkrdoc/analysis/:**_
Folder with sources for automated documentation generator without documentation markup

_**bkrdoc/markup/:**_
Folder with sources for automated documentation generator with documentation markup

_**examples/:**_
This folder contains some **BeakerLib** tests and generated documentations

_**docs/:**_
Folder contains TODO options and first documentation format.

_**tests/:**_
Folder contains files for bkrdoc testing

## 5. CI Status
**bkrdoc** is automatically tested by [Travis CI project](https://travis-ci.org). Latest build status is: 
[![Build Status](https://travis-ci.org/rh-lab-q/bkrdoc.svg?branch=master)](https://travis-ci.org/rh-lab-q/bkrdoc)

