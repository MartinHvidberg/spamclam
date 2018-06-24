#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Cleaning up the Black/White rules files
    - Looking at all .scaddr and .scrule files
    - Sorting the address books
    - Reordering (intelligently) the rules obeying grouping and headers
    - Checking for redundant rules, in and between, .scaddr and .scrule files
    - Checking for logical conflicts, in and between, .scaddr and .scrule files
    - Checking for logical conflicts between Black and White... """

import simple_bw


def reorder_rules_files(str_home_dir):
    pass


def reorder_address_books(str_home_dir):
    pass


def load_files(str_home_dir):
    return dict()


def save_files(dic_rules, str_home_dir):
    pass


def check_redundant_rules(dic_rules):
    pass


def check_logical_conflict(dic_rules):
    pass


def main(str_home_dir):

    dic_rules = load_files(str_home_dir)
    check_redundant_rules(dic_rules)
    check_logical_conflict(dic_rules)
    save_files(dic_rules, str_home_dir)
    reorder_rules_files(str_home_dir)
    reorder_address_books(str_home_dir)


if __name__ == "__main__":

    main('./')
    print "Done..."
