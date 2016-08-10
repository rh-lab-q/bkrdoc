### EC1000: Pair commands -- begin without end
Each opening pair command needs a corresponding closing command, which is mostly needed for matching phase begins with ends.
- [E1001][error] rlPhaseStart >> rlPhaseEnd
- [E1001][error] rlPhaseStartCleanup >> rlPhaseEnd
- [E1001][error] rlPhaseStartSetup >> rlPhaseEnd
- [E1001][error] rlPhaseStartTest >> rlPhaseEnd
- [E1002][error] rlFileBackup >> rlFileRestore
- [E1003][warning] rlVirtualXStart >> rlVirtualXStop
- [E1004][warning] rlServiceStart >> rlServiceStop
- [E1005][error] rlSEBooleanOff >> rlSEBooleanRestore
- [E1005][error] rlSEBooleanOn >> rlSEBooleanRestore


### EC1100: Pair commands -- end before 'before'
A command can have a `before` specified - a list of commands which should not appear before its ending counterpart has been encountered.
- [E1101][warning] rlPhaseEnd, before: PhaseStartX
- [E1102][warning] rlServiceStop, before: rlServiceRestore


### EC1200: Pair commands -- end without begin
Similarly to begins without ends, an ending without a begin has been found. This is especially useful for commands differing by some label or flag where they have to match for each pair.
- [E1201][error] rlPhaseEnd, begins: rlPhaseStart, rlPhaseStartCleanup, rlPhaseStartSetup, rlPhaseStartTest
- [E1202][error] rlFileRestore, begins: rlFileBackup
- [E1203][error] rlVirtualXStop, begins: rlVirtualXStart
- [E1204][error] rlServiceStop, begins: rlServiceStart
- [E1205][error] rlSEBooleanRestore, begins: rlSEBooleanOff, rlSEBooleanOn


### EC1500: Within phase functionality
Error class uniting problems that are related to phase composition of tests.
- [E1501][error] metric name has to be unique within a single phase
- [E1502][warning] empty phase found


### EC2000: Deprecated commands
The following commands are deprecated and should no longer be used:
- [E2001][error] rlGetArch, use: rlGetPrimaryArch, rlGetSecondaryArch
- [E2002][error] rlLogHighMetric, use: rlLogMetricHigh
- [E2002][error] rlLogLowMetric, use: rlLogMetricLow
- [E2003][error] rlShowPkgVersion, use: rlShowPackageVersion


### EC2400: Standalone rules
- [E2401][error] beakerlib environment not set
- [E2402][warning] journal not started
- [E2403][warning] journal end followed by a command other than journal print


### EC3000: Argument errors
A number of commands require specific type of arguments. The simple ones (int/float..) are checked at command parsing, while the more complex ones are checked individually. This includes passing unknown options to commands or using one too many arguments.
- [E3001][error] invalid command argument
- [E3002][warning] too many arguments / unrecognized options
- [E3010][error] rlRun status not a float(int)
- [E3011][error] rlRun range status a-b : a>b
- [E3012][info] rlWatchdog signal not a common one
- [E3013][warning] rlReport result not in (PASS,WARN,FAIL)
- [E3014][error] rlIsRHEL/Fedora invalid format of type
- [E3015][info] rlIsRHEL/Fedora negative number


### EC4000: Command typos
Class checking for the most common typos that users tend to make, case-sensitivity related errors and not ending the command with 's' where one should (such as Equal vs. Equals).
- [E4001][error] command differs by upper/lowercase
- [E4002][error] Equals vs. Equal


