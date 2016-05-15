
### ToDo ###
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
sal = spamalyse.Spamalyser(str_mode,['./data/'])

# Handle the emails on the server
print "Message overview:"
lst_dele = list() # List to cache delete commands feed back
for num_msg in range(3):#range(num_tot_msgs):#
    mid = num_msg+1 # the mail server counts from 1 (not 0)
    msg_raw = con_pop.retr(mid)
    msg_eml = email.message_from_string('\n'.join(msg_raw[1]))
    
    # Some nice printout
    print "\n====== email ====== " + str(mid)
    print con_pop.list(mid)
    spamalyse.print_main_headers(msg_eml)
    #spamalyse.print_keys(msg_eml)
    #spamalyse.print_structure(msg_eml)
    
    # The actual Spam analysis
    if spamalyse.is_spam(msg_eml):
        print "DEL: ******"
        #lst_dele.append(con_pop.dele(mid))

# Close connection to email server
con_pop.quit()

print "\nDone..."