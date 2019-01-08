#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Classic filtering

    Not (fully) implemented yet
    Classic filtering are rule based evaluation og the email, e.g.
        from = sales@microsoft.com >> +2 in spam level
        subject contains 'russian girls' >> +5 in spam level
        best_friend@homebase.net >> -3 in spam level, and Protect email
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

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class Classic(filter_base.Filter):

    """ Classic filtering are rule based evaluation og the email """

    def __init__(self):
        super().__init__()
        self.str_filter_name = 'Classic'
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        super().spamalyse(scm_in)  # overload method from Filter()
        self._load_classic_rules()
        scm_in = self._check_classic_rules(scm_in)
        return scm_in


    def _load_classic_rules(self, str_rules_dir):
        pass


    def _check_classic_rules(self, scm_i):
        """ Checks the scmail's against all Classic Rules """
        loop over rules:
            if scm_i.get('id').endswith('@ECsoftware.net'):
                scm_i.add_vote(self.str_filter_name, 1, 4, None, 'No Message-ID')
        return scm_i


if __name__ == '__main__':

    print("This is just for testing - You shoulden't be running this module directly...")