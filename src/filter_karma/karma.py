#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Karma filtering

    Not (fully) implemented yet
    Karma are small signs in or around the email, e.g.
        email have no 'Message-ID'
        'authentication-results' leave bad impression
        'dkim-signature' leave bad impression
        'received' trail looks wired
        'from', 'reply-to' and 'return-path' quite different, maybe look at x-sender?
        many more to come ...

        Notes:
            Consider: https://github.com/seatgeek/fuzzywuzzy

"""

### Versions  <-- Out of sync with the overall SpamClam versioning...
# 0.1 - initial version of this module

### ToDo
# implement more karma

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base


class Karma(filter_base.Filter):

    """ Karma is a mix of many factors, lets see where it leads... """

    def __init__(self):
        super().__init__()
        logging.debug("class init. {}".format(self.say_hi()))

    def spamalyse(self, scm_in):  # overload method from Filter()
        pass

    def _debug(self, param):
        self._data['debug'] = param
        return self._data['debug']

if __name__ == '__main__':

    print("This is just for testing - You shoulden't be running this module directly...")
    flt_k = Karma()
    print("test: {}".format(flt_k))
    print("Say: {}".format(flt_k.say_hi()))
    print("db: {}".format(flt_k._debug('Yoo')))