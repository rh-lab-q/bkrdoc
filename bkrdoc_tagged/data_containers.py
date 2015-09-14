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

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class FunctionContainer(SimpleContainer):

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class LoopContainer(SimpleContainer):

    def __init__(self):
        self.comments_list = []
        self.statement_list = []
        self.common_comments = []


class TaggedCommentContainer(object):

    comments = []
    tagged_line = ""

    def __init__(self, first_comment):
        self.comments = [first_comment]

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_tagged_line(self, line):
        self.tagged_line = line

    def get_comments(self):
        return self.comments


def is_simple_container_instance(container):
    container_names = ["LoopContainer", "FunctionContainer", "ConditionContainer"]
    return type(container).__name__ in container_names