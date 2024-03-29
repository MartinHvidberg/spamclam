#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Part of ECsoftware's SpamClam
The Spam Clam Command Line Interface
"""

### History
# 0.4.1 : A new start with argparse, aiming for a modularised MVP CLI product. (replaces sccli)
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

### ToDo XXX
# Consider only 'get' clears the log file, others just appends ...

import sys, os
import argparse
import logging

import sc_register
import sc_email_server
# sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'filter_karma'))
import filter_karma.karma as karma
#sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'filter_bw'))
import spmclm.filter_bw.bw as bw
#sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'filter_demo'))
import filter_demo.demo as demo

# Initialize logging
logging.basicConfig(filename='SpamClam.log',
                    filemode='w',
                    level=logging.INFO, # DEBUG
                    format='%(asctime)s %(levelname)7s %(module)8s %(funcName)16s | %(message)s')
                    # %(funcName)s
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))

def get_args():
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='cs')
    subparsers = parser.add_subparsers(dest='command', help='First argument is always a Command. Available: get, filter, view, mark, exclude, kill, clear, stat, log, config, version')
    # MVE only impliment get, view, filter, mark, kill
    # mark was earlier set, but get/set was unbalanced in function
    # ToDo XXX Consider an exclude command that removes one SCMail fra Register (but not from server) to reduse view-clutter
    # ToDo XXX config command must go, so 'c' means only 'clean/clear'
    # nargs=
    # N (an integer). N arguments from the command line will be gathered together into a list.
    # '?'. One argument will be consumed from the command line if possible, and produced as a single item. If no command-line argument is present, the value from default will be produced.
    # '*'. All command-line arguments present are gathered into a list.
    # '+'. Just like '*', all command-line args present are gathered into a list. Additionally, an error message will be generated if there wasn’t at least one command-line argument present.

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
    parser_get.add_argument('--dont_save_credentials',
                            action='store_false',
                            dest='save_cred',
                            help = "If included, the mail server credentials will not be stored.")

    # create the parser for the "filter" command
    parser_filter = subparsers.add_parser('filter', help='filter ... of e-mails available on the server')
    parser_filter.add_argument('fdo',
                            type=str,
                            nargs='?',
                            choices=['run'],  # XXX later extend the list ...
                            help = 'help filter_do xxx')
    parser_filter.add_argument('fname',
                            type=str,
                            nargs='?',
                            choices=['karma', 'bw', 'demo'],  # XXX later extend the list ...
                            help = 'help filter_name xxx')
    parser_filter.add_argument('fdetails',
                            type=str,
                            nargs='*',
                            help = 'help filter details xxx')

    # create the parser for the "view" command
    parser_view = subparsers.add_parser('view', help='view shows the e-mails that was collected by last get')
    parser_view.add_argument('vwhat',
                             nargs='?',
                             type=str,
                             choices=['spam', 'grey', 'white', 'all', 'shh'],
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
    parser_view.add_argument('shhs',
                            type=str,
                            nargs='*',
                            help = 'a list of shh')

    # create the parser for the "mark" command
    parser_get = subparsers.add_parser('mark', help='mark a mail with the given value')
    parser_get.add_argument('value',
                            nargs='?',
                            type=str,
                            choices=['0','1','2','3','4','5','6','7','8','9','s','o','p','u'],
                            help = "spam-value, spam, okay, protect or un-protect")
    parser_get.add_argument('shh',
                            nargs='+',
                            type=str,
                            help = 'one (or several) mail short-hand(s) (3-letter id)')

    # create the parser for the "kill" command
    parser_kill = subparsers.add_parser('kill', help='KILL (delte from server) all mails marked as spam, and not protected')
    parser_kill.add_argument('limit',
                            nargs='?',
                            type=int,
                            default = 7,
                            choices=[0,1,2,3,4,5,6,7,8,9],
                            help = "Kill all e-mails with this spam-value, or higher. Don't kill protected e-mails.")

    # create the parser for the "dumpasjson" command
    parser_json = subparsers.add_parser('dumpasjson', help='only for debug ...')

    # parse argument list
    args = parser.parse_args()
    return args

def main(arg_in):

    if arg_in:
        bol_okay = True  # Assume that everything is Okay, until proven wrong

        if arg_in.command == 'get':  # ------------------------ get -----------
            # Check parameters arg_in.server ,arg_in.user ,arg_in.password
            if not "@" in arg_in.guser:
                log.warning(" ! argument for 'user' is expected to contain an '@'")
                bol_okay = False
            if bol_okay:
                log.info("{} {} {} ****** ...running...".format(arg_in.command, arg_in.gserver, arg_in.guser))
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc = sc_email_server.get(arg_in.gserver ,arg_in.guser ,arg_in.gpassword, reg_sc)  # Fill register with e-mail info from server
                reg_sc.write_to_file()  # Write the new register to default filename
                if arg_in.save_cred:
                    sc_email_server.save_credentials(arg_in.gserver ,arg_in.guser ,arg_in.gpassword)
                log.info("{} {} e-mails. Done...".format(arg_in.command, reg_sc.count()))
        elif arg_in.command == 'filter':  # ------------------- filter --------
            str_filter_do = arg_in.fdo  # Should his always be a good idea, for all commands?
            str_filter_name = arg_in.fname
            if bol_okay:
                log.info("{} {} {} {} ...running...".format(arg_in.command, str_filter_do, str_filter_name, arg_in.fdetails))
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # read data from standard filename
                # Load Filter
                ftr_selected = None
                if str_filter_name == 'karma':
                    ftr_selected = karma.Karma()
                elif str_filter_name == 'bw':
                    ftr_selected = bw.BW()
                elif str_filter_name == 'demo':
                    ftr_selected = demo.Demo()
                # Parse Register through Filter
                if ftr_selected:
                    log.info("Found filter: {}".format(ftr_selected.filter_name))
                    reg_sc = ftr_selected.filter(reg_sc)
                    log.info("{} Done...".format(arg_in.command))
                    # Only for bebug XXX
                    #for scmail in reg_sc.list_all():
                    #    print("{} : {}".format(reg_sc.get(scmail).get_shorthand(), reg_sc.get(scmail).get_spamlevel()))
                    reg_sc.write_to_file()
                    log.info("{} {} e-mails Done...".format(arg_in.command, reg_sc.count()))
                else:
                    log.warning("The filename was not matched by any filer: {}".format(str_filter_name))
        elif arg_in.command == 'view':  # --------------------- view ----------
            if bol_okay:
                log.info("{} ...running...".format(arg_in.command))
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # Load data into register
                # View Register
                if arg_in.vwhat == 'all':  # 'spam', 'grey', 'white', 'all', 'shh'
                    for scmail_id in reg_sc.list_all():
                        print(("{}".format(reg_sc.get(scmail_id).display(arg_in.verbose))))
                elif arg_in.vwhat == 'shh':
                    for scmail_id in reg_sc.list_shh(arg_in.shhs):
                        print(("{}".format(reg_sc.get(scmail_id).display(arg_in.verbose))))
                elif arg_in.vwhat == 'spam':
                    for scmail_id in reg_sc.list_spam():
                        print(("{}".format(reg_sc.get(scmail_id).display(arg_in.verbose))))
                elif arg_in.vwhat == 'white':
                    pass
                elif arg_in.vwhat == 'grey':
                    pass
                str_msg = "... e-mails now available: {}".format(reg_sc.count())
                log.info(str_msg)
                print(str_msg)
                log.info("{} {} e-mails Done...".format(arg_in.command, reg_sc.count()))
        elif arg_in.command == 'mark':  # --------------------- mark ----------
            if bol_okay:
                log.info("{} ...running...".format(arg_in.command))
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # Load data into register
                lst_mails = list()
                for scmid in reg_sc.list_all():
                    scm = reg_sc.get(scmid)
                    if scm.get_shorthand() in arg_in.shh:
                        lst_mails.append(scm)
                if len(lst_mails) > 0:
                    for scmail in lst_mails:
                        # 1'st check spam-level options
                        num_val = None
                        if isinstance(arg_in.value, int):
                            num_val = arg_in.value
                        else:
                            if arg_in.value in ['0','1','2','3','4','5','6','7','8','9']:
                                try:
                                    num_val = int(arg_in.value)
                                except ValueError:
                                    log.warning("Strange conversion error ... arg_in.value = {}".format(arg_in.value))
                            elif arg_in.value == 's':  # Spam
                                num_val = 7  # Default. All spam-level >= 7 is considered Spam!
                            elif arg_in.value == 'o':  # Okay
                                num_val = 0
                            log.info("set: '{}' num_val = {}".format(scmail.get_shorthand(), num_val))
                        if num_val != None:  # Note: integer 0 is a legal value!
                            scmail.set_spamlevel(num_val)  # This is setting the new spamlevel in the lecal copy
                            log.info("set: '{}' spamlevel = {}".format(scmail.get_shorthand(), scmail.get_spamlevel()))
                        # 2'nd check protection-options
                        if arg_in.value == 'p':
                            scmail.protect()
                        elif arg_in.value == 'u':
                            scmail.unprotect()
                        # return the local SCMail to the Register
                        log.info("local: '{}' spamlevel = {} protected = {}".format(scmail.get_shorthand(), scmail.get_spamlevel(), scmail._protected))
                        reg_sc.insert(scmail)
                        reg_sc.write_to_file()
                else:
                    str_msg = "Found no hit for: {}. No SCMails were marked!".format(arg_in.shh)
                    log.warning(str_msg)
                    print(str_msg)
        elif arg_in.command == 'kill':  # --------------------- kill ----------
            if bol_okay:
                log.info("{} ...running...".format(arg_in.command))
                # Load credentials
                dic_cred = sc_email_server.get_credentials()
                # Load Register
                reg_sc = sc_register.Register()  # Build empty register
                reg_sc.read_from_file()  # Load data into register
                for scmail in reg_sc.list_doomed(arg_in.limit):
                    scm_doomed = reg_sc.get(scmail)
                    print(("KILL: {}".format(scm_doomed.display(1))))
                    # Kill on server
                    sc_email_server.del_this_email(dic_cred['server'], dic_cred['user'], dic_cred['passw'], scm_doomed)
                    #Remove it from Register
                    if reg_sc.remove(scm_doomed.get('id')):
                        pass
                    else:
                        log.warning("Couldn't remove from Register the doomed SCMail with id: {}".format(scm_doomed.get('id')))
                reg_sc.write_to_file()
        elif arg_in.command == 'version':  # ------------------ version -------
            print("Not implemented, yet...")  # XXX consider changing to flag --version
            #print("SpamClam - Command Line Interface. Version {}".format(__version__))
        else:
            print("You should never see this, because that would mean that get_args() have parsed a command that isn't implemented...")
    else:
        log.error("function get_args() returned None ...")

if __name__ == '__main__':

    print(f"sys_path: {sys.path}")
    print(f"PYTOPATH: {os.environ['PYTHONPATH']}")

    arg_in = get_args()
    print(("CLI arg: {}".format(arg_in)))
    # log.info("CLI args: {}".format(args))  # This may store passwords in .log !!!
    main(arg_in)

# End of Python

# Music that accompanied the coding of this script:
#   Queen - Greatest hits I
#   Dire Straits - on shuffle

