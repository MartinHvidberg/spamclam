#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Register
Defines classes: Register() and SCMail() (formerly SalMail())
The 'SCMail' object represents the SpamClam object equivalent to one e-mail.
The 'Register' object, essentially an archive of SCMails, is the central data object in all e-mail handling.
"""

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

import os
import datetime
import pickle
import uuid
import random
import email
import logging

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class SCMail(object):
    """ The 'equivalent' or 'extract' of one email.
    expects an object of type: email.message.EmailMessage
    But only the relevant parts are kept, and some more info and functions are added
    Instances are initialised with a 'real' email message.
    This object is designed to be the 'e-mail massage' to use with SpamClam. """

    def __init__(self, eml_in):
        log.debug("class init. SCMail")
        self._data = dict()  # tha data dictionary that most Spam Clam operations rely on
        self._filterres = dict()  # Dict of Filter Response objects.
        self._spamlevel = -1  # 0..9, -1 if un-set
        self._spamlevel_is_updated = True  # boolean
        self._protected = False  # If True the SCMail can't be killed, despite a high spamlevel
        self._shorthand = None  # Will only be set if SCMail becomes part of a Register
        if isinstance(eml_in, email.message.EmailMessage):
            self._mesg = eml_in  # a clean copy of the email.message.EmailMessage
            self._msg2data()  # fill _data with info from _mesg
        else:
            self._mesg = None

    def set_shorthand(self, str_shh):
        self._shorthand = str_shh

    def get_shorthand(self):
        return self._shorthand

    def set_spamlevel_from_filterres(self):
        """ Read through the filter results, and determines the final spam-level """
        if self._spamlevel == None: self._spamlevel = -1  # XXX Should never be necessary
        for frs_i in self._filterres.values():
            vote_l = frs_i.get_vote()
            self._spamlevel = max(self._spamlevel, vote_l)
        self._spamlevel_is_updated = True

    def spamlevel(self):
        """ Returns the SpamLevel of the SCMail """
        if not self._spamlevel_is_updated:  # Update the SpamLevel, before answering
            self.set_spamlevel_from_filterres()
        return self._spamlevel

    def display(self, num_level=1):
        """Displays the SCMail as text. num_level detemains the level of information."""
        str_ret = str()
        if isinstance(num_level, int):
            if num_level <= 0:
                str_ret += "{}".format(self.get_shorthand())
            elif num_level == 1:
                str_ret += "{}, {}, {}, {}".format(self.get_shorthand(), self.spamlevel(), self.get('from'), self.get('subject'))
            elif num_level == 2:
                str_ret += "{}, {}, {}".format(self.get_shorthand(), self.spamlevel(), self.get('id'))
            elif num_level == 3:
                str_ret += "{}, {}, {}, {}, {}".format(self.get_shorthand(), self.spamlevel(), self.get('id'), self.get('from'), self.get('subject'))
            if num_level in [4,5,6]:
                str_ret +=  "------ {}  {}   -------------\n".format(self.get_shorthand(), self.spamlevel())
                if num_level == 4:
                    lst_fields = ['date', 'from', 'subject']
                if num_level == 5:
                    lst_fields = ['date', 'from', 'cc', 'bcc', 'subject']
                if num_level == 6:
                    lst_fields = [key for key in self._data.keys() if (key != "" and key != 'body')]
                for key in lst_fields:
                    if self.get(key) != "":
                        str_ret +=  (" {}: {}\n".format(key.ljust(16), self.get(key)))
            else:
                log.error("Value parsed to SCMail.display() was not in legal range [0..9]")
        else:
            log.error("Value parsed to SCMail.display() was not integer")
        return str_ret

    def old_show(self):
        print("------ SCMail:")
        for key in ['id', 'date', 'from', 'to', 'cc', 'bcc', 'subject']:
            if self.get(key) != "":
                print((" {}: {}".format(key.ljust(16), self.get(key))))

    def old_showmini(self):
        print(("{}, {}, {}, {}".format(self.get_shorthand(), self.spamlevel(), self.get('from'), self.get('subject'))))

    def old_showall(self):
        print("------ {} ------ {}".format(self.get_shorthand(), self.spamlevel()))
        for key in sorted(self.keys()):
            if self.get(key) != "":
                if key != 'body':
                    print((" {}: {}".format(key.ljust(16), self.get(key))))
                else:
                    print((" {}: {}".format(key.ljust(16), "Body type/size: {} / {}".format(type(self.get(key)), len(self.get(key))))))

    def old_show_spam_status(self, minimum=1):
        """ Show the scmail id and the spam info
        if the scmail's spam-level is at least 'minimum' """
        ##print(" _ spamlevel: {}".format(self.spamlevel()))
        if self.spamlevel() >= minimum:
            print("SCMailid: {}".format(self.get('id')))
            print(" spamlev: {}".format(self.spamlevel()))
            for id_frsi in self._filterres:
                frs_i = self._filterres[id_frsi]
                print(" reasons: {}={}".format(id_frsi, frs_i.get_reasons()))

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
            log.warning("email.message seems to have no 'Message-ID'...")
            str_d = msg['date']
            str_f = msg['from']
            if str_d and str_f:
                self._data['id'] = str_d+"__"+str_f+"@ECsoftware.net"
            else:
                self._data['id'] = str(uuid.uuid4())+"@ECsoftware.net"  # random unique id
            log.info("Assigning internal EC 'Message-ID': {}".format(self._data['id']))
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
        if "@" in self._data['return-path']:
            self._data['return-path_dom'] = self._data['return-path'].rsplit("@", 1)[1].strip('>').strip()
        else:
            self._data['return-path_dom'] = self._data['return-path']
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

        for key_check in self._data.keys():
            if self._data[key_check] == None:
                self._data[key_check] = ""  # Force to "" rather than None, since it gives problems

        self._spamlevel_is_updated = False  # Maybe a little excessive here, but in rare cases...

    def keys(self):
        """ Return a list of available keys """
        return self._data.keys()

    def has_key(self, key_in):
        """ return true if a key exists, otherwise false """
        return key_in in self._data.keys()

    def get(self, mkey, nodata=None):
        """ Get one field's value """
        if self.has_key(mkey):
            return self._data[mkey]
        else:
            return nodata

    def add_filter_response(self, ftr_in):
        """ Create a new filter Response on the _filterres list.
        If the filter-response exists, it's overwritten """
        self._filterres[ftr_in['name']] = ftr_in
        self._spamlevel_is_updated = False

    def add_vote(self, filter_name, vote, fmin, fmax, reason):
        """ Adds a vote to the relevant response in _filterres
        filter_name must point to existing response
        vote, fmin, fmax must be integer [0..9]
        reason must be string """
        rsp_obj = self._filterres[filter_name]
        rsp_obj.vote(vote, fmin, fmax, reason)
        self._filterres[filter_name] = rsp_obj  # Is this really necessary? XXX
        self._spamlevel_is_updated = False

    # End of class SCMail()


class Register(object):
    """ Essentially a dict() of SCMails, with some functions to handle it ... """

    NUM_SHORTHAND_LENGTH = 3

    def __init__(self, str_infile=None):
        """ Note: Only _data is pickled """
        self._data = dict()  # dictionary of SCMails
        if str_infile:
            self.read_from_file(str_infile)

    def insert(self, scm_in):
        """ inserts a SCMail into the register """
        id = scm_in.get('id')
        if id in self.list_all():
            print("Warning: e-mail id all ready exist in register! Overwriting: {}".format(id))
        # Generate a short-hand
        str_cand = None
        while str_cand == None:
            str_cand = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(self.NUM_SHORTHAND_LENGTH))
            if str_cand in [smc.get_shorthand for smc in self._data.values()]:
                str_cand = None
        scm_in._shorthand = str_cand
        ##print("New shorthand: {}".format(scm_in._shorthand))
        self._data[id] = scm_in

    def count(self):
        """ Return number of e-mails in the register """
        return len(self._data.keys())

    def list_all(self):
        """ return a list of id's for the SCMails in the register"""
        return self._data.keys()

    def list_match(self, lst_criteria):
        """ returns a list of id's for the SCMails in the register
        that matches all the criteria in lst_criteria.
         Each criteria is string, of form "<field>=<value>" - may be extended later """
        if not isinstance(lst_criteria, list):
            print("lst_criteria not type == list, but type == {}".format(str(type(lst_criteria))))
            return []
        lst_ret = list()
        for crit in lst_criteria:
            lst_crit = crit.split("=")
            if all([len(lst_crit) == 2, all([isinstance(tok, str) for tok in lst_crit])]):
                str_fld = lst_crit[0]
                str_val = lst_crit[1]
                for scmailid in self.list_all():
                    scmail = self.get(scmailid)
                    if scmail.has_key(str_fld):
                        if scmail.get(str_fld) == str_val:
                            lst_ret.append(scmailid)
        return list(set(lst_ret))

    def list_spam(self, minimum=7, maximum=None):
        """ Returns a list of id's for the SCMails in the register
        that matches the limits of spam risk.
        General:
            0: Super clean, usually unfiltered
            1..3: Still quite clean, no serious spam suspicions
            4..6: Grey zone, my be dodgy
            7..9: Dirty and considered Spam... """
        if not isinstance(minimum, int):
            print("minimum not type == integer, but type == {}".format(str(type(minimum))))
            return []
        if maximum and not isinstance(maximum, int):
            print("maximum not type == integer, but type == {}".format(str(type(maximum))))
            return []
        lst_ret = list()
        for scmailid in self.list_all():
            scmail = self.get(scmailid)
            scmail.set_spamlevel_from_filterres()  # Update the spam level
            num_spmlvl = scmail.spamlevel()
            if num_spmlvl >= minimum:
                if num_spmlvl <= maximum or maximum == None:
                    lst_ret.append(scmailid)
        return lst_ret

    def get(self, id):
        """ return the SCMail with the given id
        if not found, then returns None """
        return self._data[id]

    def write_to_file(self, str_fn=""):
        """ writes the entire Register to a disc file """
        if str_fn == "":  # User didn't specify filename, use default
            # XXX Make sure ../register exist as a directory ...
            str_timestamp =  str(datetime.datetime.now()).split(".")[0].replace(":", "").replace("-", "").replace(" ", "_")
            str_fn = r"../register/SCreg_" + str_timestamp + ".ecscreg"
        with open(str_fn, 'wb') as fil_out:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self._data, fil_out, pickle.HIGHEST_PROTOCOL)

    def read_from_file(self, str_fn=""):
        """ fills the Register with the info from a disc file """
        # XXX Make sure ../register exist as a directory ...

        def find_newest_register():
            """ Find the newest .ecscreg file in ../register """
            str_root_dir = r"../register"
            lst_finds = list()
            for dirName, subdirList, fileList in os.walk(str_root_dir):
                for str_fn in fileList:
                    if str_fn.lower().endswith(('ecscreg')):
                        lst_finds.append(str_fn)
            if len(lst_finds) > 0:
                lst_finds.sort()
                return str_root_dir + os.sep + lst_finds[-1]
            else:
                print("No valid files found...")
                return None

        if str_fn == "":  # User didn't specify filename, get newest default file
            str_fn = find_newest_register()
        else:
            str_fn = r"../register" + os.sep + str_fn
        with open(str_fn, 'rb') as fil_in:  # XXX introduce error handle here, if file not exist
            obj_reg = pickle.load(fil_in)
        self._data = obj_reg

    # End of class Register()

if __name__ == '__main__':
    print("This unit {} can't be run, but must be called from another unit".format(__file__))

    ## test
    reg_n = Register
    lst_u = list()
    for n in range(6):
        print(reg_n._uniq_shorthand(lst_u))

# End of Python

# Music that accompanied the coding of this script:
#    Queen - Greatest hits III
#    TV2 - Sæler, Hvaler og Solskin
#    Pink Floyd - Dark side of the Moon