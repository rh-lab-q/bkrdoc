### EC1000: Pair commands -- begin without end
Each opening pair command needs a corresponding closing command, which is mostly needed for matching phase begins with ends.
- [E1001][error] rlPhaseStart >> rlPhaseEnd
- [E1001][error] rlPhaseStartCleanup >> rlPhaseEnd
- [E1001][error] rlPhaseStartSetup >> rlPhaseEnd
- [E1001][error] rlPhaseStartTest >> rlPhaseEnd
- [E1002][error] rlFileBackup >> rlFileRestore
- [E1003][warning] rlVirtualXStart >> rlVirtualXStop
- [E1004][error] rlServiceStart >> rlServiceRestore
- [E1005][error] rlServiceStop >> rlServiceRestore
- [E1006][error] rlSEBooleanOn >> rlSEBooleanRestore
- [E1007][error] rlSEBooleanOff >> rlSEBooleanRestore
- [E1008][error] rlSocketStart >> rlSocketRestore
- [E1009][error] rlSocketStop >> rlSocketRestore


### EC1100: Pair commands -- end before 'before'
A command can have a `before` specified - a list of commands which should not appear before its ending counterpart has been encountered.
- [E1101][warning] rlPhaseEnd, before: PhaseStartX
- [E1102][warning] rlServiceStop, before: rlServiceRestore


### EC1200: Pair commands -- end without begin
Similarly to begins without ends, an ending without a begin has been found. This is especially useful for commands differing by some label or flag where they have to match for each pair.
- [E1201][error] rlPhaseEnd, begins: rlPhaseStart, rlPhaseStartCleanup, rlPhaseStartSetup, rlPhaseStartTest
- [E1202][error] rlFileRestore, begins: rlFileBackup
- [E1203][error] rlVirtualXStop, begins: rlVirtualXStart
- [E1204][error] rlSEBooleanRestore, begins: rlSEBooleanOff, rlSEBooleanOn
- [E1205][error] rlSocketRestore, begins: rlSocketStart, rlSocketStop


### EC1500: Within phase functionality
Error class uniting problems that are related to phase composition of tests.
- [E1501][error] metric name has to be unique within a single phase
- [E1502][style] empty phase found
- [E1503][style] out of phase command


### EC2000: Deprecated commands
The following commands are deprecated and should no longer be used:
- [E2001][error] rlGetArch, use: rlGetPrimaryArch, rlGetSecondaryArch
- [E2002][error] rlLogLowMetric, use: rlLogMetricLow
- [E2003][error] rlLogHighMetric, use: rlLogMetricHigh
- [E2004][error] rlShowPkgVersion, use: rlShowPackageVersion
- [E2005][error] rlMountAny, use: rlMount
- [E2006][error] rlAnyMounted, use: rlCheckMount


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
- [E3013][info] rlWait signal not a common one
- [E3014][warning] rlReport result not in (PASS,WARN,FAIL)
- [E3015][error] rlIsRHEL/Fedora invalid format of type
- [E3016][error] rlHash/rlUnhash invalid hash algorithm
- [E3017][error] rlWaitForX time not a non-negative integer
- [E3018][error] rlWaitForX PID not a non-negative integer
- [E3019][error] rlWaitForCmd count not a non-negative integer
- [E3020][error] rlWaitForCmd return value not an int within range (0,255)
- [E3021][warning] rlImport library has to be in X/Y format
- [E3022][error] rlCmp/TestVersion version not composed of alphanum and '.-_'
- [E3023][error] rlTestVersion invalid operator


### EC4000: Command typos
Class checking for the most common typos that users tend to make, case-sensitivity related errors and not ending the command with 's' where one should (such as Equal vs. Equals).
- [E4001][error] command differs by upper/lowercase
- [E4002][error] Equals vs. Equal
- [E4003][info] rlUppercase command unrecognized


