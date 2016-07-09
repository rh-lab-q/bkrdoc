#!/bin/bash

# Include beaker environment
. /usr/share/beakerlib/beakerlib.sh


#rlJournalStart

rlPhaseStartSetup

	rlRun "ls"
	rlRun -o sth 2-5
	rlFileBackup --clean --namespace di "dir" "dir2"
	rlFileBackup --namespace wut "dir" "dir2"

rlPhaseEnd
rlGetArch


rlPhaseStartTest
		
	rlRun "touch dir/a"
	rlRun "touch dir2/t"
	rlMount server 

rlPhaseEnd


rlPhaseStartCleanup

	rlFileRestore --namespace di
	rlRun "ls dir"
	rlRun "ls dir2"

rlPhaseEnd
rlPhaseEnd

