# Spam Clam #

A small Python Spam-deleter, for POP3 (so far only POP3, but extendable)

### What is this repository for? ###
* You have a POP3 e-mail account. You would like to simply delete a lot of spam emails discretely on the server, following a simple rule-set, like "from contains annoying@sales.com" or "subject start with 'loan offer'".
* arround 0.2 (it works, but I'm still working on it...)
* to be added later ... See ToDo.md

### To do ideas
* Port the whole thing to Python 3.x
* Make it work with IMAP, Gmail, etc..
* ... see ToDo.md

### How do I get set up? ###
* Clone the repo
* Ajust the smapclam.config
* go to ../mode_simple_bw/ and ajust the .scrule and .scaddr files to match your desired rules
  have a look into the .scrule and .scaddr files for explanations
* To run: Call sccli.py (Spam Clam Command Line Interface) with your email credentials
  e.g. "mail.my_server.net my_name@my_server.net my_password simple"
  replace first three with your own info.
* Dependencies: Python 2.x (may easily be ported to 3.x)

### A few words about the files...

* sccli - The Spamclam CLI (command line interfaece)
* scgui - The Spamclam GUI (graphical user interfaece) - yet to be writen...
* spamclam - The major (top) module of functionality, i.e. not user interface.
  Handles the contact to the e-mail server, and so far only have POP3 capabilities.
  Hands over each email to be checked by spamalyse.
* spamclam.config - config file for spamclam
* spamalyse - Actually analysing one e-mail.
  Contains Spamclams e-mail abstraction class and calls for spamchecks for each mode.
  So far only supports one mode, i.e. Simple Balck/White.
* spamstat - Class(es) for handeling statistics
* /mode_simple_bw - Files involved in Simple Black/White mode filtereing.
        * simple_bw - Handles the black/white rules and can check a single e-mail against them.
        * simple_bw.config - config file for simple black/white mode.
* /Statistics - files involved in collecting statistics. Keeps track of which rules are more used, and who spams you most.

### "Simple Black/White mode" ../mode_simple_bw/

* "Simple Black/White mode" is controlled by these files
* there are several kinds, all with separate extensions (.scrule, .scaddr, .stat)
* .scrule
      * This is the Rule files
      * They must have either 'white' or 'black' in the name
      * The filename determines if the rules are defining white-list or black-list definitions
* .scrule_some_other_name
      * This is the exampe Rule files
      * Commented examples on how to write a .scrule file
      * Not used by the program, just for you to learn from
* .scaddr
      * This is the Address book files
      * Address books, likely in comma-seperated-values format
      * But, the program will just look at them as text files, and try to find one email address on each line. Any other text, including the commas, are ignored
* .stat
      * This is the Output statistics, written by the program
      * When run, the program will create or update the .stat file
      * It's a .json file so it's quite readable, but you should properly not edit it
      * For each rule is noted dates and counts of hit
      * For each sender is noted, number of emails (total) and number of spam-mails (delete)
      * The number accumulates, each time you run Spamclam, until you delete the file. i.e. the same good emails may be counted many times
   
/Martin