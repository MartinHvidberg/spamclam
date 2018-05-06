
"""
Dealing with spam e-mails
"""

### Versions ###
# 0.1 - The initial tries, that worked :-)
# 0.2 - Trying to make it OOP and insisting on modularizing

### To do ###
# make header print uft-8 eller noget...
# introduce prof command line parameters

__verion__ = '0.2.2'
__build__ = '20171020.'

import sys
import logging
import poplib, email, email.header

import spamalyse

sys.path.insert(0, "../../EC_stuff/ec_base/")
import ec_help

str_start = "Start:{} version:{} build:{}".format(sys.argv[0], __verion__, __build__)
print str_start

print "\n=============   Spamclam   ==========================================="

# Setup logging
logging.basicConfig(filename='spamalyse.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)7s : %(message)s')
                    # %(funcName)s
logging.info(str_start)

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
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print "Usage: spamclam.py <server> <user> <password> [mode]"
    print "e.g.   spamclam.py mailserver.company.com my_name@company.com qwerty simple"
    print "Note:  All other settings are controlled by the files in ../data/"
    sys.exit(101)

print "\n=============   Connect to POP3 server   ============================="    
    
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

print "\n=============   Spamalyse   =========================================="
    
# Create a Spamalyser object
sal = spamalyse.Spamalyser('../data/',str_mode, str_wob)

print "\n=============   Run   ================================================"

print "{}".format(con_pop.list()[0])
##lst_mls = con_pop.list()[1]
##for itm in lst_mls:
##    print itm

# DEBUG make some header stat  XXX This is noise, and should go away...
"""cd = ec_help.ec_cntdic()
cd_to = ec_help.ec_cntdic()
cd_from = ec_help.ec_cntdic()"""

for num_email in range(1,4):#num_tot_msgs+1): # 68,74): # # pop server count from 1 (not from 0)
    email_raw = con_pop.retr(num_email)
    email_string = "\n".join(email_raw[1])
    msg = email.message_from_string(email_string)
    """for keyn in msg.keys():
        cd.add(keyn.lower())
        if keyn.lower() == 'to':
            cd_to.add(msg.get('to'))
        if keyn.lower() == 'from':
            cd_from.add(msg.get('from'))"""
    ##print num_email, "from:", msg.get('from'), "subj:", msg.get('subject')  # XXX Before salmsg

    # ** Turn the email.massage into a spamalyse.Salmsg
    salmsg = spamalyse.Salmail(msg)
    #salmsg.show()
    ##if "men du tog den ikke" in salmsg.get('subject'):
    ##    print salmsg.get('from'), salmsg.get('subject')'

    # ** Check the salmsg for 'spam'
    obj_isspam = sal.is_spam(salmsg)
    print obj_isspam


print "\nProcessed {} e-mails\n".format(num_email)

"""for hit in cd.by_cnt(True):
    if hit[0] == num_email:
        print " "+str(hit)
print "\nStats on 'To'"
for itm in cd_to.by_cnt(True):
    print " "+str(itm)
print "\nStats on 'From'"
for itm in cd_from.by_cnt(True):
    print " "+str(itm)"""



# Generate Stat for the e-mails on the pop3 server.

#lst_dele = list() # List to cache delete commands feed back from server, not really used?
#for mail_number in range(1,num_tot_msgs+1): # pop server count from 1 (not from 0)
#    msg_raw = con_pop.retr(mail_number)
#    msg_eml = email.message_from_string('\n'.join(msg_raw[1]))
#    if sal.is_spam(msg_eml):
#        lst_dele.append(mail_number)  # Consider... Is it safe to have pop.retr and pop.dele in same loop, is mail_number solid enough for that?


# Actually delete the e-mails on the server
# con_pop.dele(mail_number)

#sal.stats_generate_pop3(con_pop)
#print sal.stats_show()
#sal.apply_rules_pop3(con_pop)
#sal.report_to_global_stat_file("../data/spamclam_global.stat")


#print "\n=============   Closing e-mail server connection   ==================="

# Close connection to email server
con_pop.quit()
# XXX del sal


#print "\n=============   Done...   ============================================"

# Music that accompanied the coding of this script:
#   David Bowie - Best of...
#   Buena Vista Social Club - Buena Vista Social Club