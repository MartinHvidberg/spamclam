#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Karma filtering

    Not (fully) implemented yet
    Karma are small signs in or around the email, e.g.
        Email have no 'Message-ID' +implemented
        Subject is empty +implemented
        From name and from email have little in common.
        'authentication-results' leave bad impression
        'dkim-signature' leave bad impression
        'received' trail looks wired
        'from', 'reply-to' and 'return-path' quite different, maybe look at x-sender?
        many more to come ...

        Notes:
            Consider: https://github.com/seatgeek/fuzzywuzzy

"""

__version__ = '0.4.2'
### Versions
# 0.1 - initial version of this module
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works

### ToDo
# implement more karma

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {} version: {}".format(__file__, __version__))



class Karma(filter_base.Filter):

    """ Karma is a mix of many factors, lets see where it leads... """

    def __init__(self):
        super().__init__()
        self.str_filter_name = 'Karma'
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        super().spamalyse(scm_in)  # overload method from Filter()
        scm_in = self._check_message_id(scm_in)
        scm_in = self._check_subject(scm_in)
        return scm_in


    def _debug_xxx(self, param):  # Should be deleted... ToDo
        self._data['debug'] = param
        return self._data['debug']


    def _check_message_id(self, scm_i):
        """ Checks the scmail's Messag-ID """
        if scm_i.get('id').endswith('@ECsoftware.net'):
            scm_i.add_vote(self.str_filter_name, 1, None, None, 'No Message-ID')
        ##print("MsgID: {}".format(scm_i.get('id')))
        return scm_i


    def _check_subject(self, scm_i):
        """ Check the scmail's Subject """
        if scm_i.get('subject') == "":
            scm_i.add_vote(self.str_filter_name, 1, None, None, 'Subject is Empty')
        return scm_i

    def check_from(self, scm_i):
        """ Check from-name and from-email are not too different """
        str_fnam = scm_i.get("from_nam")
        str_fadr = scm_i.get("from_adr")
        if str_fnam != str_fadr:
            pass#log.
        return scm_i


if __name__ == '__main__':

    print("This is just for testing - You shoulden't be running this module directly...")
    flt_k = Karma()
    print("test: {}".format(flt_k))
    print("Say: {}".format(flt_k.say_hi()))
    print("db: {}".format(flt_k._debug('Yoo')))