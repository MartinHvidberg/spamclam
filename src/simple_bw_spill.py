def spamalyse_old2(self, salmail_in):
    """ Do ... """

    def condit_check(condit_in, salmail_in):
        """ expect: {
            'key': ['to', 'cc', 'bcc'],
            'opr': '[=',
            'val': ['mail_list_on_Python', 'daily_letter_from_your_groser']
            } """
        lst_key = condit_in['key']
        opr = condit_in['opr']
        lst_val = condit_in['val']
        bol_condit_spam = False  # Assuming innocent until proven guilty.
        for key in lst_key:
            if salmail_in.has_key(key):
                emlval = salmail_in.get(key)
                for val in lst_val:
                    print " .....single_condit: ({}), {} {} {}".format(key, emlval, opr, val),
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
                        print "Error: Unknown operator: " + opr
                        continue
                    print "  =  ", bol_hit
                    bol_condit_spam = bol_condit_spam or bol_hit
            else:
                str_msg = "email don't seem to have header entry: {}".format(rul['key'])
                print str_msg
                logging.warning(str_msg)
                del str_msg
            print " ....condit-spam: {}".format(bol_condit_spam)
        return bol_condit_spam

    salmail_in.show()
    # logging.debug("func. simple_bw.spamalyse()")
    print " . Spamalyse - Simple black and white"
    dic_res = dict()  # initialize the output dic
    for str_colour in ['black', 'white']:
        logging.debug(".colour: {}".format(str_colour))
        dic_res[str_colour + 'hits'] = list()  # initialize the output hit-list for this colour
        for rul in self._data[str_colour]:
            # XXX consider if len(dic_res[str_colour] < 1:  # We only need one True, per colour
            print " ..rule {}-rule: {}".format(str_colour, rul)
            bol_rul_spam = True  # Must start with True, as we use AND
            for condit in rul:
                print " ...condit: {}".format(condit)
                condit_spam = condit_check(condit, salmail_in)
                bol_rul_spam = bol_rul_spam and condit_spam  # All condition in a rule must be true, for the rule to be true
                if condit_spam:
                    dic_res[str_colour + 'hits'].append(rul)  # Add the rule that turned true
            print " ..rule= {}".format(bol_rul_spam)
        dic_res[str_colour] = condit_spam  # return the boolean if this True/False in this colour
    return dic_res


def spamalyse_old_and_clumpsy(self, salmail_in):
    """ This is the simplest analyse, it is based on black-list and white-list rules.
    It will analyse, separately, if the email can be considered black or considered white.
    The final decision, outside this function, depends on a combination of black, white and self._wob. """
    salmail_in.show()
    # logging.debug("func. simple_bw.spamalyse()")
    print ">>>>>> Spamalyse - Simple black and white"
    dic_res = dict()
    for str_colour in ['black', 'white']:
        logging.debug(".colour: {}".format(str_colour))
        dic_res[str_colour] = list()
        lst_rulelinesets = self._data[str_colour]
        lst_res4colour = list()
        for rs in lst_rulelinesets:
            logging.debug("..ruleset: {}".format(rs))
            if not any(lst_res4colour):  # No reason to check more rule-sets if we already have a True
                for rul in rs:
                    if not (any(lst_res4colour)):  # No reason to check more rules if we already have a True
                        logging.debug("...rul: {}".format(rul))
                        for key_r in rul[
                            'key']:  # there can be a one or more keys to check in, e.g. ['to', 'cc', 'bcc']
                            if salmail_in.has_key(key_r):
                                emlval = salmail_in.get(key_r)
                                opr = rul['opr']
                                bol_hit = False  # Assume innocent, until proven guilty...
                                for val in rul['val']:  # there can be a one or more values to check for
                                    if not bol_hit:  # no need to look further, if we already have a hit...
                                        print ">>>>>> ", emlval, opr, val,
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
                                            print "Error: Unknown operator: " + opr
                                            continue
                                        print "  =  ", bol_hit
                                lst_res4colour.append(bol_hit)
                            else:
                                str_msg = "email don't seem to have header entry: {}".format(rul['key'])
                                print str_msg
                                logging.warning(str_msg)
                                del str_msg
            dic_res[str_colour].append(any(lst_res4colour))
    # print "<<<<<< Spamalyse < end", dic_res
    logging.debug("<<< res. simple_bw.spamalyse(): {}".format(str(dic_res)))
    return dic_res

