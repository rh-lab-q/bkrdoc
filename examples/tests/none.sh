#!/bin/bash
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include the BeakerLib environment
. /usr/share/beakerlib/beakerlib.sh

# Set the full test name

rlJournalStart
   rlPhaseStartTest "Test"

     if ! rlCheckRpm package; then
          yum install package
          # rlAssertRpm package
     fi
    
   rlPhaseEnd


rlJournalEnd
