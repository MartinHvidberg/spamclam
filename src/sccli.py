
Replaced by sc.py

""" Part of ECsoftware's SpamClam
    This module handles CLI (Command Line Interface) to SpamClam

    commands:

    get  - copy/download info about emails on server, to local data base
    list - list info in local data base
    simp - run 'simple black and white' filter, on local data base
    ussu - run 'usual suspects' filter, on local data base (in development)
    male - run 'machine learning' filter, on local data base (not available yet)
    kill - actually delete the messages pointed out by the filter(s)

    options:

    --help :
    --version :

    connecting to the email server (used by get and kill)
    --server : the email servers name, e.g. mail.company.com
    --user : user name on the email server, e.g. john@company.com
    --passw : password on the email server

    specific to list
    --spam : show emails marked as spam, by at least one filter
    --grey : show emails with a 'grey' status
    --white : show emails with white status, i.e. not tagged by any filter

    specific for simple-black-and-white filter
    --swob : simple-White-over-black. Default is true, i.e. white overrules black
    --srestat : simple-ReStat. Force stats to be wiped. Default is false

    specific for usual-suspects filter
    --usite1 : include site-1 in filter
    --usite2 : include site-2 in filter

    specific for kill
    --min : minimum number of filters that says kill. Default is all

"""

import sys

import argparse
from . import spamclam


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='SpamClam CLI interface')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0')
    parser.add_argument("command")
    args = parser.parse_args()

"""  OLD VERSION

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
    print "Usage: spamclam.py <server> <user> <password> [mode] [wob] [restat]"
    print "Default values: mode=simple, wob=true restat=false"
    print "e.g.   spamclam.py mailserver.company.com my_name@company.com qwerty simple"
    print "Note:  All other settings are controlled by spamalyse.config and the files in mode_*/"
    sys.exit(101)

print "Calling ECsoftware SpamClam, with: \n\tServer: {}\n\tUser: {}\n\tPassw: {}\n\tMode: {}\n\tWob: {}\n\tRestat: {}".format(str_srvr, str_user, '******', str_mode, str_wob, str_restat)

scresu = spamclam.spamclam_a_pop3_mailbox(str_srvr, str_user, str_pass, str_mode, str_wob, restat=str_restat.lower()=='true')

print "\nProcessed {} e-mails\n".format(scresu[0])

"""