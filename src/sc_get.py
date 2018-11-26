#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Get module
Get e-mails from the e-mail server, and fill the Register with information.
"""

__version__ = '0.4.1'

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)

import logging
logging.basicConfig(filename='sc_get.log',
                    filemode='w',
                    level=logging.INFO, # DEBUG
                    format='%(asctime)s %(levelname)7s %(funcName)s : %(message)s')
                    # %(funcName)s
logger = logging.getLogger(__name__)
str_start = "Start: {} version: {}".format(__file__, __version__)
logger.info(str_start)

import poplib, email
from email import policy
from email import parser

import sc_register as sc_reg
import sc_debug


def get(str_srvr, str_user, str_pass, reg_sc):

    def decode_header(header):
        decoded_bytes, charset = email.header.decode_header(header)[0]
        if charset is None:
            return str(decoded_bytes)
        else:
            return decoded_bytes.decode(charset)

    def cool_msg_walker(email_parsed):  # from https://gist.github.com/strayge/f619cacb972d956ddbe1472d882821fe
        """ Taks a walk inside a email_parsed """
        for part in email_parsed.walk():
            if part.is_multipart():
                # maybe need also parse all subparts
                continue
            elif part.get_content_maintype() == 'text':
                text = part.get_payload(decode=True).decode(
                    part.get_content_charset())
                print('Text:\n', text)
            elif part.get_content_maintype() == 'application' and part.get_content_disposition() == 'attachment':
                name = decode_header(part.get_filename())
                body = part.get_payload(decode=True)
                size = len(body)
                print('Attachment: "{}", size: {} bytes, starts with: "{}"'.format(name, size, body[:50]))
            else:
                print('Unknown part:', part.get_content_type())

    # =============   Connect to POP3 server   =============================

    # Open connection to email (POP) server
    try:
        con_pop = poplib.POP3_SSL(str_srvr)  # SSL is cool
        con_pop.user(str_user)
        con_pop.pass_(str_pass)
        logger.info(str(con_pop))
        logger.info("Server says:  {}".format(con_pop.getwelcome()))
        num_tot_msgs, num_tot_bytes = con_pop.stat()
        logger.info("Mailbox holds: {} messages, {} bytes total".format(str(num_tot_msgs),str(num_tot_bytes)))
    except:
        logger.error("\nSeems to be unable to access the e-mail server...")
        print("Error - Look in the log file...")
        return

    if num_tot_msgs:
        logging.info("Start reading {} messages from server".format(num_tot_msgs))
        # We have a pop3 connection :-)
        num_email = 0  # To avoid problems with counter after this loop, if no mails found.
        dic_keys = dict()  # for key stat only
        for num_email in range(1,num_tot_msgs+1):  # pop3 server count from 1 (not from 0)
            if num_email >= 300: continue  # <------------------------------------------------------------------------------ LUS¨
            # Retreive the e-mail from the server
            email_retr = con_pop.retr(num_email)[1]  # .retr() result is in form (response, ['line', ...], octets).
            email_parsed = email.message_from_bytes(b"\n".join(email_retr), policy=email.policy.default)
            # Turn the email.massage into a SCMail
            if num_email == -1: sc_debug.analyse_parsed_email(email_parsed)  # look at one email
            scm_in = sc_reg.SCMail(email_parsed)
            scm_in.show()
            # Add the SCMail to the register
            ##reg_sc.insert(scm_in)

        # Close connection to email server
        con_pop.quit()

        # Clean major objects
        del con_pop
        del str_srvr, str_user, str_pass

        return reg_sc

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits III