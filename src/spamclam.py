
### ToDo ###
# spyt noget stat ud.
# make header print uft-8 eller noget...

import sys, poplib, email

import spamalyse

# Read the command line input
try:
    str_srvr = sys.argv[1]
    str_user = sys.argv[2]
    str_pass = sys.argv[3]
    if len(sys.argv) > 3:
        str_mode = sys.argv[4]
    else:
        str_mode = "simple" # Default mode is 'simple black and white (lists)'
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print "\nUsage: spamclam.py <server> <user> <password> [mode]"
    sys.exit(101)
    
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
    
# get a Spamalyser object
sal = spamalyse.Spamalyser('../data/',str_mode)

# Handle the emails on the server
print "Message overview:"
cnt_tot = 0
cnt_god = 0
cnt_bad = 0
lst_dele = list() # List to cache delete commands feed back from server
for mid in range(1,num_tot_msgs+1): # pop server count from 1 (not from 0)
    msg_raw = con_pop.retr(mid)
    msg_eml = email.message_from_string('\n'.join(msg_raw[1]))
    cnt_tot += 1
    
    # Some nice printout
    print "\n>>>>>> email >>>>>> " + str(mid)
    print con_pop.list(mid)
    spamalyse.print_main_headers(msg_eml)
    #spamalyse.print_keys(msg_eml)
    #spamalyse.print_structure(msg_eml)
    
    # The actual Spam analysis
    if sal.is_spam(msg_eml):
        print "<<<<<< DELETE SPAM <<<<<<"
        lst_dele.append(con_pop.dele(mid))
        cnt_bad += 1
    else:
        print "<<<<<< Passed filter <<<<<<"
        cnt_god += 1

# Close connection to email server
con_pop.quit()

print "\n=============   Results   ======="
print "Expect :\t"+str(num_tot_msgs)
print "Handled:\t"+str(cnt_tot)
print "Lost...:\t"+str(num_tot_msgs-cnt_tot)
print "Good...:\t"+str(cnt_god)
print "Deleted:\t"+str(cnt_bad)
print "\nDone..."


# Music that accompanied the coding of this script:
#   David Bowie - Best of...