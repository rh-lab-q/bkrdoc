#!/usr/bin/python
__author__ = 'Jiri_Kulda'
from bkrdoc.analysis import *


class GetInformation(object):
    """
    This class is responsible for transformation from DocumentationInformation class
    to small InformationUnit class. This class contain big 2D array with reference to
    small InformationUnit classes.
    """
    array = [
        # topic: FILE(DIRECTORY),           STRING                   PACKAGE          JOURNAL,PHASE,TEST   MESSAGE         COMMAND                SERVER              BOOLEAN              SERVICE            MOUNTPOINT              SYSTEM                 VALUE  # ACTIONS
        [InformationFileExists,           0,               InformationPackageExists,              0,              0,              0,                     0,                  0,                  0,  InformationMountpointExists,           0,                     0],  # exists
        [InformationFileNotExists,        0,           InformationPackageNotExists,           0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not exists
        [InformationFileContain,          0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # contain
        [InformationFileNotContain,       0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not contain
        [InformationFilePrint,            0,           InformationPackagePrint,   InformationJournalPrint,    0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # print(show)
        [InformationFileResolve,          0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # resolve
        [InformationFileCreate, InformationStringCreate,          0,                          0, InformationMessageCreate,    0,                     0,                  0,                  0,  InformationMountpointCreate,           0,                     0],  # create
        [InformationFileCheck,            0,           InformationPackageCheck,               0,              0,              0,                     0,                  0,                  0,  InformationMountpointCheck,            0,         InformationValueCheck],  # check
        [           0,                    0,                      0,                InformationJournalReturn, 0,              0,         InformationServerReturn,        0,                  0,                   0,                    0,                     0],  # return
        [           0,                    0,                      0,                          0,              0,  InformationCommandRun, InformationServerRun,           0,       InformationServiceRun,          0,                    0,                     0],  # run
        [           0,                    0,                      0,                InformationJournalReport, 0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # report
        [           0,                    0,                      0,                          0,              0,              0,          InformationServerKill,         0,       InformationServiceKill,         0,                    0,                     0],  # kill
        [InformationFileWait,             0,                      0,                          0,              0,  InformationCommandWait,            0,                  0,                  0,                   0,                    0,                     0],  # wait
        [           0,                    0,           InformationPackageImport,              0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # import
        [           0,                    0,                      0,                          0,              0,  InformationCommandMeasures,        0,                  0,                  0,                   0,                    0,                     0],  # measures
        [           0,                    0,                      0,                          0,              0,              0,                     0,     InformationBooleanSet,           0,                   0,                    0,                     0],  # set
        [InformationFileRestore,          0,                      0,                          0,              0,              0,                     0,                  0,      InformationServiceRestore,       0,                    0,                     0],  # restore
        [InformationFileBackup,           0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # backup
        [           0,          InformationStringHash,            0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # hash
        [           0,          InformationStringUnHash,          0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # unhash
        [           0,                    0,           InformationPackageOwnedBy,             0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # owned by
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,    InformationSystemIsRHEL,               0],  # is RHEL
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,   InformationSystemIsFedora,              0],  # is Fedora
        [InformationFileDiffer,           0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # differ
        [InformationFileNotDiffer,        0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,                     0],  # not differ
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,         InformationValueEqual],  # equal
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,       InformationValueNotEqual],  # not equal
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,        InformationValueGreater],  # greater
        [           0,                    0,                      0,                          0,              0,              0,                     0,                  0,                  0,                   0,                    0,   InformationValueGreaterOrEqual],  # greater or equal
    ]

    def get_information_from_facts(self, information_obj):
        """
        Method responsible for the transformation
        :param information_obj: DocumentationInformation instanse to be transformed
        :return: InformationUnit class or empty string.
        """
        information = ""
        topic = information_obj.get_topic()
        for action in information_obj.get_action():
            column = self.get_topic_number(topic)
            row = self.get_action_number(action)
            information_class = self.array[row][column]
            if information_class:
                information = information_class(information_obj)
                information.set_information()
        return information

    def get_action_number(self, action):
        """
        method responsible for returning the right row number
        :param action: action word
        :return: row number
        """
        if self.is_action_exists(action):
            return 0
        elif self.is_action_not_exists(action):
            return 1
        elif self.is_action_contain(action):
            return 2
        elif self.is_action_not_contain(action):
            return 3
        elif self.is_action_print(action):
            return 4
        elif self.is_action_resolve(action):
            return 5
        elif self.is_action_create(action):
            return 6
        elif self.is_action_check(action):
            return 7
        elif self.is_action_return(action):
            return 8
        elif self.is_action_run(action):
            return 9
        elif self.is_action_report(action):
            return 10
        elif self.is_action_kill(action):
            return 11
        elif self.is_action_wait(action):
            return 12
        elif self.is_action_import(action):
            return 13
        elif self.is_action_measures(action):
            return 14
        elif self.is_action_set(action):
            return 15
        elif self.is_action_restore(action):
            return 16
        elif self.is_action_backup(action):
            return 17
        elif self.is_action_hash(action):
            return 18
        elif self.is_action_unhash(action):
            return 19
        elif self.is_action_owned_by(action):
            return 20
        elif self.is_action_is_rhel(action):
            return 21
        elif self.is_action_is_fedora(action):
            return 22
        elif self.is_action_differ(action):
            return 23
        elif self.is_action_not_differ(action):
            return 24
        elif self.is_action_equal(action):
            return 25
        elif self.is_action_not_equal(action):
            return 26
        elif self.is_action_greater(action):
            return 27
        elif self.is_action_greater_or_equal(action):
            return 28

    def get_topic_number(self, topic):
        """
        method responsible for returning the right topic column number
        :param topic: Topic word
        :return: column
        """
        if self.is_topic_file(topic):
            return 0
        elif self.is_topic_string(topic):
            return 1
        elif self.is_topic_package(topic):
            return 2
        elif self.is_topic_journal(topic):
            return 3
        elif self.is_topic_message(topic):
            return 4
        elif self.is_topic_command(topic):
            return 5
        elif self.is_topic_server(topic):
            return 6
        elif self.is_topic_boolean(topic):
            return 7
        elif self.is_topic_service(topic):
            return 8
        elif self.is_topic_mountpoint(topic):
            return 9
        elif self.is_topic_system(topic):
            return 10
        elif self.is_topic_value(topic):
            return 11

    def is_topic_file(self, topic):
        return topic == "FILE"

    def is_topic_string(self, topic):
        return topic == "STRING"

    def is_topic_package(self, topic):
        return topic == "PACKAGE"

    def is_topic_journal(self, topic):
        return topic == "JOURNAL"

    def is_topic_message(self, topic):
        return topic == "MESSAGE"

    def is_topic_command(self, topic):
        return topic == "COMMAND"

    def is_topic_server(self, topic):
        return topic == "SERVER"

    def is_topic_boolean(self, topic):
        return topic == "BOOLEAN"

    def is_topic_service(self, topic):
        return topic == "SERVICE"

    def is_topic_mountpoint(self, topic):
        return topic == "MOUNTPOINT"

    def is_topic_system(self, topic):
        return topic == "SYSTEM"

    def is_topic_value(self, topic):
        return topic == "VALUE"

    def is_action_exists(self, action):
        return action == "exists"

    def is_action_not_exists(self, action):
        return action == "not exists"

    def is_action_contain(self, action):
        return action == "contain"

    def is_action_not_contain(self, action):
        return action == "not contain"

    def is_action_print(self, action):
        return action == "print"

    def is_action_resolve(self, action):
        return action == "resolve"

    def is_action_create(self, action):
        return action == "create"

    def is_action_check(self, action):
        return action == "check"

    def is_action_return(self, action):
        return action == "return"

    def is_action_run(self, action):
        return action == "run"

    def is_action_report(self, action):
        return action == "report"

    def is_action_kill(self, action):
        return action == "kill"

    def is_action_wait(self, action):
        return action == "wait"

    def is_action_import(self, action):
        return action == "import"

    def is_action_measures(self, action):
        return action == "measures"

    def is_action_set(self, action):
        return action == "set"

    def is_action_restore(self, action):
        return action == "restore"

    def is_action_backup(self, action):
        return action == "backup"

    def is_action_hash(self, action):
        return action == "hash"

    def is_action_unhash(self, action):
        return action == "unhash"

    def is_action_owned_by(self, action):
        return action == "owned_by"

    def is_action_is_rhel(self, action):
        return action == "RHEL"

    def is_action_is_fedora(self, action):
        return action == "Fedora"

    def is_action_differ(self, action):
        return action == "differ"

    def is_action_not_differ(self, action):
        return action == "not differ"

    def is_action_equal(self, action):
        return action == "equal"

    def is_action_not_equal(self, action):
        return action == "not equal"

    def is_action_greater(self, action):
        return action == "greater"

    def is_action_greater_or_equal(self, action):
        return action == "greater or equal"