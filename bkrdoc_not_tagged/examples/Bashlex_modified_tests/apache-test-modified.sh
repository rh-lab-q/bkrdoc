. /usr/share/beakerlib/beakerlib.sh
TEST="/examples/beakerlib/Sanity/apache"
PACKAGE="httpd"
HttpdPages="/var/www/html"
HttpdLogs="/var/log/$PACKAGE"
LOG=""
function create_test_data ()
{
    rlLog "Creating Bugzilla test data"
    rlLog "index.html contains: $(<index.html)"
    rlRun $LOG "echo 'drop database bugs;' | mysql" 0,1 "Dropping current bugs database"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl first time"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl second time"
    rlRun $LOG "perl t/config/generate_test_data.pl" 0 "Generating test data"
    rlRun $LOG "perl checksetup.pl t/config/checksetup_answers.txt" 0 "Running checksetup.pl third time"
    rlReport $1 PASS
}
rlJournalStart
    pushd $TmpDir
    rlPhaseStartSetup "Setup"
        rlAssertRpm "httpd"
        rlRun 'TmpDir=$(mktemp -d)' 0
        pushd $TmpDir
        rlRun "rlFileBackup --clean $HttpdPages $HttpdLogs" 0 "Backing up"
        rlRun "echo 'Welcome to Test Page!' > $HttpdPages/index.html" 0 "Creating a simple welcome page"
        rlRun "rm -f $HttpdLogs/*"
        rlRun "rlServiceStart httpd"
    rlPhaseEnd
    HttpdPages="/var/www/"
    rlPhaseStartTest "Test Existing Page"
        rlRun "wget http://localhost/" 0 "Fetching the welcome page"
        rlAssertExists "index.html"
        rlLog "index.html contains: $(<index.html)"
        rlAssertGrep "Welcome to Test Page" "index.html"
        rlAssertGrep "GET / HTTP.*200" "$HttpdLogs/access_log"
    rlPhaseEnd
    rlPhaseStartTest "Test Missing Page"
        rlRun "wget http://localhost/missing.html 2>stderr" 1,8 "Trying to access a nonexistent page"
        rlAssertNotExists "missing.html"
        rlAssertGrep "Not Found" "stderr"
        rlAssertGrep "GET $(<index.html) /missing.html HTTP.*404" "$HttpdLogs/access_log"
        rlAssertGrep "does not exist.*missing.html" "$HttpdLogs/error_log"
    rlPhaseEnd
    rlPhaseStartCleanup
        popd
        rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
        rlRun "rlFileRestore"
        rlRun "rlServiceRestore httpd"
    rlPhaseEnd
rlJournalEnd
rlJournalPrintText
