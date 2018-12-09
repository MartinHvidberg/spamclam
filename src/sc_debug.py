
import logging
import email


def setup_logger(name, log_file, level=logging.INFO):
    """ open private log file """
    handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)7s %(funcName)s : %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def analyse_retreived_email(eml_in):
    """ Assumes eml_in to be of type: [line, ...]
    try to see what it's made of, and how it works... """
    if isinstance(eml_in, list): # expects list
        if len(eml_in) > 0:
            debug_logger.info("Received list of {} elements".format(len(eml_in)))
            for lin in eml_in:
                debug_logger.info("type: {}: {}".format(str(type(lin)), lin))
        else:
            debug_logger.warning("Expected Non-empty list!")
    else:
        debug_logger.warning("Expected list, but got {}".format(str(type(eml_in))))
    return

def analyse_parsed_email(eml_in):
    """ Assumes eml_in to be of type:
    try to see what it's made of, and how it works... """
    if isinstance(eml_in, email.message.EmailMessage):
        debug_logger.info("Received e-mail type: {}".format(str(type(eml_in))))
        ##debug_logger.info("    multipart: {}".format(eml_in.is_multipart()))
        for hdr in eml_in.items():
            debug_logger.info("    headers: {}".format(hdr))
        for part in eml_in.walk():
            debug_logger.info("    content: {}".format(part.get_content_type()))
    else:
        debug_logger.warning("Expected , but got {}. May be you are using wrong email.policy.".format(str(type(eml_in))))
    return eml_in.keys()


## Set up a private log file
debug_logger = setup_logger('sc_debug', 'sc_debug.log')
debug_logger.info("Start: {} ".format(__file__))
