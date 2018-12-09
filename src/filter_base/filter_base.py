#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Basic filtering functionality
"""

### Versions  <-- Out of sync with the overall SpamClam versioning...
# 0.1 - initial version of this module

### ToDo
# ...


import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import sc_register


class Filter(object):
    """ This is a basic Filter.
     It dosn't filter anything, but acts as the parent class for other filters """

    def __init__(self):
        logging.debug("class init. Filter")
        self._data = dict()  # Not really sure what to put here, yet

    def spamalyse(self, scmail):
        """ Checks a single SCMail against the filter, i.e. it self """
        return scmail  # method is supposed to be overloaded

    def filter(self, register):
        """ Checks all SCMails in a Register against the filter, i.e. it self """
        reg_out = sc_register.Register()
        for scm_id in register.list():
            scm_f = self.spamalyse(register.get(scm_id))
            reg_out.insert(scm_f)
        return reg_out

    def say_hi(self):
        """ This is a quite silly method, only used for debugging... """
        return "Hi... I'm a: {}".format(str(type(self)))