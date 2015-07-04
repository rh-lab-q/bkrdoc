#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /distribution/install/autopart
#   Description: Anaconda auto-partitioning
#   Author: Jan Stodola <jstodola@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2011 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
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
