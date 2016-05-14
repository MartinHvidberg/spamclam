import sys, poplib

str_user = sys.argv[1]
str_pass = sys.argv[2]

print str_user + " / " + str_pass

M = poplib.POP3('mail.hvidberg.net')
M.user(str_user)
M.pass_(str_pass)
numMessages = len(M.list()[1])
for i in range(numMessages):
    for j in M.retr(i+1)[1]:
        print j