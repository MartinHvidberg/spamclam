#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Basic filtering functionality
    This is a generic base for filters in general,
    this class should never be instantiated directly.
"""

### Versions  <-- Out of sync with the overall SpamClam versioning...
# 0.1 - initial version of this module

### ToDo
# ...


import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import sc_register


class Response(dict):
    """ Response objects is what comes out of a single filter-action,
    as well as an entire filer.
    A Response is a dictionary, with the following mandatory fields:
        fname: Name (str) naming the filter
        fvote: Vote (int) usually +1 or -1, +1 if filter see it as spam
        fminl: Min level (int) Filter would not predict lower threat than this
        fmaxl: Max level (int) Filter would not predict higher threat than this
    """

    def __init__(self, name=''):
        super(Response, self).__init__()
        self['name'] = name
        self['vote'] = 0
        self['fmin'] = 0
        self['fmax'] = 9
        self['reasons'] = list()


    def set_name(self, name):
        self['name'] = name


    def secure_value(self):
        """ Pushes value inside the Min Max limits """
        if self['vote'] > self['fmax']:  # Obay the Max limit
            self['vote'] = self['fmax']
        if self['vote'] < self['fmin']:  # Obay the Min limit
            self['vote'] = self['fmin']


    def secure_limits(self):
        """ If the Min Max limits are chrossed, then flip them """
        if self['fmin'] > self['fmax']:
            temp = self['fmin']
            self['fmin'] = self['fmax']
            self['fmax'] = temp
        self.secure_value()  # Secure the Vote is inside the ajusted limits


    def set_fmin(self, valu):
        if isinstance(valu, int):
            if valu >= 0 and valu <= 9:
                self['fmin'] = valu
                self.secure_limits()


    def update_fmin(self, valu):
        """ Set fmin to value, if stronger than present value. """
        if isinstance(valu, int):
            if valu >= 0 and valu <= 9:
                if valu < self['fmin']:  # Only change is new values is stronger
                    self['fmin'] = valu
                    self.secure_limits()


    def set_fmax(self, valu):
        if isinstance(valu, int):
            if valu >= 0 and valu <= 9:
                self['fmax'] = valu
                self.secure_limits()


    def update_fmax(self, valu):
        """ Set fmax to value, if stronger than present value. """
        if isinstance(valu, int):
            if valu >= 0 and valu <= 9:
                if valu > self['fmax']:  # Only change is new values is stronger
                    self['fmax'] = valu
                    self.secure_limits()


    def set_vote(self, vote):
        """ Set Vote to a defined value
        Limits Min and Max applies """
        if isinstance(vote, int):
            self['vote'] = vote
            self.secure_value()


    def vote(self, vote):
        """ Ajust Vote by a defined value, + is up and - is down
        Limits Min and Max applies """
        if isinstance(vote, int):
            self['vote'] += vote
            self.secure_value()


    def add_reason(self, str_reson):
        """ Adds a reason (string) to the reasons list """
        self['reasons'].append(str_reson)


    def merge(self, another_responce):
        """ Includes another response in this response,
        preserving the more conservative values between them """
        if isinstance(another_responce, Response):
            self['fmin'] = min(self['fmin'], another_responce['fmin'])
            self['fmax'] = max(self['fmax'], another_responce['fmax'])
            self['vote'] = max(self['vote'], another_responce['vote'])
            self['reasons'].extend(another_responce['reasons'])
            self.secure_limits()
            self.secure_value()



class Filter(object):
    """ This is a basic Filter.
    A Filter applies one, or more, filter actions to an e-mail
    A filter adds (or updates) a filter response in the scmail's filterres list.
    This filter doesn't actually filter anything, but acts as the parent class for other filters.
    """

    def __init__(self):
        logging.debug("class init. Filter")
        self.str_filter_name = "Base filter"
        ##self._data = dict()  # Not really sure what to put here, yet

    def spamalyse(self, scmail):
        """ Checks a single SCMail against the filter, i.e. it self.
         Filters always receive one scmail and return one scmail
         The filter always add (or update) one Response entry in the _filterres list
         """
        scmail.add_filter_response(self.str_filter_name, Response())
        return scmail  # method is supposed to be overloaded

    def filter(self, register):
        """ Checks all SCMails in a Register against the filter, i.e. it self """
        reg_out = sc_register.Register()
        for scm_id in register.list_all():
            scm_f = self.spamalyse(register.get(scm_id))
            reg_out.insert(scm_f)
        return reg_out

    def say_hi(self):
        """ This is a quite silly method, only used for debugging... """
        return "Hi... I'm {}, a filter of type: {}".format(self.str_filter_name, str(type(self)))