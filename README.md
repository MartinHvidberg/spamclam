# Spam Clam #

A small Python Spam-deleter, for POP3

### What is this repository for? ###

* You have a POP3 e-mail account. You would like to simply delete a lot of spam emails discretely on the server, following a simple rule-set, like "from contains annoying@sales.com" or "subject start with 'loan offer'".
* about 0.9x (it works, but I'm still working on it...)
* to be added later ...[Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Clone the repo
* go to ../data/ and ajust the .conf files to match your desired rules
  have a look into the conf_backup for explanations
* Call spamclam.py with your email credentials
  e.g. "mail.my_server.net my_name@my_server.net my_password simple"
  replace first three with your own info.
* Dependencies: Python 2.x (may easily be ported to 3.x)