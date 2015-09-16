__author__ = 'jkulda'


class SimpleContainer(object):

    comments_list = []
    statement_list = []
    common_comments = []

    def add_comment(self, comment_container):
        self.comments_list.append(comment_container)

    def add_statement_line(self, line):
        self.statement_list.append(line)

    def add_common_comment(self, common_comment):
        self.common_comments.append(common_comment)

    def get_statement_list(self):
        pom_list = []
        for member in self.statement_list:
            if is_simple_container_instance(member):
                pom_list += member.get_statement_list()
            else:
                pom_list.append(member)
        return pom_list

    def get_comments_list(self):
        pom_list = []
        for member in self.comments_list:
            if is_simple_container_instance(member):
                pom_list += member.get_comments_list()
            else:
                pom_list.append(member.get_comments())
        return pom_list

    def comments_set_up(self):
        for comment in self.comments_list:
            if is_simple_container_instance(comment):
                comment.comments_set_up()
            else:
                comment.search_for_tags()

class PhaseOutsideContainer(SimpleContainer):

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class TestPhaseContainer(SimpleContainer):

    def __init__(self):
        self.name = ""
        self.name_comment = ""
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []

    def add_statement_line(self, line):
        if self.is_name_empty() and len(self.statement_list) == 0:
            self.name = line[0]
            if len(line) > 1:
                self.name_comment = line[1]
        else:
            self.statement_list.append(line)

    def is_name_empty(self):
        return self.name == ""


class ConditionContainer(SimpleContainer):
    condition_tag = "condition"

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class FunctionContainer(SimpleContainer):
    function_tag = "function"

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class LoopContainer(SimpleContainer):
    loop_tag = "loop"

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class TaggedCommentContainer(object):

    known_tags = {"keywords": "", "key": "", "author": "", "description": ""}
    condition_tags = []
    comments = []
    tagged_line = ""
    documentation_comments = []

    def __init__(self, first_comment):
        self.comments = [first_comment]
        self.tagged_line = ""
        self.condition_tags = []
        self.documentation_comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_tagged_line(self, line):
        self.tagged_line = line

    def get_comments(self):
        return self.comments

    def add_condition_tag(self, given_tag):
        self.condition_tags.append(given_tag)

    def search_for_tags(self):
        for comment in self.comments:
            if self.get_tag_in_line(comment):
                found_tag = self.get_tag_in_line(comment)[0]
                if self.is_known_tag(self.get_tag_from_word(found_tag)):
                    self.known_tags[self.get_tag_from_word(found_tag)] = self.set_documentation_comment(comment[comment.index(found_tag) + 1:])
                    print self.known_tags[self.get_tag_from_word(found_tag)]
                else:
                    raise UnknownTagException("Not supported tag: {0}. If it's needed write an e-mail to "
                                              "jkulda@redhat.com.".format(self.get_tag_from_word(found_tag)))
            else:
                erased_comment_line = self.erase_comments_start_tags(comment)
                if self.is_code_tag():
                    erased_comment_line = self.erase_comments_start_tags(self.tagged_line)
                self.documentation_comments.append(self.set_documentation_comment(erased_comment_line))
                # print self.documentation_comments

    def is_code_tag(self):
        return self.condition_tags == ["code"]

    def get_tag_in_line(self, splitted_line):
        return [word for word in splitted_line if ((word.startswith("@") and len(word) > 1) or word.startswith("#@@"))]

    def is_known_tag(self, tag):
        return tag in self.known_tags.keys()

    def erase_comments_start_tags(self, splitted_line):
        if splitted_line[0] == "#@":
            return splitted_line[1:]
        elif len(splitted_line) > 1 and splitted_line[0] == "#" and splitted_line[1] == "@":
            return splitted_line[2:]
        elif splitted_line[0].startswith("#@"):
            return [splitted_line[0][2:]] + splitted_line[1:]
        elif splitted_line[0].startswith("#"):
            if splitted_line[0] == "#":
                return splitted_line[1:]
            else:
                return [splitted_line[0][1:]] + splitted_line[1:]
        elif splitted_line[-1] == "#@":
            return splitted_line[0:-1]
        elif splitted_line[-1].endswith("#@"):
            return splitted_line[0:-2] + [splitted_line[-1][0:-3]]
        else:
            return splitted_line

    def set_documentation_comment(self, splitted_line):
        pom_line = splitted_line[0]
        for member in splitted_line[1:]:
            pom_line += " {0}".format(member)
        return pom_line

    def get_tag_from_word(self, word):
        if word.startswith("@"):
            return word[1:]
        else:
            return word[3:]


class UnknownTagException(Exception):
    pass

def is_simple_container_instance(container):
    container_names = ["LoopContainer", "FunctionContainer", "ConditionContainer"]
    return type(container).__name__ in container_names
