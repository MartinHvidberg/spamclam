
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
        self._clean_recent(90)


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
            logging.info("Loaded stat file {} with {} units".format(expfile, len(dic_stat_unit)))


    def _clean_recent(self, num_days=90):
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
            logging.info("Stored stat file {} with {} units".format(expfile, len(dic_stat_unit)))
        logger.info("All statistics files closed...")


    def add_salres(self, salmsg, salres, restat):
        """ Absorb one salmsg and its ralres into the salstats object """
        logger.debug("Add one salmsg + salres")

        ### Compare to Recently_seen
        bol_seen = False
        msgid = salmsg.get('id')
        if msgid:
            if msgid in self._data['recently_seen'].keys() and not restat:  # restat forces evaluation of e-mails that have been seen before
                bol_seen = True
            self._data['recently_seen'][msgid] = datetime.datetime.now().isoformat() # set new date for latest seen

        ### Add to stats_by_from
        if not bol_seen: # or "oister.dk" in salmsg.get('from'): # it's a new e-mail      <-------------------------- LUS
            logger.info("Stat:(by from) New e-mail: {}".format(msgid))
            str_from = salmsg.get('from')
            obj_sbf = self._data['stat_by_from']
            # {<from>: {cnt': <num>, 'rule_hits': {"[[('subject', '&&', '<string>')]], ...}, 'cnt_spam': <num>}, ...}
            if not str_from in obj_sbf.keys():
                obj_sbf[str_from] = {'cnt':0, 'cnt_spam':0, 'rule_hits':{}}
            # count the e-mail
            obj_sbf[str_from]['cnt'] += 1
            obj_sbf[str_from]['latest_cnt'] = datetime.datetime.now().isoformat()
            # count spam
            if salres['spam']:
                obj_sbf[str_from]['cnt_spam'] += 1
            obj_sbf[str_from]['latest_cnt_spam'] = datetime.datetime.now().isoformat()
            # count rule hits
            for keyr in salres:
                if keyr[:3] == 'vot':  # it's a vote list
                    lst_vote = list(set([str(vot) for vot in salres[keyr]]))  # convert to string lables, and remove duplicates
                    for vote in lst_vote:
                        ##print "votes <<< ", vote
                        if not vote in obj_sbf[str_from]['rule_hits'].keys():
                            obj_sbf[str_from]['rule_hits'][vote] = 0
                        obj_sbf[str_from]['rule_hits'][vote] += 1

        ### Add to stats_by_rule
        if True or not bol_seen: # it's a new e-mail
            logger.info("Stat:(by rule) New e-mail: {}".format(msgid))
            str_from = salmsg.get('from')
            obj_sbr = self._data['stat_by_bwrule']
            # count rule hits
            for keyr in salres:
                if keyr[:3] == 'vot':  # it's a vote list
                    lst_vote = list(set([str(vot) for vot in salres[keyr]]))  # convert to string lables, and remove duplicates
                    for vote in lst_vote:
                        print "votes <<< ", vote
                        if not vote in obj_sbr.keys():
                            obj_sbr[vote] = {'cnt': 0, 'froms': {}, 'corules': {}, 'latest_cnt': None}
                        # update count
                        obj_sbr[vote]['cnt'] += 1
                        # append sender
                        if str_from not in obj_sbr[vote]['froms'].keys():
                            obj_sbr[vote]['froms'][str_from] = 1
                        else:
                            obj_sbr[vote]['froms'][str_from] += 1
                        # append co-rules
                        for corule in list(set([str(vot) for vot in salres[keyr]])):  # for each rule hit by this e-mail
                            if corule != vote:  # except for myself
                                if corule not in obj_sbr[vote]['corules'].keys():  # if I havent co-ruled this before
                                    obj_sbr[vote]['corules'][corule] = 1
                                else:
                                    obj_sbr[vote]['corules'][corule] += 1
                        # update latest count
                        obj_sbr[vote]['latest_cnt'] = datetime.datetime.now().isoformat()

    def show(self, table='by_from', sort='spam', rvrs=1, limit=0):
        logger.info("show()")
        # get relevant dic
        dic_in = self._data['stat_'+table]
        if sort not in ('spam', 'rule_hits', 'no_rules', 'cnt', 'cnt_spam'):
            sort = 'spam'  # fall back to default
        if limit == 0:
            limit = len(dic_in.keys())
        # make order list
        if sort == 'spam':
            lst_o = [(1.0*dic_in[keyt]['cnt_spam']/dic_in[keyt]['cnt'], keyt) for keyt in dic_in.keys()]
        elif sort == 'rule_hits':
            lst_o = [(len(dic_in[keyt][sort]), keyt) for keyt in dic_in.keys()]
        elif sort == 'no_rules':
            lst_o = [(keyt, keyt) for keyt in dic_in.keys() if len(dic_in[keyt]['rule_hits'])==0]
        else:
            lst_o = [(dic_in[keyt][sort], keyt) for keyt in dic_in.keys()]
        # sort order list
        lst_o.sort(reverse=rvrs!=0)  # anything != 0 is considered True
        # deliver stat show
        return ["spam: {} ham: {} from: {} rules-hit: {}".format(dic_in[o]['cnt_spam'], dic_in[o]['cnt']-dic_in[o]['cnt_spam'], o, dic_in[o]['rule_hits']) for o in [ord[1] for ord in lst_o]][:limit]