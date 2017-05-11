import os
import json
from datetime import datetime
from csv import DictReader, DictWriter

from lib import Plugin, cron
plgn = Plugin('share')
logger = plgn.logger
    
all = ['soumavo','bos','sumit']

def addToTable(table, p,n):
    sp = sorted(p.items(),key=lambda (x,y):y,reverse=True)
    sn = sorted(n.items(),key=lambda (x,y):y,reverse=True)

    for i in range(len(sn)):
        name,toGive  = sn[i]
        if toGive:
            for j in range(len(sp)):
                (otherName,toReceive) = sp[j]
                if toReceive:
                    if toGive>=toReceive:
                        toGive-=toReceive
                        sp[j]=(otherName,0)
                        sn[i]=(name,toGive)
                        table[name][otherName]=table[name].get(otherName,0)+toReceive
                        #print '%s gives %s  Rs. %d'%(name,otherName,toReceive)
                    else:
                        sp[j]=(otherName,toReceive-toGive)
                        sn[i]=(name,0)
                        table[name][otherName]=table[name].get(otherName,0)+toGive
                        #print '%s gives %s  Rs. %d, remaining %d'%(name,otherName,toGive,sp[j][1])
                        break

@plgn.setupmethod
def init(config):
    if not os.path.exists('exp.csv'):
        with open('exp.csv', 'w') as f:
            wr = DictWriter(f, ['by', 'amt'])
            wr.writeheader()


@plgn.command('exp (?P<by>[a-z]+)( (?P<amt>-?\d+))?')
def save(data, **details):
    if details['by'] not in all:
        return "{by} is not a memeber".format(**details)
    if details['amt'] in ('','-',None):
        with open('exp.csv','r') as f:
            rr = DictReader(f, ['by', 'amt'])
#            print [str(d) for d in rr]
            return '\n'.join(['{by},{amt}'.format(**d)for d in rr if d['amt'] != 'amt']) 
    with open('exp.csv', 'a') as f:
        wr = DictWriter(f, ['by', 'amt'])
        wr.writerow(details)
    return '{by} spent Rs. {amt} in fuckedup plans'.format(**details)

@plgn.command('closeaccount')
def close(data, **details):
    os.rename('exp.csv', 'exp'+datetime.now().strftime('%d-%h-%y,%H-%M-%S')+'.csv')
    init({}) 
    if os.path.exists('exp.csv'):
        return 'Closed'


@plgn.command('total (?P<by>[a-z]+)')
def total(data, **details):
    if details['by'] not in all:
        return "{by} is not a memeber".format(**details)
    with open('exp.csv','r') as f:
        rr = DictReader(f, ['by', 'amt'])
        return str(sum((int(d['amt']) for d in rr if d['by'] == details['by']))) 


@plgn.command('calc')
def calc(data):
    table=dict(zip(all,[{} for _ in all]))
    with open('exp.csv','r') as f:
        rr = DictReader(f, ['by', 'amt'])
        for d in rr:
            if d['by']=='by':
                continue
            d['amt'] = int(d['amt'])
            pve = {d['by']:d['amt']-(d['amt'])/3.0}
            nve = dict([(p,d['amt']/3.0) for p in all if p!=d['by']])
            addToTable(table,pve,nve)

    shouldPay = dict([(i,sum([table[i][l] for l in table[i]])) for i in all])
    shouldGet = dict([(i,sum([l.get(i,0) for l in table.values()]))for i in all])
    for i in all:
        if shouldPay[i] and shouldGet[i]:
            if shouldPay[i]>shouldGet[i]:
                shouldPay[i]-=shouldGet[i]
                shouldGet[i]=0
            else:
                shouldGet[i]-=shouldPay[i]
                shouldPay[i]=0
    table=dict(zip(all,[{} for _ in all]))
    addToTable(table,shouldGet,shouldPay)
    return json.dumps(table)
#
#addToTable(shouldGet,shouldPay)

#pve = {'a':11000-2750}
#nve = {'r':2750,'v':2750,'s':2750}
#
#addToTable(pve,nve)
#
#pve = {'a':11000-2750}
#nve = {'r':2750,'v':2750,'s':2750}
#
#addToTable(pve,nve)
#
#for d in [{'ppl':4,'amt':2506,'by':'a','btw':[i for i in all if i!='a']},
#          {'ppl':4,'amt':2006,'by':'s','btw':[i for i in all if i!='s']},
#          {'ppl':4,'amt':535,'by':'r','btw':[i for i in all if i!='r']},
#          {'ppl':4,'amt':474,'by':'v','btw':[i for i in all if i!='v']},
#          {'ppl':3,'amt':200.0,'by':'v','btw':['s','a']},
#          {'ppl':2,'amt':640.0,'by':'r','btw':['s']}]:
#    pve = {d['by']:d['amt']-(d['amt'])/d['ppl']}
#    nve = dict([(p,d['amt']/d['ppl'])for p in d['btw']])
#    addToTable(pve,nve)
#
#print '+'*10
#for i in table:
#    print i,table[i]
#print '+'*10
#
#shouldPay = dict([(i,sum([table[i][l] for l in table[i]])) for i in all])
#shouldGet = dict([(i,sum([l.get(i,0) for l in table.values()]))for i in all])
#print shouldPay
#print shouldGet
#
#for i in all:
#    if shouldPay[i] and shouldGet[i]:
#        if shouldPay[i]>shouldGet[i]:
#            shouldPay[i]-=shouldGet[i]
#            shouldGet[i]=0
#        else:
#            shouldGet[i]-=shouldPay[i]
#            shouldPay[i]=0
#print shouldPay
#print shouldGet
#
#table=dict(zip(all,[{} for _ in all]))
#
#addToTable(shouldGet,shouldPay)
#
#
#print '+'*10
#for i in table:
#    print i,table[i]
#print '+'*10

'''
pve = {'a':200}
nve = {'s':100,'r':100}
addToTable(pve,nve)
print '+'*10
for i in table:
    print i,table[i]

pve = {'v':400}
nve = {'r':200,'s':200}
addToTable(pve,nve)
print '+'*10

for i in table:
    print i,table[i]
'''
