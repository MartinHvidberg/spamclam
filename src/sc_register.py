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
    expects an object of type: email.message.EmailMessage
    But only the relevant parts, and added some more info and functions
    Instances are initialised with a 'real' email message.
    This object is designed to be the 'e-mail massage' to use with SpamClam. """

    def __init__(self, eml_in):
        logger.debug("class init. SCMail")
        self._data = dict()  # tha data dictionary that most Spam Clam operations rely on
        self._spamlevel = 0  # 0..9
        if isinstance(eml_in, email.message.EmailMessage):
            self._mesg = eml_in  # a clean copy of the email.message.EmailMessage
            self._msg2data()  # fill _data with info from _mesg
        else:
            self._mesg = None

    def show(self):
        print("------ SCMail:")
        for key in ['id', 'date', 'from', 'to', 'cc', 'bcc', 'subject']:
            if self.get(key) != "":
                print((" {}: {}".format(key.ljust(16), self.get(key))))

    def showall(self):
        print("------ SCMail:")
        for key in sorted(self.keys()):
            if self.get(key) != "":
                if key != 'body':
                    print((" {}: {}".format(key.ljust(16), self.get(key))))
                else:
                    print((" {}: {}".format(key.ljust(16), "Body type/size: {} / {}".format(len(self.get(key)), type(self.get(key))))))

    def _msg2data(self):
        """ This function tries to set all the entries, from the org. message.
         Apparently msg.get('<lable>') and msg['<lable>'] is interchangeable. Try using shorter form. """
        msg = self._mesg
        try:
            pass#print("======\n{}\n------".format(str(msg)))
        except:
            pass
        # * Message-ID:
        try:
            self._data['id'] = msg['Message-ID'].strip('<>')
        except AttributeError:
            # Try to construct a Message-ID form other headers
            logger.warning("email.message seems to have no 'Message-ID'...")
            str_d = msg['date']
            str_f = msg['from']
            if str_d or str_f:
                self._data['id'] = str_d+"__"+str_f+"@ECsoftware.net"
            else:
                self._data['id'] = str(uuid.uuid4())+"@ECsoftware.net"  # random unique id
            logger.info("Assigning internal EC 'Message-ID': {}".format(self._data['id']))
        self._data['id_dom'] = self._data['id'].rsplit("@", 1)[1]
        # * date
        self._data['date'] = self._mesg['date']
        try:
            pass # parse the date...
        except ValueError:
            print("Bad date: {}".format(self._mesg['date']))
        # * from
        self._data['from'] = msg['from']
        if "<" in self._data['from']:
            self._data['from_nam'] = self._data['from'].split('<', 1)[0].strip()
            self._data['from_adr'] = self._data['from'].rsplit("<", 1)[1].strip('>')
            self._data['from_dom'] = self._data['from_adr'].rsplit("@", 1)[1]
        else:
            self._data['from_dom'] = self._data['from'].rsplit("@", 1)[1]
        # * return-path
        self._data['return-path'] = msg['return-path']
        self._data['return-path_dom'] = self._data['return-path'].rsplit("@", 1)[1].strip('>').strip()
        # * reply-to
        if 'reply-to' in msg:  # It's email.message.EmailMessage style not to use .keys()
            self._data['reply-to'] = msg['reply-to']
            self._data['reply-to_dom'] = self._data['reply-to'].rsplit("@", 1)[1].strip('>').strip()
        # * to
        self._data['to'] = msg['to']
        # * cc
        self._data['cc'] = msg['cc']
        # * bcc
        self._data['bcc'] = msg['bcc']
        # * subject
        ##dcd_sub = email.header.decode_header(msg['Subject'])
        ##self._data['subject'] = ''.join([tup[0] for tup in dcd_sub]) # It's legal to use several encodings in same header
        self._data['subject'] = msg['subject']
        # * body
        self._data['body'] = msg.get_body()
        # * size

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
        #if mkey in ['id', 'date', 'from', 'to', 'cc', 'bcc', 'subject', 'body', 'size']:
        return self._data[mkey]
        #else:
        #    return None

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