import email

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
        self._mode = mode # default
        self._wob = wob # White over Black, White-list overrules Black-list... 
    

def is_spam(eml_in, mode_in = 'simple'):
    """ Accepts an eml (email.message) and return True or False, indicating if it's considered to be spam. 
    email message is expected to be a email.message_from_string(s[, _class[, strict]])
    for details see: https://docs.python.org/2/library/email.message.html#module-email.message
    """
    lst_known_modes = ['simple']
    if mode_in in lst_known_modes:
        if mode_in == 'simple':
            return False
    else:
        return False