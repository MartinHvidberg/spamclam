
import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

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


# Then we compose some of the basic message headers:
fromaddr = "martin@hvidberg.net"
toaddr = "martin@hvidberg.net"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Anmeldelse af poelsevognen paa torvet"
msg['Message-ID'] = "7-9-13@sender.pladderballe.net"  # this is used by SpamClam

# Next, we attach the body of the email to the MIME message:
body = "... bringer det kulfyrede Provancalske landkoekken i behagelig errindring..."
msg.attach(MIMEText(body, 'plain'))

# For sending the mail, we have to convert the object to a string, and then
# use the same prodecure as above to send using the SMTP server..

server = smtplib.SMTP(str_srvr, 587)

server.ehlo()
server.starttls()
server.ehlo()
# Next, log in to the server
server.login(str_user, str_pass)

text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
