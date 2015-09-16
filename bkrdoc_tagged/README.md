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

### Documentation tags
Firt important thing is that all documentation comments **must** start with `#@`. For example this code comment `#@ Makes temporary directory and saves work in it` will create this documentation line: `Makes temporary directory and saves work in it`.





## 4. CI Status
**bkrdoc** is automatically tested by [Travis CI project](https://travis-ci.org). Latest build status is: 
[![Build Status](https://travis-ci.org/rh-lab-q/bkrdoc.svg?branch=master)](https://travis-ci.org/rh-lab-q/bkrdoc)

