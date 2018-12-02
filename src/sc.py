#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Command Line Interface
"""

__version__ = '0.4.1'

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)

import argparse

import sc_register
import sc_get


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
        parser.add_argument('filter_activity',
                            choices = ['run', 'form'],
                            help = 'What you want to do with the filter, e.g. run')
    elif arg_comm.command == 'view':  # ------ view ---------------------------
        parser.add_argument('view_level',
                            choices = ['spam', 'gray', 'white', 'all'],
                            nargs = '+',
                            help = 'What do you want to view, e.g. spam gray')
    elif arg_comm.command == 'set':  # ------ set ----------------------------
        parser.add_argument('set_value',
                            choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'o', 's', 'p', 'u'],
                            nargs = 1,
                            help = 'What value do you want to apply to an e-mail (0..9,o,s,p,u) for spam-level, okay, spam, protected or un-protected')
        parser.add_argument('set_mailnumb',
                            metavar = 'mail#',
                            nargs = '+',
                            help = 'list of e-mail numbers you wat to apply to, e.g. 7 9 13')
    elif arg_comm.command == 'kill':  # ------ kill ---------------------------
        parser.add_argument('kill_level',
                            nargs = '?',
                            choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'spam'],
                            default = 'spam',
                            help = 'To what level do you want to kill (0..9) or spam, where spam is synonym with 7. Default is spam')
    elif arg_comm.command == 'version':  # ------ version ---------------------
        pass  # XXX consider changing to flag --version
    args = parser.parse_args()
    ##print("CLI args: {}".format(args))
    return args


if __name__ == '__main__':

    arg_in = get_args()
    ##print("CLI arg: {}".format(arg_in))

    if arg_in.command == 'get':
        print("SpamClam get : running...")
        # deal with --logmode
        reg_sc = sc_register.Register()  # Build empty register
        reg_sc = sc_get.get(arg_in.server ,arg_in.user ,arg_in.password, reg_sc)  # Fill register with e-mail info from server
        reg_sc.write_to_file()  # Write the new register to default filename
        print("SpamClam get : {} e-mails. Done...".format(reg_sc.count()))
    elif arg_in.command == 'filter':
        pass
    elif arg_in.command == 'view':
        print("SpamClam view : running...")
        reg_sc = sc_register.Register()  # Build empty register
        reg_sc.read_from_file()
        for scmail_id in reg_sc.list():
            reg_sc.get(scmail_id).showmini()
        print("... e-mails now available: {}".format(reg_sc.count()))
        print("SpamClam view : Done...".format(reg_sc.count()))
    elif arg_in.command == 'set':
        pass
    elif arg_in.command == 'kill':
        pass
    elif arg_in.command == 'version':
        print("SpamClam - Command Line Interface. Version {}".format(__version__))
    else:
        print("You should never see this, because that would mean that get_args() have parsed a command that isn't implemented...")

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits I