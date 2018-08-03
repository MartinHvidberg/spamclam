#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Cleaning up the Black/White rules files
    - Looking at all .scaddr and .scrule files
    - Sorting the address books
    - Reordering (intelligently) the rules, obeying grouping and headers
    - Checking for redundant rules, in and between, .scaddr and .scrule files
    - Checking for logical conflicts, in and between, .scaddr and .scrule files
    - Checking for logical conflicts between Black and White... """

import os
import logging

import simple_bw

logging.basicConfig(filename='rules_cleaner.log',
                    filemode='w',
                    level=logging.DEBUG,  # DEBUG, INFO
                    format='%(asctime)s %(levelname)7s %(funcName)s : %(message)s')
# %(funcName)s
logger = logging.getLogger('spamclam')


class RulesetWCheck(simple_bw.Ruleset):

    def __init__(self, rule_dir):
        simple_bw.Ruleset.__init__(self, rule_dir)
        #self._current_file = ""

    def raw_insert_rule(self, colour, rul_in):
        rul_in['source_file'] = self._current_file
        simple_bw.Ruleset.raw_insert_rule(self, colour, rul_in)

    def load_file(self, fil_in):
        self._current_file = fil_in
        simple_bw.Ruleset.load_file(self, fil_in)
        self._current_file = ""

def reorder_rules_files(str_home_dir):
    pass


def reorder_address_books(str_home_dir):
    ## Steal everything from addr_book_reorder.py :-)
    pass


def load_files(str_home_dir):
    rus_chk = RulesetWCheck(str_home_dir)
    return rus_chk

def x_load_files(str_home_dir):

    def _scan_for_files(str_hd, dic_r):
        for root, dirs, files in os.walk(str_hd):
            for file in files:
                if file.endswith(".scaddr") or file.endswith(".scrule"):
                    str_fn = os.path.join(root, file)
                    if 'white' in str_fn.lower() or 'black' in str_fn.lower():
                        dic_r['source_files'].append(str_fn)  # Consider saving full path?
        return dic_r

    def _load_all_files(dic_r):
        """ assumes _scan_for_files() have been run before, or more specifically that dic_r[source_files] have been filled """
        for str_fn in dic_r['source_files']:
            los_lines = list()
            dic_r[str_fn] = RulesetWCheck('/home')
            with open(str_fn) as fil_in:
                for line in fil_in:
                    los_lines.append(line)
            if '.scrule' in str_fn:
                print dic_r[str_fn].rules_from_strings(los_lines)
        return dic_r

    dic_rules = dict()  # The overall archive of rules
    dic_rules['source_files'] = list()  # Keep track of the source files
    dic_rules = _scan_for_files(str_home_dir, dic_rules)
    for str_fn in dic_rules['source_files']: print str_fn  # Just for debug...
    dic_rules = _load_all_files(dic_rules)
    return dic_rules


def update_files(dic_rules, str_home_dir):
    pass


def check_redundant_rules(dic_rules):
    pass


def check_logical_conflict(dic_rules):
    pass


def main(str_home_dir):

    dic_rules = load_files(str_home_dir)
    #check_redundant_rules(dic_rules)
    #check_logical_conflict(dic_rules)
    #update_files(dic_rules, str_home_dir) # We need to preserve comments and grouping, so a clean rewrite makes no sense.
    #reorder_rules_files(str_home_dir)
    #reorder_address_books(str_home_dir)


if __name__ == "__main__":

    main('./')
    print "Done..."
