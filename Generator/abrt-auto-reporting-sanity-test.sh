#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# runtest.sh of abrt-auto-reporting-sanity
# Description: does sanity on abrt-auto-reporting
# Author: Jakub Filak <jfilak@redhat.com>
# Keywords: auto-reporting
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Copyright (c) 2014 Red Hat, Inc. All rights reserved.
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

. /usr/share/beakerlib/beakerlib.sh
. ../aux/lib.sh

TEST="abrt-auto-reporting-sanity"
PACKAGE="abrt"

#@ Function that configure selected value
#@   does not require any parameter 
function get_configured_value
{
    VALUE=`grep "^AutoreportingEnabled" /etc/abrt/abrt.conf | tr -d " " | cut -f2 -d "="`
    echo $VALUE
    case "$VALUE" in
        [yY][eE][sS]|"_")
            export CONF_VALUE="enabled"
            ;;
        [nN][oO])
            export CONF_VALUE="disabled"
            ;;
        *)
            echo "Unknown option value"
            export CONF_VALUE="disabled"
            ;;
    esac
}

rlJournalStart

    #@ Make temporary directory and saves work in it
    rlPhaseStartSetup
        TmpDir=$(mktemp -d)
        pushd $TmpDir
    rlPhaseEnd

    # Additional info 

    # @ Print help informations
    # @keywords doc help
    # Using of block comment
    # This could be usefull 
    rlPhaseStartTest "--help"
        rlRun "abrt-auto-reporting --help" 0
        rlRun "abrt-auto-reporting --help 2>&1 | grep 'Usage: abrt-auto-reporting'"
    rlPhaseEnd
 
    #@ Runs script with no arguments
    rlPhaseStartTest "no args"
        rlRun "abrt-auto-reporting"

        get_configured_value
        rlAssertEquals "Reads the configuration" "_$(abrt-auto-reporting)" "_$CONF_VALUE"
    rlPhaseEnd

    #@ Single enablned as a argument
    rlPhaseStartTest "enabled"
        rlRun "abrt-auto-reporting enabled"

        get_configured_value
        rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd

    #@ Disabled as a argument
    rlPhaseStartTest "disabled"
        rlRun "abrt-auto-reporting disabled"

        get_configured_value
        rlAssertEquals "Saves the configuration" "_disabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_disabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd

    #@ More than just one enabled as a argument
    rlPhaseStartTest "enabled (once more)"
        rlRun "abrt-auto-reporting enabled"

        get_configured_value
        rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"
        rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"
    rlPhaseEnd

    #@ Various types of arguments will start this part
    rlPhaseStartTest "various argument types"
        OLD="enabled"
        #@ for every argument in selected word will do...
        for arg in disabled EnAbLeD dIsAblEd enabled no Yes nO yes 0 1
        do
            rlRun "abrt-auto-reporting $arg"  #@

            get_configured_value #@
            rlAssertNotEquals "Changed the configuration" "_$OLD" "_$CONF_VALUE"

            #@action Test if actualy value in arg is not "enabled" and "disabled"
            if [ $CONF_VALUE != "enabled" ] && [ $CONF_VALUE != "disabled" ]; then
                rlFail "Mangles the configuration value"
            fi

            OLD=$CONF_VALUE
        done
    rlPhaseEnd

    #@ clean after test
    rlPhaseStartCleanup
        #@ Disable auto reporting
        rlRun "abrt-auto-reporting disabled"
        popd # TmpDir
        rm -rf $TmpDir
    rlPhaseEnd
    
    rlJournalPrintText
rlJournalEnd
