import os
import logging
from datetime import datetime
from  random import randint
from lib import *

import re
outputs = []
crontable = []
logger = logging.getLogger('bot.blog')
plgn = Plugin()
command = lambda regex : plgn.command(regex, outputs) 
process_message = plgn.process_message

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

orig_name = 'blog.txt'
save_filepath = '/home/pi/blog/whispering-forest-1331/source/_posts/{dt}-daily-log.markdown'
para_regex = '(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)'
template = """---
layout: post
title: Daily-log
date: {dt}
path: '/home/pi/blog/whispering-forest-1331/source/_posts/{dt}-daily-log.markdown'
---
"""

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

def setup():
    if state() == STATES['blank']:
        f=open('state','w')
        f.close()
        with open(orig_name,'w') as f:
            f.write(template.format(dt=datetime.now().strftime('%Y-%m-%d')))

@command('blog '+ para_regex)
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




crontable.append([cron(
        hour=[23]
    ),'save'])
@command('saveblog')
def save(data=None, **details):                    # Crontasks are called without any arguments,
    if state() == STATES['started']:
        new_name=save_filepath.format(dt=datetime.now().strftime('%Y-%m-%d'))
        if os.path.exists(new_name):
            outputs.append(['blog', "Cant Save, a file already exists"])
        os.rename(orig_name, new_name)
        with open('state','w') as sf:
            outputs.append(['blog', "Saved and Reloaded"])


# DOC(sumitj) 
# rr selects one from the given range
# range has only part 0-59, when the range is exhusted, it will raise a stopiteration
# causing the function to reinitialize, once the next bit has toggeled.

crontable.append([cron(
    second = rr(range(0,60,59)),
    minute = rr(range(0,60,59)),    
    hour = rr(range(8,24,3)),       
    ),'ask'])
def ask():
    if state() in (STATES['started'], STATES['blank']):
        m = len(motivate)
        outputs.append(['blog',motivate[randint(1, m*10) % m]])



#crontable.append([cron(second=(range(0,60))), 'timeit'])
#def timeit(data=None, **details):
#    print "timeit", str(datetime.now().ctime())
#    outputs.append(['debug', str(datetime.now())])
