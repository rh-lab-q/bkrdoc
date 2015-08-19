. /usr/bin/rhts-environment.sh
. /usr/share/beakerlib/beakerlib.sh
KS_INSTALL="/root/ks.cfg"
rlJournalStart
    rlPhaseStartTest
        rlAssertExists $KS_INSTALL
    rlAssertGrep "^autopart" $KS_INSTALL
    rlAssertNotGrep "^part " $KS_INSTALL
    rlAssertNotGrep "^raid " $KS_INSTALL
    rlAssertNotGrep "^logvol " $KS_INSTALL
    rlAssertNotGrep "^volgroup " $KS_INSTALL
    rlFileSubmit -s "_" $KS_INSTALL
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
