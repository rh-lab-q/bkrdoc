#!/usr/bin/python

import unittest
import sys

sys.path.insert(0, '..')
sys.path.insert(0, './bkrdoc_not_tagged/')
import bkrdoc.documentation_generator as parser



class TestSequenceFunctions(unittest.TestCase):
    
    
    def test_basic(self):
        my = parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh")
        my.get_doc_data()
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
        my = parser.Parser("./bkrdoc_not_tagged/examples/tests/mozila-test.sh")
        my.get_doc_data()
        #print my.phases[0].func_list


    def test_environmental_variables(self):
        my = parser.Parser("./bkrdoc_not_tagged/examples/tests/mozila-test.sh")
        my.get_doc_data()
        self.assertEqual(my.environmental_variable,['BEAKERLIB_DIR', 'OUTPUTFILE'])

        my = parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh")
        my.get_doc_data()
        self.assertEqual(my.environmental_variable,[])

    def test_assert_equal(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlAssertEquals \"Saves the configuration\" \"_enabled\" \"$CONF_VALUE\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertEquals")
        self.assertEqual(mys.parsed_param_ref.value1,"_enabled")
        self.assertEqual(mys.parsed_param_ref.comment, "Saves the configuration")
        self.assertEqual(mys.parsed_param_ref.value2, "$CONF_VALUE")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Value1 _enabled must be equal to value2 $CONF_VALUE"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,4)


    def test_automata(self):
        my = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        my.parse_command("rlAssertRpm \"httpd\"")
        self.assertEqual(my.parsed_param_ref.argname,"rlAssertRpm")
        self.assertEqual(my.parsed_param_ref.name,"httpd")

    def test_rlRpm_commands(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlAssertRpm \"httpd\" 22 23  44")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Package httpd must be installed with version: 22, release: 23 and architecture: 44"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,4)

    def test_unknown_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        unknown = mys.parse_command("poppd asdas")
        self.assertEqual(unknown.argname,"UNKNOWN")

    def test_first_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlRun \"rm -r $TmpDir\" 2,3,4,26 \"Removing tmp directory\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        self.assertEqual(mys.parsed_param_ref.command,"rm -r $TmpDir")
        self.assertEqual(mys.parsed_param_ref.comment, "Removing tmp directory")
        self.assertEqual(mys.parsed_param_ref.status, "2,3,4,26")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" exit code must match: 2,3,4,26"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,5)

    def test_assert_commands(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        mys.parse_command("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertGrep")
        self.assertEqual(mys.parsed_param_ref.pattern,"Not Found")
        self.assertEqual(mys.parsed_param_ref.file, "stderr")

    def test_hash_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlHash \"text\" --algorithm magic!")
        self.assertEqual(mys.parsed_param_ref.argname,"rlHash")
        self.assertEqual(mys.parsed_param_ref.STRING,"text")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string text with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test = mys.parse_command("rlHash --stdin --algorithm magic!")
        self.assertEqual(mys.parsed_param_ref.argname,"rlHash")
        self.assertEqual(mys.parsed_param_ref.stdin,True)

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Hashes string from input with hashing algorithm magic!"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_backup_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        argparse_parsed_command = mys.parse_command("rlFileBackup --clean cleandir")
        self.assertEqual(argparse_parsed_command.argname,"rlFileBackup")
        self.assertEqual(argparse_parsed_command.file[0],"cleandir")
        self.assertEqual(argparse_parsed_command.clean,True)

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(argparse_parsed_command)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File or directory cleandir is backed up"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_virtual_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        mys.parse_command("rlVirtualXStart $TEST")
        self.assertEqual(mys.parsed_param_ref.argname,"rlVirtualXStart")
        self.assertEqual(mys.parsed_param_ref.name,"$TEST")

        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        mys.parse_command("rlAssert0 \"Virtual X server started\" $?")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssert0")
        self.assertEqual(mys.parsed_param_ref.comment,"Virtual X server started")
        self.assertEqual(mys.parsed_param_ref.value,"$?")

    def test_ServiceXXX(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlServiceStart boolean boool asda ")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Starts services boolean, boool and asda"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test = mys.parse_command("rlServiceRestore boolean boool asda ")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Services boolean, boool and asda are restored into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_SEBooleanXX(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlSEBooleanOn boolean boool asda ")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Sets booleans boolean, boool and asda to true"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test = mys.parse_command("rlSEBooleanRestore boolean boool asda ")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Restore booleans boolean, boool and asda into original state"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)


    def test_rlRun_command(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlRun -l 'rm -r $TmpDir' ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        self.assertEqual(mys.parsed_param_ref.command,"rm -r $TmpDir")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Command \"rm -r $TmpDir\" must run successfully and output is stored in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,5)

    def test_rlRun_rlFileBackup_extend(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlRun \"rlFileBackup --clean $HttpdPages $HttpdLogs\" \"1-2\" \"Backing up\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Files or directories $HttpdPages and $HttpdLogs are backed up and must finished with return code matching: 1-2"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlRun_rlServiceStart_extend(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlRun \"rlServiceStart httpd\" ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlRun")
        #self.assertEqual(mys.parsed_param_ref.command,"rlFileBackup --clean $HttpdPages $HttpdLogs")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Service: httpd must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlGet_commands(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlGetPrimaryArch")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetPrimaryArch")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns primary arch for the current system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test = mys.parse_command("rlGetDistroRelease")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetDistroRelease")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns release of the distribution on the system"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

        test = mys.parse_command("rlShowRunningKernel")
        self.assertEqual(mys.parsed_param_ref.argname,"rlShowRunningKernel")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Log a message with version of the currently running kernel"
        self.assertEqual(inf_data.information,inf)
        self.assertEqual(sec.inf_ref.importance,2)

        test = mys.parse_command("rlGetTestState")
        self.assertEqual(mys.parsed_param_ref.argname,"rlGetTestState")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Returns number of failed asserts"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,3)

    def test_rlLog_commands(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlLogWarning ahoj logfile priorita --prio-label")
        self.assertEqual(mys.parsed_param_ref.argname,"rlLogWarning")
        self.assertEqual(mys.parsed_param_ref.logfile,"logfile")
        self.assertEqual(mys.parsed_param_ref.priority,"priorita")
        self.assertEqual(mys.parsed_param_ref.prio_label,True)

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"ahoj\" is created in to logfile logfile"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,1)

        test = mys.parse_command("rlDie message ")
        self.assertEqual(mys.parsed_param_ref.argname,"rlDie")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Message \"message\" is created in to log"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,1)

    def test_rlBundleLogs(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlBundleLogs package file1 file2 file3 file4")
        self.assertEqual(mys.parsed_param_ref.argname,"rlBundleLogs")
        self.assertEqual(mys.parsed_param_ref.file,["file1","file2","file3", "file4"])

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Creates a tarball of files file1, file2 and file3... and attached it/them to test result"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,1)

    def test_filesubmit(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlFileSubmit path_to_file  required -s as")
        self.assertEqual(mys.parsed_param_ref.argname,"rlFileSubmit")
        self.assertEqual(mys.parsed_param_ref.s,"as")
        self.assertEqual(mys.parsed_param_ref.path_to_file,"path_to_file")
        self.assertEqual(mys.parsed_param_ref.required_name,'required')

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Resolves absolute path path_to_file, replaces / for as and rename file to required"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,2)

    def test_showpackageversion(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlShowPackageVersion as km")
        self.assertEqual(mys.parsed_param_ref.argname,"rlShowPackageVersion")
        self.assertEqual(mys.parsed_param_ref.package,["as","km"])

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Shows information about as and km version")
        self.assertEqual(sec.inf_ref.importance,2)

    def test_JournalPrint(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlJournalPrintText --full-journal")
        self.assertEqual(mys.parsed_param_ref.argname,"rlJournalPrintText")
        self.assertEqual(mys.parsed_param_ref.full_journal,True)

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        self.assertEqual(inf_data.information, "Prints the content of the journal in pretty text format with additional information")
        self.assertEqual(sec.inf_ref.importance,1)

    def test_rlWaitxxx(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlWaitForFile path")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script until file or directory with this path path starts listening"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,2)

        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlWaitForCmd path -p TENTO -r 1")

        sec = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf_unit = sec.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "Pauses script execution until command path exit status is unsuccessful\n and process with this PID TENTO must be running"
        self.assertEqual(inf_data.information, inf)
        self.assertEqual(sec.inf_ref.importance,2)


    def test_backup_doc(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        mys.parse_command("rlFileBackup --clean cleandir")
        doc = parser.DocumentationTranslator(mys.parser_ref)


    def test_assert2_commands(self):
        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlAssertGrep \"Not Found\" \"stderr\"")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertGrep")
        self.assertEqual(mys.parsed_param_ref.pattern,"Not Found")
        self.assertEqual(mys.parsed_param_ref.file, "stderr")
        pokus = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf = pokus.translate_data(test)
        inf_unit = pokus.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File: \"stderr\" must contain pattern: \"Not Found\""
        self.assertEqual(inf_data.information, inf)

        mys = parser.StatementDataSearcher(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"),parser.PhaseContainer("test"))
        test = mys.parse_command("rlAssertExists gener.html")
        self.assertEqual(mys.parsed_param_ref.argname,"rlAssertExists")
        self.assertEqual(mys.parsed_param_ref.file_directory,"gener.html")
        pokus = parser.DocumentationTranslator(parser.Parser("./bkrdoc_not_tagged/examples/tests/apache-test.sh"))
        inf = pokus.translate_data(test)
        inf_unit = pokus.translate_data(test)
        ref = parser.GetInformation()
        inf_data = ref.get_information_from_facts(inf_unit)
        inf = "File(directory): \"gener.html\" must exist"
        self.assertEqual(inf_data.information, inf)

if __name__ == '__main__':
    unittest.main()
