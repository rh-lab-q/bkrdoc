#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of bugzilla-3-6-test-suite
#   Description: This test is for testing Bugzilla version 3.6. It first installs the required rpm
#   dependencies via yum, then executes all of the test files in t/ directory to test the Bugzilla 
#   code and report the related results.
#   Author: Dave Lawrence <dkl@redhat.com>
#           Dave Lawrence <dkl@mozilla.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2010 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include beaker environment
. /usr/share/beakerlib/beakerlib.sh

PACKAGE="bugzilla"
BZ_HOME_DIR="/var/www/html/bugzilla"
LOG=""
RESULT="PASS"
TESTOUTPUTFILE=""

# List of packages to install using yum from the bz3 repo. Eventually we should be able to just do 
# yum -y install bugzilla-testsuite
# and everything will be pulled in automatically as needed.
YUM_PACKAGES="httpd mysql-server firefox.x86_64 tigervnc-server-minimal perl-Test-WWW-Selenium java-1.6.0-openjdk"

#@ function which run test case
function run_test_case ()
 {
    echo $1 >> $TESTOUTPUTFILE
    rlRun $LOG "perl -I. -Ilib -It/lib $1 >>$TESTOUTPUTFILE 2>&1 2;" 0 $1
    #@ test if previous action has passed 
    if [ $? -eq 0 ]
    then
        rlReport $1 PASS 
    else
        rlReport $1 FAIL 
        RESULT="FAIL"
    fi
}

#@ Function which creates test data
function create_test_data () 
{
    rlLog "Creating Bugzilla test data"
    rlRun $LOG "echo 'drop database bugs;' | mysql" 0,1 "Dropping current bugs database"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl first time"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl second time"
    rlRun $LOG "perl t/config/generate_test_data.pl" 0 "Generating test data"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl third time"
}

rlJournalStart
    rlPhaseStartSetup
        # Turn off SELinux
        # rlRun $LOG "/usr/sbin/setenforce 0" 0 "Turning off SELinux"

        # Extract the Bugzilla code
        rlRun $LOG "tar zxvf bugzilla.tar.gz" 0 "Unarchiving Bugzilla code"

        rlRun $LOG "yum -y install $YUM_PACKAGES" 0 "Installing required packages"
        #@ Copy yum repo config and install all necessary rpms for testing
        for i in $YUM_PACKAGES
        do
            rlAssertRpm $i
        done

        #@ Remove the i386 Firefox if installed
        rlRun "yum -y remove firefox.i386" 0,1 "Removing i386 Firefox if installed"
 
        # Setup the Bugzilla web root directory
        rlRun $LOG "rm -rf /var/www/html/bugzilla" 0 "Deleting old Bugzilla installation and installing test"
        rlRun $LOG "mv bugzilla $BZ_HOME_DIR" 0 "Moving Bugzilla directory to webroot"
        rlRun $LOG "cd $BZ_HOME_DIR" 0 "Changing to Bugzilla directory"

        # @ Setup up Bugzilla configuration files
        rlRun $LOG "mkdir -p data" 0 "Creating data directory"
        rlRun $LOG "cp t/config/params data/." 0 "Copying data/params file into right place"
        # rlRun $LOG "chmod 644 data/params" 0 "Setting permissions on data/params file"
  
        #@ Start the MySQL service
        rlServiceStart mysqld

        # Some initial MySQL configuration
        rlRun $LOG "echo 'set global max_allowed_packet=1000000000000;' | mysql" 0 "Increase the value of max_allow_packet variable"
        rlRun $LOG "cat t/config/create_bugs_user.sql | mysql" 0 "Creating bugs user in database"

        # Setup Apache to find the Bugzilla installation
        rlRun $LOG "cp t/config/bugzilla.conf /etc/httpd/conf.d/" 0 "Setting up web server and starting httpd service"
        rlServiceStart httpd

        # @ Create the initial test data needed by the testsuite
        create_test_data

        # Startup a headless X server for later Selenium testing and start the Selenium RC remote proxy
        DISPLAY=:4
        rlRun "Xvnc $DISPLAY -alwaysshared -geometry 1600x1200 -depth 24 -SecurityTypes None 2>/dev/null >/dev/null &" 0 "Starting Selenium VNC desktop"
        #rlRun "x11vnc -display :4 -viewonly -forever -nopw -quiet 2> /dev/null &" 0 "Starting Selenium VNC desktop"
        rlRun "env DISPLAY=$DISPLAY java -jar t/config/selenium-server.jar -log selenium.log 2>/dev/null >/dev/null &" 0 "Starting Selenium RC server"

        # @ Fix the firefox path in the selenium config file
        FIREFOX_PATH=$( rpm -ql firefox | grep "/usr/lib\(64\)\?/firefox-[^/]\+/firefox" )
        rlAssertExists "$FIREFOX_PATH"
        rlRun "sed -i 's|FIREFOX_PATH|$FIREFOX_PATH|g' t/config/selenium_test.conf" 0 "Updating Selenium config file with Firefox path"
    rlPhaseEnd

    rlPhaseStartTest
        #@ Set the testoutputlog to the current beaker log dir
        TESTOUTPUTFILE="$BEAKERLIB_DIR/test_results.log"

        rlLog "Running common sanity tests"
        # @ Running basic Bugzilla sanity test scripts as shipped with Bugzilla
        for i in `ls t/0*.t`
        do
            run_test_case $i
        done

        rlLog "Running Selenium tests"
        #@ Running the automated web UI tests using Selenium
        for i in `ls t/test_*.t`
        do
            run_test_case $i
        done

        # We need to refresh the database now for the WebService testsuite
        rlRun $LOG "cd $BZ_HOME_DIR" 0 "Changing to Bugzilla directory"
        create_test_data

        rlLog "Running WebService tests"
        #@ Running the XMLRPC WebService test scripts
        for i in `ls t/webservice_*.t`
        do
            run_test_case $i
        done
        
        # Return final result
        echo "----- Test complete: result=$RESULT -----" | tee -a $OUTPUTFILE
        rlReport "Overall testing result" $RESULT 0 $OUTPUTFILE
        rlLog "Full test log: $TESTOUTPUTFILE" 
    rlPhaseEnd

    #@ Stoping httpd and mysqld services
    rlPhaseStartCleanup
        rlServiceStop httpd
        rlServiceStop mysqld
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
