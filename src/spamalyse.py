
### History
# ver. 0.1.x Early running stages
# ver. 0.2   Experimenting with Object Rule-set

import os, email
import logging

import simple_bw


class Salmail(object):
    """ The 'equvivalent' or 'extract' of one email.
    But only the relevant parts, and added some more info and functions
    Instances are initialised with a 'real' email message.
    This object is designed to be the 'e-mail massage' to put into Spamalyser methods. """

    def __init__(self, emlmsg):
        self._mesg = emlmsg
        self._data = dict()
        self._mandatory_fields = ('id', 'from', 'to', 'cc', 'bcc', 'subject')
        for key_i in self._mandatory_fields:
            self._data[key_i] = "" # Initialize to empty string, rather than None
        self._msg2data()

    def show(self):
        print ""
        print(" id      : {}".format(self.get('id')))
        print(" from    : {}".format(self.get('from')))
        print(" to      : {}".format(self.get('to')))
        print(" cc      : {}".format(self.get('cc')))
        print(" bcc     : {}".format(self.get('bcc')))
        print(" subject : {}".format(self.get('subject')))

    def _msg2data(self):
        """ This function tries to set all the data entries, from the org. message """
        msg = self._mesg
        # * id
        try:
            self._data['id'] = msg.get('Message-ID').strip('<>')
            ##print msg.get('Message-ID')
        except AttributeError:
            logging.warning("email.message seems to have no 'Message-ID'...\n{}".format(self._mesg))  # XXX This is BAD, Dont dump this entire, likely Spam, message to the log file XXX
            print "email.message seems to have no 'Message-ID'...\n{}".format(" - See message in log file...")
            self._data['id'] = None
        # * from
        self._data['from'] = email.utils.parseaddr(msg.get('from'))[1]
        # * to
        self._data['to'] = email.utils.parseaddr(msg.get('to'))[1]
        # * cc
        self._data['cc'] = msg.get('cc') # happens to return None in no cc available
        # * bcc
        self._data['bcc'] = msg.get('bcc') # happens to return None in no cc available
        # * subject
        raw_sub = msg.get('Subject')
        dcd_sub = email.header.decode_header(raw_sub)
        self._data['subject'] = ''.join([tup[0] for tup in dcd_sub]) # It's legal to use several encodings in same header
        # * body
        # * Date
        # * size


        # print "multi?: {}".format(msg.is_multipart())
        # print "keys  : {}".format("\n = ".join(sorted(msg.keys())))
        # print "rplto : {}".format(email.utils.parseaddr(msg.get('reply-to')))
        # Return-Path
        # Message-ID: in particulary the part right of @
        # X-Sender
        # Sender (sending 'on behalf of' from)

        for key_check in self._data.keys():
            if self._data[key_check] == None:
                self._data[key_check] = ""  # Force to "" rather than None, since it gives problems

    def keys(self):
        """ Return a list of available keys """
        return list(self._data.keys())

    def has_key(self, key_in):
        ##print "  key type and val: {}, {}".format(str(type(key_in)), key_in)
        ##print "  _data.keys(): {}".format(self._data.keys())
        return key_in in self._data.keys()

    def get(self, mkey):
        """ Get one field from the message """
        if mkey == 'id':
            return self._data['id']
        elif mkey == 'from':
            return self._data['from']
        elif mkey == 'to':
            return self._data['to']
        elif mkey == 'cc':
            return self._data['cc']
        elif mkey == 'bcc':
            return self._data['bcc']
        elif mkey == 'subject':
            return self._data['subject']
        elif mkey == 'body':
            return self._data['body']
        elif mkey == 'size':
            return self._data['size']
        # XXX Consider reply-to, date, has-attachments...
        #elif mkey == '':
        #    return self._data['']
        else:
            return None


class Spamalyser(object):

    """ The Spamalyser class """
    
    def __init__(self, mode, conf_dir, wob='True'):
        logging.debug("class init. Spamalyser")
        self._mode = mode # default mode is 'simple'
        if wob.lower() == 'true': # white over black, white-list overrules black-list... default is True
            self._wob = True # cast from string to boolean
        else:
            self._wob = False
        if mode == 'simple':
            self._rulob = simple_bw.Ruleset(conf_dir)  # The rules object
            self._stat = {'cnt_eml': 0, 'cnt_del':0, 'senders': {}} # consider WGB stat (white, Grey, black)

            self._rulob.show_rules_pp() # XXX Just for debug... consider writing to logfile


    def is_spam(self, salmail_in):
        """ Accepts an eml (Salmail) as defined above)
        returning ??? indicating if it's considered to be spam.
        """
        ##obj_ret = []
        lst_known_modes = ['simple']
        if self._mode in lst_known_modes:
            if self._mode == 'simple': # The default 'simple black and white' analyser
                obj_ret = self._rulob.spamalyse(salmail_in, self._wob)
            else:
                obj_ret = False  # This only happens if the programmer f*cked up...
        else:
            obj_ret = False # if mode is unknown, it's not Spam
        logging.debug(" func. is_spam. {}; {} = {}".format(salmail_in.get('from'), salmail_in.get('subject'), obj_ret))
        return obj_ret


# End class - Spamalyser


# Music that accompanied the coding of this script:
#   David Bowie - Best of...