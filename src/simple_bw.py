
"""
Simple Black and White functionality for spamalyser.
"""

### Versions
# 0.2 - initial version of this module

### To do
# Address book 2 white/black lists
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


    def __init__(self, conf_dir):
        logging.debug("class init. Ruleset")
        self._cnfd = conf_dir  # Where to look for the .conf files
        self._data = {'white': list(), 'black': list()}
        self._rank = 'white'  # Default 'white', meaning white overrules black.


    def load_rulesfiles(self):
        """ Find and load all .scrule files in the conf_dir """
        logging.debug("func. load_rulesfiles.")
        for fil_cnf in os.listdir(self._cnfd):
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
                with open(self._cnfd+fil_cnf) as f:
                    lst_conf = f.readlines()
                logging.debug("lst_cnf1: {}".format(lst_conf))
                lst_conf = [conf.split("#")[0].strip() for conf in lst_conf] # Get rid of comments
                lst_conf = [conf for conf in lst_conf if conf != ''] # Get rid of empty lines
                logging.debug("lst_cnf2: {}".format(lst_conf))
                # XXX we need to actually add the rule :-)
        return


    def load_addressbooks(self):
        """ Find and load all address (.scaddr) files in the conf_dir """
        logging.debug(" func. load_addressbooks.")
        # Find addressbook files
        for fil_cnf in os.listdir(self._cnfd):
            if fil_cnf.endswith(".scaddr"):
                # Crunch the addressbook file
                if "white" in fil_cnf.lower():
                    str_colour = 'white'
                elif "black" in fil_cnf.lower():
                    str_colour = "black"
                else:
                    str_colour = ""
                    print "!!! file name contained neither 'white' nor 'black'... I'm confused."
                    continue
                logging.info("Addressbook {}: {}".format(str_colour, fil_cnf))
                with open(self._cnfd+fil_cnf, 'r') as f:
                    for line in f:
                        str_tmp = line.split("#")[0] # Get rid of comments
                        str_emladd = self.get_email_address_from_string(str_tmp)
                        if len(str_emladd) > 0: # Insert email address in ruleset
                            logging.debug("{} <addr {}".format(str_colour, str_emladd))
                            dic_rul = {'key': ['from'], 'opr': '==', 'val': [str_emladd]}
                            rule_a = [dic_rul] # 'A rule' is a list dics, so we need to wrap it...
                            self.add_rule(str_colour, rule_a)
                        del str_emladd, str_tmp
        return


    def add_rule(self, colour, rul_in):
        """
        Receives, validates and (if valid) adds the 'rule' to the main rule-set.
        :param colour: 'black' or 'white'
        :param rul_in: A 'rule'
        :return: TBD
        """

        def rule_check_packeage(colour, rul_pk):
            if colour in ['white', 'black']:  # Rule must be white or black
                if isinstance(rul_pk, list):  # a 'rule'
                    for rule in rul_pk:
                        if isinstance(rule, dict):  # a 'condition'
                            # {'key': ['from'], 'opr': '==', 'val': ['someone@work.com']}
                            if all(key in rule.keys() for key in ['key', 'opr', 'val']):
                                logging.debug(" add_rule() (packed): {}, {}".format(colour, rule))
                                pass  # All seems okay, ready to be exploded
                            else:
                                logging.warning("address rule rul_in is missing one or more of the keys: {}".format(str(lst_expected_keys)))
                                return False
                        else:
                            logging.warning("address rule rul_in. 'condition' is not type dict")
                            return False
                else:
                    logging.warning("address rule rul_in. 'rule' is not type list")
                    return False
            else:
                logging.warning("illegal colour in added rule: {}".format(str(colour)))
                return False
            return True

        def unpack_conditions(rul_pk):
            """ Unpack all packed condition, in a 'rule', into several unpacked conditions,
                eliminating lists in fields 'key' and 'val'.
                The unpacker makes no checks, the result should be checked with the appropriate function.
            """
            lst_singlekey_conds = list()
            logging.debug("rul_pk1: {}".format(json.dumps(rul_pk)))
            for cond in rul_pk:
                if len(cond['key']) > 1:
                    for key_a in cond['key']:
                        lst_singlekey_conds.append({'key': key_a, 'opr': cond['opr'], 'val': cond['val']})
                else:
                    lst_singlekey_conds = rul_pk
            logging.debug("rul_pk2: {}".format(json.dumps(lst_singlekey_conds)))
            for cond in lst_singlekey_conds:
                if len(cond['val']) > 1:
                    lst_singleval_conds = list()
                    for val_a in cond['val']:
                        lst_singleval_conds.append({'key': cond['key'],'opr': cond['opr'], 'val': val_a})
                else:
                    lst_singleval_conds = lst_singlekey_conds
            logging.debug("rul_pk3: {}".format(json.dumps(lst_singleval_conds)))
            return lst_singleval_conds

        def rule_check_unpacked(lst_rules):
            for rule in lst_rules:
                # 'key'
                if all(key in ['subject', 'from', 'body', 'to', 'cc', 'bcc', 'size'] for key in
                       rule['key']):
                    pass
                else:
                    logging.warning("address rule rul_pk has a bad 'key': {}".format(str(rule)))
                    return False
                    # XXX add check that key is in [,,,]
                    # XXX add check that dic[key] is list of valid e-mail header fields
                    # XXX add check that opr is in [,,,]
                    # XXX add check that dic[val] is list of valid text strings
            return True

        logging.debug(" add_rule() received: {}, {}".format(colour, rul_in))
        logging.debug("rul_in0: {}".format(json.dumps(rul_in)))
        # validate and explode
        if rule_check_packeage(colour, rul_in):
            rul_a = unpack_conditions(rul_in)
            if rule_check_unpacked(rul_a):
                # check if exist
                #     XXX add some check here...
                # add
                self._data[colour].append(rul_a)
            else:
                logging.warning("add_rule: rule_check_unpacked() returned False")
        else:
            logging.warning("add_rule: rule_check_packeage() returned False")
        return


    def show_rules_backdoor(self):
        """ Show the rules """
        logging.debug(" func. show_rules.")
        print "\n * Pritty print the rules, via the back door..."
        for key_colour in sorted(self._data.keys()):
            itm_colour = self._data[key_colour]
            print "\n + Colour: {} ({})".format(key_colour, str(len(itm_colour)))
            for lst_rule_a in itm_colour:
                print "     + type: {}\n\t :: {}".format(str(type(lst_rule_a)), str(lst_rule_a))
                #print "           : {} {} {}".format(lst_rule_a['key'], lst_rule_a['opr'], lst_rule_a['val'])
        return


    def spamalyse(self, eml_in):
        """ This is the simplest analyse, it is based on black-list and white-list rules.
        It will analyse, separately, if the email can be considered black or considered white.
        The final decision, outside this function, depends on a combination of black, white and self._wob. """
        logging.debug(" func. simple_bw.spamalyse()")
        #print ">>>>>> Spamalyse - Simple black and white"
        dic_res = dict()
        for str_colour in ['black', 'white']:
            #print "*** ", str_colour
            dic_res[str_colour] = list()
            lst_rulesets = self._data[str_colour]
            lst_res = list()
            for rs in lst_rulesets:
                if not any(lst_res): # No reason to check more rule-sets if we already have a True
                    anyall = rs[0]
                    #print "**  ", anyall
                    for rul in rs[1]:
                        if not (any(lst_res) and anyall=='if_any_of'): # No reason to check more rules if we already have a True
                            #print "*rul", rul
                            if eml_in.has_key(rul['key']):
                                #print "    ", rul['key']
                                emlval = eml_in.get(rul['key'])
                                opr = rul['opr']
                                bol_hit = False # Assume innocent, until proven guilty...
                                for val in rul['val']: # there can be a one or more values to check for
                                    if not bol_hit: # no need to look further, if we already have a hit...
                                        #print "    ", emlval, opr, val
                                        if opr == '&&': # contains
                                            bol_hit = val in emlval
                                        elif opr == '!&': # do_not_contain
                                            bol_hit = not val in emlval
                                        elif opr == '==': # is
                                            bol_hit = val == emlval
                                        elif opr == '!=': # is_not
                                            bol_hit = val != emlval
                                        elif opr == '[=': # begins_with
                                            bol_hit = val == emlval[:len(val)]
                                        elif opr == ']=': # ends_with
                                            bol_hit =  val == emlval[-len(val):]
                                        elif opr == '[!': # not_begins_with
                                            bol_hit = not val == emlval[:len(val)]
                                        elif opr == ']!': # not_ends_with
                                            bol_hit = not val == emlval[-len(val):]
                                        else:
                                            print "Error: Unknown operator: "+opr
                                            continue
                                lst_res.append(bol_hit)
                            else:
                                print "email don't seem to have header entry:", rul['key']
                dic_res[str_colour].append(any(lst_res))
        #print "<<<<<< Spamalyse < end", dic_res
        return dic_res


    # helper functions

    def get_email_address_from_string(self,str_in):
        if '@' in str_in:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str_in)
            str_return = match.group(0).lower()
            return str_return
        else:
            return ""


# End class - Ruleset
