import sys, poplib

str_serv = sys.argv[1]
str_user = sys.argv[2]
str_pass = sys.argv[3]

#print str_user + " / " + str_pass

con_pop = poplib.POP3('')
con_pop.user(str_user)
con_pop.pass_(str_pass)
print "Server says:  "+con_pop.getwelcome()
tup_stat = con_pop.stat()
print "Mailbox stat:\n  {} messages\n  {} bytes".format(str(tup_stat[0]),str(tup_stat[1]))

#===============================================================================
# num_popessages = len(con_pop.list()[1])
# print "I see {} messages.".format(num_popessages)
# for i in range(num_popessages):
#     for j in con_pop.retr(i+1)[1]:
#         pass#print j
#===============================================================================