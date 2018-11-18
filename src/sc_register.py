#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Register
Defines classes: Register() and SCMail() (formerly SalMail())
The 'SCMail' object represents the SpamClam object equivalent to one e-mail.
The 'Register' object, essentially an archive of SCMails, is the central data object in all e-mail handling.
"""

__version__ = '0.4.1'

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)

import uuid
import email
import logging
logger = logging.getLogger('spamclam')


class SCMail(object):
    """ The 'equivalent' or 'extract' of one email.
    But only the relevant parts, and added some more info and functions
    Instances are initialised with a 'real' email message.
    This object is designed to be the 'e-mail massage' to use with SpamClam. """

    def __init__(self, emlmsg):
        logger.debug("class init. SCMail")
        self._mesg = emlmsg
        self._data = dict()
        self._spamlevel = 0  # 0..9
        self._mandatory_fields = ('id', 'from', 'to', 'cc', 'bcc', 'subject')
        for key_i in self._mandatory_fields:
            self._data[key_i] = "" # Initialize to empty string, rather than None
        self._msg2data()

    def show(self):
        print("")
        print((" id      : {}".format(self.get('id'))))
        print((" date    : {}".format(self.get('date'))))
        print((" from    : {}".format(self.get('from'))))
        print((" to      : {}".format(self.get('to'))))
        print((" cc      : {}".format(self.get('cc'))))
        print((" bcc     : {}".format(self.get('bcc'))))
        print((" subject : {}".format(self.get('subject'))))

    def _msg2data(self):
        """ This function tries to set all the entries, from the org. message """
        msg = self._mesg
        # * id
        try:
            self._data['id'] = msg.get('Message-ID').strip('<>')
        except AttributeError:
            logger.warning("email.message seems to have no 'Message-ID'...\n")
            # Try to construct a Message-ID form other headers
            str_d = msg.get('date')
            str_f = msg.get('from')
            if str_d or str_f:
                self._data['id'] = "EC_"+str_d+"__"+str_f
            else:
                self._data['id'] = "EC_"+str(uuid.uuid4())  # random unique id
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
        # * date
        self._data['date'] = msg.get('date')
        # * size

        # print "multi?: {}".format(msg.is_multipart())
        # print "keys  : {}".format("\n = ".join(sorted(msg.keys())))
        # print "rplto : {}".format(email.utils.parseaddr(msg.get('reply-to')))
        # Return-Path
        # Message-ID: in particulary the part right of @
        # X-Sender
        # Sender (sending 'on behalf of' from)

        for key_check in list(self._data.keys()):
            if self._data[key_check] == None:
                self._data[key_check] = ""  # Force to "" rather than None, since it gives problems

    def keys(self):
        """ Return a list of available keys """
        return list(self._data.keys())

    def has_key(self, key_in):
        """ return true if a key exists, otherwise false """
        return key_in in list(self._data.keys())

    def get(self, mkey):
        """ Get one field's value """
        if mkey in ['id', 'date', 'from', 'to', 'cc', 'bcc', 'subject', 'body', 'size']:
            return self._data[mkey]
        # XXX Consider reply-to, date, has-attachments...
        else:
            return None

    # End of class SCMail()


class Register(object):
    """ Essentially a dict() of SCMails, with some functions to handle it ... """

    def __init__(self, str_infile=None):
        self._data = dict()  # dictionary of SCMails
        self._count = 0
        if str_infile:
            self.read_from_file(str_infile)

    def insert(self, scm_in):
        """ inserts a SCMail into the register """
        pass

    def list(self):
        """ return a list of id's for the SCMails in the register"""
        return self._data.keys()

    def list_match(self, lst_criteria):
        """ returns a list of id's for the SCMails in the register
        that matches all the criteria in lst_criteria """
        pass

    def get(self, id):
        """ return the SCMail with the given id
        if not found, then returns None """
        return None

    def write_to_file(self, str_fn):
        """ writes the entire Register to a disc file """
        pass

    def read_from_file(self, str_fn):
        """ fills the Register with the info from a disc file """
        pass

    # End of class Register()

if __name__ == '__main__':
    print("This unit {} can't be run, but must be called from another unit".format(__file__))

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits III