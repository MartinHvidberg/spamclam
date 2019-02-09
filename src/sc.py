#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Command Line Interface
"""

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

import sys, os
import argparse
import logging

import sc_register
import sc_get
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'filter_karma'))
import karma
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'filter_classic'))
import classic

# Initialize logging
logging.basicConfig(filename='SpamClam.log',
                    filemode='w',
                    level=logging.INFO, # DEBUG
                    format='%(asctime)s %(levelname)7s %(funcName)s >> %(message)s')
                    # %(funcName)s
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))

def get_args():
    """ Getting and handling command line arguments. """
    parser = argparse.ArgumentParser(
        description = "SpamClam's Command Line Interface.",
        epilog = "/ ECsoftware",
        allow_abbrev = True
    )
    parser.add_argument('command',
                        choices=['get', 'filter', 'view', 'set', 'kill', 'clear', 'stat', 'log', 'config', 'version'], #ssccvv
                        help='The main command, i.e. what you want sc to do')
    arg_comm, arg_rest = parser.parse_known_args()
    ##print("CLI comm: {}".format(arg_comm))
    ##print("CLI rest: {}".format(arg_rest))
    if arg_comm.command == 'get':  # ------ get -------------------------------
        parser.add_argument('server',
                           help = 'your e-mail server, e.g. mail.company.com')
        parser.add_argument('user',
                            help = 'Your e-mail user name, e.g. bill@company.com')
        parser.add_argument('password',
                            help = 'Your secret e-mail pasword, e.g. Fu6hx!2Z')
    elif arg_comm.command == 'filter':  # ------ filter -----------------------
        parser.add_argument('fdo',
                            choices = ['run', 'form'],
                            nargs = 1,
                            help = 'What you want to do with the filter, e.g. run')
        parser.add_argument('fname',
                            choices = ['classic', 'karma'],
                            nargs = 1,
                            help = 'Name of the filter you want to run, e.g. karma')
        parser.add_argument('--fdetails',
                            nargs = '*',
                            help = 'More options, specific to the selected filter')
    elif arg_comm.command == 'view':  # ------ view ---------------------------
        parser.add_argument('vlevel',
                            choices = ['spam', 'gray', 'white', 'all'],
                            nargs = '+',
                            help = 'What do you want to view, e.g. spam gray')
    elif arg_comm.command == 'set':  # ------ set ----------------------------
        parser.add_argument('sval',
                            choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'o', 's', 'p', 'u'],
                            nargs = 1,
                            help = 'What value do you want to apply to an e-mail (0..9,o,s,p,u) for spam-level, okay, spam, protected or un-protected')
        parser.add_argument('smails',
                            metavar = 'mail#',
                            nargs = '+',
                            help = 'list of e-mail numbers you wat to apply to, e.g. 7 9 13')
    elif arg_comm.command == 'kill':  # ------ kill ---------------------------
        parser.add_argument('klevel',
                            nargs = '?',
                            choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'spam'],
                            default = 'spam',
                            help = 'To what level do you want to kill (0..9) or spam, where spam is synonym with 7. Default is spam')
    elif arg_comm.command == 'version':  # ------ version ---------------------
        pass  # XXX consider changing to flag --version
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    arg_in = get_args()
    print("CLI arg: {}".format(arg_in))
    # log.info("CLI args: {}".format(args))  # This may store passwords in .log !!!

    bol_okay = True  # Assume that everything is Okay, until proven wrong

    if arg_in.command == 'get':
        # Check parameters arg_in.server ,arg_in.user ,arg_in.password
        if not "@" in arg_in.user:
            log.warning(" ! argument for 'user' is expected to contain an '@'")
            print("! Warning in .log")
            bol_okay = False
        if bol_okay:
            log.info("{} {} {} ****** ...running...".format(arg_in.command, arg_in.server, arg_in.user))
            reg_sc = sc_register.Register()  # Build empty register
            reg_sc = sc_get.get(arg_in.server ,arg_in.user ,arg_in.password, reg_sc)  # Fill register with e-mail info from server
            reg_sc.write_to_file()  # Write the new register to default filename
            log.info("{} {} e-mails. Done...".format(arg_in.command, reg_sc.count()))

    elif arg_in.command == 'filter':
        str_filter_do = arg_in.fdo[0]
        str_filter_name = arg_in.fname[0]
        if bol_okay:
            log.info("{} {} {} {} ...running...".format(arg_in.command, str_filter_do, str_filter_name, arg_in.fdetails))
            # Load Register
            reg_sc = sc_register.Register()  # Build empty register
            reg_sc.read_from_file()
            # Load Filter
            if str_filter_name == 'karma':
                ftr_selected = karma.Karma()
            elif str_filter_name == 'classic':
                ftr_selected = classic.Classic()
            # Parse Register through Filter
            reg_sc = ftr_selected.filter(reg_sc)
            log.info("{} Done...".format(arg_in.command))
            # Only for bebug XXX
            for scmail in reg_sc.list_all():
                reg_sc.get(scmail).show_spam_status()

    elif arg_in.command == 'view':
        if bol_okay:
            log.info("{} ...running...".format(arg_in.command))
            # Load Register
            reg_sc = sc_register.Register()  # Build empty register
            reg_sc.read_from_file()
            # View Register
            for scmail_id in reg_sc.list_all():
                reg_sc.get(scmail_id).showmini()
            str_msg = "... e-mails now available: {}".format(reg_sc.count())
            log.info(str_msg)
            print(str_msg)
            log.info("{} {} e-mails Done...".format(arg_in.command, reg_sc.count()))

    elif arg_in.command == 'set':
        if bol_okay:
            pass

    elif arg_in.command == 'kill':
        if bol_okay:
            pass

    elif arg_in.command == 'version':
        print("SpamClam - Command Line Interface. Version {}".format(__version__))

    else:
        print("You should never see this, because that would mean that get_args() have parsed a command that isn't implemented...")

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits I

