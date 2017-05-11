import os
import logging
from datetime import datetime
from  random import randint
from lib import *
import yaml

plgn = Plugin('blog')
logger = plgn.logger

# This is testcode for threadpool.py
# counter = 0
#def test():
#    global counter
#    counter +=1
#    time.sleep(5)
#    outputs.append(('debug',str(counter)))



# HACK HACK HACK !!!!!
datetime.strptime("01","%H")
# http://bugs.python.org/issue7980

para_regex = '(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)'

STATES={
        'blank':'blank',
        'started':'started',
        }

motivate=[
        'It looks like you have started the blog, Do you want to talk about anything?',
        'Hey there, What do you want to write on this page of your life?',
        'So, did you complete any tasks today?',
        'Come on, it cant be that bad to write?, Remeber when it felt, Nice?'
        ]

@plgn.setupmethod
def init(config):
    global save_filepath, orig_name, template, header_slice
    save_filepath = config['save_filepath']
    orig_name = config['orig_name' ]
    template = config['template']
    header_slice = slice(1,len(template.splitlines())-2)

    if state() == STATES['blank']:
        f=open('state','w')
        f.close()
        with open(orig_name,'w') as f:
            f.write(template.format(dt=datetime.now().strftime('%Y-%m-%d')))

@plgn.command('blog '+ para_regex)
def blogging(data, **details):
    fs = '`{dt}`: {what}\n\n\n'.format(dt=datetime.now().strftime('%H-%M'), what=details['what'])
    ret = ''
    if state() == STATES['blank']:
        with open(orig_name,'w') as f:
            f.write(template.format(dt=datetime.now().strftime('%Y-%m-%d')))
            ret += 'Created the file.\n'
    with open(orig_name,'a') as f:
        f.write(fs)
    state(STATES['started'])
    return ret + 'Thanks a lot, have a wonderfull day'
 



def state(now=''):
    if now == '':
        try:
            with open('state','r') as f:
                st = f.readline()
                return STATES[st] if st in STATES else STATES['blank']
        except:
            return STATES['blank']
    else:
        with open('state', 'w') as f:
            f.write(now)




@plgn.schedule(cron(hour=[23]))
@plgn.command('saveblog')
def save(data=None, **details):                    # Crontasks are called without any arguments,
    if state() == STATES['started']:
        new_name=save_filepath.format(dt=datetime.now().strftime('%Y-%m-%d'))
        if os.path.exists(new_name):
            plgn.outputs.append(['blog', "Cant Save, a file already exists"])
            return
        os.rename(orig_name, new_name)
        with open('state','w') as sf:
            plgn.outputs.append(['blog', "Saved and Reloaded"])


# DOC(sumitj) 
# rr selects one from the given range
# range has only part 0-59, when the range is exhusted, it will raise a stopiteration
# causing the function to reinitialize, once the next bit has toggeled.

@plgn.schedule(cron(
    second = rr(range(0,60,59)),
    minute = rr(range(0,60,59)),    
    hour = rr(range(8,24,3)),       
    ))
def ask():
    if state() in (STATES['started'], STATES['blank']):
        m = len(motivate)
        plgn.outputs.append(['blog',motivate[randint(1, m*10) % m]])



#plgn.schedule(cron(second=(range(0,60))))
#def timeit(data=None, **details):
#    print "timeit", str(datetime.now().ctime())
#    plgn.outputs.append(['debug', str(datetime.now())])


@plgn.command('rename (?P<title>[a-zA-Z0-9!@#$%^&*() {}:?"<>]+)')
def rename(data, **details):
    if state() == STATES['started']:
        alllines = None
        with open(orig_name,'r') as f:
            alllines = f.readlines()
        header = yaml.load("".join(alllines[header_slice]))
        header['title'] = str(details['title']) or header['title']
        alllines[header_slice] = yaml.dump(header,default_flow_style=False).splitlines(True)
        with open(orig_name, 'w') as f:
            f.writelines(alllines)
        return 'Ok, Renamed to ' + header['title']
