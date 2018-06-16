
""" Part of ECsoftware's SpamClam
    This module handles: ...
"""

### Versions ###
# 0.1 - The initial tries, that worked :-)
# 0.2 - Trying to make it OOP and insisting on modularizing
# 0.3 - Introducing Statistics

### To do ###
# make header print uft-8 eller noget...
# introduce prof command line parameters, though sccli takes care of some cli

__verion__ = '0.3.0'
__build__ = '20180616.'

import sys
import logging
logging.basicConfig(filename='spamalyse.log',
                    filemode='w',
                    level=logging.INFO, # DEBUG
                    format='%(asctime)s %(levelname)7s %(funcName)s : %(message)s')
                    # %(funcName)s
logger = logging.getLogger('spamclam')
str_start = "Start: {} version: {} build: {}".format(sys.argv[0], __verion__, __build__)
logger.info(str_start)

import poplib, email, email.header

import spamalyse, spamstat

def spamclam_a_pop3_mailbox(str_srvr, str_user, str_pass, str_mode, str_wob):

    print "\n=============   Connect to POP3 server   ============================="  # XXX This is a non-ui module, to be called from cli and gui alike.

    # Open connection to email (POP) server
    try:
        con_pop = poplib.POP3(str_srvr)
        con_pop.user(str_user)
        con_pop.pass_(str_pass)
        print "Server says:  "+con_pop.getwelcome()
        num_tot_msgs, num_tot_bytes = con_pop.stat()
        print "Mailbox stat:\n  {} messages\n  {} bytes total".format(str(num_tot_msgs),str(num_tot_bytes))
    except:
        print "\nSeems to be unable to access the e-mail server..."
        sys.exit(102)

    print "\n=============   Spamalyse   =========================================="  # XXX This is a non-ui module, to be called from cli and gui alike.

    # Create a Spamalyser object
    salysr = spamalyse.Spamalyser(str_mode, 'mode_simple_bw/', str_wob)  # Consider moving WOB to simple_bw.py

    # Create a Statistics object
    salsta = spamstat.Spamstat()

    print "\n=============   Run   ================================================"  # XXX This is a non-ui module, to be called from cli and gui alike.

    dic_trr = dict()  # dic_this_runs_results
    print "{}".format(con_pop.list()[0])  # XXX This is a non-ui module, to be called from cli and gui alike.

    num_email = 0  # To avoid problems with counter after this loop, if no mails found.
    for num_email in range(1,num_tot_msgs+1): # 68,74): # # pop server count from 1 (not from 0)
        email_raw = con_pop.retr(num_email)
        email_string = "\n".join(email_raw[1])
        msg = email.message_from_string(email_string)
        ##print num_email, "from:", msg.get('from'), "subj:", msg.get('subject')  # XXX Before salmsg

        # ** Turn the email.massage into a spamalyse.Salmsg
        salmsg = spamalyse.Salmail(msg)
        #salmsg.show()

        # ** Check the salmsg for 'spam'
        logger.debug("Email: {}; {}".format(salmsg.get('from'),salmsg.get('subject')))
        sal_res = salysr.is_spam(salmsg)

        # write to log file
        logger.info("Email: [{}] {}; {} = {}".format(num_email, salmsg.get('from'),salmsg.get('subject'), sal_res['spam']))
        if sal_res['spam']:
            logger.info("  hit: {}".format(sal_res['stmb']))  # if it's spam print the proof, which must be black...

            # ** Actually delete the file (on some pop3 servers this do not really happen until we log out...)
            print "[{}] {}; {}; {} {}".format(num_email, salmsg.get('from'),salmsg.get('subject'), sal_res['tone'], sal_res['kill'])  # XXX This is a non-ui module, to be called from cli and gui alike.
            # Actually delete the e-mails on the server
            #ovod.lithium
            #con_pop.dele(num_email)  # <-------------------------------------------------------------------- Here...

        # ** Collect info for later Stats
        dic_trr[num_email] = {'salmail': salmsg, 'salresu': sal_res}
        # ** send this email, and sal_result to the stat object
        salsta.add_salres(salmsg, sal_res)

    print "\nProcessed {} e-mails\n".format(num_email)  # XXX This is a non-ui module, to be called from cli and gui alike.

    ##print "\n=============   Closing e-mail server connection   ==================="

    # Close connection to email server
    con_pop.quit()

    # Close statistics collector
    salsta.close()

    # Clean major objects
    del con_pop
    del salysr
    del salsta
    del str_srvr, str_user, str_pass


##print "\n=============   Done...   ============================================"

# Music that accompanied the coding of this script:
#   David Bowie - Best of...
#   Buena Vista Social Club - Buena Vista Social Club