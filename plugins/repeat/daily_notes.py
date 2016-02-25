
import time
import logging
amount = {}
import time,re,getpass,os,csv

from lib import Plugin, cron
logger = logging.getLogger('bot.wallet')
logger.setLevel(logging.DEBUG)
plgn = Plugin('wallet')

fieldnames = ['Date','Seperator','Todo','Type']

@plgn.command('remind\Z')
def receiving(data):
    retrieving()
    return sending_back(retrieving())

def retrieving(*args):
        global fieldnames
        task_status={'Pending':[],'Done':[]}
        with open('daily-task.csv','r') as f:
                final=""
                r = csv.DictReader(f)
                for row in r:
                    if args:
                            f = fieldnames[args[1]]
                            if args[0] in row[str(f)]:
                                temp = ' '.join([value for key,value in row.items() if key!='Type'])
                                if row['Type']=='Pending':
                                    task_status['Pending'].append(temp)
                                else:
                                    task_status['Done'].append(temp)
                    else:
                        temp = ' '.join([value for key,value in row.items() if key!='Type'])
                        if row['Type']=='Pending':
                            task_status['Pending'].append(temp)
                        else:
                            task_status['Done'].append(temp)
        return task_status
def sending_back(task_status):
        final = ""
        temp=[[key,"\n".join(value)] for key,value in task_status.items()]
        for item in temp:
            final = final + str(item[0]) + ":" + "\n" + item[1] + "\n"
        return final
@plgn.command('remind today\Z')
def receiving(data):
        date = (time.asctime()).split(" ")
        date.remove(date[3])
        return sending_back(retrieving(" ".join(date),0))
        
@plgn.command('remind acads\Z')
def receiving(data):
    return sending_back(retrieving('acads',1))

@plgn.command('remind regular\Z')
def receiving(data):
        return sending_back(retrieving('regular',1))

@plgn.command('remind special\Z')
def receiving(data):
    return sending_back(retrieving('special',1))

def noting(data):
    global fieldnames
    with open('daily-task.csv','a') as f:
                w= csv.DictWriter(f,fieldnames=fieldnames)
                if data == ' ':
                    w.writeheader()
                else:
                    if len(data)<3:
                        while len(data)<3:
                            data.append(" ")
                    t = (time.asctime()).split(" ")
                    t.remove(t[3])
                    date = " ".join(t)
                    w.writerow({'Date':date,'Seperator':data[0],'Todo':" ".join(data[1:]),'Type':'Pending'})
@plgn.command('note (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def listening(data,what):
	if not os.access('daily-task.csv',os.F_OK):
		noting(' ')
        temp=map(str,what.split(" "))
        noting(temp)	
