
### History
# ver. 0.1.x Early running stages
# ver. 0.2   Experimenting with Object Rule-set

import os, email
import re # for helper function
import logging

# Setup logging
logging.basicConfig(filename='spamalyse.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)7s %(message)s')
                    # %(funcName)s
logging.info("====== Start ======")


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


class Ruleset(object):
    """ Rule-set to be used with Spamalyser.
    A dictionary of (2) lists of lists of dictionaries.
    in pseudocode looking like this
    _data {'White':
            [
                [{from == 'dave@mygrocer.com'}],
                [{subject && 'spamalyser'}],
                [{from ]= 'python.org'}, {subject !& 'python in greek'}]
            ],
           'Black:
            [
                [{from == 'spammer_dude@highprice.com}],
                [{to !& 'myemail@home.net'}],
                [{from ]= microsoft.com}, {subject && 'open source'}]
            ]
          }
    """

    def __init__(self):
        logging.debug("class init. Ruleset")
        self._data = {'White': list(), 'Black': list()}

    def add_rule(self, colour, rul_in):
        # validate
        if colour in ['White', 'Black']:
            if aoa.lower() in ['any', 'all']:
                if isinstance(rul_in, dict):
                    pass
                    # {'key': 'from', 'opr': '==', 'val': [str_emladd]}
                    lst_expected_keys = ['key', 'opr', 'val']
                    lst_keys_in = rul_in.keys()
                    if all(key in lst_keys_in for key in lst_expected_keys):
                        pass
                        #XXX add check that key is in [,,,]
                        #XXX add check that opr is in [,,,]
                    else:
                        logging.warning("address rule rul_in is missing one or more of the keys: {}".format(str(lst_expected_keys)))
                        return 996
                else:
                    logging.warning("address rule rul_in is not type dictionary")
                    return 997
            else:
                logging.warning("illegal AOA in added rule: {}".format(str(aoa)))
                return 998
        else:
            logging.warning("illegal Colour in added rule: {}".format(str(colour)))
            return 999
        # check if exist
        #  XXX add some check here...
        # add
        self._data[colour][aoa].append(rul_in)
        return

    def get_rules_as_list(self, colour):
        return

    def show_rules(self):
        print "\n * Rules object..."
        for colour in sorted(self._data.keys()):
            col_set = self._data[colour]
            print "\n + Colour: {} ({})".format(colour, str(len(col_set)))
            for aoa in sorted(col_set.keys()):
                print "   + AoA: ".format(aoa)
                print "     + type: {} length: {}".format(aoa, len(aoa))

        return


class Spamalyser(object):
    """ The Spamalyser class """
    
    def __init__(self, conf_dir, mode='simple', wob=True):
        logging.debug("class init. Spamalyser")
        self._cnfd = conf_dir # Where to look for the .conf files
        self._mode = mode # default mode is 'simple'
        self._wob = wob # White over Black, White-list overrules Black-list... default is True
        self._rules = {'White': list(), 'Black': list()}  # XXX Should diapear as _rulob works
        self._rulob = Ruleset()  # The rules object
        self._stat = {'cnt_eml': 0, 'cnt_del':0, 'senders': {}} # consider WGB stat (White, Grey, Black)

        #self.load_rulesfiles()
        self.load_addressbooks()
        
        # Check that rules were filled
        for colour in ['Black', 'White']:
            if len(self._rules[colour]) < 1:
                print "!!! No rules of colour: "+colour

        # Experiment w. Rules
        #rus = Ruleset()
        #rus.show_rules()
        
    # Functions handling 'rules'
    
    def load_rulesfiles(self):
        """ Find and load all .conf files in the conf_dir """
        logging.debug(" func. load_rulesfiles.")
        # Find rule files
        for fil_cnf in os.listdir(self._cnfd):
            if fil_cnf.endswith(".scrule"):
                print("Config file: " + fil_cnf)
                # Crunch the rule file
                if "white" in fil_cnf.lower():
                    str_colour = 'White'
                elif "black" in fil_cnf.lower():
                    str_colour = "Black"
                else:
                    str_colour = ""
                    print "!!! file name contained neither 'white' nor 'black'... I'm confused."
                    continue
                with open(self._cnfd+fil_cnf) as f:
                    lst_conf = f.readlines()
                for n in range(len(lst_conf)):
                    str_tmp = lst_conf[n].split("#")[0] # Get rid of comments
                    while '  ' in str_tmp: # Replace all multi-space with single-space
                        str_tmp.replace('  ',' ')
                    if str_tmp in [' ', '\n', '\t']: # delete all whitespace-only lines
                        str_tmp = ''
                    lst_conf[n] = str_tmp # put it back in the list
                lst_conf = [lin.strip() for lin in lst_conf if len(lin)>0] # remove all the empty lines, and leading and trailing whitespace
                str_conf = " ".join(lst_conf) # connect all lines to one string
                lst_rulesets = ["if_a"+rs for rs in str_conf.split("if_a") if len(rs)>4] # turn the string into list of rules
                #print "StarRaw: ", lst_rulesets
                del str_conf, lst_conf # cleaning ...
                # Analyse the rule-set and establish rules
                for rule in lst_rulesets:
                    print "  rule:",rule
                    lst_aruleset = list()
                    allany, cond = rule.split(' ',1)
                    lst_cond = cond.strip().strip('{}').strip().split(';')
                    for con in lst_cond: # Replace each cond. with True or False
                        key_c, oprt, values = con.strip().split(' ',2)
                        lst_values = [v.strip() for v in values.split(',')]
                        rul_a = {'key':key_c, 'opr':oprt, 'val':lst_values}
                        lst_aruleset.append(rul_a)
                        print "    :", rul_a['key'], rul_a['opr'], rul_a['val'] 
                    self._rules[str_colour].append([allany,lst_aruleset])
        return
    
    def load_addressbooks(self):
        """ Find and load all address (.scaddr) files in the conf_dir """
        logging.debug(" func. load_addressbooks.")
        # Find addressbook files
        for fil_cnf in os.listdir(self._cnfd):
            if fil_cnf.endswith(".scaddr"):
                # Crunch the addressbook file
                if "white" in fil_cnf.lower():
                    str_colour = 'White'
                elif "black" in fil_cnf.lower():
                    str_colour = "Black"
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
                            logging.debug("<addr. {} = {}".format(str_colour, str_emladd))
                            dic_rul = {'key': 'from', 'opr': '==', 'val': [str_emladd]}
                            self._rulob.add_rule(str_colour, 'any', dic_rul)
                        del str_emladd, str_tmp
        return

    def rule_cleaner(self):
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

    def show_rules(self):
        """ Show the rules """
        logging.debug(" func. show_rules.")
        print "\n * Pritty print the rules..."
        for key1 in sorted(self._rules.keys()):
            itm1 = self._rules[key1]
            print "\n + Colour: {} ({})".format(key1, str(len(itm1)))
            for itm2 in itm1:
                print "   + RulL:"
                print "     + type: {}".format(itm2[0])
                for itm3 in itm2[1]:
                    print "           : {} {} {}".format(itm3['key'], itm3['opr'], itm3['val'])
        return
    
    # Functions processing email, checking them for spam...

    def is_spam(self, eml_in):
        """ Accepts an eml (email.message) and return True or False, indicating if it's considered to be spam. 
        email message is expected to be a email.message_from_string(s[, _class[, strict]])
        for details see: https://docs.python.org/2/library/email.message.html#module-email.message
        """
        logging.debug(" func. is_spam.")
        bol_return = None
        lst_known_modes = ['simple']
        if self._mode in lst_known_modes:
            if self._mode == 'simple': # The default 'simple black and white' analyser
                dic_result = self._simple_bw_spamalyse(eml_in)
                if self._wob:
                    if any(dic_result['White']):
                        bol_return = False # i.e. Not Spam
                    else:
                        bol_return = any(dic_result['Black']) # i.e. Spam if any reason found...
                else: # wob is false
                    bol_return = any(dic_result['Black']) # i.e. Spam if any reason found...
        else:
            bol_return = False # if rule unknown, it's not Spam
        self.stat_count_email(eml_in,bol_return)
        return bol_return
        
    def _simple_bw_spamalyse(self, eml_in):
        """ This is the simplest analyse, it is based on black-list and white-list rules.
        It will analyse, separately, if the email can be considered Black or considered White.
        The final decision, outside this function, depends on a combination of Black, White and self._wob. """
        logging.debug(" func. _simple_bw_spamalyser.")
        #print ">>>>>> Spamalyse - Simple Black and White"
        dic_res = dict()
        for str_colour in ['Black', 'White']:
            #print "*** ", str_colour
            dic_res[str_colour] = list()
            lst_rulesets = self._rules[str_colour]
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
    
    # Functions related to: Statistics
    
    def stat_count_email(self,eml_in,bol_spam):
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
                self._stat['senders'][str_from] = {'tot':1, 'del':int(bol_spam)}
            else:
                dic_sndr = self._stat['senders'][str_from]
                dic_sndr['tot'] += 1
                dic_sndr['del'] += int(bol_spam)
                self._stat['senders'][str_from] = dic_sndr
        return
    
    def get_statistics(self, key):
        """ Return a named element from stat, if it exists... """
        logging.debug(" func. get_statistics.")
        if key in self._stat.keys():
            return self._stat[key]
        else:
            return None
    
    def show_raw_statistics(self):
        """ Raw print the stat dicionary """
        logging.debug(" func. show_raw_statistics.")
        print self._stat
        
    def show_pritty_statistics(self):
        """ Pritty-print the stat """
        logging.debug(" func. show_pritty_statistics.")
        print " ------ Stat ------"
        print " Total e-mails: "+str(self._stat['cnt_eml'])
        print " Deleted e-mails: "+str(self._stat['cnt_del'])
        print "   Senders stat:"
        lst_sndr = list()
        for sender in self._stat['senders'].keys():
            str_sndr = sender.replace('"','').replace(',',';')+", total: "+str(self._stat['senders'][sender]['tot'])+", delete: "+str(self._stat['senders'][sender]['del'])
            if self._stat['senders'][sender]['del'] > 0:
                str_sndr = " ! "+str_sndr
            else:
                str_sndr = "   "+str_sndr
            lst_sndr.append("  "+str_sndr)
        lst_sndr.sort()
        for sndr in lst_sndr:
            print sndr
            
    def report_to_global_stat_file(self,str_filename):
        """ report to global statistics file """
        logging.debug(" func. report_to_global_stat_file.")
        # load existing, if exists...
        dic_global = dict()
        if os.path.isfile(str_filename):
            with open(str_filename) as fil_g:
                for line_i in fil_g.readlines():
                    lst_i = line_i.lower().split(',')
                    dic_global[lst_i[0]] = dict()
                    dic_global[lst_i[0]]['tot'] = int(lst_i[1].replace('total:','').strip())
                    dic_global[lst_i[0]]['del'] = int(lst_i[2].replace('delete:','').strip())
            
        # Turn the recent harvest into concurrent format
        dic_update = dict()
        for sender in self._stat['senders'].keys():
            str_emladd = self.get_email_address_from_string(sender)
            dic_stat = self._stat['senders'][sender]
            #print "#\n" + sender + "\n\t" + str_emladd + "\n\t" + str(dic_stat)
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
                str_ret = sender + ', total: '+ str_tot + ', delete: ' + str_del + '\n'
                fil_g.write(str_ret)
        
        return   

    # helper functions
    
    def get_email_address_from_string(self,str_in):
        #print '<<<',str_in
        if '@' in str_in:
            match = re.search(r'[\w\.-]+@[\w\.-]+', str_in)
            str_return = match.group(0).lower()
            #print '>>>', str_return
            return str_return
        else:
            return ""
    
# Music that accompanied the coding of this script:
#   David Bowie - Best of...