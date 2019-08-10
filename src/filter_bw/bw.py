#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Demo filtering
    It's not a real filter - You shouldn't run it.
    The intention is to be a bw and template for making your own filter.
"""

# Versions
# 0.1 - initial version of this module

# ToDo

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base
import rules

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class BW(filter_base.Filter):

    """ Good old Black and White filter, you can trust """

    def __init__(self):
        """ Nothing much really for users to change here ... except change the name """
        super().__init__()
        self.filter_name = 'BW'
        self._rules = rules.Rules()  # We only want to do this once, so make it part of BW
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        """ This is the main function, that every e-mail is parsed through. """
        log.info("*spamalyse(bw) w.: {}".format(scm_in.get('id')))
        scm_in = super().spamalyse(scm_in)  # please keep this, though likely an empty method.
        return self._rules.spamalyse(scm_in)  # All the good stuff is handled by the Rules object ...


if __name__ == '__main__':

    print("This is not the main module - You shouldn't be running this module directly...")
