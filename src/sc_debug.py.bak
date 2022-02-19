

### Versions
# 0.1 - initial version of this module

import logging

# Set up a private log file
fh_log = logging.FileHandler("sc_debug.log", mode='w')
formatter = logging.Formatter('%(asctime)s %(levelname)7s %(funcName)s : %(message)s')
fh_log.setFormatter(formatter)
log = logging.getLogger("sc_debug")
log.setLevel('DEBUG')
log.addHandler(fh_log)
log.info("Initialize: {}".format(__file__))
import email


def analyse_retreived_email(eml_in):
    """ Assumes eml_in to be of type: [line, ...]
    try to see what it's made of, and how it works... """
    if isinstance(eml_in, list): # expects list
        if len(eml_in) > 0:
            log.info("Received list of {} elements".format(len(eml_in)))
            for lin in eml_in:
                log.info("type: {}: {}".format(str(type(lin)), lin))
        else:
            log.warning("Expected Non-empty list!")
    else:
        log.warning("Expected list, but got {}".format(str(type(eml_in))))
    return

def analyse_parsed_email(eml_in):
    """ Assumes eml_in to be of type:
    try to see what it's made of, and how it works... """
    if isinstance(eml_in, email.message.EmailMessage):
        log.info("Received e-mail type: {}".format(str(type(eml_in))))
        ##log.info("    multipart: {}".format(eml_in.is_multipart()))
        for hdr in eml_in.items():
            log.info("    headers: {}".format(hdr))
        for part in eml_in.walk():
            log.info("    content: {}".format(part.get_content_type()))
    else:
        log.warning("Expected , but got {}. May be you are using wrong email.policy.".format(str(type(eml_in))))
    return eml_in.keys()

