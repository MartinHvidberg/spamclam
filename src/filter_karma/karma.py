#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Karma filtering

    Not (fully) implemented yet
    Karma are small signs in or around the email, e.g.
        Email have no 'Message-ID' +implemented
        Subject is empty +implemented
        From-name and from-addr have nothing in common.
        'from', 'reply-to' and 'return-path' quite different, maybe look at x-sender?
        'authentication-results' leave bad impression
        'dkim-signature' leave bad impression
        'received' trail looks wired
        many more to come ...

        Notes:
            Consider: https://github.com/seatgeek/fuzzywuzzy

"""

### Versions
# 0.1 - initial version of this module
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

### ToDo
# implement more karma

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'filter_base'))
import filter_base

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class Karma(filter_base.Filter):

    """ Karma is a mix of many factors, lets see where it leads... """

    def __init__(self):
        super().__init__()
        self.str_filter_name = 'Karma'
        log.info("{}".format(self.say_hi()))


    def spamalyse(self, scm_in):
        log.info("*spamalyse(karma) w.: {}".format(scm_in.get('id')))
        super().spamalyse(scm_in)  # overload method from Filter()
        scm_in = self._check_message_id(scm_in)
        scm_in = self._check_subject(scm_in)
        scm_in = self._check_from(scm_in)
        return scm_in


    def _check_message_id(self, scm_i):
        """ Checks the scmail's Messag-ID """
        log.debug(" chk msgid(karma) w.: {}".format(scm_i.get('id')))
        if scm_i.get('id').endswith('@ECsoftware.net'):
            scm_i.add_vote(self.str_filter_name, 1, 4, None, 'No Message-ID')
        ##print("MsgID: {}".format(scm_i.get('id')))
        return scm_i


    def _check_subject(self, scm_i):
        """ Check the scmail's Subject """
        log.debug(" chk subj(karma) w.: {}".format(scm_i.get('id')))
        if scm_i.get('subject') == "":
            scm_i.add_vote(self.str_filter_name, 1, None, None, 'Subject is Empty')
        return scm_i


    def _check_from(self, scm_i):
        """ Check various 'from' parameters, and compare them """
        log.debug(" chk from(karma) w.: {}".format(scm_i.get('id')))

        # Check that from-name and from-addr have something in common
        num_cnt_sim = 0  # No similarities, yet
        str_fnam = scm_i.get("from_nam", nodata="").lower()  # all comparison as lower
        str_fadr = scm_i.get("from_adr", nodata="").lower()  # all comparison as lower
        if str_fnam != "":  # Empty from-name is handled by other Karma rule
            # Count Name-tokens in Address
            lst_fnam = str_fnam.split()  # tokenise name by split on wide-spaces
            for tok_fnam in lst_fnam:
                if tok_fnam in str_fadr:
                    num_cnt_sim += 1
            # Count Address-tokens in Name
            lst_fadr = str_fadr.replace("@",".").split(".")
            for tok_fadr in lst_fadr:
                if tok_fadr in str_fnam:
                    num_cnt_sim += 1
            if num_cnt_sim < 1:
                scm_i.add_vote(self.str_filter_name, 1, 4, None, 'from-name and from-addr mismatch')

        # Check that 'from', 'reply-to' and 'return-path' have something in common, maybe look at x-sender?
        print(" * Check from- reply- and return-address integrity")
        los_dom = list()
        los_dom.append(scm_i.get('from_dom'))
        los_dom.append(scm_i.get('return-path_dom'))
        los_dom.append(scm_i.get('reply-to_dom'))
        lol_dom = list()
        for dom in los_dom:
            if dom:
                dom = dom.split(".")[:-1]  # tokenize and loose TLD
            else:  # in case dom was None
                dom = list()  # set it to an emply list
            lol_dom.append(dom)
        print("\n{}".format(lol_dom))
        num_max_friends = len(lol_dom) * (len(lol_dom)-1)
        lst_dom_friends = list()
        for i in range(len(lol_dom)):
            for j in range(len(lol_dom)):
                if i != j:  # Don't compare to self
                    lst_dom_friends.append([hit for hit in lol_dom[i] if hit in lol_dom[j]])
        num_hit_friends = len([hit for hit in lst_dom_friends if hit != []])
        hit_rate = num_hit_friends * 100.0 / num_max_friends
        print("hits: {} = {}".format(lst_dom_friends, hit_rate))
        if hit_rate > 0 and hit_rate < 33:
            num_suspicion = 2
        if hit_rate >= 33 and hit_rate < 66:
            num_suspicion = 1
        else:
            num_suspicion = 0
        scm_i.add_vote(self.str_filter_name, num_suspicion, 4, None, 'from-, return- and reply-domain mismatch')

        return scm_i


if __name__ == '__main__':

    print("This is just for testing - You shoulden't be running this module directly...")
    flt_k = Karma()
    print("test: {}".format(flt_k))
    print("Say: {}".format(flt_k.say_hi()))
    print("db: {}".format(flt_k._debug('Yoo')))