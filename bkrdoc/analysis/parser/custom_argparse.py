__author__ = 'Zuzana Baranova'

'''
In order not to system.exit from argparse parsing error, one has to subclass ArgumentParser
and override the 'error' method.
'''

import argparse
import sys


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            raise exc
        raise argparse.ArgumentError(argument=None, message=self.format_usage() + message)
