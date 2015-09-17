bkrdoc
======

This project aims to provide tool for automated documentation generation for BeakerLib tests.

## 1. Introduction
### 1.1 What is bkrdoc?
**bkrdoc** is a documentation generator from tests written using **BeakerLib** library. This generator makes documentation from test code with specific documentation markup.

### 1.2 What it`s good for?
For fast, brief and reliable documentation creation.  

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

## 3. Using
### 3.1 Basic usage
Documentation generator is `tagged_generator.py` file. To create documentation from **BeakerLib** test you need to execute `tagged_generator.py` file. Shown on this example:`python tagged_generator.py [BeakerLib_test.sh]`.

### 3.2 Documentation tags
Firt important thing is that all documentation comments **must** start with `#@`. For example this code comment `#@ Makes temporary directory and saves work in it` will create this documentation line: `Makes temporary directory and saves work in it`.

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

In the top of every generated documentation are three lines consits of description, information about authors and keyword of the test. These three lines are generated from test template. But it can occur that the template is missing or you want to add more data and that you can do using these tags: `@keyword`, `@key`, `@author` and `@description`. For example: `#@ @key httpd` will add key into keywords line:
```
Description: Simple test
Author: Jan Kresla
Keywords: httpd
```

Also tagged generator supports block comments. Block comments must start with `#@` but following documentation comments can start with simple `#` as you can see on this example:

```bash
    #@ Somenthing in start of the test
    # Could be anything
    # Make temporary directory and saves work in it
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


## 4. CI Status
**bkrdoc** is automatically tested by [Travis CI project](https://travis-ci.org). Latest build status is: 
[![Build Status](https://travis-ci.org/rh-lab-q/bkrdoc.svg?branch=master)](https://travis-ci.org/rh-lab-q/bkrdoc)

