#!/usr/bin/python
__author__ = 'Jiri_Kulda'

from bkrdoc.analysis import Option


class DocumentationInformation(object):
    """
    This class contains data to describe every BeakerLib command
    :param cmd_name: Command name
    :param topic_object: Instance of Topic class
    :param action: BeakerLib command action
    :param importance: BeakerLib command importance
    :param options: Instance of Option class
    """
    command_name = ""

    topic = ""

    options = Option

    action = []

    importance = ""

    def __init__(self, cmd_name, topic_object, action, importance, options=None):
        if options is None:
            self.options = Option()
        else:
            self.options = options
        self.command_name = cmd_name
        self.topic = topic_object
        self.action = action
        self.importance = importance

    def get_topic(self):
        return self.topic.get_topic()

    def get_topic_subject(self):
        return self.topic.get_subject()

    def get_action(self):
        return self.action

    def get_importance(self):
        return self.importance

    def get_status(self):
        return self.options.get_status()

    def get_option(self):
        return self.options.get_option()

    def set_status(self, status):
        self.options.set_status(status)

    def get_command_name(self):
        return self.command_name
