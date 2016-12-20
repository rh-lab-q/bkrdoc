#!/usr/bin/python

import unittest

import sys

from bkrdoc.analysis.parser import bkrdoc_parser, documentation_translator
from bkrdoc.analysis.generator import documentation_generator, get_information, credibility

# redirecting stdout
try:
    from cStringIO import StringIO  #Python2
except ImportError:
    from io import StringIO  #Python3

sys.path.insert(0, '..')
sys.path.insert(0, './bkrdoc_not_tagged/')


class PomArgparse(object):
        FILE_NAME = ""
        additional_info = False

        def __init__(self, file_name="", additional_info=False):
            self.FILE_NAME = file_name
            self.additional_info = additional_info

        def print_all(self):
            return ""


class TestSequenceFunctions(unittest.TestCase):

    def test_basic(self):
        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        my = generator._parser_ref
        # generator.get_doc_data()
        pom_list = ['/examples/beakerlib/Sanity/apache', 'httpd', '/var/www/', '/var/log/httpd', '$(mktemp -d)']
        self.assertListEqual(my.variables.variable_values_list, pom_list, "EQUAL")
        
        self.assertEqual(len(my.phases), 11)
        self.assertEqual(my.phases[2].phase_name, "Setup: Setup")
        self.assertEqual(my.phases[4].phase_name, "Test: Test Existing Page")
        self.assertEqual(my.phases[6].phase_name, "Test: Test Missing Page")
        self.assertEqual(my.phases[8].phase_name, "Cleanup: Cleanup")
        
    def test_func(self):
        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/mozila-test.sh")
        # generator.get_doc_data()
        #print my.phases[0].func_list

    def test_environmental_variables(self):
        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/mozila-test.sh")

        my = generator._parser_ref
        # generator.get_doc_data()
        self.assertEqual(my.get_environmental_variables(), ['BEAKERLIB_DIR', 'OUTPUTFILE'])

        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        my = generator._parser_ref
        # generator.get_doc_data()
        self.assertEqual(my.environmental_variable, [])

    def test_assert_equal(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlAssertEquals \"Saves the configuration\" \"_enabled\" \"$CONF_VALUE\"")
        command_argparse = parser.argparse_data_list[0]

        self.assertEqual(command_argparse.argname, "rlAssertEquals")
        self.assertEqual(command_argparse.value1, "_enabled")
        self.assertEqual(command_argparse.comment, "Saves the configuration")
        self.assertEqual(command_argparse.value2, "$CONF_VALUE")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Value1 _enabled must be equal to value2 $CONF_VALUE"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)

    def test_automata(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlAssertRpm \"httpd\"")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlAssertRpm")
        self.assertEqual(command_argparse.name, "httpd")

    def test_rlRpm_commands(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlAssertRpm \"httpd\" 22 23  44")
        command_argparse = parser.argparse_data_list[0]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Package httpd must be installed with version: 22, release: 23 and architecture: 44"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)

    def test_unknown_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("poppd asdas")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "UNKNOWN")

    def test_first_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlRun \"rm -r $TmpDir\" 2,3,4,26 \"Removing tmp directory\"")
        command_argparse = parser.argparse_data_list[1]

        self.assertEqual(command_argparse.argname, "rlRun")
        self.assertEqual(command_argparse.command.data, ["rm", "-r", "$TmpDir"])
        self.assertEqual(command_argparse.comment, "Removing tmp directory")
        self.assertEqual(command_argparse.status, "2,3,4,26")

        sec = documentation_translator.DocumentationTranslator(documentation_generator.DocumentationGenerator())
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" exit code must match: 2,3,4,26"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    def test_assert_commands(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlAssertGrep \"Not Found\" \"stderr\"")
        command_argparse = parser.argparse_data_list[0]

        self.assertEqual(command_argparse.argname, "rlAssertGrep")
        self.assertEqual(command_argparse.pattern, "Not Found")
        self.assertEqual(command_argparse.file, "stderr")

    def test_hash_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlHash \"text\" --algorithm magic!")
        command_argparse = parser.argparse_data_list[0]

        self.assertEqual(command_argparse.argname, "rlHash")
        self.assertEqual(command_argparse.STRING, "text")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string text with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        parser.parse_data("rlHash --stdin --algorithm magic!")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlHash")
        self.assertEqual(command_argparse.stdin, True)

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string from input with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_backup_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlFileBackup --clean cleandir")
        command_argparse = parser.argparse_data_list[0]

        self.assertEqual(command_argparse.argname, "rlFileBackup")
        self.assertEqual(command_argparse.file[0], "cleandir")
        self.assertEqual(command_argparse.clean, True)

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File or directory cleandir is backed up"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_virtual_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlVirtualXStart $TEST")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname,"rlVirtualXStart")
        self.assertEqual(command_argparse.name, "$TEST")

        parser.parse_data("rlAssert0 \"Virtual X server started\" $?")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlAssert0")
        self.assertEqual(command_argparse.comment, "Virtual X server started")
        self.assertEqual(command_argparse.value, "$?")

    def test_ServiceXXX(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlServiceStart boolean boool asda ")
        command_argparse = parser.argparse_data_list[0]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Starts services boolean, boool and asda"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlServiceRestore boolean boool asda ")
        command_argparse = parser.argparse_data_list[1]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Services boolean, boool and asda are restored into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_SEBooleanXX(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlSEBooleanOn boolean boool asda ")
        command_argparse = parser.argparse_data_list[0]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Sets booleans boolean, boool and asda to true"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlSEBooleanRestore boolean boool asda ")
        command_argparse = parser.argparse_data_list[1]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Restore booleans boolean, boool and asda into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_rlRun_command(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlRun -l 'rm -r $TmpDir' ")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlRun")
        self.assertEqual(command_argparse.command.data, ["rm", "-r", "$TmpDir"])

        sec = documentation_translator.DocumentationTranslator(documentation_generator.DocumentationGenerator())
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" must run successfully and output is stored in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    def test_rlRun_rlFileBackup_extend(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlRun \"rlFileBackup --clean $HttpdPages $HttpdLogs\" \"1-2\" \"Backing up\"")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlRun")

        sec = documentation_translator.DocumentationTranslator(documentation_generator.DocumentationGenerator())
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Files or directories $HttpdPages and $HttpdLogs are backed up and must finished with return " \
              "code matching: 1-2"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_rlRun_rlServiceStart_extend(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlRun \"rlServiceStart httpd\" ")
        command_argparse = parser.argparse_data_list[1]

        self.assertEqual(command_argparse.argname, "rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Service: httpd must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_rlGet_commands(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlGetPrimaryArch")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlGetPrimaryArch")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns primary arch for the current system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlGetDistroRelease")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlGetDistroRelease")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns release of the distribution on the system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlShowRunningKernel")
        command_argparse = parser.argparse_data_list[2]
        self.assertEqual(command_argparse.argname, "rlShowRunningKernel")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Log a message with version of the currently running kernel"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

        parser.parse_data("rlGetTestState")
        command_argparse = parser.argparse_data_list[3]
        self.assertEqual(command_argparse.argname, "rlGetTestState")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns number of failed asserts"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlLog_commands(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlLog ahoj logfile priorita --prio-label")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlLog")
        self.assertEqual(command_argparse.logfile, "logfile")
        self.assertEqual(command_argparse.priority, "priorita")
        self.assertEqual(command_argparse.prio_label, True)

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"ahoj\" is created in to logfile logfile"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

        parser.parse_data("rlDie message ")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlDie")

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"message\" is created in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlBundleLogs(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlBundleLogs package file1 file2 file3 file4")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlBundleLogs")
        self.assertEqual(command_argparse.file, ["file1", "file2", "file3", "file4"])

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Creates a tarball of files file1, file2 and file3... and attached it/them to test result"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_filesubmit(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlFileSubmit path_to_file  required -s as")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlFileSubmit")
        self.assertEqual(command_argparse.s, "as")
        self.assertEqual(command_argparse.path_to_file, "path_to_file")
        self.assertEqual(command_argparse.required_name, 'required')

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Resolves absolute path path_to_file, replaces / for as and rename file to required"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_showpackageversion(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlShowPackageVersion as km")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlShowPackageVersion")
        self.assertEqual(command_argparse.package, ["as", "km"])

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Shows information about as and km version")
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_JournalPrint(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlJournalPrintText --full-journal")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlJournalPrintText")
        self.assertEqual(command_argparse.full_journal, True)

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf_line = "Prints the content of the journal in pretty text format with additional information"
        self.assertEqual(inf_data.information, inf_line)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlWaitxxx(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlWaitForFile path")
        command_argparse = parser.argparse_data_list[0]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script until file or directory with this path path starts listening"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

        parser.parse_data("rlWaitForCmd path -p TENTO -r 1")
        command_argparse = parser.argparse_data_list[1]

        sec = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script execution until command path exit status is unsuccessful\n and process with this " \
              "PID TENTO must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_backup_doc(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlFileBackup --clean cleandir")
        command_argparse = parser.argparse_data_list[0]
        doc = documentation_translator.DocumentationTranslator(command_argparse)

    def test_assert2_commands(self):
        parser = bkrdoc_parser.Parser("nothing")
        parser.parse_data("rlAssertGrep \"Not Found\" \"stderr\"")
        command_argparse = parser.argparse_data_list[0]
        self.assertEqual(command_argparse.argname, "rlAssertGrep")
        self.assertEqual(command_argparse.pattern, "Not Found")
        self.assertEqual(command_argparse.file, "stderr")
        pokus = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))

        inf_unit = pokus.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File: \"stderr\" must contain pattern: \"Not Found\""
        self.assertEqual(inf_data.information, inf)

        parser.parse_data("rlAssertExists gener.html")
        command_argparse = parser.argparse_data_list[1]
        self.assertEqual(command_argparse.argname, "rlAssertExists")
        self.assertEqual(command_argparse.file_directory, "gener.html")
        pokus = documentation_translator.DocumentationTranslator(bkrdoc_parser.Parser("./examples/tests/apache-test.sh"))
        inf_unit = pokus.translate_data(command_argparse)
        ref = get_information.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File(directory): \"gener.html\" must exist"
        self.assertEqual(inf_data.information, inf)

    def test_autopart_test(self):
        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/autopart-test.sh")
        generator.get_documentation_information()
        generator.generate_documentation()

    def test_credibility_percentage(self):
        cr = credibility.DocumentationCredibility(0, 0)
        perc = cr.compute_percent_correct(0, 0)
        self.assertEqual(cr.compute_credibility_key(perc), list(cr.credibilityTable)[-1])  # 0 total, should be MAX

        def compare(percent, expected_credibility):
            cr = credibility.DocumentationCredibility(percent, 100)
            self.assertEqual(cr.get_credibility(), cr.credibilityTable[expected_credibility])

        for (perc, cred) in [(100,0),(99,1),(81,1),(80,2),(61,2),(60,3),(41,3),(40,4),(21,4),(20,5),(1,5),(0,5)]:
            compare(perc, cred)

    def test_overall_credibility(self):
        generator = documentation_generator.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/autopart-test.sh")
        for phase in generator._phases:
            if phase.phase_name == "Test":
                credibility = generator.get_phase_credibility(phase).get_credibility()
        self.assertEqual(credibility, generator.get_overall_credibility())


    def test_credibility_computation_of_file(self):

        def test_file(file, below_medium_present):
            old_stdout = sys.stdout
            sys.stdout = my_stdout = StringIO()
            generator = documentation_generator.DocumentationGenerator()
            generator.parse_given_file(file)
            generator.print_documentation(PomArgparse())
            sys.stdout = old_stdout
            phrase = "Phases with below Medium credibility are present."
            assert_ = self.assertNotEqual if below_medium_present else self.assertEqual
            assert_(my_stdout.getvalue().find(phrase), -1)

        for (file, is_present) in [("tests/mozila-test", True),
                                    ("tests/pxe-boot-test", True),
                                    ("tests/none", True),
                                    ("tests/apache-test", False),
                                    ("markup/testFromBugzila", False)]:
            test_file("./examples/" + file + ".sh", is_present)


if __name__ == '__main__':
    unittest.main()
