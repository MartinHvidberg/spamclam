
import os
import logging
import csv

class Condition(dict):
    """ A 'condition' is a dictionary. It has entries 'key', 'opr' and 'val'
        'opr' is a string
        'key' and 'val' are lists of strings. In simple cases the lists only has one element.
        in 'packed conditions' the lists can have multiple elements
        There are implicit OR between the elements in a packed condition list. """

    # Some class 'constants'
    VALID_OPR_STRAIGHT = {'&&', '!&', '==', '!=', '[=', ']=', '[!', ']!'}  # a set()
    VALID_OPR_REVERSED = {'&!', '=!', '=[', '=]', '![', '!]'}
    VALID_OPR = VALID_OPR_STRAIGHT | VALID_OPR_REVERSED
    VALID_EMAIL_HEADERS = {'sub', 'from', 'body', 'to', 'cc', 'bcc', 'size'}
    VALID_RULE_KEYS = {'key', 'opr', 'val'}

    def __init__(self, str_input):
        logging.debug("class init. Condition")
        self['opr'] = None
        self['key'] = None
        self['val'] = None
        self.str_to_cond(str_input)

    def str_to_cond(self, str_in):  XXX Triple None Condition sneaked into every Rule XXX
        lst_opr = [opr for opr in self.VALID_OPR if opr in str_in]
        if len(lst_opr) == 1:  # Check exactely 1 opr
            str_opr = lst_opr[0]
            lst_cnd = str_in.split(" {} ".format(str_opr), 1)
            lst_cnd = [tok.split(',') for tok in lst_cnd]  # conveniently also turns simple conditions into lists
            # pack it up in a dic. Leaving any further validation to the validator...
            if str_opr in self.VALID_OPR_REVERSED:
                str_opr = str_opr[::-1]
            self['opr'] = str_opr
            self['key'] = [tok.strip() for tok in lst_cnd[0]]  XXX '+' not cleaned from key in complex Rule XXX
            self['val'] = [tok.strip() for tok in lst_cnd[1]]
        else:
            logging.warning("! Condition have either No or Mutiple valid OPR: {}".format(str_in))

    def is_valid(self):
        """ XXX """

        return True

    def statement_check(self, salstmn, salmail):
        """ Used by condition_check()
        Checks the SCMail against a single statement
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

    def condtion_check(self, salcond, scm_in):
        """ Checks the SCMail against a single condition
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
            if key in scm_in:
                for opr in [salcond['opr']]:  # prepared for future list_of_opr
                    for val in salcond['val']:
                        bol_spam, tup_stmn = self.statement_check((key, opr, val), scm_in)
                        if bol_spam:
                            dic_ret['lst_bool'].append(bol_spam)
                            dic_ret['lst_stmn'].append(tup_stmn)
        logging.debug("    func. condit. {} {} {} = {}".format(salcond['key'], salcond['opr'], salcond['val'], any(dic_ret['lst_bool'])))
        return (any(dic_ret['lst_bool']), dic_ret['lst_stmn'])

class Rule(list):
    """ A 'rule' is a Reaction + a list of Conditions.
        A 'simple rule' have one condition.
        A 'complex rule' have several conditions.
        There are implicit AND between the conditions in a complex rule. """

    def __init__(self, los_in):
        logging.debug("class init. Rule")
        log.debug("Rule() receive LOS: {}".format(los_in))
        self._reaction = None
        self._conditions = list()
        rul_in = self.rule_from_strings(los_in)
        log.debug("RUL: {}".format(rul_in))

    def is_valid(self):
        """ XXX """
        return True

    def magic_parse_string_as_csv(self, str_in, deli=',', quot='\''):
        """ Take a string and return a list, split by deli, while respecting quot. """
        ##print("magic a: deli:{} quot:{} in:{}".format(deli, quot, str_in))
        lst_1cut = list()
        if quot in str_in:
            protected = False
            str_tmp = str()
            for char in str_in:
                if char == quot:
                    if str_tmp != "":
                        lst_1cut.append([str_tmp, protected])
                        protected = not protected  # Switch protection status
                    str_tmp = ""
                else:
                    str_tmp += char
        else:
            lst_1cut = [[str_in, False]]
        ##print("magic b: {}".format(lst_1cut))
        lst_ret = list()
        for blox in lst_1cut:
            if blox[1]:  # It's a protected block
                lst_ret.append(blox[0])
            else:
                lst_sliced = [tok.strip() for tok in blox[0].split(deli) if tok.strip() != '']
                ##print("magic d: - {}".format(lst_sliced))
                lst_ret.extend(lst_sliced)
        ##print("magic d: {}".format(lst_ret))
        return lst_ret


    def rule_from_strings(self, los_in):
        log.debug("r_f_s({})".format(los_in))
        lst_ret = list()
        # Parse Reaction
        lst_reaction = list()  # Empty result list
        str_reaction = los_in[0].strip('()')
        if isinstance(str_reaction, str):
            loi = self.magic_parse_string_as_csv(str_reaction)
            if len(loi) == 6:
                for n in range(4):
                    try:
                        lst_reaction.append(int(loi[n]))
                    except ValueError:
                        log.warning("Rule() received invalid Condition, expected integer in position: {}".format(n))
                        return []  # On critical error return empty list
                if loi[4].lower() == 'true':
                    lst_reaction.append(True)
                elif loi[4].lower() == 'false':
                    lst_reaction.append(False)
                lst_reaction.append(loi[5])
            else:
                log.warning("Rule() received invalid Condition, not 6 elements: {}".format(str_reaction))
                return []  # On critical error return empty list
        else:
            log.warning("Rule() received invalid Condition, not type string: {}".format(str_reaction))
            return []  # On critical error return empty list
        lst_ret.append(lst_reaction)  # Add the Reaction as 1'st element in return list
        del lst_reaction, str_reaction, loi  # Cleaning up a bit ...
        # Parse Conditions
        for str_cond in los_in[1:]:
            con_in = Condition(str_cond)
            if con_in.is_valid():
                lst_ret.append(con_in)
            else:  # Condition failed to build ...
                return []  # On critical error return empty list
        print(lst_ret)
        return lst_ret


    def OLD_rule_from_strings(self, los_in):
        """ ! This is still messy, and I want to nice it up. !
        Make a list of 'rule's from a list of raw strings, typically the content of a .scrule or .scaddr file
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

    def OLD_rules_from_listofaddressers(self, los_adr):
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


class Rules(object):
    """ Rules to be used with SpamClam.
    A rewrite of the older class Ruleset(object) Black & White is now replaced with Reaction.
    Now divided into three class'es Rules(), Rule(), Condition()"""

    def __init__(self, rule_dir):
        logging.debug("class init. Rules")
        self._rldr = rule_dir  # Where to look for the rule files
        self._rules = list()
        self.load_all_rule_files()  # Load all rule- and address files

    def spamalyse(self, scm_in):
        """ Checks an email agains entire rules, i.e. self """
        for rule in self._rules:
            scm_in = rule.spamalyse(scm_in)  # Do this have a chance... How do we collect results?
        return scm_in

    ######  Rule-builder ######

    def los_to_lor(self, los_in, str_assume):
        """
        Interpret list_of_strings, depending on str_assume, and returning list_of_rules
        :param los list: list of strings
        :param str_assume str: What type of info it's assumed to be
        :return: list -- list of rules
        """
        lor_ret = list()
        if str_assume == 'rules':
            if los_in[0].strip()[0] == '(':
                los_collect = list()
                for str_i in los_in:
                    if str_i.strip()[0] == '(':
                        if len(los_collect) > 0:
                            lor_ret.append(los_collect)
                        los_collect = list()
                    los_collect.append(str_i)
                lor_ret.append(los_collect)  # Catch the last rule ...
            else:
                log.warning("First non-comment line in .scrules file must start with '('. Failed for line: {}".format(los_in[0]))
        elif str_assume == 'addresses':
            lor_ret = self.rules_from_listofaddressers(los_in)
        else:
            pass  # XXX Consider making a qualified guess, based on contents, rather than returning empty...
        # Enforce one rule per Reaction
        ##log.debug("ENFORCE: in: {}".format(lor_ret))
        lol_1to1reaction2rule = list()
        for reaction in lor_ret:
            if isinstance(reaction, list) and len(reaction) >= 2:  # expects at least a Reaction and one Condition
                if reaction[0][0] == '(':  # just checking ... first element is a Reaction
                    if len([itm for itm in reaction if itm[0] == '(']) == 1:  # make sure only one Reaction element
                        str_reaction = reaction[0]
                        lst_temp = [str_reaction]
                        for str_cond in reaction[1:]:
                            if str_cond.strip()[0] == '+':
                                lst_temp.append(str_cond.strip())
                            else:
                                if len(lst_temp) > 1:  # save previous collected lines
                                    lol_1to1reaction2rule.append(lst_temp)
                                    lst_temp = [str_reaction]  # Inotialise the next ...
                                lst_temp.append(str_cond)
                        if len(lst_temp) > 1:  # save last collected lines
                            lol_1to1reaction2rule.append(lst_temp)
                    else:
                        log.warning("Enforce one rule per Reaction, received invalid data, multibles start with a '(': {}".format(reaction))
                else:
                    log.warning("Enforce one rule per Reaction, received invalid data, not starting with a '(': {}".format(reaction))
            else:
                log.warning("Enforce one rule per Reaction, received invalid data, expected at least 2 elements in list: {}".format(reaction))
        ##log.debug("ENFORCE: ou {}".format(lol_1to1reaction2rule))
        return lol_1to1reaction2rule  # Return empty list of rules, if str_assume is not recognised. XXX Consider raising warning

    def OLD_raw_insert_rule(self, colour, rul_in):
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

    def rul_insert(self, rul_in):
        """ Insert a Rule object in Rules """
        if rul_in.is_valid():
            self._rules.append(rul_in)
        else:
            log.warning("rul_insert() failed since rule failed .is_valid()")

    def OLD_lor_inserter(self, str_colour, lor):
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

    def load_a_rule_file(self, str_fn):
        """ Load the specified rule file (rule or address) to the rules collection
        - read the file with load_file(), to get a list_of_strings
        - call los_to_lor(), setting str_assume= based on str_fn, to get a list_of_rules
        - call lor_validator(), to filter away invalid rules
        - insert the validated lor into collection
        :param str_fn: name of the file to be loaded. Just the file name, assuming it's in self._rldr
        :return: None """
        log.debug(" func. load_a_rule_file: {}".format(str_fn))
        los_in = self.load_file(str_fn)
        for string in los_in:
            log.debug("  los: {}".format(string))
        if '.scrule' in str_fn:
            str_assume = 'rules'
        elif 'scaddr' in str_fn:
            str_assume = 'addresses'
        else:
            str_assume = ""
        lor_in = self.los_to_lor(los_in, str_assume)
        for rul in lor_in:
            rul_in = Rule(rul)
            self.rul_insert(rul_in)
        return None

    def load_all_rule_files(self):
        """
        Load all rule files (rule and address) from default dir.
        - walk the dir
        - send all reasonable files to load_a_rule_file()
        :return: None
        """
        log.debug(" func. load_all_rule_files in: {}".format(self._rldr))
        for fil_in in os.listdir(self._rldr):
            if fil_in.endswith(".scrules"): # or fil_in.endswith(".scaddr"):
                log.debug(".scxxxx file: {}".format(fil_in))
                self.load_a_rule_file(fil_in)
                log.info("Loaded rule file: {}".format(fil_in))
        return None

    ######  helpers ######

    def get_email_address_from_string(self,str_in):
        if '@' in str_in:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str_in)
            str_return = match.group(0).lower()
            return str_return
        else:
            return ""

    ######  get stuff ######

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

    ######  prints and misc ######

    def show_rules_backdoor(self):
        """ Show the rules """
        log.debug(" func. show_rules_backdoor()")
        print("\nPrint the rules, via the back door...")
        print(self._rules)
        return None

    def show_rules_pp(self):  # XXX This needs some working on, to be real pretty...
        """ Show the rules - pretty print """
        log.debug(" func. show_rules_pp()")
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

    def spamalyse(self, salmail, wob_in):
        """ Checks an email agains entire rules, i.e. self
            EBNF: input: rules = { 'white': [<rule>]; 'black':[<rule>] }
                  returns: ( True|False, ({win_stnm})) """
        dic_white_and_black = dict()
        for str_colour in ('white', 'black'):
            dic_white_and_black[str_colour] = {'lst_bool': list(), 'lst_stmn': list()}
            for num_rule in self.list_rulenumbers_of_colour(str_colour):
                salrule = self.get_rule_by_number(num_rule)
                rul_ret = self.rule_check(salrule, salmail)  # Check every rule in the rules
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
        log.debug("  func. spamalyse. wob: {}; white: {}; black: {} = Spam: {}".format(wob_in, bol_white, bol_black, sal_ret['spam']))
        return sal_ret

# End class - Ruleset

if __name__ == '__main__':

    # Initialize logging
    logging.basicConfig(filename='SpamClam_Rules_test.log',
                        filemode='w',
                        level=logging.DEBUG, # INFO, # DEBUG,
                        format='%(asctime)s %(levelname)7s %(funcName)s >> %(message)s')
                        # %(funcName)s
    log = logging.getLogger(__name__)
    log.info("Initialize: {}".format(__file__))

    rul_test = Rules('./')
    rul_test.show_rules_backdoor()
