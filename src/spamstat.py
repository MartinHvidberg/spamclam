
""" Part of ECsoftware's SpamClam
    This module handles Keeping stats on which filters catch which email, and stuff...
"""

#import os
import logging
logger = logging.getLogger('spamclam')
import json
import datetime
import dateutil.parser

class Spamstat(object):


    def __init__(self, stat_dir = "./statistics"):
        logger.info("class init. Spamstat")
        self._data = dict()
        self._stdr = stat_dir
        self._los_fn = ("stat_by_from.scstat", "stat_by_bwrule.scstat", "recently_seen.scstat")
        self._load_stats_files()
        self._clean_recent(30)


    def _file2dic(self, str_dir, str_fn):
        try:
            with open(str_dir+'/'+str_fn, 'r') as fil_in:
                return json.load(fil_in)
        except IOError:
            logger.warning("Failed to read .scstat file: {} from {}".format(str_fn, str_dir))
            return dict()


    def _dic2file(self, dic_stat, str_dir, str_fn):
        try:
            with open(str_dir+'/'+str_fn, 'w') as fil_out:
                json.dump(dic_stat, fil_out)
        except IOError:
            logger.warning("Failed to write .scstat file: {} to {}".format(str_fn, str_dir))


    def _load_stats_files(self):
        """ Find and load all .scstat files in the stat_dir """
        logger.debug(" func. load_stats_files()")
        for expfile in self._los_fn:
            dic_stat_unit = self._file2dic(self._stdr, expfile)
            self._data[expfile.split('.')[0]] = dic_stat_unit
            logging.info("Loaded stat file {}".format(expfile))


    def _clean_recent(self, num_days=30):
        logging.info("Cleaning 'recently_seen' to newest {} days".format(num_days))
        dat_now = datetime.datetime.now()
        for recn in self._data['recently_seen']:
            dat_last = dateutil.parser.parse(self._data['recently_seen'][recn])
            age = dat_now - dat_last
            if age > datetime.timedelta(num_days):
                del self._data['recently_seen'][recn]
                logging.info("Not seen in {} days: {}".format(num_days, recn))


    def close(self):
        """ Saves the present contents of self._data to the self._stat_dir files """
        logger.info("closing statistics")
        for expfile in self._los_fn:
            dic_stat_unit = self._data[expfile.split('.')[0]]
            self._dic2file(dic_stat_unit, self._stdr, expfile)
            logging.info("Stored stat file {}".format(expfile))
        logger.info("All statistics files closed...")


    def add_salres(self, salmsg, salres):
        """ Absorbe one salmsg and its ralres into the salstats object """
        logger.debug("Add one salmsg + salres")

        ### Compare to Recently_seen
        bol_seen = False
        msgid = salmsg.get('id')
        if msgid:
            if msgid in self._data['recently_seen'].keys():
                bol_seen = True
            self._data['recently_seen'][msgid] = datetime.datetime.now().isoformat() # set new date for latest seen

        ### Add to stats_by_from
        if not bol_seen: # or "oister.dk" in salmsg.get('from'): # :# # it's a new e-mail      <-------------------------- LUS
            ##print "New e-mail: {}".format(msgid)
            logger.info("new e-mail: {}".format(msgid))
            str_from = salmsg.get('from')
            if not str_from in self._data['stat_by_from'].keys():
                self._data['stat_by_from'][str_from] = {'cnt':0, 'cnt_spam':0, 'rule_hits':{}}
            # count the e-mail
            self._data['stat_by_from'][str_from]['cnt'] += 1
            # count spam
            if salres['spam']:
                self._data['stat_by_from'][str_from]['cnt_spam'] += 1
            # count rule hits
            for keyr in salres:
                if keyr[:3] == 'vot':  # it's a vote list
                    lst_vote = list(set([str(vot) for vot in salres[keyr]]))  # convert to string lables, and remove duplicates
                    for vote in lst_vote:
                        ##print "votes <<< ", vote
                        if not vote in self._data['stat_by_from'][str_from]['rule_hits'].keys():
                            self._data['stat_by_from'][str_from]['rule_hits'][vote] = 0
                        self._data['stat_by_from'][str_from]['rule_hits'][vote] += 1

    def show(self):
        logger.info("show()")
        print "show stats: To be implimented..."