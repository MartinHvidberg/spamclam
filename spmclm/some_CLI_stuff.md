
	*** PLEASE TURN THIS TEXT INTO MARKDOWN ***


sc COMMAND [Argument ...] [option ...] [--flag ...]

GET Server,User,Pasw  # Read e-mails on the server, building/updating the register

FILTERS
	Run # Apply a filter to the register, adding spam risks to e-mails
		Bw		bow  --train_ai
		Known	list_server(s)	--add_to_bw  --train_ai
		Ai
	Form
		bw	black|white (from,subj.,...) mail#|string

VIEW (Spam,Grey,White)  # show the register, and status of e-mails in it

SET <value> <mail#(, mail#)>  # Manually change spam risk of one or more e-mails
	values 0..9, oOsS, pP (for protect), uU (for Unprotect)
	mail# are as listed by STATUS

KILL spam|number # Actually delete e-mails on the server, based og their spam risk number in the register
	Delete, on the e-mail server, all e-mails that hold a spam rank in the register.
	spam = Any e-mail with spam ranking >= 7
	number = Any e-mail with spam ranking >= Number
	Default: Spam, i.e. if argument omitted, then >= 7 assumed

CLEAN  # Empty the register and any login credentials set by CONFIG, e.g. because you are on a public computer

STATISTICS  # Access the statistics that was collected over time

LOG  # Access the log files

CONFIG  # store login credential in local file (inspired by git)

VERSION # Show version info

-h, --help			# Show help
-y, --yes   		# Assume Yes. Do not prompt, pick each first option
-f, --force			# Force. Override reasonable warnings
-v n, --verbose n	# Verbose level n (0..9) where 9 is most detailed. Default 4
					# 0: No output
					# 1: Only critical errors
					# 2: All errors
					# 3: Warnings
					# 4: Overall progress info
					# 5: Detailed progress info
					# 6: Intimate details of execution
					# 9: Debug mode
-q, --quiet			# Quiet (supress output) same as --verbose 1
-l n, --logging	n	# Logging level (0..9) Same as for --verbose. Default 4
--logfile name		# name is full or relative path to log-file
--logmode s|a		# s: session (log cleared by GET command). a: accumulated (log not cleared). Default s
