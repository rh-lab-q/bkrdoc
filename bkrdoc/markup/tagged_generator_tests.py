
__author__ = 'jkulda'

import unittest
from bkrdoc.markup.tagged_generator import Generator


class TaggedGeneratorTests(unittest.TestCase):

    def test_phases(self):
        generator = Generator("./examples/markup/abrt-auto-reporting-sanity-test.sh")
        generator.parse_file()
        parser = generator.parser_ref
        self.assertEqual(len(parser.phases), 19)
        self.assertEqual(type(parser.phases[0]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[1]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[2]).__name__,  "TestPhaseContainer")
        self.assertEqual(type(parser.phases[3]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[4]).__name__,  "TestPhaseContainer")
        self.assertEqual(type(parser.phases[5]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[6]).__name__,  "TestPhaseContainer")
        self.assertEqual(type(parser.phases[7]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[8]).__name__,  "TestPhaseContainer")
        self.assertEqual(type(parser.phases[9]).__name__,  "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[10]).__name__, "TestPhaseContainer")
        self.assertEqual(type(parser.phases[11]).__name__, "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[12]).__name__, "TestPhaseContainer")
        self.assertEqual(type(parser.phases[13]).__name__, "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[14]).__name__, "TestPhaseContainer")
        self.assertEqual(type(parser.phases[15]).__name__, "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[16]).__name__, "TestPhaseContainer")
        self.assertEqual(type(parser.phases[17]).__name__, "PhaseOutsideContainer")
        self.assertEqual(type(parser.phases[18]).__name__, "PhaseOutsideContainer")

    def test_phases_statement(self):
        generator = Generator("./examples/markup/abrt-auto-reporting-sanity-test.sh")
        generator.parse_file()
        parser = generator.parser_ref

        self.assertEqual(parser.phases[0].get_statement_list(), ['. /usr/share/beakerlib/beakerlib.sh',
                                                                 '. ../aux/lib.sh', 'TEST="abrt-auto-reporting-sanity"',
                                                                 'PACKAGE="abrt"', 'function get_configured_value()',
                                                                 '{', 'VALUE=`grep "^AutoreportingEnabled" '
                                                                      '/etc/abrt/abrt.conf | tr -d " " | cut -f2 '
                                                                      '-d "="`', 'echo $VALUE', 'case "$VALUE" in',
                                                                 '[yY][eE][sS]|"_")', 'export CONF_VALUE="enabled"',
                                                                 ';;', '[nN][oO])', 'export CONF_VALUE="disabled"',
                                                                 ';;', '*)', 'echo "Unknown option value"',
                                                                 'export CONF_VALUE="disabled"', ';;', 'esac'])
        self.assertEqual(parser.phases[2].statement_list, ['TmpDir=$(mktemp -d)', 'pushd $TmpDir'])
        self.assertEqual(parser.phases[4].statement_list, ['rlRun "abrt-auto-reporting --help" 0',
                                                           'rlRun "abrt-auto-reporting --help 2>&1 | grep \'Usage: '
                                                           'abrt-auto-reporting\'"'])
        self.assertEqual(parser.phases[6].statement_list, ['rlRun "abrt-auto-reporting"', 'get_configured_value',
                                                           'rlAssertEquals "Reads the configuration" "_$(abrt-auto-reporting)" "_$CONF_VALUE"'])
        self.assertEqual(parser.phases[8].statement_list, ['rlRun "abrt-auto-reporting enabled"', 'get_configured_value',
                                                           'rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"', 'rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"'])
        self.assertEqual(parser.phases[10].statement_list, ['rlRun "abrt-auto-reporting disabled"',
                                                            'get_configured_value', 'rlAssertEquals "Saves the configuration" "_disabled" "_$CONF_VALUE"',
                                                            'rlAssertEquals "Reads the configuration" "_disabled" "_$(abrt-auto-reporting)"'])
        self.assertEqual(parser.phases[12].statement_list, ['rlRun "abrt-auto-reporting enabled"',
                                                            'get_configured_value', 'rlAssertEquals "Saves the configuration" "_enabled" "_$CONF_VALUE"',
                                                            'rlAssertEquals "Reads the configuration" "_enabled" "_$(abrt-auto-reporting)"'])
        self.assertEqual(parser.phases[14].statement_list[0], 'OLD="enabled"')
        self.assertEqual(parser.phases[14].get_statement_list(), ['OLD="enabled"', 'for arg in disabled EnAbLeD '
                                                                                   'dIsAblEd enabled no Yes nO yes 0 1',
                                                                  'do', 'rlRun "abrt-auto-reporting $arg"#@',
                                                                  'get_configured_value #@', 'rlAssertNotEquals '
                                                                                             '"Changed the '
                                                                                             'configuration" '
                                                                                             '"_$OLD" "_$CONF_VALUE"',
                                                                  'if [ $CONF_VALUE != "enabled" ] && [ $CONF_VALUE !='
                                                                  ' "disabled" ]; then',
                                                                  'rlFail "Mangles the configuration value"#@',
                                                                  'OLD=$CONF_VALUE #@'])
        self.assertEqual(parser.phases[16].statement_list, ['rlRun "abrt-auto-reporting disabled"', 'popd # TmpDir',
                                                            'rm -rf $TmpDir'])

    def test_phases_comments(self):
        generator = Generator("./examples/markup/abrt-auto-reporting-sanity-test.sh")
        generator.parse_file()
        parser = generator.parser_ref
        self.assertEqual(parser.phases[0].get_comments_list(), [[['#@', '@description', 'does', 'what', 'it', 'does']], [['#@', 'Function', 'that', 'configure', 'selected', 'value'], ['#@', 'does', 'not', 'require', 'any', 'parameter']], [['#@', 'comment', 'on', 'the', 'beggining']], [['#@', 'Important', 'case']], [['#@', 'comment', 'on', 'the', 'end']], [['#@', '@author', 'Janosik', 'Karel']]])
        self.assertEqual(parser.phases[1].get_comments_list(), [[['#@', 'Somenthing', 'in', 'start', 'of', 'the', 'test'], ['#Could', 'be', 'anything']]])
        self.assertEqual(parser.phases[2].get_comments_list(), [[['#@', 'Make', 'temporary', 'directory', 'and', 'saves', 'work', 'in', 'it']]])
        self.assertEqual(parser.phases[3].get_comments_list(), [[['#@', 'Additional', 'info']]])
        self.assertEqual(parser.phases[4].get_comments_list(), [[['#', '@', 'Print', 'help', 'informations'], ['#', '@keywords', 'doc', 'help'], ['#', 'blah', 'sfsdf', 'sdf', 'sdfsd', 'f'], ['#', 'Using', 'of', 'block', 'comment'], ['#', 'This', 'could', 'be', 'usefull']], [['#@', 'TESTING']], [['#@', 'Back', 'phase', 'testing']]])
        self.assertEqual(parser.phases[5].get_comments_list(), [])
        self.assertEqual(parser.phases[6].get_comments_list(), [[['#@', 'Runs', 'script', 'with', 'no', 'arguments']]])
        self.assertEqual(parser.phases[7].get_comments_list(), [])
        self.assertEqual(parser.phases[8].get_comments_list(), [[['#@Single', 'enablned', 'as', 'a', 'argument']]])
        self.assertEqual(parser.phases[9].get_comments_list(), [])
        self.assertEqual(parser.phases[10].get_comments_list(), [[['#@', 'Disabled', 'as', 'a', 'argument']], [['#@@key', 'mamut']]])
        self.assertEqual(parser.phases[11].get_comments_list(), [])
        self.assertEqual(parser.phases[12].get_comments_list(), [[['#@', 'More', 'than', 'just', 'one', 'enabled', 'as', 'a', 'argument']]])
        self.assertEqual(parser.phases[13].get_comments_list(), [])
        self.assertEqual(parser.phases[14].get_comments_list(), [[['#@', 'Various', 'types', 'of', 'arguments', 'will', 'start', 'this', 'part']], [['#@', 'for', 'every', 'argument', 'in', 'selected', 'word', 'will', 'do...']], [['']], [['']], [['#@', 'Test', 'if', 'actualy', 'value', 'in', 'arg', 'is', 'not', '"enabled"', 'and', '"disabled"']], [['#@', 'wee', 'will', 'seee']], [['']], [['#@', 'something', 'which', 'is', 'connected', 'to', 'this', 'loop']], [['']], [['#@', 'Documentation', 'test']]])
        self.assertEqual(parser.phases[15].get_comments_list(), [])
        self.assertEqual(parser.phases[16].get_comments_list(), [[['#@', 'clean', 'after', 'test']], [['#@', 'Disable', 'auto', 'reporting']]])
        self.assertEqual(parser.phases[17].get_comments_list(), [[['#@Something', 'on', 'the', 'end', 'of', 'the', 'test'], ['#could', 'be', 'anything']]])
        self.assertEqual(parser.phases[18].get_comments_list(), [])

    def test_conditions(self):
        generator = Generator("./examples/markup/condition_test.sh")
        generator.parse_file()
        parser = generator.parser_ref
        phases = parser.phases
        first_condition = phases[0].comments_list[0]
        self.assertEqual(first_condition.statement_list, ['if [ $? -eq 0 ]', 'then', 'rlReport $1 PASS'])
        self.assertEqual(first_condition.elif_parts[0].statement_list, ['else', 'rlReport $1 FAIL', 'RESULT="FAIL"'])

        second_condition = phases[0].comments_list[1]
        self.assertEqual(second_condition.statement_list, ['if [ $year -eq "0" ]; then', 'echo "This is a leap year.  February has 29 days."'])
        self.assertEqual(second_condition.elif_parts[0].statement_list, ['elif [ $year -eq 0 ]; then', 'echo "This is not a leap year, February has 29 days."'])
        self.assertEqual(second_condition.elif_parts[1].statement_list, ['else', 'echo "This is not a leap year.  February has 28 days."'])

        third_condition = phases[0].comments_list[2]
        self.assertEqual(third_condition.statement_list, ['if [ $year -eq "0" ]; then', 'echo "This is a leap year.  February has 29 days."'])
        self.assertEqual(third_condition.elif_parts[0].statement_list[0], "elif [ $year -eq 0 ]; then")
        self.assertEqual(third_condition.elif_parts[0].statement_list[1].statement_list, ['if [ $year -ne 0 ]; then', 'echo "This is not a leap year, February has 29 days."'])
        self.assertEqual(third_condition.elif_parts[0].statement_list[1].elif_parts[0].statement_list, ['else', 'echo "This is a leap year.  February has 28 days."'])
        self.assertEqual(third_condition.elif_parts[1].statement_list, ['else', 'echo "This is not a leap year.  February has 28 days."'])
        # print phases[0].comments_list
        self.assertEqual(phases[0].get_statement_list(), ['rlReport $1 FAIL', 'if [ $? -eq 0 ]', 'then', 'rlReport $1 PASS', 'else', 'rlReport $1 FAIL', 'RESULT="FAIL"', 'if [ $year -eq "0" ]; then', 'echo "This is a leap year.  February has 29 days."', 'elif [ $year -eq 0 ]; then', 'echo "This is not a leap year, February has 29 days."', 'else', 'echo "This is not a leap year.  February has 28 days."', 'if [ $year -eq "0" ]; then', 'echo "This is a leap year.  February has 29 days."', 'elif [ $year -eq 0 ]; then', 'if [ $year -ne 0 ]; then', 'echo "This is not a leap year, February has 29 days."', 'else', 'echo "This is a leap year.  February has 28 days."', 'else', 'echo "This is not a leap year.  February has 28 days."'])

        self.assertEqual(phases[0].get_comments_list(), [[['#@', 'condition']], [['#@', 'conditionaaaaaaaaaaaa']], [['#@', 'conditionoooooooooooo']], [['#@', 'conditioneeeeeeeeeee']], [['#@', 'conditionesss']], [['#@', 'conditionassss']], [['#@', 'conditionsdaswewqw']], [['#@', 'conditionttttttttttttt']]])

    def test_abrt(self):
        generator = Generator("./examples/markup/abrt-auto-reporting-sanity-test.sh")
        generator.parse_file()
        generator.comments_set_up()
        doc = generator.get_documentation()
        first_doc = open("./examples/markup/abrt-PURPOSE.txt", 'r')
        data = first_doc.read()
        self.assertEqual(doc, data)

    def test_condition(self):
        generator = Generator("./examples/markup/condition_test.sh")
        generator.parse_file()
        generator.comments_set_up()
        doc = generator.get_documentation()
        first_doc = open("./examples/markup/condition-PURPOSE.txt", 'r')
        data = first_doc.read()
        self.assertEqual(doc, data)

    def test_containers(self):
        generator = Generator("./examples/markup/containers_tests.sh")
        generator.parse_file()
        generator.comments_set_up()
        doc = generator.get_documentation()
        first_doc = open("./examples/markup/containers-PURPOSE.txt", 'r')
        data = first_doc.read()
        self.assertEqual(doc, data)

if __name__ == '__main__':
    unittest.main()
