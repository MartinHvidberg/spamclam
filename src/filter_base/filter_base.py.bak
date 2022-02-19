#!/usr/bin/env python
# -*- coding: UTF-8 -*-

""" Part of ECsoftware's SpamClam
    This module handles: Basic filtering functionality
    This is a generic base for filters in general,
    this class should never be instantiated directly.
"""

# Versions
# 0.1 - initial version of this module
# 0.4.2 : Loading emails from server works, View works and First minimalistic filter (Karma) works
# 0.4.3 : Quite more .log, similar less print()

# ToDo
# ...


import logging
import sys
import os
##sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
##import sc_register

# Initialize logging
log = logging.getLogger(__name__)
log.info("Initialize: {}".format(__file__))


class Response(dict):
    """ Response objects is what comes out of a filter-action.

    Thoughts on Response objects...
    A filter have a name, the name is unique.
    A filter returns one Response object, i.e. A Response is a Filter-Response.
    A filter may have several checks, so a response object may have several cres (Check-RESponces)
    Spam-level is an integer between 0..9. 0: Not assigned, 1..3: Lowest risk, 4..6: High risk, 7..9: Considered Spam
    Confidence is an integer between 0..9. 0: Not assigned, 1..3: Uncertain, 4..6: Quite sure, 7..9: Trusted

    A Response is a dictionary, with the following fields:
        name: Name (str) naming the filter
        vote: Vote (int) The Filters best over-all estimate of the e-mails spam-level.
        conf: Confidence in this Filter vote (int)
        minl: Min level (int) Filter do not predict lower threat than this
        maxl: Max level (int) Filter do not predict higher threat than this
        _upda: Updated (boolean) True if all f* are updated in accordance with _dcre
        _dcre: Dictionary of cres (dict)
            cvote: Vote (int) The Checks best over-all estimate of the e-mails spam-level.
            cconf: Confidence in this Check result(int)
            cminl: Min level (int) Check do not predict lower threat than this
            cmaxl: Max level (int) Check do not predict higher threat than this
            cnote: Note (str) Mentioning the reason for this spam-level, e.g. "'from' appears in black-list. (7,7,4,0)"

    The f* values are calculated by _update() based of the values in _dcre. This process is critical, but non trivial.
    """

    def __init__(self, name=''):
        super().__init__()
        self['name'] = name
        self['vote'] = 0
        self['fmin'] = 0
        self['fmax'] = 0
        self['_dcre'] = dict()
        self['_upda'] = True

    def set_updated(self, bol_upd):
        self['_upda'] = bol_upd

    def vote(self, cname, cvote, cconf, cmin, cmax, cnote):  # The individual filter checks have to deliver these.
        """
        Adds one cres (Check-Result) to the Result (Filter-Result)
        :param cname: (str) Name of the Check
        :param cvote: (int) Vote from the Check
        :param cconf: (int) Confidense in that vote
        :param cmin:  (int) Minimum spamlevel imagined by the check
        :param cmax:  (int) Maximum spamlevel imagined by the check
        :param cnote: (str) Reason/explanation for the vote
        :return:
        """
        if any([itm == None for itm in [cvote, cconf, cmin, cmax]]):  # Emergency check - Try remove this later ...
            raise("vote don't take None for an ansver ...")
        if (all([isinstance(itm, int) for itm in [cvote, cconf, cmin, cmax]])  # type check
                and all([isinstance(itm, str) for itm in [cname, cnote]])):
            if ((all([itm>=0 and itm<=9 for itm in [cvote, cconf, cmin, cmax]]))  # value check
                and all([len(itm)>0 for itm in [cname, cnote]])):
                str_note = "{} ({},{},{},{})".format(cnote, cvote, cconf, cmin, cmax)
                self['_dcre'][cname] = {'vote': cvote,
                                        'conf': cconf,
                                        'min': cmin,
                                        'max': cmax,
                                        'note': str_note}
                self.set_updated(False)
                log.info("add_cres({}, {}, {}, {}, {}, {})".format(cname, cvote, cconf, cmin, cmax, cnote))
                return True
            else:
                log.warning("Illegal value: add_cres({}, {}, {}, {}, {}, {})".
                            format(cname, cvote, cconf, cmin, cmax, cnote))
                return False
        else:
            str_warn = "Illegal type: add_cres(st, int, int, int, int, str) got: {}".\
                format([str(type(itm)) for itm in [cname, cvote, cconf, cmin, cmax, cnote]])
            log.warning(str_warn)
            return False

    def _update(self):
        """ This is likely the most delicate/controversial process in SpamClam ... """
        if len(self['_dcre'].keys()) > 0:  # We have at least one check on archive
            xvot = 0  # Worst case it remains 0 (un-set)
            xcon = 0  # Worst case it remains 0 (un-set)
            xmin = 10  # Anyting legal should be less than 10
            xmax = -1  # Anyting legal should be more than -1
            knot = ""  # Killer-Note starts un-set
            for keyc in self['_dcre']:
                if self['_dcre'][keyc]['vote'] > xvot:  # We found a new 'most xtreme' vote
                    xvot = self['_dcre'][keyc]['vote']
                    xcon = self['_dcre'][keyc]['conf']
                    knot = self['_dcre'][keyc]['note']
                if self['_dcre'][keyc]['min'] < xmin:  # We found a more xtreme lower border
                    xmin = self['_dcre'][keyc]['min']
                if self['_dcre'][keyc]['max'] > xmax:  # We found a more xtreme upper border
                    xmax = self['_dcre'][keyc]['max']
            self['vote'] = xvot
            self['conf'] = xcon
            self['fmin'] = xmin
            self['fmax'] = xmax
            self['note'] = knot
        else:
            self['vote'] = 0
            self['conf'] = 0
            self['fmin'] = 0
            self['fmax'] = 0
            self['note'] = ""

    def get_vote(self):
        if not self['_upda']:
            self._update()
        return self['vote']

    # def OLD__update_fmin(self, valu):
    #     """ Set fmin to valu, if stronger than present value. """
    #     if isinstance(valu, int):
    #         if valu >= 0 and valu <= 9:
    #             if valu > self['fmin']:  # Only change is new values is stronger
    #                 self['fmin'] = valu
    #                 self._secure_limits()
    #
    # def OLD__update_fmax(self, valu):
    #     """ Set fmax to valu, if stronger than present value. """
    #     if isinstance(valu, int):
    #         if valu >= 0 and valu <= 9:
    #             if valu < self['fmax']:  # Only change is new values is stronger
    #                 self['fmax'] = valu
    #                 self._secure_limits()
    #
    # def OLD__add_reason(self, vote, fmin, fmax, reason):
    #     """ Adds a reason (string) to the reasons list
    #     reason-strin contains reason & (min,vote,max) """
    #     if vote >= 0:
    #         sign = '+'
    #     else:
    #         sign = '-'
    #     str_reason = "{r} ({i}/{s}{v}/{a})".format(v=vote, i=fmin, a=fmax, r=reason, s=sign)
    #     self['reasons'].append(str_reason)
    #
    # def OLD_vote(self, vote, fmin, fmax, reason):
    #     """ Adjust Vote by a defined value, + is up and - is down
    #     Limits Min and Max applies, and reason is added. """
    #     if isinstance(vote, int):
    #         self['vote'] += vote
    #         self._update_fmin(fmin)
    #         self._update_fmax(fmax)
    #         self._secure_value()
    #         self._add_reason(vote, fmin, fmax, reason)
    #
    # def OLD_get_vote(self):
    #     return self['vote']
    #
    # def OLD_get_reasons(self):
    #     return self['reasons']
    #
    # def OLD__secure_value(self):
    #     """ Pushes value inside the Min Max limits """
    #     if self['vote'] > self['fmax']:  # Obay the Max limit
    #         self['vote'] = self['fmax']
    #     if self['vote'] < self['fmin']:  # Obay the Min limit
    #         self['vote'] = self['fmin']
    #
    # def OLD__secure_limits(self):
    #     """ If the Min Max limits are crossed, then flip them """
    #     if self['fmin'] > self['fmax']:
    #         temp = self['fmin']
    #         self['fmin'] = self['fmax']
    #         self['fmax'] = temp
    #     self._secure_value()  # Secure the Vote is inside the adjusted limits
    #
    # def OLD_merge(self, another_responce):
    #     """ Includes another response in this response,
    #     preserving the more conservative values between them. """
    #     if isinstance(another_responce, Response):
    #         self['fmin'] = min(self['fmin'], another_responce['fmin'])
    #         self['fmax'] = max(self['fmax'], another_responce['fmax'])
    #         self['vote'] = max(self['vote'], another_responce['vote'])
    #         self['reasons'].extend(another_responce['reasons'])
    #         self._secure_limits()
    #         self._secure_value()


class Filter(object):
    """ This is a basic Filter.
    A Filter applies one, or more, filter actions to an e-mail
    A filter adds (or updates) it's filter-response in the scmail's filterres list.
    This basic filter doesn't actually filter anything, but acts as the parent class for other filters.
    """

    def __init__(self):
        logging.debug("class init. Filter")
        self.filter_name = "Base filter"
        log.debug("class init. {}".format(self.say_hi()))

    def spamalyse(self, scmail):  # method is supposed to be overloaded
        """ Checks a single SCMail against the filter, i.e. it self.
        Always receive one scmail and return one scmail
        """
        if not scmail.has_filter_response(self.filter_name):
            rsp_in = Response(self.filter_name)  # Create a filter Response obj.
            scmail.add_filter_response(rsp_in)  # This should be the only place a Response() is added to a SCMail() !
        return scmail

    def filter(self, reg_in):
        """ Checks all SCMails in a Register against the filter, i.e. it self """
        #reg_out = sc_register.Register()  # The return Register starts empty  XXX BIG TIME try to avoid this...!!! XXX
        for scm_id in reg_in.list_all():  # reg_in.list_match(["id=0102016c530dd369-0343fba1-a4d3-499d-8259-82fc5ae7306b-000000@eu-west-1.amazonses.com"]): # reg_in.list_all():  # <-- LUS
            log.info("filter(base) <- {}".format(scm_id))
            scm_f = self.spamalyse(reg_in.get(scm_id))  # Do the actual Spam Analysis
            #reg_out.insert(scm_f)  # try avoid calling sc_register.Register() from this module
            reg_in.set(scm_id, scm_f)
        return reg_in  # alternative: return reg_out

    def say_hi(self):
        """ This is a quite silly method, only used for debugging... """
        return "Hi... I'm {}, a filter of type: {}".format(self.filter_name, str(type(self)))

if __name__ == '__main__':
    r = Response()
    r.add_cres(0, 1, 2, 3, 4, 'meme')
    r.add_cres('nam', 1, 2, '3', 4, 'meme')
    r.add_cres('nam', 1, 2, 3, 4, '')
    r.add_cres('nam', 1, 2, 3, 99, 'meme')
    r.add_cres('nam', 1, 2, 3, 4, 'meme')

# End of Python

# Music that accompanied the coding of this script:
#   Saga - Saga (1978)
#   Dvorak - From the new World