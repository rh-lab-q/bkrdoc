#!/usr/bin/python
__author__ = 'Jiri_Kulda'


class Option(object):
    """
    Option class which is consist of option and status of BeakerLib command
    :param option_data: BeakerLib command options data
    :param status_data: BeakerLib command future exit status
    """
    option = []

    status = []

    def __init__(self, option_data=None, status_data="-"):
        if option_data is None:
            self.option = []
        else:
            self.option = option_data
        self.status = status_data

    def get_option(self):
        return self.option

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status
