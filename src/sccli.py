
""" Part of ECsoftware's SpamClam
    This module handles
"""

import sys

import spamclam


# Read the command line input
try:
    str_srvr = sys.argv[1]
    str_user = sys.argv[2]
    str_pass = sys.argv[3]
    if len(sys.argv) > 4:
        str_mode = sys.argv[4]
    else:
        str_mode = "simple" # Default mode is 'simple black and white (lists)'
    if len(sys.argv) > 5:
        str_wob = sys.argv[5]
    else:
        str_wob = 'True' # Default wob=true, i.e. white overrules black
    if len(sys.argv) > 6:
        str_rescan = sys.argv[6]
    else:
        str_rescan = 'False' # Default is to NOT scan old massages, set to true to enforce new rules on old e-mails.
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print "Usage: spamclam.py <server> <user> <password> [mode]"
    print "e.g.   spamclam.py mailserver.company.com my_name@company.com qwerty simple"
    print "Note:  All other settings are controlled by spamalyse.config and the files in mode_*/"
    sys.exit(101)

print "Calling ECsoftware SpamClam, with: \n\tServer: {}\n\tUser: {}\n\tPassw: {}\n\tMode: {}\n\tWob: {}\n\tRescan: {}".format(str_srvr, str_user, '******', str_mode, str_wob, str_rescan)
spamclam.spamclam_a_pop3_mailbox(str_srvr, str_user, str_pass, str_mode, str_wob, rescan=str_rescan.lower()=='true')
