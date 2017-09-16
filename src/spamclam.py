
__verion__ = '0.2.1'
__build__ = '201709162000seq'


### ToDo ###
# Address book 2 white/black lists
# Sanitise the rule complex, before applying
# make header print uft-8 eller noget...
# introduce prof command line parameters


print "\n=============   Spamclam   ==========================================="


import sys
import poplib, email

import spamalyse

print "Start:{} version:{} build:{}".format(sys.argv[0], __verion__, __build__)

# Read the command line input
try:
    str_srvr = sys.argv[1]
    str_user = sys.argv[2]
    str_pass = sys.argv[3]
    if len(sys.argv) > 3:
        str_mode = sys.argv[4]
    else:
        str_mode = "simple" # Default mode is 'simple black and white (lists)'
    if len(sys.argv) > 4:
        str_wob = sys.argv[5]
    else:
        str_wob = 'True'
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print "\nUsage: spamclam.py <server> <user> <password> [mode]"
    print "\ne.g.   spamclam.py mailserver.company.com my_name@company.com qwerty simple"
    print "\nNote:  All other settings are controlled by the files in ../data/"
    sys.exit(101)
    

print "\n=============   Connect to POP3 server   ============================="    
    
# # Open connection to email (POP) server
# try:
#     con_pop = poplib.POP3(str_srvr)
#     con_pop.user(str_user)
#     con_pop.pass_(str_pass)
#     print "Server says:  "+con_pop.getwelcome()
#     num_tot_msgs, num_tot_bytes = con_pop.stat()
#     print "Mailbox stat:\n  {} messages\n  {} bytes total".format(str(num_tot_msgs),str(num_tot_bytes))
# except:
#     print "\nSeems to be unable to access the e-mail server..."
#     sys.exit(102)
    
print "\n=============   Spamalyse   =========================================="
    
# Create a Spamalyser object
sal = spamalyse.Spamalyser('../data/',str_mode, str_wob)

#sal.import_addressfile('filename', 'white')
#sal.import_rulefile('filename', 'black')
#sal.export_2json('filename')

print "\n=============   Run   ================================================"

#sal.stats_generate_pop3(con_pop)
#print sal.stats_show()
#sal.apply_rules_pop3(con_pop)
#sal.report_to_global_stat_file("../data/spamclam_global.stat")


# # Handle the emails on the server
# lst_dele = list() # List to cache delete commands feed back from server, not really used?
# for mail_number in range(1,num_tot_msgs+1): # pop server count from 1 (not from 0)
#     msg_raw = con_pop.retr(mail_number)
#     msg_eml = email.message_from_string('\n'.join(msg_raw[1]))
#     if sal.is_spam(msg_eml):
#         lst_dele.append(con_pop.dele(mail_number))  # Consider... Is it safe to have pop.retr and pop.dele in same loop, is mail_number solid enough for that?

# # Close connection to email server
# con_pop.quit()

del sal

# Music that accompanied the coding of this script:
#   David Bowie - Best of...
#   Buena Vista Social Club - Buena Vista Social Club