#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Public Black-list functionality for spamalyser.py

### Versions
# 0.1 - initial version of this module  <- Out of sync with the overall SpamClam versioning.

### ToDo

# include functionality for open/public BlackList-lists like
	spamhaus.org,
	uribl.com (free Frankfurt: ff.uribl.com) and
	SURBL.org
	http://www.uceprotect.net

"""

import requests
import json

class pblists(object):
    """ is a ..
    """

    def __init__(self):
        # Dictionary of the lists we subscribe to.
        with open("public_blists.json", "rb") as f:
            self._dic_lists = json.load(f)
        ## print(json.dumps(self._dic_lists))
        self.update_lists()
        self.load_lists()

    def load_lists(self):
        pass

    def update_a_list(self, str_url, str_fn):
        print(('Beginning file download with requests of {}'.format(str_url)))
        r = requests.get(str_url)
        if r.status_code == 200:
            # XXX Consider more checks, before overwriting local data.
            with open(str_fn, 'wb') as f:
                f.write(r.content)
        else:  # Any http response != 200
            # Retrieve HTTP meta-data
            print(("!!! Can't load resource from {}".format(str_url)))
            print(("    Server say: status: {}".format(r.status_code)))
            print(("    Server say: content-type: {}".format(r.headers['content-type'])))
            print(("    Server say: Encoding: {}".format(r.encoding)))

    def update_lists(self):
        for key_l in list(self._dic_lists.keys()):
            dic_bl = self._dic_lists[key_l]
            self.update_a_list(dic_bl['url'], dic_bl['fn'])

    def spamalyse(self, salmail):
        """ Checks an email against all lists
            returns: ( True|False ) """


if __name__ == "__main__":
    print("Debug...")
    pbl = pblists()