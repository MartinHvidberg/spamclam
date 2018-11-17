
""" Part of ECsoftware's SpamClam
    This module handles CLI (Command Line Interface) to SpamClam

    version 0.1, i.e. before introducing argparse
    Don't use this, go find a newer version
"""

OLD version!

import sys

from . import spamclam

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
        str_restat = sys.argv[6]
    else:
        str_restat = 'False' # Default is to NOT scan old massages, set to True to enforce new statistics on old e-mails.
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print("Usage: spamclam.py <server> <user> <password> [mode] [wob] [restat]")
    print("Default values: mode=simple, wob=true restat=false")
    print("e.g.   spamclam.py mailserver.company.com my_name@company.com qwerty simple")
    print("Note:  All other settings are controlled by spamalyse.config and the files in mode_*/")
    sys.exit(101)

print("Calling ECsoftware SpamClam, with: \n\tServer: {}\n\tUser: {}\n\tPassw: {}\n\tMode: {}\n\tWob: {}\n\tRestat: {}".format(str_srvr, str_user, '******', str_mode, str_wob, str_restat))

scresu = spamclam.spamclam_a_pop3_mailbox(str_srvr, str_user, str_pass, str_mode, str_wob, restat=str_restat.lower()=='true')

print("\nProcessed {} e-mails\n".format(scresu[0]))
