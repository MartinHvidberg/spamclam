

def print_main_headers(eml_in):
    """ Just print the interesting headers """
    print ">>>>>> Headers"
    print "Subj.: " + str(eml_in['Subject'])
    print "Date : " + str(eml_in['Date'])
    print "From : " + str(eml_in['From'])
    print "Rtrn : " + str(eml_in['Return-Path'])
    print "To_d : " + str(eml_in['Delivered-To'])
    print "To_o : " + str(eml_in['X-Original-To'])
    #print "multi: " + str(eml_in.is_multipart())


def print_keys(eml_in):
    print ">>>>>> Keys"
    print eml_in.keys()


def print_structure(eml_in):
    print ">>>>>> Structure"
    print email.Iterators._structure(eml_in)

# clean etc. rules

def x_rule_cleaner(self):
    """ Clean the rules """
    logging.debug(" func. rule_cleaner.")
    #print self._rules
    self._rules_backup = self._rules
    for colour in self._rules.keys():
        print "\n * ", colour
        lst_new_any = list()
        lst_new_all = list()
        for lst_old_rule in self._rules[colour]:
            print "<<<", lst_old_rule
            if lst_old_rule[0] == 'if_any_of':
                lst_new_any.extend(lst_old_rule)  # Note: Extend
            elif lst_old_rule[0] == 'if_all_of':
                lst_new_all.append(lst_old_rule)  # Note: Append
        print ">>>", lst_new_all
        print ">>>", lst_new_any


def x_get_rules_as_list(self, colour):
    return


def x_rules_as_json(self):
    return json.dumps(self._data)


def x_rules_as_text(self):
    """ Simply make a nice, multi-line, text version of a rule-set """
    return json.dumps(self._data, sort_keys=True, indent=2, separators=(',', ': '))



# Functions related to: Statistics

def x_stat_count_email(self, eml_in, bol_spam):
    """ Update _stat with email handled by this spamalyse instance """
    logging.debug(" func. stat_count_email.")
    # Count 1 mail
    self._stat['cnt_eml'] += 1
    # Count 1 mail, _deleted_
    if bol_spam:
        self._stat['cnt_del'] += 1
    # Note the sender, and if his mail was deleted
    if eml_in.has_key('from'):
        str_from = eml_in.get('from')
        if not str_from in self._stat['senders'].keys():
            self._stat['senders'][str_from] = {'tot': 1, 'del': int(bol_spam)}
        else:
            dic_sndr = self._stat['senders'][str_from]
            dic_sndr['tot'] += 1
            dic_sndr['del'] += int(bol_spam)
            self._stat['senders'][str_from] = dic_sndr
    return

def x_get_statistics(self, key):
    """ Return a named element from stat, if it exists... """
    logging.debug(" func. get_statistics.")
    if key in self._stat.keys():
        return self._stat[key]
    else:
        return None

def x_show_raw_statistics(self):
    """ Raw print the stat dicionary """
    logging.debug(" func. show_raw_statistics.")
    print self._stat

def x_show_pritty_statistics(self):
    """ Pritty-print the stat """
    logging.debug(" func. show_pritty_statistics.")
    print " ------ Stat ------"
    print " Total e-mails: " + str(self._stat['cnt_eml'])
    print " Deleted e-mails: " + str(self._stat['cnt_del'])
    print "   Senders stat:"
    lst_sndr = list()
    for sender in self._stat['senders'].keys():
        str_sndr = sender.replace('"', '').replace(',', ';') + ", total: " + str(
            self._stat['senders'][sender]['tot']) + ", delete: " + str(self._stat['senders'][sender]['del'])
        if self._stat['senders'][sender]['del'] > 0:
            str_sndr = " ! " + str_sndr
        else:
            str_sndr = "   " + str_sndr
        lst_sndr.append("  " + str_sndr)
    lst_sndr.sort()
    for sndr in lst_sndr:
        print sndr

def x_report_to_global_stat_file(self, str_filename):
    """ report to global statistics file """
    logging.debug(" func. report_to_global_stat_file.")
    # load existing, if exists...
    dic_global = dict()
    if os.path.isfile(str_filename):
        with open(str_filename) as fil_g:
            for line_i in fil_g.readlines():
                lst_i = line_i.lower().split(',')
                dic_global[lst_i[0]] = dict()
                dic_global[lst_i[0]]['tot'] = int(lst_i[1].replace('total:', '').strip())
                dic_global[lst_i[0]]['del'] = int(lst_i[2].replace('delete:', '').strip())

    # Turn the recent harvest into concurrent format
    dic_update = dict()
    for sender in self._stat['senders'].keys():
        str_emladd = self.get_email_address_from_string(sender)
        dic_stat = self._stat['senders'][sender]
        # print "#\n" + sender + "\n\t" + str_emladd + "\n\t" + str(dic_stat)
        dic_update[str_emladd] = dic_stat

    # Merge the two dics
    for upd in dic_update.keys():
        if not upd in dic_global.keys():
            dic_global[upd] = dic_update[upd]
        else:
            tmp_tot = dic_global[upd]['tot'] + dic_update[upd]['tot']
            tmp_del = dic_global[upd]['del'] + dic_update[upd]['del']
            dic_global[upd] = {'tot': tmp_tot, 'del': tmp_del}
            del tmp_tot, tmp_del
    del dic_update

    # return the updated collection
    with open(str_filename, 'w') as fil_g:
        for sender in dic_global.keys():
            str_tot = str(dic_global[sender]['tot'])
            str_del = str(dic_global[sender]['del'])
            str_ret = sender + ', total: ' + str_tot + ', delete: ' + str_del + '\n'
            fil_g.write(str_ret)

    return


