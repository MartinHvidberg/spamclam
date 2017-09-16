

def print_main_headers(eml_in):
    """ Just print the interesting headers """
    print ">>>>>> Headers"
    print "Subj.: " + str(eml_in['Subject'])
    print "Date : " + str(eml_in['Date'])
    print "From : " + str(eml_in['From'])
    print "Rtrn : " + str(eml_in['Return-Path'])
    print "To_d : " + str(eml_in['Delivered-To'])
    print "To_o : " + str(eml_in['X-Original-To'])
    #print "multi: " + str(eml_in.is_multipart())


def print_keys(eml_in):
    print ">>>>>> Keys"
    print eml_in.keys()


def print_structure(eml_in):
    print ">>>>>> Structure"
    print email.Iterators._structure(eml_in)
