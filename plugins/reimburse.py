import os
from datetime import datetime
import logging
from csv import DictWriter, DictReader
from lib import Plugin, cron
from collections import defaultdict



plgn = Plugin('reimburse')
logger = plgn.logger
plgn.__doc__ = "Use this plugin to store reimbursements. The details will be mailed to you by the end of month"


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
    sendMonthlyEmail(None, **details)
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
            d['dt'] = datetime.strptime(d['dt'],'%Y-%m-%d %H:%M:%S.%f')
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
    os.rename(plgn.exp_filename, plgn.exp_bkpname % datetime.now().strftime('%d-%h-%y,%H-%M-%S'))
    init(None) 
    if os.path.exists(plgn.exp_filename):
        return 'Closed'
 
import smtplib
from email.mime.multipart import MIMEMultipart
from email import Encoders
from email.MIMEBase import MIMEBase
import StringIO


def sendMonthlyEmail(data, by, **kwargs):
    ret = []
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(plgn.mail['from']['login'] ,plgn.mail['from']['password'] )
    user = by
    details = userwise()[by]
    if user not in plgn.mail.keys():
        logger.info('Unable to send mail to %s' % user)
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Monthly ReImbursement details for ' + datetime.now().strftime('%B of %Y')
    msg['From'] = plgn.mail['from']['email']
    msg['To'] =  plgn.mail[user]['email']
    #msg['Text'] = "Here is the latest data"
    csvfile = StringIO.StringIO()
    wr = DictWriter(csvfile, ['key','value'])
    wr.writerow({'key':'Name', 'value':plgn.mail[user]['fullname'] })
    wr.writerow({'key':'Purpose', 'value': 'Company Expenses'})
    wr.writerow({'key':'Period', 'value': datetime.now().strftime('%B of %Y')})
    wr = DictWriter(csvfile, ['Date','Description', 'Cost'])
    wr.writerow({ 'Date':'', 'Description': '', 'Cost':'' }) # empty row
    wr.writerow({ 'Date':'', 'Description': '', 'Cost':'' }) # empty row
    wr.writeheader()
    total = 0
    for det in details:
        dt = det['dt'].strftime('%d:%b:%Y')
        total += det['amt']
        wr.writerow({
            'Date':dt,
            'Description': det['why'],
            'Cost':det['amt']
            })
    wr.writerow({
        'Date':'',
        'Description': 'total',
        'Cost': total
        })

    wr.writerow({ 'Date':'', 'Description': '', 'Cost':'' }) # empty row
    wr.writerow({ 'Date':'', 'Description': '', 'Cost':'' }) # empty row

    part = MIMEBase('application', 'csv')
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=exp.csv')
    part.set_payload(csvfile.getvalue())
#        logger.debug(csvfile.getvalue())

    msg.attach(part)

    server.sendmail(msg['from'], msg['to'], msg.as_string())
    ret.append(user+ " - " +plgn.mail[user]['email'])
    server.quit()
    if ret:
        return "\n".join(["Sent Mail to users"] + ret)
    else:
        return "No Mails were sent"

@plgn.setupmethod
def init(config):
    if config != None: 
        plgn.exp_filename = config.get('exp_filename', 'exp.csv')
        plgn.exp_bkpname = config.get('bkp_filename', 'exp-%s.csv')
        plgn.admin_names = config['admins']
        plgn.mail = config['mail']
    if not os.path.exists(plgn.exp_filename):
        with open(plgn.exp_filename, 'a') as f:
            wr = DictWriter(f, ['dt','by','amt', 'why','status'])
            wr.writeheader()
