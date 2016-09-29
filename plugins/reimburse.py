import os
from datetime import datetime
import logging
from csv import DictWriter, DictReader
from lib import Plugin, cron
from collections import defaultdict



logger = logging.getLogger('bot.reimburse')
logger.setLevel(logging.DEBUG)
plgn = Plugin('reimburse')


@plgn.command('reim (?P<amt>-?\d+) (?P<why>[A-Za-z0-9 !@#$%^&*()]+)')
def save(data, **details):
    """
    save reimbursement details:
    usage: reim <amt> <why>
    """
    with open(plgn.exp_filename, 'a') as f:
        wr = DictWriter(f, ['dt','by','amt', 'why','status'])
        dt = datetime.now()
        details['status'] = 1
        details['dt'] = dt
        details['by'] = data['user_object'].name if data.get('user_object') else data['user']
        wr.writerow(details)
    return '{amt} was spent for {why}'.format(**details)

def userwise():
    """
    arrange data in a dict 
    ret = {
    sj : <record from csv file>
    }
    """
    with open(plgn.exp_filename, 'r') as f:
        rr = DictReader(f)
        ret = defaultdict(list)
        for d in filter(lambda x: int(x['status']), rr):
            d['amt'] = float(d['amt'])
            ret[d['by']].append(d)
    return ret

def describefor(username, redata):
    """
    Data formatting:
    1. 100 just like that
    ...
    total (sj): xxx.0000
    """
    retstr = [("%2i.  %10.2f %s" % (ind+1, d['amt'], d['why'])) for ind,d in enumerate(redata[username])]
    retstr.append("total (%s): %5.2f" % (username, sum(d['amt'] for d in redata[username])))
    return "\n".join(retstr) if len(redata[username]) > 0 else "No Details Recorded"


@plgn.command('relist (?P<by>[A-Za-z0-9 ]+)', private_only=True, restrict_to='admin_names')
def relist(data, **details):
    """
    Get reimbursement details of username
    usage: relist <username>
    """
    return describefor(details['by'], userwise())

@plgn.command('relist', private_only=True)
def relist_user(data, **details):
    """
    See you reimbursement details
    usage: relist
    """
    return describefor(data['user_object'].name if data.get('user_object') else data['user'], userwise())



@plgn.command('closeaccount', private_only=True, restrict_to='admin_names')
def close(data, **details):
    os.rename(plgn.exp_filename, plgn.bkp_filename % datetime.now().strftime('%d-%h-%y,%H-%M-%S'))
    init(None) 
    if os.path.exists(plgn.exp_filename):
        return 'Closed'



@plgn.setupmethod
def init(config):
    if config != None: 
        plgn.exp_filename = config.get('exp_filename', 'exp.csv')
        plgn.exp_bkpname = config.get('bkp_filename', 'exp-%s.csv')
        plgn.admin_names = config['admins']
    if not os.path.exists(plgn.exp_filename):
        with open(plgn.exp_filename, 'a') as f:
            wr = DictWriter(f, ['dt','by','amt', 'why','status'])
            wr.writeheader()
