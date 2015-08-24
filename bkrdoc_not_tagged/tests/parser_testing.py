#!/usr/bin/python

import unittest
import sys

sys.path.insert(0, '..')
sys.path.insert(0, './bkrdoc_not_tagged/')
import bkrdoc


class TestSequenceFunctions(unittest.TestCase):

    def test_basic(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        my = generator._parser_ref
        # generator.get_doc_data()

        pom_list = ['/examples/beakerlib/Sanity/apache', 'httpd', '/var/www/', '/var/log/$PACKAGE', '$(mktemp -d)']
        # print(my.variables.variable_values_list)
        self.assertListEqual(my.variables.variable_values_list, pom_list, "EQUAL")
        self.assertEqual(len(my.phases), 11)
        self.assertEqual(my.phases[2].phase_name, "Setup: Setup")
        self.assertEqual(my.phases[4].phase_name, "Test: Test Existing Page")
        self.assertEqual(my.phases[6].phase_name, "Test: Test Missing Page")
        self.assertEqual(my.phases[8].phase_name, "Cleanup")
        argparse_list = my.phases[2].statement_list
        self.assertEqual(argparse_list[0].argname, "rlAssertRpm")
        self.assertEqual(argparse_list[1].argname, "rlRun")
        self.assertEqual(argparse_list[2].argname, "UNKNOWN")
        self.assertEqual(argparse_list[3].argname, "rlRun")
        self.assertEqual(argparse_list[4].argname, "rlRun")
        self.assertEqual(argparse_list[5].argname, "rlRun")
        self.assertEqual(argparse_list[6].argname, "rlRun")

    @unittest.skip("Problem with functions in mozilla test")
    def test_func(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/mozila-test.sh")
        generator.get_doc_data()
        # print my.phases[0].func_list

    @unittest.skip("Problem with functions in mozilla test")
    def test_environmental_variables(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/mozila-test.sh")
        my = generator._parser_ref
        generator.get_doc_data()
        self.assertEqual(my.environmental_variable, ['BEAKERLIB_DIR', 'OUTPUTFILE'])

        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        my = generator._parser_ref
        generator.get_doc_data()
        self.assertEqual(my.environmental_variable, [])

    def test_assert_equal(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        parser = bkrdoc.Parser("")
        parser.parse_data("rlAssertEquals \"Saves the configuration\" \"_enabled\" \"$CONF_VALUE\"")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlAssertEquals")
        self.assertEqual(parser.argparse_data_list[0].value1, "_enabled")
        self.assertEqual(parser.argparse_data_list[0].comment, "Saves the configuration")
        self.assertEqual(parser.argparse_data_list[0].value2, "$CONF_VALUE")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Value1 _enabled must be equal to value2 $CONF_VALUE"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)


    def test_automata(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlAssertRpm \"httpd\"")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlAssertRpm")
        self.assertEqual(parser.argparse_data_list[0].name, "httpd")

    def test_rlRpm_commands(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlAssertRpm \"httpd\" 22 23  44")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Package httpd must be installed with version: 22, release: 23 and architecture: 44"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)

    def test_unknown_command(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("poppd asdas")
        self.assertEqual(parser.argparse_data_list[0].argname, "UNKNOWN")

    def test_first_command(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        parser = bkrdoc.Parser("")
        parser.parse_data("rlRun \"rm -r $TmpDir\" 2,3,4,26 \"Removing tmp directory\"")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlRun")
        self.assertEqual(parser.argparse_data_list[0].command.data, ['rm', '-r', '$TmpDir'])
        self.assertEqual(parser.argparse_data_list[0].comment, "Removing tmp directory")
        self.assertEqual(parser.argparse_data_list[0].status, "2,3,4,26")

        sec = bkrdoc.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" exit code must match: 2,3,4,26"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    def test_assert_commands(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(parser.argparse_data_list[0].argname,"rlAssertGrep")
        self.assertEqual(parser.argparse_data_list[0].pattern,"Not Found")
        self.assertEqual(parser.argparse_data_list[0].file, "stderr")

    def test_hash_command(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlHash \"text\" --algorithm magic!")
        self.assertEqual(parser.argparse_data_list[0].argname,"rlHash")
        self.assertEqual(parser.argparse_data_list[0].STRING,"text")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string text with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        parser.parse_data("rlHash --stdin --algorithm magic!")
        self.assertEqual(parser.argparse_data_list[1].argname,"rlHash")
        self.assertEqual(parser.argparse_data_list[1].stdin,True)

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string from input with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_backup_command(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlFileBackup --clean cleandir")
        self.assertEqual(parser.argparse_data_list[0].argname,"rlFileBackup")
        self.assertEqual(parser.argparse_data_list[0].file[0],"cleandir")
        self.assertEqual(parser.argparse_data_list[0].clean,True)

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File or directory cleandir is backed up"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_virtual_command(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlVirtualXStart $TEST")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlVirtualXStart")
        self.assertEqual(parser.argparse_data_list[0].name, "$TEST")

        parser.parse_data("rlAssert0 \"Virtual X server started\" $?")
        self.assertEqual(parser.argparse_data_list[1].argname, "rlAssert0")
        self.assertEqual(parser.argparse_data_list[1].comment, "Virtual X server started")
        self.assertEqual(parser.argparse_data_list[1].value, "$?")

    def test_ServiceXXX(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlServiceStart boolean boool asda ")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Starts services boolean, boool and asda"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlServiceRestore boolean boool asda ")
        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Services boolean, boool and asda are restored into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_SEBooleanXX(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlSEBooleanOn boolean boool asda ")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Sets booleans boolean, boool and asda to true"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,3)

        parser.parse_data("rlSEBooleanRestore boolean boool asda ")
        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Restore booleans boolean, boool and asda into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlRun_command(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        parser = bkrdoc.Parser("")
        parser.parse_data("rlRun -l 'rm -r $TmpDir' ")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlRun")
        self.assertEqual(parser.argparse_data_list[0].command.data, ['rm', '-r', '$TmpDir'])

        sec = bkrdoc.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" must run successfully and output is stored in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    # @unittest.skip("Missing implementation of searching in rlRun commands for possible BeakerLib commands")
    def test_rlRun_rlFileBackup_extend(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        parser = bkrdoc.Parser("")
        parser.parse_data("rlRun \"rlFileBackup --clean $HttpdPages $HttpdLogs\" \"1-2\" \"Backing up\"")
        self.assertEqual(parser.argparse_data_list[0].argname,"rlRun")

        sec = bkrdoc.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Files or directories $HttpdPages and $HttpdLogs are backed up and must finished with return code matching: 1-2"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    # @unittest.skip("Missing implementation of searching in rlRun commands for possible BeakerLib commands")
    def test_rlRun_rlServiceStart_extend(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlRun \"rlServiceStart httpd\" ")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Service: httpd must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_rlGet_commands(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlGetPrimaryArch")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlGetPrimaryArch")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns primary arch for the current system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlGetDistroRelease")
        self.assertEqual(parser.argparse_data_list[1].argname,"rlGetDistroRelease")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns release of the distribution on the system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        parser.parse_data("rlShowRunningKernel")
        self.assertEqual(parser.argparse_data_list[2].argname, "rlShowRunningKernel")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[2])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Log a message with version of the currently running kernel"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

        parser.parse_data("rlGetTestState")
        self.assertEqual(parser.argparse_data_list[3].argname, "rlGetTestState")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[3])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns number of failed asserts"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlLog_commands(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlLogWarning ahoj logfile priorita --prio-label")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlLogWarning")
        self.assertEqual(parser.argparse_data_list[0].logfile, "logfile")
        self.assertEqual(parser.argparse_data_list[0].priority, "priorita")
        self.assertEqual(parser.argparse_data_list[0].prio_label, True)

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"ahoj\" is created in to logfile logfile"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

        parser.parse_data("rlDie message ")
        self.assertEqual(parser.argparse_data_list[1].argname, "rlDie")
        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"message\" is created in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlBundleLogs(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlBundleLogs package file1 file2 file3 file4")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlBundleLogs")
        self.assertEqual(parser.argparse_data_list[0].file, ["file1", "file2", "file3", "file4"])

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Creates a tarball of files file1, file2 and file3... and attached it/them to test result"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_filesubmit(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlFileSubmit path_to_file  required -s as")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlFileSubmit")
        self.assertEqual(parser.argparse_data_list[0].s, "as")
        self.assertEqual(parser.argparse_data_list[0].path_to_file, "path_to_file")
        self.assertEqual(parser.argparse_data_list[0].required_name, 'required')

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Resolves absolute path path_to_file, replaces / for as and rename file to required"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_showpackageversion(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlShowPackageVersion as km")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlShowPackageVersion")
        self.assertEqual(parser.argparse_data_list[0].package, ["as", "km"])

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Shows information about as and km version")
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_JournalPrint(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlJournalPrintText --full-journal")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlJournalPrintText")
        self.assertEqual(parser.argparse_data_list[0].full_journal, True)

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Prints the content of the journal in pretty text format with additional information")
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlWaitxxx(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlWaitForFile path")

        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script until file or directory with this path path starts listening"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

        parser.parse_data("rlWaitForCmd path -p TENTO -r 1")
        sec = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf_unit = sec.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script execution until command path exit status is unsuccessful\n and process with this PID TENTO must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_backup_doc(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh")
        parser = bkrdoc.Parser("")
        parser.parse_data("rlFileBackup --clean cleandir")
        doc = bkrdoc.DocumentationTranslator(parser.argparse_data_list[0])

    def test_assert2_commands(self):
        parser = bkrdoc.Parser("")
        parser.parse_data("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(parser.argparse_data_list[0].argname, "rlAssertGrep")
        self.assertEqual(parser.argparse_data_list[0].pattern, "Not Found")
        self.assertEqual(parser.argparse_data_list[0].file, "stderr")
        pokus = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf = pokus.translate_data(parser.argparse_data_list[0])
        inf_unit = pokus.translate_data(parser.argparse_data_list[0])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File: \"stderr\" must contain pattern: \"Not Found\""
        self.assertEqual(inf_data.information, inf)

        parser.parse_data("rlAssertExists gener.html")
        self.assertEqual(parser.argparse_data_list[1].argname,"rlAssertExists")
        self.assertEqual(parser.argparse_data_list[1].file_directory,"gener.html")
        pokus = bkrdoc.DocumentationTranslator(bkrdoc.Parser("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/apache-test.sh"))
        inf = pokus.translate_data(parser.argparse_data_list[1])
        inf_unit = pokus.translate_data(parser.argparse_data_list[1])
        ref = bkrdoc.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File(directory): \"gener.html\" must exist"
        self.assertEqual(inf_data.information, inf)

    def test_autopart_test(self):
        generator = bkrdoc.DocumentationGenerator()
        generator.parse_given_file("./bkrdoc_not_tagged/examples/Bashlex_modified_tests/autopart-test.sh")
        generator.get_documentation_information()
        generator.generate_documentation()

if __name__ == '__main__':
    unittest.main()
