#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Classic filtering

    Not (fully) implemented yet
    Classic filtering are rule based evaluation of the email, e.g.
        from = sales@microsoft.com >> 2 in spam level
        subject contains 'russian girls' >> 5 in spam level
        best_friend@homebase.net >> 0 in spam level, and Protect email
        many more to come ...
"""

### Versions
# 0.1 - initial version of this module

### ToDo
# Consider loading rules from e.g. http://

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base
#import classic_ruleset  --- Does this exist at all? 20180728

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class Classic(filter_base.Filter):

    """ Classic filtering are rule based evaluation og the email """

    def __init__(self):
        super().__init__()
        self.filter_name = 'Classic'
        self._load_ruleset()
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        super().spamalyse(scm_in)  # overload method from Filter()
        scm_in = self._rup.spamalyse(scm_in)  # WTF is _rup?
        return scm_in


    def _load_ruleset(self):
        """"""
        str_rule_dir = os.path.dirname(os.path.realpath(__file__))  # i.e. This files dir
        log.info("Loading ruleset from: {}".format(str_rule_dir))
        self._rup = classic_ruleset.Ruleset(str_rule_dir)


if __name__ == '__main__':

    print("This is just for testing - You shoulden't be running this module directly...")