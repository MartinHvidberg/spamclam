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
        self._rules = dict()
        
        # Find rule files
        for fil_cnf in os.listdir(self._cnfd):
            if fil_cnf.endswith(".conf"):
                # Crunch the rule file
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
                    allany, cond = rule.split(' ',1)
                    lst_cond = cond.strip().strip('{}').strip().split(';')
                    print "***", allany, lst_cond
                    for con in lst_cond: # Replace each cond. with True or False
                        key_c, oprt, values = con.strip().split(' ',2)
                        lst_values = [v.strip() for v in values.split(',')]
                        print "  k:", key_c 
                        print "  o:", oprt
                        print "  v:", lst_values

    def is_spam(self, eml_in):
        """ Accepts an eml (email.message) and return True or False, indicating if it's considered to be spam. 
        email message is expected to be a email.message_from_string(s[, _class[, strict]])
        for details see: https://docs.python.org/2/library/email.message.html#module-email.message
        """
        lst_known_modes = ['simple']
        if self._mode in lst_known_modes:
            if self._mode == 'simple':
                return False
        else:
            return False