#!/usr/bin/python
__author__ = 'Jiri_Kulda'

import bkrdoc.analysis


class DocumentationTranslator:
    """Class making documentation information from argparse data.
    Generated information are focused on BeakerLib commands"""
    inf_ref = ""

    low = 1
    lowMedium = 2
    medium = 3
    high = 4
    highest = 5

    def __init__(self, generator_ref):
        self.generator_ref = generator_ref
        self.inf_ref = ""

    def translate_data(self, argparse_data):
        """
        This method translate argparse object into DocumentationInformation object
        :param argparse_data: argparse object
        :return: DocumentationInformation object
        """
        self.inf_ref = ""

        argname = argparse_data.argname
        condition = bkrdoc.analysis.ConditionsForCommands()

        if condition.is_rlrun_command(argname):
            self.set_rlrun_data(argparse_data)

        elif condition.is_rpm_command(argname):
            self.set_rpmcommand_data(argparse_data)

        elif condition.is_check_or_assert_mount(argname):
            self.set_check_or_assert_mount_data(argparse_data)

        elif condition.is_assert_command(argname):

            if condition.is_assert_grep(argname):
                self.set_assert_grep_data(argparse_data)

            elif condition.is_rlpass_or_rlfail_command(argname):
                self.set_rlpass_or_rlfail_data(argparse_data)

            elif condition.is_assert0(argname):
                self.set_rlassert0_data(argparse_data)

            elif condition.is_assert_comparasion(argname):
                self.set_assert_comparison_data(argparse_data)

            elif condition.is_assert_exists(argname):
                self.set_assert_exits_data(argparse_data)

            elif condition.is_assert_differ(argname):
                self.set_assert_differ_data(argparse_data)

            elif condition.is_assert_binary_origin(argname):
                self.set_assertbinaryorigin_data(argparse_data)

        elif condition.is_rlfilebackup_command(argname):
            self.set_rlfilebackup_data(argparse_data)

        elif condition.is_rlfilerestore_command(argname):
            self.set_rlfile_restore_data(argparse_data)

        elif condition.is_rlisrhel_or_rlisfedora_command(argname):
            self.set_isrhel_or_isfedora_data(argparse_data)

        elif condition.is_rlmount(argname):
            self.set_rlmount_data(argparse_data)

        elif condition.is_rlhash_or_rlunhash_command(argname):
            self.set_rlhash_or_rlunhash_data(argparse_data)

        elif condition.is_rllog_command(argname):
            self.set_rllog_data(argparse_data)

        elif condition.is_rldie_command(argname):
            self.set_rldie_data(argparse_data)

        elif condition.is_rlget_x_arch_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlgetdistro_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlgetphase_or_test_state_command(argname):
            self.set_rlget_commands_data(argparse_data)

        elif condition.is_rlreport_command(argname):
            self.set_rlreport_data(argparse_data)

        elif condition.is_rlwatchdog_command(argname):
            self.set_rlwatchdog_data(argparse_data)

        elif condition.is_rlbundlelogs_command(argname):
            self.set_rlbundlelogs_data(argparse_data)

        elif condition.is_rlservicexxx(argname):
            self.set_rlservicexxx_data(argparse_data)

        elif condition.is_sebooleanxxx_command(argname):
            self.set_sebooleanxxx_data(argparse_data)

        elif condition.is_rlshowrunningkernel_command(argname):
            self.set_rlshowrunningkernel_data()

        elif condition.is_get_or_check_makefile_requires(argname):
            self.set_rlget_or_rlcheck_makefilerequeries_data(argparse_data)

        elif condition.is_rlcleanup_apend_or_prepend_command(argname):
            self.set_rlcleanup_apend_or_prepend_data(argparse_data)

        elif condition.is_rlfilesubmit_command(argname):
            self.set_rlfilesubmit_data(argparse_data)

        elif condition.is_rlperftime_runsintime_command(argname):
            self.set_rlperftime_runsintime_data(argparse_data)

        elif condition.is_rlperftime_avgfromruns_command(argname):
            self.set_rlperftime_avgfromruns_data(argparse_data)

        elif condition.is_rlshowpackageversion_command(argname):
            self.set_rlshowpackageversion_data(argparse_data)

        elif condition.is_rljournalprint_command(argname):
            self.set_rljournalprint_data(argparse_data)

        elif condition.is_rlimport_command(argname):
            self.set_rlimport_data(argparse_data)

        elif condition.is_rlwaitfor_command(argname):
            self.set_rlwaitfor_data(argparse_data)

        elif condition.is_rlwaitforcmd_command(argname):
            self.set_rlwaitforcmd_data(argparse_data)

        elif condition.is_rlwaitforfile_command(argname):
            self.set_rlwaitforfile_data(argparse_data)

        elif condition.is_rlwaitforsocket_command(argname):
            self.set_rlwaitforsocket_data(argparse_data)

        elif condition.is_virtualxxx_command(argname):
            self.set_rlvirtualx_xxx_data(argparse_data)

        return self.inf_ref

    def set_rljournalprint_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = []
        param_option = []
        if argparse_data.argname == "rlJournalPrint":
            if len(argparse_data.type):
                subject.append(argparse_data.type)
            else:
                subject.append("xml")
        else:
            subject.append("text")
            if argparse_data.full_journal:
                param_option.append("additional information")

        topic_obj = bkrdoc.analysis.Topic("JOURNAL", subject)
        action = ["print"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlshowpackageversion_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        action = ["print"]
        subject = argparse_data.package
        topic_obj = bkrdoc.analysis.Topic("PACKAGE", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlfilesubmit_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.path_to_file]
        print(argparse_data.required_name)
        if not len(argparse_data.s) and not len(argparse_data.required_name):
            subject.append('-')

        elif len(argparse_data.s) and argparse_data.required_name is None:
            subject.append(argparse_data.s)

        elif len(argparse_data.s) and argparse_data.required_name is not None and len(argparse_data.required_name):
            subject.append(argparse_data.s)
            subject.append(argparse_data.required_name)
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = ["resolve"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlbundlelogs_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = argparse_data.file
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = ["create"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rldie_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = [argparse_data.message]
        subject += argparse_data.file
        topic_obj = bkrdoc.analysis.Topic("MESSAGE", subject)
        action = ["create"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rllog_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.low
        subject = [argparse_data.message]
        topic_obj = bkrdoc.analysis.Topic("MESSAGE", subject)
        action = ["create"]
        param_option = []
        if argparse_data.logfile:
            param_option.append(argparse_data.logfile)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlshowrunningkernel_data(self):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        """
        importance = self.lowMedium
        topic_obj = bkrdoc.analysis.Topic("MESSAGE", ["kernel"])
        action = ["create"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation("rlShowRunningKernel", topic_obj, action, importance)

    def set_rlget_or_rlcheck_makefilerequeries_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        topic_obj = bkrdoc.analysis.Topic("FILE", ["makefile"])
        action = []
        if argparse_data.argname == "rlGetMakefileRequires":
            action.append("print")
        else:
            action.append("check")
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlget_commands_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        action = []
        if bkrdoc.analysis.ConditionsForCommands().is_rlgetphase_or_test_state_command(argparse_data.argname):
            if argparse_data.argname == "rlGetTestState":
                subject.append("test")
            else:
                subject.append("phase")
        elif bkrdoc.analysis.ConditionsForCommands().is_rlgetdistro_command(argparse_data.argname):
            if argparse_data.argname == "rlGetDistroRelease":
                subject.append("release")
            else:
                subject.append("variant")
        elif argparse_data.argname == "rlGetPrimaryArch":
            subject.append("primary")
        else:
            subject.append("secondary")
        topic_obj = bkrdoc.analysis.Topic("JOURNAL", subject)
        action.append("return")
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwatchdog_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.highest
        subject = ["watchdog", argparse_data.command, argparse_data.timeout]
        param_option = []
        if argparse_data.signal:
            param_option.append(argparse_data.signal)
        topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
        action = ["run"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlreport_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.name, argparse_data.result]
        topic_obj = bkrdoc.analysis.Topic("JOURNAL", subject)
        action = ["report"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlrun_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.highest
        subject = [argparse_data.command, argparse_data.status]
        possible_beakerlib_command = self.get_argparse_of_command(argparse_data.command)

        if possible_beakerlib_command.argname == "UNKNOWN":
            param_option = []
            if argparse_data.l:
                param_option.append("l")
            elif argparse_data.c:
                param_option.append("c")
            elif argparse_data.t and argparse_data.s:
                param_option.append("s")
                param_option.append("t")
            elif argparse_data.t:
                param_option.append("t")
            elif argparse_data.s:
                param_option.append("s")
            topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
            action = ["run"]
            self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

        else:
            beakerlib_information_unit = self.translate_data(possible_beakerlib_command)
            beakerlib_information_unit.set_status(argparse_data.status)

    def get_argparse_of_command(self, command):
        """
        Gets argparse from command. This method is called in few methods. It depends
        on BeakerLib commands. If argparse of BeakerLib command contain command data,
        then this method will be used.
        :param command: command line
        :return: argparse object
        """
        pom_phase = bkrdoc.analysis.PhaseContainer("Helpful phase")
        return bkrdoc.analysis.StatementDataSearcher(self.generator_ref, pom_phase).parse_command(command)

    def set_rlvirtualx_xxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = [argparse_data.name]
        action = []
        if argparse_data.argname == "rlVirtualXStop":
            action.append("kill")
        elif argparse_data.argname == "rlVirtualXStart":
            action.append("run")
        else:
            action.append("return")
        topic_obj = bkrdoc.analysis.Topic("SERVER", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwaitfor_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = []
        if len(argparse_data.n):
            subject = argparse_data.n
        topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlwaitforsocket_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.port_path]
        param_option = []
        if argparse_data.close:
            param_option.append("close")
        elif argparse_data.p:
            param_option.append("p")

        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlwaitforfile_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = ["file", argparse_data.path]
        param_option = []
        if argparse_data.p:
            param_option.append(argparse_data.p)
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = ["wait"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlwaitforcmd_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = ["cmd", argparse_data.command]
        param_option = ["", ""]
        if argparse_data.r:
            param_option[0] = argparse_data.r

        if argparse_data.p:
            param_option[1] = argparse_data.p

        topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
        action = ["wait"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlimport_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = argparse_data.LIBRARY
        topic_obj = bkrdoc.analysis.Topic("PACKAGE", subject)
        action = ["import"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlperftime_runsintime_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.command]
        param_option = [argparse_data.time]
        topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlperftime_avgfromruns_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.command]
        topic_obj = bkrdoc.analysis.Topic("COMMAND", subject)
        action = ["measures"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlcleanup_apend_or_prepend_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlCleanupAppend":
            subject.append("append")
        subject.append(argparse_data.string)
        topic_obj = bkrdoc.analysis.Topic("STRING", subject)
        action = ["create"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_sebooleanxxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = []
        if argparse_data.argname == "rlSEBooleanOn":
            subject.append("on")
        elif argparse_data.argname == "rlSEBooleanOff":
            subject.append("off")
        subject += argparse_data.boolean
        topic_obj = bkrdoc.analysis.Topic("BOOLEAN", subject)
        action = ["set"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlservicexxx_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = argparse_data.service
        action = []
        if argparse_data.argname == "rlServiceStart":
            action.append("run")
        elif argparse_data.argname == "rlServiceStop":
            action.append("kill")
        else:
            action.append("restore")
        topic_obj = bkrdoc.analysis.Topic("SERVICE", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlfile_restore_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        param_option = []
        if argparse_data.namespace:
            param_option.append(argparse_data.namespace)
        topic_obj = bkrdoc.analysis.Topic("FILE", [""])
        action = ["restore"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlfilebackup_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        param_option = []
        subject = argparse_data.file
        if argparse_data.namespace:
            param_option.append(argparse_data.namespace)

        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = ["backup"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_rlhash_or_rlunhash_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        param_option = []
        subject = []
        if argparse_data.stdin:
            subject.append(argparse_data.stdin)
        else:
            subject.append(argparse_data.STRING)
        action = []
        if argparse_data.argname == "rlUnhash" or argparse_data.decode:
            action.append("unhash")
        else:
            action.append("hash")
        if argparse_data.algorithm:
            param_option.append(argparse_data.algorithm)
        topic_obj = bkrdoc.analysis.Topic("STRING", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_check_or_assert_mount_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.mountpoint]
        action = []
        if argparse_data.argname == "rlCheckMount":
            action.append("check")
        else:
            action.append("exists")
        if argparse_data.server and argparse_data.mountpoint:
            subject.append(argparse_data.server)
        topic_obj = bkrdoc.analysis.Topic("MOUNTPOINT", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlmount_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.lowMedium
        subject = [argparse_data.mountpoint, argparse_data.server]
        topic_obj = bkrdoc.analysis.Topic("MOUNTPOINT", subject)
        action = ["create"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assertbinaryorigin_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        subject = [argparse_data.binary]
        subject += argparse_data.package
        topic_obj = bkrdoc.analysis.Topic("PACKAGE", subject)
        action = ["owned by"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rpmcommand_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = []
        action = []
        subject.append(argparse_data.name)
        if argparse_data.argname == "rlCheckRpm":
            action.append("check")
        elif argparse_data.argname == "rlAssertRpm":
            action.append("exists")
            if argparse_data.all:
                subject.append("all")
        else:
            action.append("not exists")
        topic_obj = bkrdoc.analysis.Topic("PACKAGE", subject)
        param_option = []
        if argparse_data.version or argparse_data.release or \
                argparse_data.arch:
            if argparse_data.version:
                param_option.append(argparse_data.version)

            if argparse_data.release:
                param_option.append(argparse_data.release)

            if argparse_data.arch:
                param_option.append(argparse_data.arch)

        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))

    def set_isrhel_or_isfedora_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.medium
        action = []
        subject = []
        if argparse_data.argname == "rlIsRHEL":
            action.append("RHEL")
        else:
            action.append("Fedora")
        if len(argparse_data.type):
            subject = argparse_data.type
        topic_obj = bkrdoc.analysis.Topic("SYSTEM", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_differ_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        action = []
        if argparse_data.argname == "rlAssertDiffer":
            action.append("differ")
        else:
            action.append("not differ")
        subject = [argparse_data.file1, argparse_data.file2]
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_exits_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.file_directory]
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertExists":
            action.append("exists")
        else:
            action.append("not exists")
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_assert_comparison_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        action = []
        subject = [argparse_data.value1, argparse_data.value2]
        if argparse_data.argname == "rlAssertEquals":
            action.append("equal")
        elif argparse_data.argname == "rlAssertNotEquals":
            action.append("not equal")
        elif argparse_data.argname == "rlAssertGreater":
            action.append("greater")
        else:
            action.append("greater or equal")
        topic_obj = bkrdoc.analysis.Topic("VALUE", subject)
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlassert0_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        topic_obj = bkrdoc.analysis.Topic("VALUE", [argparse_data.value])
        action = ["check"]
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance)

    def set_rlpass_or_rlfail_data(self, argparse_data):
        pass

    def set_assert_grep_data(self, argparse_data):
        """
        Sets DocumentationInformation object to specified BeakerLib command
        :param argparse_data: argparse object
        """
        importance = self.high
        subject = [argparse_data.file, argparse_data.pattern]
        topic_obj = bkrdoc.analysis.Topic("FILE", subject)
        action = []
        if argparse_data.argname == "rlAssertGrep":
            action.append("contain")
        else:
            action.append("not contain")
        param_option = []
        if argparse_data.text_in:
            param_option.append("text_in")
        elif argparse_data.moin_in:
            param_option.append("moin_in")
        elif argparse_data.out_in:
            param_option.append("out_in")
        self.inf_ref = bkrdoc.analysis.DocumentationInformation(argparse_data.argname, topic_obj, action, importance, bkrdoc.analysis.Option(param_option))