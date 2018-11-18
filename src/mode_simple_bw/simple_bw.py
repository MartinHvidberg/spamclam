#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Simple Black- and Whitelist functionality for spamalyser.py

### Versions  <-- Out of sync with the overall SpamClam versioning...
# 0.2 - initial version of this module
# 0.3 - changing rules fra dic_of_lists to dic_of_dics, to better support child class (RulesetWChecks)
# 0.4 - rewriting rule- and address-file reading, to make it clearer and DRY.

### ToDo
# Make all docstrings reST format
# Sanitise the rule complex, before applying, preferably by calls to ./rule_cleaner module
# Consider xtra syntax where:
#  subject && Ansøg om
#  + subject && i dag
#  + subject && og få dem lynhurtigt
# is replaced by:
#  subject && Ansøg om + i dag + og få dem lynhurtigt
# though it would add + to reserved chars.
"""


import os
import sys
import logging
#import json
import re # for helper function


class Ruleset(object):

    """ Rule-set to be used with Spamalyser.
    A 'rule-set' is a dictionary of (2) dictionaries of 'rules'.
        The only valid rule-keys in this dictionary are 'black' and 'white'.
        There is an additional key called 'num_last_rule', for compatibility with some child classes
    A 'rule' is a list of conditions.
        A 'simple rule' have one condition.
        A 'complex rule' have several conditions.
        There are implicit AND between the conditions in a complex rule.
    A 'condition' is a dictionary. It has entries 'key', 'opr' and 'val'
        'opr' is a string
        'key' and 'val' are lists of strings. In simple cases the lists only has one element.
        in 'packed conditions' the lists can have multiple elements
        There are implicit OR between the elements in a packed condition list.

    In code, a sample rule-set with 4 white and 2 black rules, look like this.
    Notice that rules 3, 4 and 6 are complex rules, i.e. have multiple conditions.
    Notice that rules 1, 2 and 3 hold packed conditions.
    self._data {
    'white': {
        1: [{'key': ['from'], 'opr': '&&', 'val': ['nicesite.com', 'anothernicesite.com']}],
        2: [{'key': ['to', 'cc', 'bcc'], 'opr': '[='}, 'val': ['mail_list_on_Python', 'daily_letter']],
        3: [{'key': ['from'], 'opr': '&&', 'val': ['python.org']},
            {'key': ['subject'], 'opr': '!&', 'val': ['greek', 'dutch']}],
        4: [{'key': ['from'], 'opr': '&&', 'val': ['fsf.org']},
            {'key': ['subject'], 'opr': '!&', 'val': ['python_on_windows']},
            {'key': ['to'], 'opr': '[='}, 'val': ['@mydomain.org']]
        },
    'black': {
        5: [{'key': ['from'], 'opr': '==', 'val': ['marketing101@somewhere.ch']}],
        6: [{'key': ['subject'], 'opr': '&&', 'val': ['Use just a few minutes']},
            {'key': ['subject'], 'opr': '&&', 'val': ['you will not regret it']}]
        }
    'num_last_rule': 6,
    }

    """

    # Some class 'constants'
    VALID_OPR = ('&&', '!&', '==', '!=', '[=', ']=', '[!', ']!')
    VALID_EMAIL_HEADERS = ('subject', 'from', 'body', 'to', 'cc', 'bcc', 'size')
    VALID_RULE_KEYS = ['key', 'opr', 'val']

    def __init__(self, rule_dir):
        logging.debug("class init. Ruleset")
        self._rldr = rule_dir  # Where to look for the rule files
        self._data = {'white': dict(), 'black': dict(), 'num_last_rule': 0}
        self._wob = 'white'  # Default 'white', meaning white overrules black. XXX Consider making it boolean

        self.load_all_rule_files()  # Load all rule- and address files

    ######  Rule-builder ######


    def rules_from_strings(self, los_in):
        """ ! This is still messy, and I want to nice it up. !
        Make a list of 'rule's from a list of raw strings, typically the content of a .scrule file
        Assume all #comments have been removed
        Assume no blank lines
        Assume one (packed) condition-string per line
        Assume some lines starts with +, which indicate it's part of a complex rule, together with the line(s) before.
        :param los_in list: list of strings
        :return: list of rules
        """
        logging.debug("rules_from_strings() begin")
        lst_ret = list()  # initialize a return-list
        if isinstance(los_in, list) and len(los_in) > 0:  # if input is a list
            if all([isinstance(s, str) for s in los_in]):  # if input is list of strings
                lst_in = [[str(raw)] for raw in los_in]  # Wrap each line of text in a list
                if lst_in[0][0][0] != '+':  # if the first line don't start with +
                    # Handle + lines ... This is still bloody ugly! XXX
                    lst_tmp = list()
                    for i in lst_in:
                        if i[0][0] == '+':  # the first letter in the first string, is '+'
                            lst_last = lst_tmp[-1]  # get back the last item we put in lst_tmp
                            lst_tmp = lst_tmp[:-1]  # remove it from the list
                            lst_last.append(i[0].lstrip('+').strip())  # extend it with the + condition, stripping the +
                            lst_tmp.append(lst_last)  # put it back...
                            del lst_last
                        else:
                            lst_tmp.append(i)
                    lst_srules = lst_tmp
                    del lst_tmp, i
                    # We now have a list of lists of strings, each string representing a (packed) condition.
                    for lo_pcon in lst_srules:  # each rule is a list_of_packed-conditions, as strings
                        ##print ".", lo_pcon  # show for debug
                        rule = list()  # variable name 'rule' is used for the next step
                        for pcon in lo_pcon:
                            lst_opr = [opr for opr in self.VALID_OPR if opr in pcon]
                            if len(lst_opr) == 1:  # Check exactely 1 opr
                                str_opr = lst_opr[0]
                                lst_cnd = pcon.split(" {} ".format(str_opr), 1)
                                lst_cnd = [tok.split(',') for tok in lst_cnd]  # conveniently also turns simple conditions into lists
                                # pack it up in a dic. Leaving any further validation to the validator...
                                dic_cnd = dict()
                                dic_cnd['opr'] = str_opr
                                dic_cnd['key'] = [tok.strip() for tok in lst_cnd[0]]
                                dic_cnd['val'] = [tok.strip() for tok in lst_cnd[1]]
                                rule.append(dic_cnd)
                            else:
                                logging.warning("! Condition have either No or Mutiple valid OPR: {}".format(pcon))
                        ##print " ^rule:", rule
                        lst_ret.append(rule)
                    ##print "^^lor_rules:",lst_ret
                else:
                    logging.warning("! The first string should never start with +: {}".format(lst_in[0][0]))
            else:
                logging.warning("! received list containing non-string object: {}".format([str(type(o)) for o in los_in]))
        else:
            logging.warning("! received empty list, or non-list object: {}".format(str(type(los_in))))
        return lst_ret

    def rules_from_listofaddressers(self, los_adr):
        """
        Convert list of addresses into an equivalent list of rules.
        Ignores anything in the string, that is't part of the (first) e-mail address
        :param los_adr: list-of-strings, each string containing an address
        :return: list_of_rules
        """
        lor_ret = list()
        for str_addline in los_adr:
            str_emladd = self.get_email_address_from_string(str_addline)
            if len(str_emladd) > 0:  # Insert email address in ruleset
                logging.debug("e-mail addr: {}".format(str_emladd))
                dic_rul = {'key': ['from'], 'opr': '==', 'val': [str_emladd]}
                rule_a = [dic_rul]  # 'A rule' is a list of dics, so we need to wrap it...
                lor_ret.append(rule_a)
            del str_emladd
        return lor_ret

    def los_to_lor(self, los_in, str_assume):
        """
        Interpret list_of_strings, depending on str_assume, and returning list_of_rules
        :param los list: list of strings
        :param str_assume str: What type of info it's assumed to be
        :return: list -- list of rules
        """
        lor_ret = list()
        if str_assume == 'rules':
            lor_ret = self.rules_from_strings(los_in)
        elif str_assume == 'addresses':
            lor_ret = self.rules_from_listofaddressers(los_in)
        else:
            pass  # XXX Consider making a qualified guess, based on contents, rather than returning empty...
        return lor_ret  # Return empty list of rules, if str_assume is not recognised. XXX Consider raising warning

    def raw_insert_rule(self, colour, rul_in):
        """
        The raw insert just push the rule into the rule-store, assuming you have made sure it's valid.
        This function is overloaded in child classes, e.g. RulesetWCheck() to support different rule-store format.
        :param colour str: 'black' or 'white'
        :param rul_in list: A rule - that you vouch for
        :return: None, there is no error handling anyway...
        """
        num_next_rule = self._data['num_last_rule'] + 1
        self._data[colour][num_next_rule] = rul_in
        self._data['num_last_rule'] = num_next_rule
        return None

    def lor_validator(self, lor):
        """ Looks through a list-of-rules, returning the list with invalid rules removed """
        #XXX code missing here.
        return lor

    def lor_inserter(self, str_colour, lor):
        # call validator
        for rul_in in lor:
            self.raw_insert_rule(str_colour, rul_in)
        return None

    def load_file(self, fil_in):
        """ Opens a single file (rule-, address-, or other) and return it as cleaned list_of_strings """
        with open(self._rldr + fil_in) as f:
            lst_lines = f.readlines()
        lst_lines = [conf.split("#")[0].strip() for conf in lst_lines]  # Get rid of comments
        lst_lines = [conf for conf in lst_lines if conf != '']  # Get rid of empty lines
        return lst_lines

    def load_a_rule_file(self, str_colour, str_fn):
        """
        Load the specified rule file (rule or address) to the rules collection
        - read the file with load_file(), to get a list_of_strings
        - call los_to_lor(), setting str_assume= based on str_fn, to get a list_of_rules
        - call lor_validator(), to filter away invalid rules
        - insert the validated lor into collection of colour str_colour
        :param str_colour str: 'black' or 'white'
        :param str_fn: name of the file to be loaded. Just the file name, assuming it's in self._rldr
        :return: None
        """
        logging.debug(" func. load_a_rule_file: {}, {}".format(str_colour, str_fn))
        los_in = self.load_file(str_fn)
        if '.scrule' in str_fn:
            str_assume = 'rules'
        elif 'scaddr' in str_fn:
            str_assume = 'addresses'
        else:
            str_assume = ""
        lor_in = self.los_to_lor(los_in, str_assume)
        lor_va = self.lor_validator(lor_in)
        self.lor_inserter(str_colour, lor_va)
        ##print "\n{}".format(self._data)
        return None

    def load_all_rule_files(self):
        """
        Load all rule files (rule and address) from default dir.
        - walk the dir
        - send all reasonable files to load_a_rule_file()
        :return: None
        """
        logging.debug(" func. load_all_rule_files in: {}".format(self._rldr))
        for fil_in in os.listdir(self._rldr):
            if fil_in.endswith(".scrule") or fil_in.endswith(".scaddr"):
                logging.debug(".scxxxx file: {}".format(fil_in))
                if "white" in fil_in.lower():
                    str_colour = 'white'
                elif "black" in fil_in.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    str_report = "!!! file-name: {} contained neither 'white' nor 'black'... I'm confused.".format(fil_in)
                    print(str_report)
                    logging.debug(str_report)
                    continue
                if str_colour != "":
                    self.load_a_rule_file(str_colour, fil_in)
                    logging.info("Loaded {} rule file: {}".format(str_colour, fil_in))
        return None

    def get_email_address_from_string(self,str_in):
        if '@' in str_in:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str_in)
            str_return = match.group(0).lower()
            return str_return
        else:
            return ""

    def list_rulenumbers_of_colour(self, str_colour):
        """ return a sorted list of numbers, pointing to rules of colour str_colour """
        return sorted(self._data[str_colour].keys())

    def get_number_of_rules(self):
        """ return the total number of rules in black and white
            actually counting them, rather than just quoting self._data['num_last_rule'] """
        return sum(len(j) for j in [i for i in [list(self._data[col].keys()) for col in ['white', 'black']]])

    def get_rule_by_number(self, num_rule):
        for str_colour in ('white', 'black'):
            for num_crule in list(self._data[str_colour].keys()):
                if num_crule == num_rule:
                    return self._data[str_colour][num_rule]
        return None  # If nothing found.

    def show_rules_backdoor(self):
        """ Show the rules """
        logging.debug(" func. show_rules_backdoor()")
        print("\nPrint the rules, via the back door...")
        for key_colour in ('white', 'black'):
            for num_col in self.list_rulenumbers_of_colour(key_colour):
                print("\t{} # {} = {}".format(key_colour, num_col, self.get_rule_by_number(num_col)))
        return None

    def show_rules_pp(self):  # XXX This needs some working on, to be real pretty...
        """ Show the rules - pretty print """
        logging.debug(" func. show_rules_pp()")
        ##print "\nPretty Print the rules..."
        los_pp = list()
        if self._wob == "white":
            los_pp.append("*** : White over black")
        elif self._wob == "black":
            los_pp.append("*** : Black over white")
        else:
            los_pp.append("*** : WoB is a mess...: {}".format(self._wob))
        los_rules = list()
        for key_colour in ('white', 'black'):
            for num_col in self.list_rulenumbers_of_colour(key_colour):
                los_pp.append("*** : {}".format(key_colour))
                for num_rule in self.list_rulenumbers_of_colour(key_colour):
                    lst_rulelines_a = self.get_rule_by_number(num_rule)
                    if len(lst_rulelines_a) > 0:
                        rul = lst_rulelines_a[0]
                        los_rules.append("\t[{}] rule: {} {} {}".format(num_rule, rul['key'], rul['opr'], rul['val']))
                    if len(lst_rulelines_a) > 1:
                        for rul in lst_rulelines_a[1:]:
                            los_rules.append("\t[{}]  && : {} {} {}".format(num_rule, rul['key'], rul['opr'], rul['val']))
                los_pp.extend(los_rules)
        for str_pp in los_pp:
            print(str_pp)
        return None


    ######  Spalyse ######

    def statement_check(self, salstmn, salmail):
        """ Checks the salmail against a single statement
            EBNF: salstmn = (key, opr, val) """
        key, opr, val = salstmn
        emlval = salmail.get(key)
        if opr == '&&':  # contains
            bol_hit = val in emlval
        elif opr == '!&':  # do_not_contain
            bol_hit = not val in emlval
        elif opr == '==':  # is
            bol_hit = val == emlval
        elif opr == '!=':  # is_not
            bol_hit = val != emlval
        elif opr == '[=':  # begins_with
            bol_hit = val == emlval[:len(val)]
        elif opr == ']=':  # ends_with
            bol_hit = val == emlval[-len(val):]
        elif opr == '[!':  # not_begins_with
            bol_hit = not val == emlval[:len(val)]
        elif opr == ']!':  # not_ends_with
            bol_hit = not val == emlval[-len(val):]
        else:
            bol_hit = False
            print("Error: Unknown operator: " + opr)
        return  (bol_hit, salstmn)  # EBNF: ( True|False, The_statement )

    def condtion_check(self, salcond, salmail):
        """ Checks the salmail against a single condition
            EBNF: salcond = ((key, {key}), opr, (val, {val}))
            e.g.: {'key':['to','cc','bcc'],'opr':'[=','val':['mail_list_on_Python','daily_letter_from_your_groser']}
                  returns ( True|False, ({win_stnm}) ) """
        # input check
        # if not isinstance(salcond, dict):
        #     str_warning = "sal-condition is not a dict())".format(salcond)
        #     logging.warning(str_warning)
        #     return (False, (str_warning))
        # if not all(['key' in salcond.keys(), 'opr' in salcond.keys(), 'val' in salcond.keys()]):
        #     str_warning = "sal-condition lacks one, or more, entries ('key', 'opr' or 'val'))".format(salcond)
        #     logging.warning(str_warning)
        #     return (False, (str_warning))
        # do check
        dic_ret = {'lst_bool': list(), 'lst_stmn': list()}
        for key in salcond['key']:
            if key in salmail:
                for opr in [salcond['opr']]:  # prepared for future list_of_opr
                    for val in salcond['val']:
                        bol_spam, tup_stmn = self.statement_check((key, opr, val), salmail)
                        if bol_spam:
                            dic_ret['lst_bool'].append(bol_spam)
                            dic_ret['lst_stmn'].append(tup_stmn)
        logging.debug("    func. condit. {} {} {} = {}".format(salcond['key'], salcond['opr'], salcond['val'], any(dic_ret['lst_bool'])))
        return (any(dic_ret['lst_bool']), dic_ret['lst_stmn'])

    def rule_check(self, salrule, salmail):
        """ Checks the salmail agains a single rule
            EBNF: salrule = (salcond, {salcond})
            e.g.:
[{'key':['from'],'opr':'&&','val':['python.org']},{'key':['subject'],'opr':'!&','val':['python_in_greek','python_on_windows']}] """
        dic_ret = {'lst_bool': list(), 'lst_stmn': list()}
        for salcond in salrule:
            lst_cond_res = self.condtion_check(salcond, salmail)
            dic_ret['lst_bool'].append(lst_cond_res[0])
            dic_ret['lst_stmn'].append(lst_cond_res[1])
        bol_rule = all(dic_ret['lst_bool'])
        logging.debug("   func. rule. = {}".format(bol_rule))
        return  [bol_rule, dic_ret['lst_stmn']]  # EBNF: salrule_res = ( True|False, ({win_stnm}))

    def spamalyse(self, salmail, wob_in):
        """ Checks an email agains entire rule-set, i.e. self
            EBNF: input: rule-set = { 'white': [<rule>]; 'black':[<rule>] }
                  returns: ( True|False, ({win_stnm})) """
        dic_white_and_black = dict()
        for str_colour in ('white', 'black'):
            dic_white_and_black[str_colour] = {'lst_bool': list(), 'lst_stmn': list()}
            for num_rule in self.list_rulenumbers_of_colour(str_colour):
                salrule = self.get_rule_by_number(num_rule)
                rul_ret = self.rule_check(salrule, salmail)  # Check every rule in the rule-set
                if rul_ret[0]:
                    dic_white_and_black[str_colour]['lst_bool'].append(rul_ret[0])
                    dic_white_and_black[str_colour]['lst_stmn'].append(rul_ret[1])
                else:
                    dic_white_and_black[str_colour]['lst_bool'].append(False)
        # Summerize the results
        bol_white = any([itm for itm in dic_white_and_black['white']['lst_bool']])
        bol_black = any([itm for itm in dic_white_and_black['black']['lst_bool']])
        lst_w_stm = [itm for itm in dic_white_and_black['white']['lst_stmn']]
        lst_b_stm = [itm for itm in dic_white_and_black['black']['lst_stmn']]
        # construck sal_res as {'spam': boolean(), 'mode': str(), tone: str(), 'votw'. list(), 'votb': list()}
        # wob decision tree
        if wob_in:  # i.e. wob is True
            if bol_white:  # wob, white hit exists = Not spam
                bol_spam = False
                lst_kill = lst_w_stm  # the killer arguments
                if bol_black:  # there are also black hits
                    str_tone = 'grey'
                else:
                    str_tone = 'white'
            elif bol_black:  # wob, only black hit exists = Spam
                bol_spam = True
                lst_kill = lst_b_stm  # the killer arguments
                str_tone = 'black'
            else:  # wob, neither white not black hits = Not spam
                bol_spam = False
                lst_kill = []  # the killer arguments
                str_tone = 'clear'
        else:  # i.e. wob is False
            if bol_black:  # not wob, black hit exists = Spam
                bol_spam = True
                lst_kill = lst_b_stm  # the killer arguments
                if bol_white:  # there are also white hits
                    str_tone = 'grey'
                else:
                    str_tone = 'black'
            elif bol_white:  # not wob, only white hit exists = Not spam
                bol_spam = False
                lst_kill = lst_w_stm  # the killer arguments
                str_tone = 'white'
            else:  # not wob, neither white not black hits = Not spam
                bol_spam = False
                lst_kill = []  # the killer arguments
                str_tone = 'clear'
        sal_ret = {'spam': bol_spam, 'mode': 'simple', 'tone': str_tone, 'kill': lst_kill, 'votw': lst_w_stm, 'votb': lst_b_stm}
        logging.debug("  func. spamalyse. wob: {}; white: {}; black: {} = Spam: {}".format(wob_in, bol_white, bol_black, sal_ret['spam']))
        return sal_ret


    # helper functions
# End class - Ruleset

# Historic maerial


    def xx_add_rule(self, colour, rul_in):
        """
        Receives, validates and (if valid) adds the 'rule' to the main rule-set.
        :param colour str: 'black' or 'white'
        :param rul_in list: A 'rule', i.e. a list of conditions
        :return: TBD
        """

        def rule_check_packeage(colour, rul_pk):
            if colour in ['white', 'black']:  # Rule must be white or black
                if isinstance(rul_pk, list):  # a 'rule'
                    for rule in rul_pk:
                        if isinstance(rule, dict):  # a 'condition'
                            # {'key': ['from'], 'opr': '==', 'val': ['someone@work.com']}
                            if all(key in list(rule.keys()) for key in self.VALID_RULE_KEYS):
                                logging.debug("add_rule() okayrule: {}, {}".format(colour, rule))
                                pass  # All seems okay, ready to be exploded
                            else:
                                logging.warning("! address rule rul_in is missing one or more of the keys: {}".format(str(lst_expected_keys)))
                                return False
                        else:
                            logging.warning("! address rule rul_in. 'condition' is not type dict")
                            return False
                else:
                    logging.warning("! address rule rul_in. 'rule' is not type list")
                    return False
            else:
                logging.warning("! illegal colour in added rule: {}".format(str(colour)))
                return False
            return True

        def rule_check_unpacked(lst_rulelines):
            for rule in lst_rulelines:
                # 'key'
                if all(key in self.VALID_EMAIL_HEADERS for key in rule['key']):
                    pass
                else:
                    logging.warning("! address rule rul_pk has a bad 'key': {}".format(str(rule)))
                    return False
                    # XXX add check that key is in [,,,]
                    # XXX add check that dic[key] is list of valid e-mail header fields
                    # XXX add check that opr is in [,,,]
                    # XXX add check that dic[val] is list of valid text strings
            return True

        logging.debug("add_rule() received: {}, {}".format(colour, rul_in))
        ##logging.debug("rul_in0: {}".format(json.dumps(rul_in)))
        # validate and explode
        if rule_check_packeage(colour, rul_in):
            logging.debug("add_rule() okay pak: {}, {}".format(colour, rul_in))
            self.raw_insert_rule(colour, rul_in)
        else:
            logging.warning("! add_rule: rule_check_packeage() returned False")
        return None

    def xx_load_rulefile(self, str_colour, fil_in):
        """ Open and read a single rule file """
        lst_rulelines = self.load_file(fil_in)
        # Converting text strings to rule-set object
        lor_in = self.rules_from_strings(lst_rulelines)
        # We need to actually add the rule :-)
        for rule_a in lor_in:
            self.add_rule(str_colour, rule_a)
        return None

    def xx_load_rulesfiles(self):
        """ Find and load all .scrule files in the rule_dir """
        logging.debug(" func. load_rulesfiles in: {}".format(self._rldr))
        for fil_in in os.listdir(self._rldr):
            if fil_in.endswith(".scrule"):
                logging.debug(".scrule file: {}".format(fil_in))
                if "white" in fil_in.lower():
                    str_colour = 'white'
                elif "black" in fil_in.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    str_report = "!!! file name contained neither 'white' nor 'black'... I'm confused."
                    print(str_report)
                    logging.debug(str_report)
                    continue
                if str_colour != "":
                    self.load_rulefile(str_colour, fil_in)
                    logging.info("Loaded rule file {}: {}".format(str_colour, fil_in))
        return None

    def xx_load_addressbook(self, str_colour, fil_in):
        lst_addlines = self.load_file(fil_in)
        for add_line in lst_addlines:
            str_emladd = self.get_email_address_from_string(add_line)
            if len(str_emladd) > 0:  # Insert email address in ruleset
                logging.debug("{} << addr {}".format(str_colour, str_emladd))
                dic_rul = {'key': ['from'], 'opr': '==', 'val': [str_emladd]}
                rule_a = [dic_rul]  # 'A rule' is a list of dics, so we need to wrap it...
                self.add_rule(str_colour, rule_a)
            del str_emladd
        return None

    def xx_load_addressbooks(self):
        """ Find and load all address (.scaddr) files in the rule_dir """
        logging.debug(" func. load_addressbooks.")
        # Find addressbook files
        for fil_in in os.listdir(self._rldr):
            if fil_in.endswith(".scaddr"):
                # Crunch the addressbook file
                if "white" in fil_in.lower():
                    str_colour = 'white'
                elif "black" in fil_in.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    print("!!! file name: {} contained neither 'white' nor 'black'... I'm confused.".format(fil_in))
                    continue
                self.load_addressbook(str_colour, fil_in)
                logging.info("Loaded addressbook {}: {}".format(str_colour, fil_in))
        return None
