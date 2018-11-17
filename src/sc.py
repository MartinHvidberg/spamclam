""" Part of ECsoftware's SpamClam
    The Spam Clam Command Line Interface (replaces sccli)
"""

import argparse


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
    print("comm: {}".format(arg_comm))
    print("rest: {}".format(arg_rest))
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
                            choices = ['spam', 'gray', 'white'],
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
    args = parser.parse_args()
    print("args: {}".format(args))
    return args


if __name__ == '__main__':
    arg_in = get_args()

    print("arg: {}".format(arg_in))