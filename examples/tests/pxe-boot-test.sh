#!/bin/bash

# Copyright (c) 2006 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#
# Author: Alexander Todorov <atodorov@redhat.com>

# Include Beaker environment
. /usr/bin/rhts-environment.sh
. /usr/share/beakerlib/beakerlib.sh

rlJournalStart
    #@ Testing of syslog in OS made by RH
    rlPhaseStartTest PXE-Boot

    #@ @key RedHatEnterpriseLinux7, RedHatEnterpriseLinux*, Fedora*  
        case $FAMILY in
            RedHatEnterpriseLinux7)
                SYSLOG_FILE="/var/log/anaconda/syslog"
            ;;
            RedHatEnterpriseLinux*)
                SYSLOG_FILE="/var/log/anaconda.syslog"
            ;;
            Fedora*)
                SYSLOG_FILE="/var/log/anaconda/syslog"
            ;;
            *)
                rlDie "Unknown syslog file!"
            ;;
        esac

        cat $SYSLOG_FILE | grep netboot_method | grep pxe
        rlAssert0 "System booted via PXE" $?
    rlPhaseEnd
rlJournalEnd

rlJournalPrintText
