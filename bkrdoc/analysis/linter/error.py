__author__ = 'blurry'


class Error(object):

    def __init__(self, line=0, message=""):
        self.line = line
        self.message = message
