import os, email

def print_main_headers(eml_in):
    """ Just print the interesting headers """
    print "------ Headers"
    print "Subj.: " + str(eml_in['Subject'])
    print "Date : " + str(eml_in['Date'])
    print "From : " + str(eml_in['From'])
    print "Rtrn : " + str(eml_in['Return-Path'])
    print "To_d : " + str(eml_in['Delivered-To'])
    print "To_o : " + str(eml_in['X-Original-To'])
    #print "multi: " + str(eml_in.is_multipart())
    
def print_keys(eml_in):
    print "------ Keys"
    print eml_in.keys()
    
def print_structure(eml_in):
    print "------ Structure"
    print email.Iterators._structure(eml_in)
    
class Spamalyser(object):
    """ The Spamalyser class """
    def __init__(self, conf_dir, mode='simple', wob=True):
        self._cnfd = conf_dir # Where to look for the .conf files
        self._mode = mode # default mode is 'simple'
        self._wob = wob # White over Black, White-list overrules Black-list... default is True
        self._rules = {'White': list(), 'Black': list()}
        
        # Find rule files
        for fil_cnf in os.listdir(self._cnfd):
            if fil_cnf.endswith(".conf"):
                # Crunch the rule file
                if "white" in fil_cnf.lower():
                    str_colour = 'White'
                elif "black" in fil_cnf.lower():
                    str_colour = "Black"
                else:
                    str_colour = ""
                    continue
                print(fil_cnf)
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
                #print "StarRaw\n", lst_rulesets
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
                        lst_aruleset.append({'key':key_c, 'opr':oprt, 'val':lst_values})
                    self._rules[str_colour].append([allany,lst_aruleset])
        print "Rules: ", self._rules
                        
    def add_ruleset(self,lst_rs):
        self._rules.append(lst_rs) 

    def is_spam(self, eml_in):
        """ Accepts an eml (email.message) and return True or False, indicating if it's considered to be spam. 
        email message is expected to be a email.message_from_string(s[, _class[, strict]])
        for details see: https://docs.python.org/2/library/email.message.html#module-email.message
        """
        lst_known_modes = ['simple']
        if self._mode in lst_known_modes:
            if self._mode == 'simple':
                return self._simple_bw_spamalyse(eml_in)
        else:
            return False
        
    def _simple_bw_spamalyse(self, eml_in):
        """ This is the simplest analyse, it is based on black-list and white-list rules, 
        maintained in separate files... 
        It will analyse, seperately, if the email can be consisered Black or White.
        The final decision depends on a combination of Black, White and self._wob. """
        print "================================================================"
        dic_res = dict()
        for str_colour in ['Black', 'White']:
            print "*** Colour is", str_colour
            lst_rulesets = self._rules[str_colour]
            lst_res = list()
            for rs in lst_rulesets:
                anyall = rs[0]
                print "**  AllAny is", anyall
                for rul in rs[1]:
                    print "*   rul is", rul
                    if eml_in.has_key(rul['key']):
                        print "    check key", rul['key']
                        emlval = eml_in.get(rul['key'])
                        opr = rul['opr']
                        bol_hit = False # Assume innocent, until proven guilty...
                        for val in rul['val']: # there can be a one or more values to check for
                            if not bol_hit: # no need to look further, if we allready have a hit...
                                print "    for opr, val", opr, val
                                if opr == '&&': # contains
                                    if val in emlval:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == '!&': # do_not_contain
                                    if not val in emlval:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == '==': # is
                                    if val == emlval:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == '!=': # is_not
                                    if val != emlval:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == '[=': # begins_with
                                    if val == emlval[:len(val)]:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == ']=': # ends_with
                                    if val == emlval[-len(val):]:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == '[!': # not_begins_with
                                    if not val == emlval[:len(val)]:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                elif opr == ']!': # not_ends_with
                                    if not val == emlval[-len(val):]:
                                        bol_hit = True
                                        print "   !HIT", opr, val
                                else:
                                    print "Error: Unknown operator: "+opr
                                    continue
                        lst_res.append(bol_hit)
                    else:
                        print "email don't seem to have header entry:", rul['key']
            print "TF?", lst_res
        print "----------------------------------------------------------------"