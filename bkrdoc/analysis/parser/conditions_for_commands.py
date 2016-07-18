#!/usr/bin/python
__author__ = 'Jiri_Kulda'


class ConditionsForCommands:
    """ Class consists of conditions for testing commands used in
    StatementDataSearcher and DocumentationTranslator """

    def is_rlwatchdog_command(self, command):
        return command == "rlWatchdog"

    def is_rlreport_command(self, command):
        return command == "rlReport"

    def is_virtualxxx_command(self, command):
        pom_list = ["rlVirtualXStop", "rlVirtualXStart", "rlVirtualXGetDisplay"]
        return command in pom_list

    def is_rlwaitfor_command(self, command):
        return command == "rlWait"

    def is_rlwaitforsocket_command(self, command):
        return command == "rlWaitForSocket"

    def is_rlwaitforfile_command(self, command):
        return command == "rlWaitForFile"

    def is_rlwaitforcmd_command(self, command):
        return command == "rlWaitForCmd"

    def is_rlwaitforxxx_command(self, command):
        pom_list = ["rlWaitForCmd", "rlWaitForFile", "rlWaitForSocket"]
        return command in pom_list

    def is_rlimport_command(self, command):
        return command == "rlImport"

    def is_rlperftime_runsintime_command(self, command):
        return command == "rlPerfTime_RunsInTime"

    def is_rlperftime_avgfromruns_command(self, command):
        return command == "rlPerfTime_AvgFromRuns"

    def is_rlcleanup_append_or_prepend_command(self, command):
        return command == "rlCleanupAppend" or command == "rlCleanupPrepend"

    def is_seboolean_on_off_command(self, command):
        pom_list = ["rlSEBooleanOn", "rlSEBooleanOff"]
        return command in pom_list

    def is_sebooleanrestore_command(self, command):
        return command == "rlSEBooleanRestore"

    def is_rlservicexxx(self, command):
        pom_list = ["rlServiceStart", "rlServiceStop", "rlServiceRestore"]
        return command in pom_list

    def is_rlfilebackup_command(self, command):
        return command == "rlFileBackup"

    def is_rlfilerestore_command(self, command):
        return command == "rlFileRestore"

    def is_rlhash_or_rlunhash_command(self, command):
        return command == "rlHash" or command == "rlUnhash"

    def is_check_or_assert_mount(self, command):
        return command == "rlCheckMount" or command == "rlAssertMount"

    def is_get_or_check_makefile_requires(self, command):
        return command == "rlCheckMakefileRequires" or command == "rlGetMakefileRequires"

    def is_checkrequirements(self, command):
        return command == "rlCheckRequirements"

    def is_rlmount(self, command):
        return command == "rlMount"

    def is_assert_binary_origin(self, command):
        return command == "rlAssertBinaryOrigin"

    def is_rlisrhel_or_rlisfedora_command(self, command):
        return command == "rlIsRHEL" or command == "rlIsFedora"

    def is_assert_differ(self, command):
        return command == "rlAssertDiffer" or command == "rlAssertNotDiffer"

    def is_assert_exists(self, command):
        return command == "rlAssertExists" or command == "rlAssertNotExists"

    def is_assert_comparasion(self, command):
        pom_list = ["rlAssertEquals", "rlAssertNotEquals", "rlAssertGreater",
                    "rlAssertGreaterOrEqual"]
        return command in pom_list

    def is_rlpass_or_rlfail_command(self, command):
        return command == "rlPass" or command == "rlFail"

    def is_assert_grep(self, command):
        return command == "rlAssertGrep" or command == "rlAssertNotGrep"

    def is_assert0(self, command):
        return command == "rlAssert0"

    def is_assert_command(self, command):
        pom_list = ["rlPass", "rlFail"]
        return command[0:len("rlAssert")] == "rlAssert" or command in pom_list

    def is_rpm_command(self, command):
        pom_list = ["rlCheckRpm", "rlAssertRpm", "rlAssertNotRpm"]
        return command in pom_list

    def is_rlrun_command(self, command):
        return command == "rlRun"

    def is_rljournalprint_command(self, command):
        pom_list = ["rlJournalPrint", "rlJournalPrintText"]
        return command in pom_list

    def is_rlgetphase_or_test_state_command(self, command):
        pom_list = ["rlGetPhaseState", "rlGetTestState"]
        return command in pom_list

    def is_rllog_command(self, command):
        pom_list = ["rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo",
                    "rlLogDebug", "rlLog"]
        return command in pom_list

    def is_rllogmetric_command(self, command):
        pom_list = ["rlLogMetricLow", "rlLogMetricHigh"]
        return command in pom_list

    def is_rldie_command(self, command):
        return command == "rlDie"

    def is_rlbundlelogs_command(self, command):
        return command == "rlBundleLogs"

    def is_rlfilesubmit_command(self, command):
        return command == "rlFileSubmit"

    def is_rlshowpackageversion_command(self, command):
        return command == "rlShowPackageVersion"

    def is_rlget_x_arch_command(self, command):
        pom_list = ["rlGetArch", "rlGetPrimaryArch", "rlGetSecondaryArch"]
        return command in pom_list

    def is_rlgetdistro_command(self, command):
        pom_list = ["rlGetDistroRelease", "rlGetDistroVariant"]
        return command in pom_list

    def is_rlshowrunningkernel_command(self, command):
        return command == "rlShowRunningKernel"

    def is_phase_start(self, command):
        return command == "rlPhaseStart"

    def is_phase_startxxx(self, command):
        return any([self.is_phase_clean(command),
                    self.is_phase_setup(command),
                    self.is_phase_test(command)])

    def is_phase_clean(self, command):
        return command == "rlPhaseStartCleanup"

    def is_phase_test(self, command):
        return command == "rlPhaseStartTest"

    def is_phase_setup(self, command):
        return command == "rlPhaseStartSetup"

    def is_phase_journal_end(self, command):
        return command in ["rlPhaseEnd", "rlJournalEnd"]

    def is_journal_start(self, command):
        return command == "rlJournalStart"

    def is_deprecated_command(self, command):
        deprecated = ['rlLogLowMetric', 'rlLogHighMetric', 'rlShowPkgVersion']
        return command in deprecated

