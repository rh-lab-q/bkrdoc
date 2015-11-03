from __future__ import division  # floating-point division


class DocumentationCredibility:
    """
    DocumentationCredibility class provides simple key(0-5 (LOW to HIGH)) to credibility conversion
    based on Unknown to Total commands ratio.
    :param credibility: credibility computed from number of unknown vs. total commands provided to the constructor
    :param credibilityTable: dictionary-like key-to-credibility conversion
    """
    credibility = ""

    credibilityTable = {0: 'None',
                        1: 'Very low',
                        2: 'Low',
                        3: 'Medium',
                        4: 'High',
                        5: 'Very high'}

    def __init__(self, unknown_commands, total_commands):
        percent_correct = self.compute_percent_correct(unknown_commands, total_commands)
        self.credibility = self.compute_credibility(percent_correct)

    def lookup_credibility(self, key):
        return self.credibilityTable.get(key, "unknown")

    def compute_credibility_key(self, percent_correct):
        """
        Computes credibility key by 20% increments (known/total commands ratio), starting from zero.
        :return: key for credibility computation (0-5)
        """
        if self.is_zero(percent_correct):
            return 0
        elif self.all_correct(percent_correct):
            return 5
        else:
            return (percent_correct // 20) + 1

    def compute_credibility(self, percent_correct):
        key = self.compute_credibility_key(percent_correct)
        return self.lookup_credibility(key)

    def get_credibility(self):
        return self.credibility

    def compute_percent_correct(self, unknown_commands, total_commands):
        if self.is_zero(total_commands):
            return 100
        else:
            return self.round_to_two_places((1 - (unknown_commands / total_commands)) * 100)

    @staticmethod
    def is_zero(number):
        return round(number) == 0

    @staticmethod
    def all_correct(number):
        return round(number) == 100

    @staticmethod
    def round_to_two_places(number):
        return round(number, 2)
