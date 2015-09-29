#!/usr/bin/python
__author__ = 'Jiri_Kulda'


class InformationUnit(object):
    """
    This is main class containing nature language information
    :param inf: DocumentationInformation object with data
    """
    information = ""
    information_obj = ""

    def __init__(self, inf):
        self.information = ""
        self.information_obj = inf

    def set_information(self):
        pass

    def get_command_name(self):
        return self.information_obj.get_command_name()

    def connect_multiple_facts(self, facts, max_size=5):
        """
        This method makes more human language sentences by
        correct representing of word enumeration
        :param facts: list of words to enumerate
        :param max_size: Maximum size of words to be shown.
                         Default is 5.
        :return: set upped string line with enumerated words
        """
        pom_inf = ""
        if len(facts) == 1:
            pom_inf = facts[0]
        elif len(facts) == 2:
            pom_inf = facts[0] + " and " + facts[1]
        else:
            i = 0
            while i < max_size:
                pom_inf += facts[i]
                if len(facts) > (i + 2) and (i + 2) < max_size:
                    pom_inf += ", "
                elif (i + 1) == len(facts):
                    return pom_inf
                elif (i + 1) == max_size:
                    pom_inf += "..."
                    return pom_inf
                else:
                    pom_inf += " and "
                i += 1
            pom_inf += "..."
        return pom_inf

    def print_information(self):
        print("   " + self.information)

    def get_information_weigh(self):
        """
        This method calculates information weight.
        The weight is amount of lines on which information
        will be displayed

        :return: information weight
        """
        line_size = 60  # char per line
        weigh = (len(self.information)//line_size)
        mod_weigh = (len(self.information) % line_size)
        if weigh == 0:
            return 1
        elif mod_weigh >= 20:  # tolerance
            return weigh + 1
        else:
            return weigh

    def get_information_value(self):
        """
        :return: Return information importance
        """
        return self.information_obj.get_importance()

    def is_list_empty(self, tested_list):
        return len(tested_list) == 0

    def check_status_and_add_information(self, status):
        """
        This method replaces status number for better information string.
        :param status: command status
        """
        if not status == "-":
            if status == "1":
                self.information += " and must finished unsuccessfully"
            elif not status == "0":
                self.information += " and must finished with return code matching: " + status

    def set_correct_singulars_or_plurals(self, word, number_of_subject, ending="s", verb=False):
        """
        This method correctly represent singulars or plurals in word.
        :param word: word to set up
        :param number_of_subject: count of subjects in sentence
        :param ending: word ending in plural. default is "s"
        :param verb: possible verb after word
        :return: Correctly set upped word
        """
        pom_word = word
        if number_of_subject >= 2:
            if pom_word[-1] == "y" and ending == "ies":
                pom_word = word[:-1] + ending
            else:
                pom_word += ending

            if verb:
                pom_word += " are"
        elif verb:
            pom_word += " is"

        if not verb:
            pom_word += " "
        return pom_word


class InformationFileExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must exist"
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileNotExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\""
        self.information += " must not exist"
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must not exist"
        elif status == "1":
            self.information = "File(directory): \"" + self.information_obj.get_topic_subject()[0] + "\" must exist"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileContain(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                           + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationFileNotContain(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                           + "\" must not contain pattern \"" + self.information_obj.get_topic_subject()[1]
        self.information += "\""
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """
        Overloaded method to correctly represent status in this case
        :param status: status number
        :return: correctly represented status number.
        """
        if status == "0":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must not contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif status == "1":
            self.information = "File: \"" + self.information_obj.get_topic_subject()[0] \
                               + "\" must contain pattern: \"" + self.information_obj.get_topic_subject()[1] + "\""
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationJournalPrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Prints the content of the journal in pretty " + self.information_obj.get_topic_subject()[0]
        self.information += " format"
        if len(self.information_obj.get_option()):
            self.information += " with additional information"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackagePrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Shows information about "
        self.information += self.connect_multiple_facts(self.information_obj.get_topic_subject(), 4)
        self.information += " version"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileResolve(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Resolves absolute path " + subjects[0]
        if len(subjects) == 3:
            self.information += ", replaces / for " + subjects[1]
            self.information += " and rename file to " + subjects[2]
        else:
            self.information += " and replaces / for " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Creates a tarball of " + self.set_correct_singulars_or_plurals("file", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.information += " and attached it/them to test result"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMessageCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if subjects[0] == "kernel":  # rlShowRunningKernel
            self.information = "Log a message with version of the currently running kernel"
        else:  # rlDie & rlLog
            self.information = "Message \"" + subjects[0]
            if len(subjects) > 1:
                self.information += "\" is created in to log and "
                self.information += self.set_correct_singulars_or_plurals("file", len(subjects[1:]))
                self.information += self.connect_multiple_facts(subjects[1:], 3)
                if len(subjects[1:]) > 1:
                    self.information += "\" are uploaded"
                else:
                    self.information += "\" is uploaded"
            else:
                if not self.is_list_empty(option):
                    self.information += "\" is created in to logfile "
                    self.information += option[0]
                else:
                    self.information += "\" is created in to log"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFilePrint(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Prints comma separated list of requirements defined in Makefile"
        else:
            self.information = "Prints file content"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "makefile":
            self.information = "Checks requirements in Makefile and returns number of compliance"
        else:
            self.information = "Checks file " + self.information_obj.get_topic_subject()[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationJournalReturn(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "phase":
            self.information = "Returns number of failed asserts in current phase"
        elif subjects[0] == "test":
            self.information = "Returns number of failed asserts"
        elif subjects[0] == "variant":
            self.information = "Returns variant of the distribution on the system"
        elif subjects[0] == "release":
            self.information = "Returns release of the distribution on the system"
        elif subjects[0] == "primary":
            self.information = "Returns primary arch for the current system"
        elif subjects[0] == "secondary":
            self.information = "Returns base arch for the current system"
        else:
            self.information = "Returns data from Journal"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "watchdog":
            self.information = "Runs command " + subjects[1]
            self.information += " for " + subjects[2]
            self.information += " seconds"
            if not self.is_list_empty(self.information_obj.get_option()):
                self.information += " and killed with signal "
                self.information += self.information_obj.get_option()[0]

        else:  # rlRun
            self.information = "Command \"" + subjects[0]
            if subjects[1] == "0":
                self.information += "\" must run successfully"
            elif subjects[1] == "1":
                self.information += "\" must run unsuccessfully"
            else:
                self.information += "\" exit code must match: " + subjects[1]

            option = self.information_obj.get_option()
            if not self.is_list_empty(option):
                if option[0] == "l":
                    self.information += " and output is stored in to log"
                elif option[0] == "c":
                    self.information += " and failed output is stored in to log"
                elif len(option) > 1:
                    self.information += " and stdout and stderr are tagged and stored"
                elif option[0] == "t":
                    self.information += " and stdout and stderr are tagged"
                elif option[0] == "s":
                    self.information += " and stdout and stderr are stored"


class InformationServerRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Starts virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " server on a first free display"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServerKill(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Kills virtual X " + self.information_obj.get_topic_subject()[0] + " server"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServerReturn(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Shows number of displays where virtual X " + self.information_obj.get_topic_subject()[0] + \
                           " is running"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationJournalReport(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Reports test \"" + subjects[0]
        self.information += "\" with result " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandWait(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "cmd":
            # rlWaitForCmd
            option = self.information_obj.get_option()
            self.information = "Pauses script execution until command " + subjects[1]
            if option[0] == "0":
                self.information += " exit status is successful"
            elif option[0] == "1":
                self.information += " exit status is unsuccessful"
            else:
                self.information += " exit status match " + option[0]

            if option[1]:
                self.information += "\n and process with this PID " + option[1]
                self.information += " must be running"
        else:  # rlWait
            if subjects:
                self.information = "Wait for " + self.connect_multiple_facts(subjects, 3)
            else:
                self.information = "All currently active child processes are"
                self.information += " waited for, and the return status is zero"
            self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileWait(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        if self.information_obj.get_topic_subject()[0] == "file":  # rlWaitForFile
            if not self.is_list_empty(option):
                self.information = "Pauses script until file or directory with this path "
                self.information += self.information_obj.get_topic_subject()[1] + " starts existing"
                self.information += "\n and process with this PID " + option[0]
                self.information += " must be running"
            else:
                self.information = "Pauses script until file or directory with this path "
                self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
        else:  # rlWaitForScript
            if not self.is_list_empty(option):
                if option[0] == "close":
                    self.information = "Waits for the socket with this path"
                    self.information += self.information_obj.get_topic_subject()[1] + "to stop listening"
                elif option[0] == "p":
                    self.information = "Pauses script until socket with this path or port "
                    self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
                    self.information += "\n and process with this PID " + option[0]
                    self.information += " must be running"
            else:
                self.information = "Pauses script until socket with this path or port "
                self.information += self.information_obj.get_topic_subject()[1] + " starts listening"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageImport(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Imports code provided by "
        self.information += self.connect_multiple_facts(subject, 2)
        self.information += self.set_correct_singulars_or_plurals(" library", len(subject), "ies")
        self.information += "  library(ies) into the test namespace"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationCommandMeasures(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if not self.is_list_empty(option):
            self.information = "Measures, how many runs of command "
            self.information += subjects[0] + " in "
            self.information += option[0] + " second(s)"
        else:
            self.information = "Measures the average time of running command "
            self.information += subjects[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationStringCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        if self.information_obj.get_topic_subject()[0] == "append":
            self.information = "Appends string: " + self.information_obj.get_topic_subject()[1]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        else:
            self.information = "Prepends string: " + self.information_obj.get_topic_subject()[0]
            self.information += " to the cleanup buffer"
            self.information += " and recreates the cleanup script"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationBooleanSet(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        if subjects[0] == "on":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to true"
        elif subjects[0] == "off":
            self.information = "Sets "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects[1:]))
            self.information += self.connect_multiple_facts(subjects[1:], 3)
            self.information += " to false"
        else:
            self.information = "Restore "
            self.information += self.set_correct_singulars_or_plurals("boolean", len(subjects))
            self.information += self.connect_multiple_facts(subjects, 3)
            self.information += " into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationServiceRun(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Starts "
        self.information += self.set_correct_singulars_or_plurals("service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""

        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(subject, 3) + \
                               " must be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(subject, 3) + \
                               " must not be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationServiceKill(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = "Kills "
        self.information += self.set_correct_singulars_or_plurals("service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        self.check_status_and_add_information(self.information_obj.get_status())

    def check_status_and_add_information(self, status):
        """self.information[-1] is here because method set_correct_singulars... adds one space on the end of the word"""
        subject = self.information_obj.get_topic_subject()
        if status == "0":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                               " must not be running"
        elif status == "1":
            self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
            self.information = self.information[:-1] + ": " + self.connect_multiple_facts(self.information_obj.get_topic_subject(), 3) + \
                               " must be running"
        elif not status == "-":
            self.information += " and exit code must match " + status


class InformationServiceRestore(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("Service", len(subject))
        self.information += self.connect_multiple_facts(subject, 3)
        if len(subject) > 1:
            self.information += " are restored into original state"
        else:
            self.information += " is restored into original state"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileRestore(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        if not self.is_list_empty(option):
            self.information = "Restores backed up file with namespace: "
            self.information += option[0]
            self.information += "to original state"
        else:
            self.information = "Restores backed up files to their "
            self.information += "original location"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileBackup(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        status = self.information_obj.get_status()
        subject = self.information_obj.get_topic_subject()
        self.information = self.set_correct_singulars_or_plurals("File", len(subject))
        self.information += "or " + self.set_correct_singulars_or_plurals("directory", len(subject), "ies")
        self.information += self.connect_multiple_facts(subject, 2)
        if len(subject) >= 2:
            self.information += " are backed up"
        else:
            self.information += " is backed up"
        if not self.is_list_empty(option):
            self.information += "with namespace " + option[0]
        self.check_status_and_add_information(status)


class InformationStringHash(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        self.information = "Hashes string "
        if subjects[0] == True:
            self.information += "from input"
        else:
            self.information += subjects[0]
        if not self.is_list_empty(option):
            self.information += " with hashing algorithm "
            self.information += option[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationStringUnHash(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        subjects = self.information_obj.get_topic_subject()
        self.information = "Unhashes string "
        if subjects[0] ==  True:
            self.information += "from input"
        else:
            self.information += subjects[0]

        if not self.is_list_empty(option):
            self.information += " with hashing algorithm "
            self.information += option[0]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Directory "
        self.information += subjects[0]
        self.information += "must be a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointCreate(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Creates mount point " + subjects[0]
        if subjects[1]:
            self.information += " and mount NFS " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationMountpointCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Checks if directory "
        self.information += subjects[0]
        self.information += "is a mountpoint"

        if subjects[1]:
            self.information += " to server " + subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageOwnedBy(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Binary " + subjects[0] + "must be"
        self.information += " owned by "
        self.information += self.set_correct_singulars_or_plurals("package", len(subjects[1:]))
        self.information += self.connect_multiple_facts(subjects[1:], 4)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationSystemIsRHEL(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " RHEL "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationSystemIsFedora(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information += "Checks if we are running on"
        self.information += " Fedora "
        if subjects:
            self.information += self.connect_multiple_facts(subjects)
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileDiffer(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be different"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationFileNotDiffer(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "File1 " + subjects[0] + " and file2 "
        self.information += subjects[1]
        self.information += " must be identical"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueNotEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must not be equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueGreater(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater than value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueGreaterOrEqual(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        self.information = "Value1 " + subjects[0]
        self.information += " must be greater or equal to value2 "
        self.information += subjects[1]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationValueCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        self.information = "Value " + self.information_obj.get_topic_subject()[0] + " must be 0"
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageCheck(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        self.information = "Package " + self.information_obj.get_topic_subject()[0]
        self.information += " must be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        subjects = self.information_obj.get_topic_subject()
        option = self.information_obj.get_option()
        if subjects[0] == "all":
            self.information = "Packages in $PACKAGES, $REQUIRES"
            self.information += " and $COLLECTIONS must be installed"
        else:
            self.information = "Package " + subjects[0]
            self.information += " must be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())


class InformationPackageNotExists(InformationUnit):
    """
    Small InformationUnit class which contains information in human language.
    """
    def set_information(self):
        """
        Sets nature language information. This setting depends on small
        InformationUnit class.
        """
        option = self.information_obj.get_option()
        self.information = "Package " + self.information_obj.get_topic_subject()[0]
        self.information += " must not be installed"

        if not self.is_list_empty(option):
            self.information += " with"
            if len(option) == 1:
                self.information += " version: " + option[0]

            elif len(option) == 2:
                self.information += " version: " + option[0]
                self.information += " and release: " + option[1]

            else:
                self.information += " version: " + option[0]
                self.information += ", release: " + option[1]
                self.information += " and architecture: " + option[2]
        self.check_status_and_add_information(self.information_obj.get_status())
