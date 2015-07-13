bkrdoc
======

This project aims to provide tools for automated documentation generation for BeakerLib tests.

## 1. Introduction
### 1.1 What is bkrdoc?
**bkrdoc** is a documentation generator from tests written using **BeakerLib** library. This generator makes documentation from test code without any documentation markup.

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
Instalation is very simple. First you need to download whole project and after that run setup.py script in bkrdoc_not_tagged folder. For executing setup.py file you need to run this standart `python setup.py install`. 

## 3. Using
### 3.1 Basic usage
Documentation generator is `documentation_generator.py` file. To create documentation from **BeakerLib** test you need to execute `documentation_generator.py` file. Shown on this example:`python documentation_generator.py [BeakerLib_test.sh]`.

## 4. Package contents
After downloading bkrdoc project, you will see following files and directories:

_**README.md:**_
This README file.

_**LICENSE:**_
File with bkrdoc license.

_**bkrdoc_not_tagged/:**_
Folder with bkrdoc generator which is creating documentations from **BeakerLib** tests without any documentation markup.

_**bkrdoc_tagged/:**_
Folder with bkrdoc generator which is creating documentation from **BeakerLib** test _with_ specific documentation markup.

## 5. CI Status
**bkrdoc** is automatically tested by [Travis CI project](https://travis-ci.org). Latest build status is: 
[![Build Status](https://travis-ci.org/rh-lab-q/bkrdoc.svg?branch=master)](https://travis-ci.org/rh-lab-q/bkrdoc)

