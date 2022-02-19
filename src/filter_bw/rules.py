
import os
import logging

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))

### ToDo
# Handle rules with "'" in them, e.g. + sub !& 'Poetry', 'children's books'

def magic_parse_string_as_csv(str_in, deli=',', quot='\''):
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
                    str_tmp = ""
                protected = not protected  # Switch protection status
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
            ##("magic c: - {}".format(lst_sliced))
            lst_ret.extend(lst_sliced)
    ##print("magic d: {}".format(lst_ret))
    return lst_ret


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
        super(Condition, self).__init__()  # Initialising the super-class
        self['opr'] = None
        self['key'] = None
        self['val'] = None
        self._valid = True
        self.str_to_cond(str_input)

    def str_to_cond(self, str_in):
        print(("\n » {}".format(str_in)))
        str_in = str_in.lstrip('+').strip()  # Clean + and spaces
        lst_opr = [opr for opr in self.VALID_OPR if opr in str_in]
        if len(lst_opr) == 1:  # Check exactly 1 opr
            str_opr = lst_opr[0]
            lst_cnd = str_in.split(" {} ".format(str_opr), 1)
            lst_cnd = [magic_parse_string_as_csv(tok, ",", "'") for tok in lst_cnd]
            if all([tok in self.VALID_EMAIL_HEADERS for tok in lst_cnd[0]]):
                # fine tuning ...
                if str_opr in self.VALID_OPR_REVERSED:
                    str_opr = str_opr[::-1]  # flip reversed operators
                # pack it up in a dic. Leaving any further validation to the validator...
                self['opr'] = str_opr
                self['key'] = [tok.strip() for tok in lst_cnd[0]]
                self['val'] = [tok.strip() for tok in lst_cnd[1]]
            else:
                self._valid = False
                logging.error("Invalid email header used in condition: {}".format(lst_cnd[0]))
        else:
            self._valid = False
            logging.error("! Condition do not have exactly 1 valid OPR: {}".format(str_in))

    def is_valid(self):
        """ XXX """
        if not self._valid:
            return False
        if all([tok == None for tok in [self['opr'], self['key'], self['val']]]):
            return False
        return True

    def statement_check(self, tup_stmnt, scmail):
        """ Used by condition_check()
        Checks the SCMail against a single statement
        EBNF: tup_stmnt = (key, opr, val)
        Returns: True|False """
        log.info("....stmn. check: {}".format(tup_stmnt))
        key_k, opr_o, val_v = tup_stmnt
        val_eml = scmail.get(key_k)
        if opr_o == '&&':  # contains
            bol_hit = val_v in val_eml
        elif opr_o == '!&':  # do_not_contain
            bol_hit = not val_v in val_eml
        elif opr_o == '==':  # is
            bol_hit = val_v == val_eml
        elif opr_o == '!=':  # is_not
            bol_hit = val_v != val_eml
        elif opr_o == '[=':  # begins_with
            bol_hit = val_v == val_eml[:len(val_v)]
        elif opr_o == ']=':  # ends_with
            bol_hit = val_v == val_eml[-len(val_v):]
        elif opr_o == '[!':  # not_begins_with
            bol_hit = not val_v == val_eml[:len(val_v)]
        elif opr_o == ']!':  # not_ends_with
            bol_hit = not val_v == val_eml[-len(val_v):]
        else:
            bol_hit = False
            log.error("Error: Unknown operator: {} in statement {}".format(opr_o, tup_stmnt))
        log.info("....stmn. returns: {}".format(bol_hit))
        return bol_hit  # EBNF: ( True|False )

    def condtion_check(self, scm_in):
        """ Checks the SCMail against a single condition
            EBNF: cond = ((key, {key}), opr, (val, {val}))
            e.g.: {'key':['to','cc','bcc'],'opr':'[=','val':['mail_list_on_Python','daily_letter_from_your_grosser']}
            :returns: list of true statements, this may be an empty list """
        log.info("...cond. check: {} {} {}".format(self['key'], self['opr'], self['val']))
        lst_true_stmn = list()
        for key_k in self['key']:
            if key_k == 'sub': key_k = 'subject'  # .scrule use shorthand 'sub', emails uses 'subject'
            if key_k in scm_in:
                for opr_o in [self['opr']]:  # Why do we insist that opr_o is from a list?
                    for val_v in self['val']:
                        if self.statement_check((key_k, opr_o, val_v), scm_in):
                            lst_true_stmn.append((key_k, opr_o, val_v))
            else:
                log.info("SCMail did not have an entry: {}".format(key_k))
        log.info("...cond. returns {}".format(lst_true_stmn))
        return lst_true_stmn

class Rule(object):
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
        if rul_in != []:
            self._reaction = rul_in[0]
            self._conditions = rul_in[1:]
        log.info("RUL: {}".format(rul_in))

    def __repr__(self):
        return "Rule({}, {})".format(self._reaction, self._conditions)

    def __str__(self):
        return "r: {}, c: {}".format(self._reaction, self._conditions)

    def is_valid(self):
        """ XXX """
        if isinstance(self._reaction, list):
            if len(self._reaction) == 6:
                if isinstance(self._conditions, list):
                    if len(self._conditions) > 0:
                        return True
                    else:
                        log.warning("Invalid condition, empty _condition")
                else:
                    log.warning("Invalid condition, _condition is not a list")
            else:
                log.warning("Invalid condition, _reaction do not have 6 elements: {}".format(self._reaction))
        else:
            log.warning("Invalid condition, _reaction is not a list: {} {}".format(str(type(self._reaction)), self._reaction))
        return False

    def reaction(self):
        return self._reaction

    def rule_from_strings(self, los_in):
        log.debug("r_f_s({})".format(los_in))
        lst_ret = list()
        # Parse Reaction
        lst_reaction = list()  # Empty result list
        str_reaction = los_in[0].strip('()')
        if isinstance(str_reaction, str):
            loi = magic_parse_string_as_csv(str_reaction)
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

    def rule_check(self, scmail):
        """ Checks the SCMail against a single rule """
        log.info("..rule check: {} if {}".format(self._reaction, self._conditions))
        dic_ret = {'lst_bool': list(), 'lst_stmn': list()}
        for cond in self._conditions:  # These ALL need to be True, for the Rule to be True
            lst_cond_res = cond.condtion_check(scmail)
            dic_ret['lst_bool'].append(len(lst_cond_res) > 0)  # the cond. check True|False any conditions met
            dic_ret['lst_stmn'].extend(lst_cond_res)  # the true cond. statement(s)
        bol_rule = len(dic_ret['lst_bool']) > 0 and all(dic_ret['lst_bool'])  # the entire Rule check True|False
        if bol_rule:
            log.info("..rule. returns: {} because {}".format(self._reaction, dic_ret['lst_stmn']))
            return self._reaction, dic_ret['lst_stmn']
        else:
            log.info("..rule. returns: False")
            return None, []


class Rules(object):
    """ Rules to be used with SpamClam, it's part of BW filter.
    A rewrite of the older class Ruleset(object) Black & White is now replaced with Reaction, and WoB is dead.
    Now divided into three class'es Rules(), Rule(), Condition()"""

    def __init__(self, rule_dir=os.path.dirname(os.path.realpath(__file__))):
        """ Initialises the Rules object.
        :param rule_dir: Where to find the .scrules files, etc. Default is in the same dir.
        """
        logging.info("class init. Rules. loading from: {}".format(rule_dir))
        self._rldr = rule_dir  # Where to look for the rule files
        self._rules = list()
        self._valid = True
        self.load_all_rule_files()  # Load all rule- and address files

    def is_valid(self):
        if self._valid:
            return True
        return False

    def spamalyse(self, scm_in):
        """ Checks an email against entire rules, i.e. self """
        log.info(".Rules check")
        lst_results = list()
        for rule in self._rules:
            res_of_rule = rule.rule_check(scm_in)
            ##log.info("Xtra: {}, {}\n".format(str(type(res_of_rule[0])), res_of_rule))
            if isinstance(res_of_rule[0], list):  # the rule is met, implement the Reaction
                log.info(".Rules: hit result: {}\n".format(res_of_rule))
                # expect res_of_rule[0] as [7, 7, 1, 9, False, 'Bloody xxx']
                scm_in.vote("BW", res_of_rule[0][5], res_of_rule[0][0], res_of_rule[0][1], res_of_rule[0][2], res_of_rule[0][3], str(res_of_rule[1]))
                lst_results.append(res_of_rule)
        log.info(".Rules returning: {}".format(lst_results))
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
        with open(self._rldr + os.sep + fil_in) as f:
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
            log.debug("\n >> {}\n << {}".format(rul, rul_in))
            if rul_in.is_valid():
                self.rul_insert(rul_in)
            else:
                self._valid = False  # If one Rule() is invalid, entire Rules() become invalid!
        return None

    def load_all_rule_files(self):
        """
        Load all rule files (rule and address) from default dir.
        - walk the dir
        - send all reasonable files to load_a_rule_file()
        :return: None
        """
        log.info("Start: load_all_rule_files in: {}".format(self._rldr))
        for fil_in in os.listdir(self._rldr):
            log.debug("candidate file: {}".format(fil_in))
            if fil_in.endswith(".scrules"): # or fil_in.endswith(".scaddr"):
                log.info(".scxxxx file: {}".format(fil_in))
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
        if self.is_valid():
            print((self._rules))
        else:
            print("Rules are INVALID ...")


# End class - Rules

if __name__ == '__main__':

    # Initialize logging
    logging.basicConfig(filename='SpamClam_Rules_test.log',
                        filemode='w',
                        level=logging.INFO, # INFO, # DEBUG,
                        format='%(asctime)s %(levelname)7s %(funcName)s | %(message)s')
                        # %(funcName)s
    log = logging.getLogger(__name__)
    log.info("Initialize: {}".format(__file__))

    rul_test = Rules('./')
    rul_test.show_rules_backdoor()
