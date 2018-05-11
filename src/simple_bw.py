
"""
Simple Black and White functionality for spamalyser.
"""

### Versions
# 0.2 - initial version of this module

### To do
# Sanitise the rule complex, before applying

import os
import logging
import json
import re # for helper function


class Ruleset(object):

    """ Rule-set to be used with Spamalyser.
    A 'rule-set' is a dictionary of (2) lists of 'rules'.
        The only valid keys in this dictionary are 'black' and 'white'.
    A 'rule' is a lists of conditions.
        A 'simple rule' have one condition.
        A 'complex rule' have several conditions.
        There are implicit AND between the conditions in a complex rule.
    A 'condition' is a dictionary. It has entries 'key', 'opr' and 'val'
        'opr' is a string
        'key' and 'val' are lists. In simple cases the lists only has one element each.
        in 'packed conditions' the lists can have multiple elements
        There are implicit OR between the elements in a packed condition list.

    In code it all looks like this:
    _data {'white':
            [
                [{[from] == ['dave@mygrocer.com']}],
                [{[subject] && ['spamalyser']}],
                [{[from] ]= ['python.org', 'python.net']}, {[subject] !& ['python in greek']}]
            ],
           'black:
            [
                [{[from] == ['spammer_dude@highprice.com']}],
                [{[to] !& ['myemail@home.net']}],
                [{[from] ]= [microsoft.com]}, {[subject] !& ['open source', 'free license']}]
            ]
          }
    """

    # Some class 'constants'
    VALID_OPR = ('&&', '!&', '==', '!=', '[=', ']=', '[!', ']!')
    VALID_EMAIL_HEADERS = ('subject', 'from', 'body', 'to', 'cc', 'bcc', 'size')
    VALID_RULE_KEYS = ['key', 'opr', 'val']

    def __init__(self, rule_dir):
        logging.debug("class init. Ruleset")
        self._rldr = rule_dir  # Where to look for the rule files
        self._data = {'white': list(), 'black': list()}
        self._wob = 'white'  # Default 'white', meaning white overrules black.

        self.load_rulesfiles()  # Load any rule files
        self.load_addressbooks()  # Load any address books

    ######  Rule-builder ######

    def rules_from_strings(self, los_raw):
        """ Make a list of 'rule's from a list of raw strings, typically the content of a .scrule file """
        lst_ret = list()
        # assume one (complex) condition-string per line, except lines starting with +
        lst_conds = [[str(raw)] for raw in los_raw]
        # XXX This is ugly - make it nicer...
        num_iter = len(lst_conds)
        for cnt in range(num_iter):
            for num_con in range(len(lst_conds)):
                if lst_conds[num_con][0][0] == '+':
                    lst_conds[num_con-1].append(lst_conds[num_con][0].lstrip('+').strip())
                    del lst_conds[num_con]
                    continue
        ##for conds in lst_conds:
        ##    print " cond: {}".format(conds)
        # list of strings 2 list of rules
        for lo_conds in lst_conds:
            rule = list()
            for conds in lo_conds:
                if any(opr in conds for opr in self.VALID_OPR):
                    # Check only 1 opr in condition-string
                    num_opr = 0
                    for str_valopr in self.VALID_OPR:
                        if " {} ".format(str_valopr) in conds:
                            num_opr += 1
                            lst_cnd = conds.split(" {} ".format(str_valopr), 1)
                            lst_cnd = [tok.split(',') for tok in lst_cnd] # conveniently also turns simple conditions into lists
                            dic_cnd = dict()
                            dic_cnd['opr'] = str_valopr
                            dic_cnd['key'] = lst_cnd[0]
                            dic_cnd['val'] = lst_cnd[1]
                    if num_opr == 1:
                        # strip all strings - XXX this is ugly, try fix that...
                        for keyval in ('key', 'val'):
                            dic_cnd[keyval] = [tok.strip() for tok in dic_cnd[keyval]]
                        # fanally add the condition
                        ##print "good:", conds, str(dic_cnd)
                        rule.append(dic_cnd)
                        ##print " ^rule:", rule
                    else:
                        logging.warning("! Condition have more that one OPR: {}".format(conds))
                else:
                    logging.warning("! Condition have no valid OPR: {}".format(conds))
            lst_ret.append(rule)
        ##print "^^lor_rules:",lst_ret
        return lst_ret

    def load_rulesfiles(self):
        """ Find and load all .scrule files in the rule_dir """
        logging.debug("func. load_rulesfiles.")
        for fil_cnf in os.listdir(self._rldr):
            if fil_cnf.endswith(".scrule"):
                logging.debug(".scrule file: {}".format(fil_cnf))
                if "white" in fil_cnf.lower():
                    str_colour = 'white'
                elif "black" in fil_cnf.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    str_report = "!!! file name contained neither 'white' nor 'black'... I'm confused."
                    print str_report
                    logging.debug(str_report)
                    continue
                with open(self._rldr+fil_cnf) as f:
                    lst_rulelines = f.readlines()
                logging.debug("lst_cnf1: {}".format(lst_rulelines))
                lst_rulelines = [conf.split("#")[0].strip() for conf in lst_rulelines] # Get rid of comments
                lst_rulelines = [conf for conf in lst_rulelines if conf != ''] # Get rid of empty lines
                logging.debug("lst_cnf2: {}".format(lst_rulelines))

                # Converting text strings to rule-set object
                lor_in = self.rules_from_strings(lst_rulelines)
                logging.debug("lst_cnf3: {}".format(lor_in))

                # We need to actually add the rule :-)
                for rule_a in lor_in:
                    self.add_rule(str_colour, rule_a)
                logging.info("Loaded rule file {}: {}".format(str_colour, fil_cnf))
        return

    def load_addressbooks(self):
        """ Find and load all address (.scaddr) files in the rule_dir """
        logging.debug("func. load_addressbooks.")
        # Find addressbook files
        for fil_cnf in os.listdir(self._rldr):
            if fil_cnf.endswith(".scaddr"):
                # Crunch the addressbook file
                if "white" in fil_cnf.lower():
                    str_colour = 'white'
                elif "black" in fil_cnf.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    print "!!! file name: {} contained neither 'white' nor 'black'... I'm confused.".format(fil_cnf)
                    continue
                with open(self._rldr+fil_cnf, 'r') as f:
                    for line in f:
                        str_tmp = line.split("#")[0] # Get rid of comments
                        str_emladd = self.get_email_address_from_string(str_tmp)
                        if len(str_emladd) > 0: # Insert email address in ruleset
                            logging.debug("{} << addr {}".format(str_colour, str_emladd))
                            dic_rul = {'key': ['from'], 'opr': '==', 'val': [str_emladd]}
                            rule_a = [dic_rul] # 'A rule' is a list of dics, so we need to wrap it...
                            self.add_rule(str_colour, rule_a)
                        del str_emladd, str_tmp
                logging.info("Loaded addressbook {}: {}".format(str_colour, fil_cnf))
        return

    def add_rule(self, colour, rul_in):
        """
        Receives, validates and (if valid) adds the 'rule' to the main rule-set.
        :param colour: 'black' or 'white'
        :param rul_in: A 'rule', i.e. a list of conditions
        :return: TBD
        """

        def rule_check_packeage(colour, rul_pk):
            if colour in ['white', 'black']:  # Rule must be white or black
                if isinstance(rul_pk, list):  # a 'rule'
                    for rule in rul_pk:
                        if isinstance(rule, dict):  # a 'condition'
                            # {'key': ['from'], 'opr': '==', 'val': ['someone@work.com']}
                            if all(key in rule.keys() for key in self.VALID_RULE_KEYS):
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

        def xxx_unpack_conditions(rul_pk):
            ### Unpacking dosn't make sense, as it would create lists with mixed AND/OR relations between elements.
            """ Unpack all packed condition, in a 'rule', into several unpacked conditions,
                eliminating lists in fields 'key' and 'val'.
                The unpacker makes no checks, the result should be checked with the appropriate function.
            """
            lst_simple_cnd = list()
            return lst_simple_cnd

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
            self._data[colour].append(rul_in)
        else:
            logging.warning("! add_rule: rule_check_packeage() returned False")
        return

    def show_rules_backdoor(self):
        """ Show the rules """
        logging.debug("func. show_rules_backdoor()")
        ##print "\nPrint the rules, via the back door..."
        for key_colour in sorted(self._data.keys()):
            itm_colour = self._data[key_colour]
            print "\nColour: {} ({})".format(key_colour, str(len(itm_colour)))
            for lst_rule_a in itm_colour:
                print "\t{}".format(str(type(lst_rule_a)))
                if isinstance(lst_rule_a, list):
                    for itm in lst_rule_a:
                        print "\t\t{}".format(str(itm))
                else:
                    print "\t\t{}".format(str(lst_rule_a))
        return

    def show_rules_pp(self):
        """ Show the rules - pretty print """
        logging.debug("func. show_rules_pp()")
        ##print "\nPretty Print the rules..."
        los_pp = list()
        if self._wob == "white":
            los_pp.append("*** : White over black")
        elif self._wob == "black":
            los_pp.append("*** : Black over white")
        else:
            los_pp.append("*** : WoB is a mess...: {}".format(self._wob))
        for key_colour in sorted(self._data.keys()):
            itm_colour = self._data[key_colour]
            los_pp.append("*** : {}".format(key_colour))
            los_rules = list()
            for lst_rulelines_a in itm_colour:
                if len(lst_rulelines_a) > 0:
                    rul = lst_rulelines_a[0]
                    los_rules.append("rule: {} {} {}".format(rul['key'], rul['opr'], rul['val']))
                if len(lst_rulelines_a) > 1:
                    for rul in lst_rulelines_a[1:]:
                        los_rules.append(" && : {} {} {}".format(rul['key'], rul['opr'], rul['val']))
            ##los_rules.sort() messing up the rule, && conections
            los_pp.extend(los_rules)
        for str_pp in los_pp:
            print str_pp


    ######  Spalyse ######

    def statement_check(self, salstmn, salmail):
        """ Checks the salmail against a single statement
            EBNF: salstmn = (key, opr, val) """

        return  # EBNF: True|False

    def condtion_check(self, salcond, salmail):
        """ Checks the salmail against a single condition
            EBNF: salcond = ((key, {key}), opr, (val, {val})) """

        return  # EBNF: salcond_res = ( True|False, ({win_stnm}))

    def rule_check(self, salrule, salmail):
        """ Checks the salmail agains a single rule
            EBNF: salrule = (salcond, {salcond}) """

        return  (True, [salrule]) # EBNF: salrule_res = ( True|False, ({win_stnm}))

    def spamalyse(self, salmail, wob_in):
        """ Checks an email agains entire rule-set, i.e. self
            EBNF: input: rule-set = { 'white': [<rule>]; 'black':[<rule>] }
                  returns: ( True|False, ({win_stnm})) """
        """
{
    'white': [
        [
            {'key': ['from'],
             'opr': '&&',
             'val': ['nicesite.com', 'anothernicesite.com']
             }
        ],
        [
            {
                'key': ['to', 'cc', 'bcc'],
                'opr': '[=',
                'val': ['mail_list_on_Python', 'daily_letter_from_your_groser'],
            }
        ],
        [
            {'val': ['python.org'],
             'key': ['from'],
             'opr': '&&'
             },
            {'val': ['python_in_greek', 'python_on_windows'],
             'key': ['subject'],
             'opr': '!&'
             }
        ],
    ],
    'black': [
        [
            {'val': ['Vi ringede til dig', 'men du tog den ikke'],
             'key': ['subject'],
             'opr': '&&'}
        ],
        [
            {'val': ['no-reply@euroinvestor.com'],
             'opr': '==',
             'key': ['from']}
        ]
    ]
}"""
        
        dic_white_and_black = dict()
        for str_colour in ('white', 'black'):
            dic_white_and_black[str_colour] = {'lst_bool': list(), 'lst_stmn': list()}
            for salrule in self._data[str_colour]:
                rul_ret = self.rule_check(salrule, salmail)  # Check every rule in the rule-set
                if rul_ret[0]:
                    dic_white_and_black[str_colour]['lst_bool'].append(rul_ret[0])
                    dic_white_and_black[str_colour]['lst_stmn'].append(rul_ret[1])
                else:
                    dic_white_and_black[str_colour]['lst_bool'].append(False)
        bol_white = any([itm for itm in dic_white_and_black['white']['lst_bool']])
        bol_black = any([itm for itm in dic_white_and_black['black']['lst_bool']])
        lst_w_stm = [itm for itm in dic_white_and_black['white']['lst_stmn']]
        lst_b_stm = [itm for itm in dic_white_and_black['black']['lst_stmn']]
        if wob_in:  # i.e. wob is True
            if bol_white:
                obj_ret = (False, lst_w_stm)  # wob, white hit exists = Not spam
            elif bol_black:  # wob is false
                obj_ret = (True, lst_b_stm)  # wob, only black hit exists = Spam
            else:
                obj_ret = (False, [])  # wob, neither white not black hits = Not spam
        else:  # i.e. wob is False
            if bol_black:
                obj_ret = (True, lst_b_stm)  # not wob, black hit exists = Spam
            elif bol_white:  # wob is false
                obj_ret = (False, lst_w_stm)  # not wob, only white hit exists = Not spam
            else:
                obj_ret = (False, [])  # not wob, neither white not black hits = Not spam



    # helper functions

    def get_email_address_from_string(self,str_in):
        if '@' in str_in:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str_in)
            str_return = match.group(0).lower()
            return str_return
        else:
            return ""


# End class - Ruleset
