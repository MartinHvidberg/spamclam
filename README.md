# Spam Clam #

A small Python Spam-deleter, for POP3 (so far only POP3, but extendable)

### What is this repository for? ###

* You have a POP3 e-mail account. You would like to simply delete a lot of spam emails discretely on the server, following a simple rule-set, like "from contains annoying@sales.com" or "subject start with 'loan offer'".
* about 0.9x (it works, but I'm still working on it...)
* to be added later ...[Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### To do ideas
* Port the whole thing to Python 3.x
* Make it work with IMAP, Gmail, etc..

### How do I get set up? ###

* Clone the repo
* go to ../data/ and ajust the .config, .csrule and .scaddr files to match your desired rules
  have a look into the .scaddr_* for explanations
* Call spamclam.py with your email credentials
  e.g. "mail.my_server.net my_name@my_server.net my_password simple"
  replace first three with your own info.
* Dependencies: Python 2.x (may easily be ported to 3.x)

### A few words about ../data/

* The files controlling the behaviour of Spamclam is located in ../data/
* there are several kinds, all with separate extensions (.config, .scrule, .scaddr, .stat)
* spamclam.config
      * This is the configuration file..
* .scrule
      * This is the Rule files
      * They must have either 'white' or 'black' in the name.
      * The filename determines if the rules are defining white-list or black-list definitions.
* .scrule_some_other_name
      * This is the exampe Rule files
      * Commented examples on how to write a .scrule file.
      * Not used by the program, just for you to learn from.
* .scaddr
      * This is the Address book files
      * Address books, likely in comma-seperated-values format.
      * But, the program will just look at them as text files, and try to find one email address on each line. any other text, including the commas, are ignored.
* .stat
      * This is the Output statistics, written by the program
      * When run, the program will create a .stat file.
      * It's a csv fil, with a line for each found sender.
      * For each sender is noted, number of emails (total) and number of spam-mails (delete).
      * The number accumulates, each time you run Spamclam, until you delete the file. i.e. the same good emails are counted over and over again, until you delete them from the server, with other software.
   
/Martin