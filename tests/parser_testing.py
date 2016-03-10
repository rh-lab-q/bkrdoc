#!/usr/bin/python

import unittest
import sys

# redirecting stdout
try:
    from cStringIO import StringIO  #Python2
except ImportError:
    from io import StringIO  #Python3

sys.path.insert(0, '..')
sys.path.insert(0, './bkrdoc_not_tagged/')
import bkrdoc.analysis
import bkrdoc.markup


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
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        my = generator._parser_ref
        generator.get_doc_data()
        pom_list = ['/examples/beakerlib/Sanity/apache', 'httpd', '/var/www/', '/var/log/httpd', '$(mktemp -d)']
        self.assertListEqual(my.phases[-3].variables.variable_values_list, pom_list,"EQUAL")
        
        self.assertEqual(len(my.phases),10)
        self.assertEqual(my.phases[1].phase_name,"Setup \"Setup\"")
        self.assertEqual(my.phases[3].phase_name,"Test \"Test Existing Page\"")
        self.assertEqual(my.phases[5].phase_name,"Test \"Test Missing Page\"")
        self.assertEqual(my.phases[7].phase_name,"Cleanup \"Cleanup\"")
        list1 = ['rlAssertRpm "httpd"', "rlRun 'TmpDir=$(mktemp -d)' 0",
        'pushd $TmpDir', 'rlRun "rlFileBackup --clean $HttpdPages $HttpdLogs" 0 "Backing up"',
         'rlRun "echo \'Welcome to Test Page!\' > $HttpdPages/index.html" 0 "Creating a simple welcome page"',
          'rlRun "rm -f $HttpdLogs/*"', 'rlRun "rlServiceStart httpd"']
        self.assertEqual(my.phases[1].statement_list,list1)
        
    def test_func(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/mozila-test.sh")
        generator.get_doc_data()
        #print my.phases[0].func_list

    def test_environmental_variables(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/mozila-test.sh")

        my = generator._parser_ref
        generator.get_doc_data()
        self.assertEqual(my.environmental_variable, ['BEAKERLIB_DIR', 'OUTPUTFILE'])

        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        my = generator._parser_ref
        generator.get_doc_data()
        self.assertEqual(my.environmental_variable, [])

    def test_assert_equal(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlAssertEquals \"Saves the configuration\" \"_enabled\" \"$CONF_VALUE\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertEquals")
        self.assertEqual(mys.parsed_param_ref.value1,"_enabled")
        self.assertEqual(mys.parsed_param_ref.comment, "Saves the configuration")
        self.assertEqual(mys.parsed_param_ref.value2, "$CONF_VALUE")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Value1 _enabled must be equal to value2 $CONF_VALUE"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)

    def test_automata(self):
        my = bkrdoc.analysis.StatementDataSearcher()
        my.parse_command("rlAssertRpm \"httpd\"")
        self.assertEqual(my.parsed_param_ref.argname,"rlAssertRpm")
        self.assertEqual(my.parsed_param_ref.name,"httpd")

    def test_rlRpm_commands(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlAssertRpm \"httpd\" 22 23  44")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Package httpd must be installed with version: 22, release: 23 and architecture: 44"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 4)

    def test_unknown_command(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        unknown, var = mys.parse_command("poppd asdas")
        self.assertEqual(unknown.argname,"UNKNOWN")

    def test_first_command(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlRun \"rm -r $TmpDir\" 2,3,4,26 \"Removing tmp directory\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        self.assertEqual(mys.parsed_param_ref.command,"rm -r $TmpDir")
        self.assertEqual(mys.parsed_param_ref.comment, "Removing tmp directory")
        self.assertEqual(mys.parsed_param_ref.status, "2,3,4,26")

        sec = bkrdoc.analysis.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" exit code must match: 2,3,4,26"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    def test_assert_commands(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        mys.parse_command("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertGrep")
        self.assertEqual(mys.parsed_param_ref.pattern,"Not Found")
        self.assertEqual(mys.parsed_param_ref.file, "stderr")

    def test_hash_command(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlHash \"text\" --algorithm magic!")
        self.assertEqual(mys.parsed_param_ref.argname,"rlHash")
        self.assertEqual(mys.parsed_param_ref.STRING,"text")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string text with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test, var = mys.parse_command("rlHash --stdin --algorithm magic!")
        self.assertEqual(mys.parsed_param_ref.argname,"rlHash")
        self.assertEqual(mys.parsed_param_ref.stdin,True)

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string from input with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_backup_command(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        argparse_parsed_command, var = mys.parse_command("rlFileBackup --clean cleandir")
        self.assertEqual(argparse_parsed_command.argname,"rlFileBackup")
        self.assertEqual(argparse_parsed_command.file[0],"cleandir")
        self.assertEqual(argparse_parsed_command.clean,True)

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(argparse_parsed_command)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File or directory cleandir is backed up"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_virtual_command(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        mys.parse_command("rlVirtualXStart $TEST")
        self.assertEqual(mys.parsed_param_ref.argname,"rlVirtualXStart")
        self.assertEqual(mys.parsed_param_ref.name,"$TEST")

        mys = bkrdoc.analysis.StatementDataSearcher()
        mys.parse_command("rlAssert0 \"Virtual X server started\" $?")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssert0")
        self.assertEqual(mys.parsed_param_ref.comment,"Virtual X server started")
        self.assertEqual(mys.parsed_param_ref.value,"$?")

    def test_ServiceXXX(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlServiceStart boolean boool asda ")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Starts services boolean, boool and asda"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        test, var = mys.parse_command("rlServiceRestore boolean boool asda ")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Services boolean, boool and asda are restored into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_SEBooleanXX(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlSEBooleanOn boolean boool asda ")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Sets booleans boolean, boool and asda to true"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test, var = mys.parse_command("rlSEBooleanRestore boolean boool asda ")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Restore booleans boolean, boool and asda into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlRun_command(self):

        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlRun -l 'rm -r $TmpDir' ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        self.assertEqual(mys.parsed_param_ref.command,"rm -r $TmpDir")

        sec = bkrdoc.analysis.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" must run successfully and output is stored in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 5)

    # @unittest.skip("Missing implementation of searching in rlRun commands for possible BeakerLib commands")
    def test_rlRun_rlFileBackup_extend(self):

        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlRun \"rlFileBackup --clean $HttpdPages $HttpdLogs\" \"1-2\" \"Backing up\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = bkrdoc.analysis.DocumentationTranslator(generator)
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Files or directories $HttpdPages and $HttpdLogs are backed up and must finished with return code matching: 1-2"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    # @unittest.skip("Missing implementation of searching in rlRun commands for possible BeakerLib commands")
    def test_rlRun_rlServiceStart_extend(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlRun \"rlServiceStart httpd\" ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Service: httpd must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

    def test_rlGet_commands(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlGetPrimaryArch")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetPrimaryArch")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns primary arch for the current system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        test, var = mys.parse_command("rlGetDistroRelease")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetDistroRelease")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns release of the distribution on the system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 3)

        test, var = mys.parse_command("rlShowRunningKernel")
        self.assertEqual(mys.parsed_param_ref.argname,"rlShowRunningKernel")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Log a message with version of the currently running kernel"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

        test, var = mys.parse_command("rlGetTestState")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetTestState")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns number of failed asserts"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlLog_commands(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlLogWarning ahoj logfile priorita --prio-label")
        self.assertEqual(mys.parsed_param_ref.argname,"rlLogWarning")
        self.assertEqual(mys.parsed_param_ref.logfile,"logfile")
        self.assertEqual(mys.parsed_param_ref.priority,"priorita")
        self.assertEqual(mys.parsed_param_ref.prio_label,True)

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"ahoj\" is created in to logfile logfile"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

        test, var = mys.parse_command("rlDie message ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlDie")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()

        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"message\" is created in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlBundleLogs(self):

        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlBundleLogs package file1 file2 file3 file4")
        self.assertEqual(mys.parsed_param_ref.argname,"rlBundleLogs")
        self.assertEqual(mys.parsed_param_ref.file,["file1","file2","file3", "file4"])

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Creates a tarball of files file1, file2 and file3... and attached it/them to test result"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_filesubmit(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlFileSubmit path_to_file  required -s as")
        self.assertEqual(mys.parsed_param_ref.argname,"rlFileSubmit")
        self.assertEqual(mys.parsed_param_ref.s,"as")
        self.assertEqual(mys.parsed_param_ref.path_to_file,"path_to_file")
        self.assertEqual(mys.parsed_param_ref.required_name,'required')

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Resolves absolute path path_to_file, replaces / for as and rename file to required"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_showpackageversion(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlShowPackageVersion as km")
        self.assertEqual(mys.parsed_param_ref.argname,"rlShowPackageVersion")
        self.assertEqual(mys.parsed_param_ref.package,["as","km"])

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Shows information about as and km version")
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_JournalPrint(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlJournalPrintText --full-journal")
        self.assertEqual(mys.parsed_param_ref.argname,"rlJournalPrintText")
        self.assertEqual(mys.parsed_param_ref.full_journal,True)

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Prints the content of the journal in pretty text format with additional information")
        self.assertEqual(sec.inf_ref.importance, 1)

    def test_rlWaitxxx(self):

        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlWaitForFile path")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script until file or directory with this path path starts listening"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,2)

        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlWaitForCmd path -p TENTO -r 1")

        sec = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script execution until command path exit status is unsuccessful\n and process with this PID TENTO must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance, 2)

    def test_backup_doc(self):

        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        mys = bkrdoc.analysis.StatementDataSearcher()
        mys.parse_command("rlFileBackup --clean cleandir")
        doc = bkrdoc.analysis.DocumentationTranslator(mys.parsed_param_ref)


    def test_assert2_commands(self):
        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertGrep")
        self.assertEqual(mys.parsed_param_ref.pattern,"Not Found")
        self.assertEqual(mys.parsed_param_ref.file, "stderr")
        pokus = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf = pokus.translate_data(test)
        inf_unit = pokus.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File: \"stderr\" must contain pattern: \"Not Found\""
        self.assertEqual(inf_data.information, inf)

        mys = bkrdoc.analysis.StatementDataSearcher()
        test, var = mys.parse_command("rlAssertExists gener.html")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertExists")
        self.assertEqual(mys.parsed_param_ref.file_directory,"gener.html")
        pokus = bkrdoc.analysis.DocumentationTranslator(bkrdoc.analysis.Parser("./examples/tests/apache-test.sh"))
        inf = pokus.translate_data(test)
        inf_unit = pokus.translate_data(test)
        ref = bkrdoc.analysis.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File(directory): \"gener.html\" must exist"
        self.assertEqual(inf_data.information, inf)

    def test_autopart_test(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/autopart-test.sh")
        generator.get_documentation_information()
        generator.generate_documentation()


    def test_credibility(self):
        cr = bkrdoc.analysis.DocumentationCredibility(0, 0)
        perc = cr.compute_percent_correct(0, 0)
        self.assertEqual(cr.compute_credibility_key(perc), list(cr.credibilityTable)[-1])  # 0 total, should be MAX

        cr0 = bkrdoc.analysis.DocumentationCredibility(100, 100)
        self.assertEqual(cr0.get_credibility(), cr0.credibilityTable[0])
        cr1 = bkrdoc.analysis.DocumentationCredibility(99, 100)
        self.assertEqual(cr1.get_credibility(), cr1.credibilityTable[1])
        cr2 = bkrdoc.analysis.DocumentationCredibility(81, 100)
        self.assertEqual(cr2.get_credibility(), cr2.credibilityTable[1])
        cr3 = bkrdoc.analysis.DocumentationCredibility(80, 100)
        self.assertEqual(cr3.get_credibility(), cr3.credibilityTable[2])
        cr4 = bkrdoc.analysis.DocumentationCredibility(61, 100)
        self.assertEqual(cr4.get_credibility(), cr4.credibilityTable[2])
        cr5 = bkrdoc.analysis.DocumentationCredibility(60, 100)
        self.assertEqual(cr5.get_credibility(), cr5.credibilityTable[3])
        cr6 = bkrdoc.analysis.DocumentationCredibility(41, 100)
        self.assertEqual(cr6.get_credibility(), cr6.credibilityTable[3])
        cr7 = bkrdoc.analysis.DocumentationCredibility(40, 100)
        self.assertEqual(cr7.get_credibility(), cr7.credibilityTable[4])
        cr8 = bkrdoc.analysis.DocumentationCredibility(21, 100)
        self.assertEqual(cr8.get_credibility(), cr8.credibilityTable[4])
        cr9 = bkrdoc.analysis.DocumentationCredibility(20, 100)
        self.assertEqual(cr9.get_credibility(), cr9.credibilityTable[5])
        cr10 = bkrdoc.analysis.DocumentationCredibility(1, 100)
        self.assertEqual(cr10.get_credibility(), cr10.credibilityTable[5])
        cr11 = bkrdoc.analysis.DocumentationCredibility(0, 100)
        self.assertEqual(cr11.get_credibility(), cr11.credibilityTable[5])

    def test_overall_credibility(self):
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/autopart-test.sh")
        credibility = ""
        for phase in generator._phases:
            if phase.phase_name == "Test":
                credibility = phase.get_phase_credibility().get_credibility()
        self.assertEqual(credibility, generator.get_overall_credibility())

    def test_below_medium_credibility_present_low(self):
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/mozila-test.sh")
        generator.print_documentation(PomArgparse())
        sys.stdout = old_stdout
        credibility = "Phases with below Medium credibility are present."
        self.assertNotEqual(my_stdout.getvalue().find(credibility), -1)

    def test_below_medium_credibility_present_very_low(self):
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/pxe-boot-test.sh")
        generator.print_documentation(PomArgparse())
        sys.stdout = old_stdout
        credibility = "Phases with below Medium credibility are present."
        self.assertNotEqual(my_stdout.getvalue().find(credibility), -1)

    def test_below_medium_credibility_present_none(self):
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/none.sh")
        generator.print_documentation(PomArgparse())
        sys.stdout = old_stdout
        credibility = "Phases with below Medium credibility are present."
        self.assertNotEqual(my_stdout.getvalue().find(credibility), -1)

    def test_below_medium_credibility_not_present_high(self):
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/tests/apache-test.sh")
        generator.print_documentation(PomArgparse())
        sys.stdout = old_stdout
        credibility = "Phases with below Medium credibility are present."
        self.assertEqual(my_stdout.getvalue().find(credibility), -1)

    def test_below_medium_credibility_not_present_medium(self):
        old_stdout = sys.stdout
        sys.stdout = my_stdout = StringIO()
        generator = bkrdoc.analysis.DocumentationGenerator()
        generator.parse_given_file("./examples/markup/testFromBugzila.sh")
        generator.print_documentation(PomArgparse())
        sys.stdout = old_stdout
        credibility = "Phases with below Medium credibility are present."
        self.assertEqual(my_stdout.getvalue().find(credibility), -1)


if __name__ == '__main__':
    unittest.main()
