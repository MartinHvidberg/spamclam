#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Demo filtering
    It's not a real filter - You shouldn't run it.
    The intention is to be a demo and template for making your own filter.
"""

# Versions
# 0.1 - initial version of this module

# ToDo

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class Demo(filter_base.Filter):

    """ Demo is a template for your own filter """

    def __init__(self):
        """ Nothing much really for users to change here ... except change the name """
        super().__init__()
        self.filter_name = 'Demo'  # <--- Put your filter name here
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        """ This is the main function, that every e-mail is parsed through.
        Your own filter will have one or more separate logical checks.
        Each check should preferably be implemented as a separate functions below,
        grouping the functionality in a way that makes sense to you.
        The function spamalyse() should call each of these functions, with the incoming mail as argument.

        The present demo calls two check functions: check_xxx() and check_yyy()
        Your checks, and thereby functions, are likely to be way more complex,
        but the principle, for all check-function, are the same:
            Analyse the e-mail object
            Vote (and maybe Protect/Unprotect)
            Return the e-mail object - and that is important!
        """
        log.info("*spamalyse(demo) w.: {}".format(scm_in.get('id')))
        scm_in = super().spamalyse(scm_in)  # please keep this, though likely an empty method.
        scm_in = self._check_xxx(scm_in)  # <-- replace these lines with calls to the functions you will write below.
        scm_in = self._check_yyy(scm_in)
        return scm_in


    def _check_xxx(self, scm_i):
        """ Handling a suspect Spam e-mail """
        log.info(" chk xxx(demo) w.: {}".format(scm_i.get('id')))  # Just for showing activity in the log
        #if "money is waiting for you" in scm_i.get('subject'):
        if "Din låneansøgning er klar" in scm_i.get('subject'):
            scm_i.vote(self.filter_name, 'check_xxx', 7, 7, 7, 9, 'Subject is suspicious')  # Please see SCMail.vote() for details.
        return scm_i  # Always remember to return the e-mail object, it's votes have changed!


    def _check_yyy(self, scm_i):
        """ Handling a friendly e-mail """
        log.info(" chk yyy(demo) w.: {}".format(scm_i.get('id')))
        if 'ecsoftware.net' in scm_i.get('from'):  # These e-mails are always important to receive ...
            scm_i.vote(self.filter_name, 'check_yyy', 0, 9, 1, 3, 'from friendly EC-software')
            scm_i.protect()  # Protect the e-mail from being deleted, regardless of other filters verdict.
        return scm_i


if __name__ == '__main__':

    print("This is not the main module - You shouldn't be running this module directly...")
