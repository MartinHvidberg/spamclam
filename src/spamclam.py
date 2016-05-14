
### ToDo ###
# make header print uft-8 eller noget...

import sys, poplib, email

str_srvr = sys.argv[1]
str_user = sys.argv[2]
str_pass = sys.argv[3]

con_pop = poplib.POP3(str_srvr)
con_pop.user(str_user)
con_pop.pass_(str_pass)
print "Server says:  "+con_pop.getwelcome()
num_tot_msgs, num_tot_bytes = con_pop.stat()
print "Mailbox stat:\n  {} messages\n  {} bytes total".format(str(num_tot_msgs),str(num_tot_bytes))

print "Message overview:"
for num_msg in range(num_tot_msgs):
    print "====== New email ======"
    print con_pop.list(num_msg+1)
    msg_raw = con_pop.retr(num_msg+1)
    msg_eml = email.message_from_string('\n'.join(msg_raw[1]))
    print "------"
    print "From: " + str(msg_eml['From'])
    print "Sub.: " + str(msg_eml['Subject'])
    print "------ Structure"
    print email.Iterators._structure(msg_eml)
    
con_pop.quit()