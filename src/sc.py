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
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='cs')
    ##parser.add_argument('--foo', action='store_true', help='foo help')  # arguments to general command
    subparsers = parser.add_subparsers(dest='command', help='First argument is always a Command. Available: get, filter, view, mark, exclude, kill, clear, stat, log, config, version')
    # MVE only impliment get, view, filter, mark, kill
    # mark was earlier set, but get/set was unbalanced in function
    # ToDo XXX Consider an exclude command that removes one SCMail fra Register (but not from server) to reduse view-clutter
    # ToDo XXX config command must go, so 'c' means only 'clean'

    # create the parser for the "get" command
    parser_get = subparsers.add_parser('get', help='get collects a list of e-mails available on the server')
    parser_get.add_argument('gserver',
                            type=str,
                            help = 'your e-mail server, e.g. mail.company.com')
    parser_get.add_argument('guser',
                            type=str,
                            help = 'Your e-mail user name, e.g. bill@company.com')
    parser_get.add_argument('gpassword',
                            type=str,
                            help = 'Your secret e-mail pasword, e.g. Fu6hx!2Z')

    # create the parser for the "view" command
    parser_view = subparsers.add_parser('view', help='view shows the e-mails that was collected by last get')
    parser_view.add_argument('vwhat',
                             type=str,
                             choices=['spam', 'gray', 'white', 'all', 'shh'],
                             help = '')
    parser_view.add_argument('--verbose',
                             nargs='?',
                             type=int,
                             default = 5,
                             #choices=['tiny', 'mini', 'normal', ...],
                             help = """verbose: [0..9] where 9 is most info. Default is 5')
                             # 0: Only short-hand (shh)
                             # 1: One-liner       (shh, from, subj) * good for overview
                             # 2: One-liner       (shh, id)
                             # 3: One-liner       (shh, id, from, subj)
                             # 4: Multi-liner     (shh, +few param)
                             # 5: Multi-liner     (shh, +default param) * This is deafult
                             # 6: Multi-liner     (shh, +all param)
                             # 7: Very much info  (shh, +all param +orig. e-mail)
                             # 8: VERY much info  (shh, +all param +orig. e-mail +all attacments)
                             # 9: VERY MUCH INFO  (shh, +all param +orig. e-mail +all attacments +all else)""")
    # parse argument list
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    arg_in = get_args()
    print("CLI arg: {}".format(arg_in))
    # log.info("CLI args: {}".format(args))  # This may store passwords in .log !!!

    if arg_in:
        bol_okay = True  # Assume that everything is Okay, until proven wrong

        if arg_in.command == 'get':
            # Check parameters arg_in.server ,arg_in.user ,arg_in.password
            if not "@" in arg_in.guser:
                log.warning(" ! argument for 'user' is expected to contain an '@'")
                print("! Warning in .log")
                bol_okay = False
            if bol_okay:
                log.info("{} {} {} ****** ...running...".format(arg_in.command, arg_in.gserver, arg_in.guser))
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc = sc_get.get(arg_in.gserver ,arg_in.guser ,arg_in.gpassword, reg_sc)  # Fill register with e-mail info from server
                reg_sc.write_to_file()  # Write the new register to default filename
                log.info("{} {} e-mails. Done...".format(arg_in.command, reg_sc.count()))

        elif arg_in.command == 'filter':
            str_filter_do = arg_in.fdo[0]
            str_filter_name = arg_in.fname[0]
            if bol_okay:
                log.info("{} {} {} {} ...running...".format(arg_in.command, str_filter_do, str_filter_name, arg_in.fdetails))
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # read data from standard filename
                # Load Filter
                if str_filter_name == 'karma':
                    ftr_selected = karma.Karma()
                elif str_filter_name == 'classic':
                    ftr_selected = classic.Classic()
                # Parse Register through Filter
                if ftr_selected:
                    log.info("Found filter: {}".format(ftr_selected.str_filter_name))
                    reg_sc = ftr_selected.filter(reg_sc)
                    log.info("{} Done...".format(arg_in.command))
                    # Only for bebug XXX
                    for scmail in reg_sc.list_all():
                        reg_sc.get(scmail).show_spam_status()
                else:
                    log.warning("The filename was not matched by any filer: {}".format(str_filter_name))

        elif arg_in.command == 'view':
            ##print('(view, okay: {})'.format(bol_okay))
            if bol_okay:
                log.info("{} ...running...".format(arg_in.command))
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # Load data into register
                # View Register
                for scmail_id in reg_sc.list_all():
                    print("{}".format(reg_sc.get(scmail_id).display(arg_in.verbose)))
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
            print("Not implemented, yet...")  # XXX consider changing to flag --version
            #print("SpamClam - Command Line Interface. Version {}".format(__version__))

        else:
            print("You should never see this, because that would mean that get_args() have parsed a command that isn't implemented...")
    else:
        log.error("function get_args() returned None ...")

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits I

