
### History
# ver. 0.1.x Early running stages
# ver. 0.2   Experimenting with Object Rule-set

import os, email
import logging

import simple_bw


class Spamalyser(object):

    """ The Spamalyser class """
    
    def __init__(self, conf_dir, mode='simple', wob='True'):
        logging.debug("class init. Spamalyser")
        self._mode = mode # default mode is 'simple'
        if wob.lower() == 'true': # white over black, white-list overrules black-list... default is True
            self._wob = True # cast from string to boolean
        else:
            self._wob = False
        if mode == 'simple':
            self._rulob = simple_bw.Ruleset(conf_dir)  # The rules object
            self._stat = {'cnt_eml': 0, 'cnt_del':0, 'senders': {}} # consider WGB stat (white, Grey, black)

            self._rulob.load_rulesfiles()
            self._rulob.load_addressbooks()

            # sal.import_addressfile('filename', 'white')
            # sal.import_rulefile('filename', 'black')
            # sal.export_2json('filename')

            #print "Show rules backdoor Begin:"
            #self._rulob.show_rules_backdoor()
            #print "Show rules backdoor End..."

            print "Show rules PP Begin:"
            self._rulob.show_rules_pp()
            print "Show rules PP End..."

    # Functions handling 'rules'
    # Functions processing email, checking them for spam...

    def x_is_spam(self, eml_in):
        """ Accepts an eml (email.message) and return True or False, indicating if it's considered to be spam. 
        email message is expected to be a email.message_from_string(s[, _class[, strict]])
        for details see: https://docs.python.org/2/library/email.message.html#module-email.message
        """
        logging.debug(" func. is_spam.")
        bol_return = None
        lst_known_modes = ['simple']
        if self._mode in lst_known_modes:
            if self._mode == 'simple': # The default 'simple black and white' analyser
                dic_result = simple_bw.spamalyse(eml_in)
                if self._wob:
                    if any(dic_result['white']):
                        bol_return = False # i.e. Not Spam
                    else:
                        bol_return = any(dic_result['black']) # i.e. Spam if any reason found...
                else: # wob is false
                    bol_return = any(dic_result['black']) # i.e. Spam if any reason found...
        else:
            bol_return = False # if rule unknown, it's not Spam
        self.stat_count_email(eml_in,bol_return)
        return bol_return

# End class - Spamalyser


# Music that accompanied the coding of this script:
#   David Bowie - Best of...