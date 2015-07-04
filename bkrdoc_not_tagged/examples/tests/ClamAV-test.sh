#!/bin/bash

# Include the BeakerLib environment
. /usr/share/beakerlib/beakerlib.sh

# Packaget to be tested
PACKAGE="clamav"

# Set the full test name
TEST="QA:Testcase ClamAV"

rlJournalStart
    rlPhaseStartTest
        grep "^Example" /etc/freshclam.conf
        if [ $? -eq 0 ]; then
            rlRun "sed -i 's/Example/#Example/' /etc/freshclam.conf" 0 "Comment out Example line"
        fi
    rlPhaseEnd

    rlPhaseStartTest
        rlRun "freshclam" 0 "Run freshclam"
    rlPhaseEnd

    rlPhaseStartSetup
        rlRun "curl -O http://www.eicar.org/download/eicar.com" 0 "Getting test virus"
    rlPhaseEnd

    rlPhaseStartTest
        # if virus is found, it returns 1
        rlRun "clamscan eicar.com" 1 "Scanning test virus"
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "rm -f eicar.com" 0 "Remove test virus"
    rlPhaseEnd

rlJournalEnd

# Print the test report
rlJournalPrintText
