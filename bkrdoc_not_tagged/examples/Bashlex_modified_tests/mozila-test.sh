. /usr/share/beakerlib/beakerlib.sh
PACKAGE="bugzilla"
BZ_HOME_DIR="/var/www/html/bugzilla"
LOG=""
RESULT="PASS"
TESTOUTPUTFILE=""
YUM_PACKAGES="httpd mysql-server firefox.x86_64 tigervnc-server-minimal perl-Test-WWW-Selenium java-1.6.0-openjdk"
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
        rlRun $LOG "tar zxvf bugzilla.tar.gz" 0 "Unarchiving Bugzilla code"
        rlRun $LOG "yum -y install $YUM_PACKAGES" 0 "Installing required packages"
        for i in $YUM_PACKAGES
        do
            rlAssertRpm $i
        done
        rlRun "yum -y remove firefox.i386" 0,1 "Removing i386 Firefox if installed"
        rlRun $LOG "rm -rf /var/www/html/bugzilla" 0 "Deleting old Bugzilla installation and installing test"
        rlRun $LOG "mv bugzilla $BZ_HOME_DIR" 0 "Moving Bugzilla directory to webroot"
        rlRun $LOG "cd $BZ_HOME_DIR" 0 "Changing to Bugzilla directory"
        rlRun $LOG "mkdir -p data" 0 "Creating data directory"
        rlRun $LOG "cp t/config/params data/." 0 "Copying data/params file into right place"
        rlServiceStart mysqld
        rlRun $LOG "echo 'set global max_allowed_packet=1000000000000;' | mysql" 0 "Increase the value of max_allow_packet variable"
        rlRun $LOG "cat t/config/create_bugs_user.sql | mysql" 0 "Creating bugs user in database"
        rlRun $LOG "cp t/config/bugzilla.conf /etc/httpd/conf.d/" 0 "Setting up web server and starting httpd service"
        rlServiceStart httpd
        create_test_data
        DISPLAY=:4
        rlRun "Xvnc $DISPLAY -alwaysshared -geometry 1600x1200 -depth 24 -SecurityTypes None 2>/dev/null >/dev/null &" 0 "Starting Selenium VNC desktop"
        rlRun "env DISPLAY=$DISPLAY java -jar t/config/selenium-server.jar -log selenium.log 2>/dev/null >/dev/null &" 0 "Starting Selenium RC server"
        FIREFOX_PATH=$( rpm -ql firefox | grep "/usr/lib\(64\)\?/firefox-[^/]\+/firefox" )
        rlAssertExists "$FIREFOX_PATH"
        rlRun "sed -i 's|FIREFOX_PATH|$FIREFOX_PATH|g' t/config/selenium_test.conf" 0 "Updating Selenium config file with Firefox path"
    rlPhaseEnd
    rlPhaseStartTest
        TESTOUTPUTFILE="$BEAKERLIB_DIR/test_results.log"
        rlLog "Running common sanity tests"
        for i in `ls t/0*.t`
        do
            run_test_case $i
        done
        rlLog "Running Selenium tests"
        for i in `ls t/test_*.t`
        do
            run_test_case $i
        done
        rlRun $LOG "cd $BZ_HOME_DIR" 0 "Changing to Bugzilla directory"
        create_test_data
        rlLog "Running WebService tests"
        for i in `ls t/webservice_*.t`
        do
            run_test_case $i
        done
        echo "----- Test complete: result=$RESULT -----" | tee -a $OUTPUTFILE
        rlReport "Overall testing result" $RESULT 0 $OUTPUTFILE
        rlLog "Full test log: $TESTOUTPUTFILE"
    rlPhaseEnd
    rlPhaseStartCleanup
        rlServiceStop httpd
        rlServiceStop mysqld
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
