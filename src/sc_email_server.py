#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Get module
Get e-mails from the e-mail server, and fill the Register with information.
"""

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

import logging
import json

import poplib, email
from email import policy

from . import sc_register

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))

def save_credentials(gserver ,guser ,gpassword):
    """ Saves the e-mail server credentials in a file.
    ToDo XXX This needs way more encryption ... """
    dic_cred = {'server':gserver, 'user':guser, 'passw':gpassword}
    with open('cred.json', 'w') as filj:
        filj.write(json.dumps(dic_cred))

def get_credentials():
    """ Reads the e-mail server credentials from a file """
    with open('cred.json', 'r') as filj:
        dic_cred = json.load(filj)
    return dic_cred

def connect_pop3(str_srvr, str_user, str_pass):
    """ Connect to a POP3 server
    :param str_srvr: server
    :param str_user: user name
    :param str_pass: user password
    :return: pop3 connection obj.
    """
    try:
        con_pop = poplib.POP3_SSL(str_srvr)  # SSL is cool
        con_pop.user(str_user)
        con_pop.pass_(str_pass)
        log.info(str(con_pop))
        log.info("Server says:  {}".format(con_pop.getwelcome()))
        num_tot_msgs, num_tot_bytes = con_pop.stat()
        log.info("Mailbox holds: {} messages, {} bytes total".format(str(num_tot_msgs),str(num_tot_bytes)))
    except:
        log.error("\nSeems to be unable to access the e-mail server...")
        print("Error - Look in the log file...")
        return None
    return con_pop

def get(str_srvr, str_user, str_pass, reg_sc):
    con_pop = connect_pop3(str_srvr, str_user, str_pass)
    if con_pop:
        num_tot_msgs, num_tot_bytes = con_pop.stat()
    else:
        return None

    if num_tot_msgs:
        logging.info("Start reading {} messages from server".format(num_tot_msgs))
        # We have a pop3 connection :-)
        num_email = 0  # To avoid problems with counter after this loop, if no mails found.
        dic_keys = dict()  # for key stat only
        for num_email in range(1,num_tot_msgs+1):  # pop3 server count from 1 (not from 0)
            if num_email >= 9999: continue  # short-hand have 26^3 = 17576 kombinations. We stop a bit before that
            # Retreive the e-mail from the server
            email_retr = con_pop.retr(num_email)[1]  # .retr() result is in form (response, ['line', ...], octets).
            email_parsed = email.message_from_bytes(b"\n".join(email_retr), policy=email.policy.default)
            scm_in = sc_register.SCMail(email_parsed)
            # Add the SCMail to the register
            reg_sc.insert(scm_in)
        # Close connection to email server
        con_pop.quit()
        # Clean major objects
        del con_pop
        del str_srvr, str_user, str_pass
        return reg_sc

def del_this_email(str_srvr, str_user, str_pass, scm_kill):
    """ Find and delete the given SCMail from the server """
    con_pop = connect_pop3(str_srvr, str_user, str_pass)
    if con_pop:
        num_tot_msgs, num_tot_bytes = con_pop.stat()
    else:
        return None

    if num_tot_msgs:
        logging.info("Start reading {} messages from server".format(num_tot_msgs))
        for num_email in range(1,num_tot_msgs+1):  # pop3 server count from 1 (not from 0)
            ##log.info("email # {}".format(num_email))
            if num_email >= 9999: continue  # short-hand have 26^3 = 17576 kombinations. We stop a bit before that
            email_retr = con_pop.retr(num_email)[1]  # .retr() result is in form (response, ['line', ...], octets).
            ##log.info("email r {}".format(email_retr))
            email_parsed = email.message_from_bytes(b"\n".join(email_retr), policy=email.policy.default)
            scm_cand = sc_register.SCMail(email_parsed)
            # Match on datetime, from and subject. ID may be empty for many spam e-mails
            if scm_cand.get('date') == scm_kill.get('date'):
                if scm_cand.get('from') == scm_kill.get('from'):
                    if scm_cand.get('subject') == scm_kill.get('subject'):
                        # We assume this is the right email to delete
                        log.info("Killing email: {}, with date: {} from: {} subj.: {}".format(num_email,
                                    scm_kill.get('date'), scm_kill.get('from'), scm_kill.get('subject')))
                        con_pop.dele(num_email)
    con_pop.quit()

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits III