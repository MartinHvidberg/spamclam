
import sys
import smtplib

# Read the command line input
try:
    str_srvr = sys.argv[1]
    str_user = sys.argv[2]
    str_pass = sys.argv[3]
except:
    # Not as expected: mail.domain.tld user@domain.tld somepassword simple
    print "Usage: send_a_mail_01.py <server> <user> <password>"
    print "e.g.   send_a_mail_01.py mailserver.company.com my_name@company.com qwerty"
    sys.exit(101)

print str_srvr
print str_user
print str_pass

server = smtplib.SMTP(str_srvr, 587)

#Next, log in to the server
server.login(str_user, str_pass)

#Send the mail
msg = "Hello world..." # The /n separates the message from the headers
server.sendmail("martin@hvidberg.net", "martin@hvidberg.net", msg)
