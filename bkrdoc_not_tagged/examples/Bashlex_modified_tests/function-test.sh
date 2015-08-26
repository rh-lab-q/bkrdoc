. /usr/share/beakerlib/beakerlib.sh
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
TEST="/examples/beakerlib/Sanity/apache"
PACKAGE="httpd"
HttpdPages="/var/www/html"
