#!/bin/bash
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   #@ does nothing at all ?
#
# Description: this is a sample description
# that constitutes of so many lines
# we are still describing
# so MANY lines
# Keywords: yay keywords
# more keywords
# Author: author1 <rh>, authr37
# another sample author
# author4? <??@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2009 Red Hat, Inc. All rights reserved.
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

# Include the BeakerLib environment
. /usr/share/beakerlib/beakerlib.sh

# Set the full test name
#@@key sthsth

rlJournalStart

    rlPhaseStartSetup "Setup"
	# does nothing
    rlPhaseEnd

#@ @key i dont like keys
    #@ Cleanup after test

    rlPhaseStartCleanup "Cleanup"
	#@ we better clean up after doing nothing
     #@ @key dummykey
    rlPhaseEnd

rlJournalEnd





