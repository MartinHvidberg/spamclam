
""" Part of ECsoftware's SpamClam
    This module handles: Connection to the email server, and is the main (non-ui) module
"""

### Versions ###
# 0.1 - The initial tries, that worked :-)
# 0.2 - Trying to make it OOP and insisting on modularizing
# 0.3 - Introducing Statistics
# 0.3.1 intro stat by rule

### ToDo
# Forward to spamclam_myuser@mydomain.tld

__verion__ = '0.3.1'
__build__ = '20180624.'

### To do ###
# make header print uft-8 eller noget...
# introduce prof command line parameters, though sccli takes care of some cli
# remove remaining print sentences, this is not a ui-module

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

def spamclam_a_pop3_mailbox(str_srvr, str_user, str_pass, str_mode, str_wob, restat='False'):

    # =============   Connect to POP3 server   =============================

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

    # =============   Spamalyse   ==========================================

    # Create Spamalyser object(s)
    salysr_sbw = spamalyse.Spamalyser(str_mode, 'mode_simple_bw/', str_wob)  # Consider moving WOB to simple_bw.py
    ##salysr_sbw.show_rules()  ## only for debug - a non ui-module should not use print, nor pp

    # Create a Statistics object
    salsta = spamstat.Spamstat()

    # =============   Run   ================================================"

    ##print "{}".format(con_pop.list()[0])  # XXX This is a non-ui module, to be called from cli and gui alike.

    num_email = 0  # To avoid problems with counter after this loop, if no mails found.
    for num_email in range(1,num_tot_msgs+1):  # pop server count from 1 (not from 0)
        email_raw = con_pop.retr(num_email)
        email_string = "\n".join(email_raw[1])
        msg = email.message_from_string(email_string)
        #print "------- HDR e-mail --------------"
        #print num_email, "date:", msg.get('date'),  "from:", msg.get('from'), "subj:", msg.get('subject')  # XXX Before salmsg
        #print "------- raw e-mail --------------"
        #print msg
        #print "------- raw e-mail --------------"

        # ** Turn the email.massage into a spamalyse.Salmsg
        salmsg = spamalyse.Salmail(msg)
        #salmsg.show()

        # ** Check the salmsg for 'spam'
        logger.debug("Email: {}; {}".format(salmsg.get('from'),salmsg.get('subject')))
        sal_res_sbw = salysr_sbw.is_spam(salmsg)

        # Actually delete the e-mail, and write to log file
        logger.info("Email: [{}] {} {}; {}".format(num_email, sal_res_sbw['spam'], salmsg.get('from'),salmsg.get('subject')))
        if sal_res_sbw['spam']:
            logger.info("  hit: {}".format(sal_res_sbw['votb']))  # if it's spam print the proof, which must be black...
            print "  hit: {}".format(sal_res_sbw['votb'])

            # ** Actually delete the file (on some pop3 servers this do not really happen until we log out...)
            con_pop.dele(num_email)  # <-------------------------------------------------------------------- LUS

        # ** send this email, and sal_res_sbw to the stat object
        salsta.add_salres(salmsg, sal_res_sbw, restat=restat)

    # Close connection to email server
    con_pop.quit()

    # Close statistics collector
    #for line in salsta.show(sort='spam'): # sort: 'spam', 'rule_hits', 'no_rules', 'cnt', 'cnt_spam'
    #    print "stat > ", line
    salsta.close()

    # Clean major objects
    del con_pop
    del salysr_sbw
    del salsta
    del str_srvr, str_user, str_pass

    return [num_email]  # List of return elements can be expanded later...


# Music that accompanied the coding of this script:
#   David Bowie - Best of...
#   Buena Vista Social Club - Buena Vista Social Club