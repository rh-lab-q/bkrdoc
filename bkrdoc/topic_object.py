#!/usr/bin/python
__author__ = 'Jiri_Kulda'

class Topic(object):
    """
    Class which is consist of information topic data.
    For example for BeakerLib command rlRun is topic command.

    :param topic_data: topic data (Facts)
    :param subject: Subject data which are "connected" to topic_data
    """
    topic = ""

    subject = []

    def __init__(self, topic_data, subject):
        self.topic = topic_data
        self.subject = subject

    def get_topic(self):
        return self.topic

    def get_subject(self):
        return self.subject