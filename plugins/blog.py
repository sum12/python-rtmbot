import time
import os
from datetime import datetime, timedelta
from  random import randint
outputs = []
crontable = []
# This is testcode for threadpool.py
# counter = 0
#def test():
#    global counter
#    counter +=1
#    time.sleep(5)
#    outputs.append(('debug',str(counter)))


#crontable = [( 2, 'test'), ]
import re
funcs = {}
def command(regex, outputs):
    global funcs
    def wrapper(func):
        funcs.setdefault('['+regex[0]+regex[0].upper()+']'+regex[1:], (func, outputs))
        return func
    return wrapper


def process_message(data):
    global funcs
    for regex, (fnname, outputs) in funcs.items():
        if 'text' in data:
            args = re.match(regex, data['text'])
            if args:
                ret = fnname(data, **(args.groupdict()))
                print 'setting output {ret} for {fnname}'.format(ret=ret,fnname=fnname.__name__)
                outputs.append([data['channel'], ret or 'Nothing'])
                return 



# HACK HACK HACK !!!!!
datetime.strptime("01","%H")
# http://bugs.python.org/issue7980

def atTime(dt):
    def wrap():
        d = 0
        i = 0
        a = datetime.today().date()
        b = datetime.strptime(dt,"%H:%M").time()
        while(d <= 0.0):
            i += 1
            c = datetime.combine(a,b)
            d =time.mktime(c.timetuple()) - time.time()
            a = datetime.today() + timedelta(seconds=60*i)
            a = a.date()
#            print time.time(), time.mktime(c.timetuple()) 

        return d
    return wrap

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

@command('blog '+ para_regex, outputs)
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




crontable.append([atTime("23:50"), 'save'])
@command('saveblog',outputs)
def save(data=None, **details):                    # Crontasks are called without any arguments,
    if state() == STATES['started']:
        new_name=save_filepath.format(dt=datetime.now().strftime('%Y-%m-%d'))
        if os.path.exists(new_name):
            outputs.append(['blog', "Cant Save, a file already exists"])
        os.rename(orig_name, new_name)
        with open('state','w') as sf:
            outputs.append(['blog', "Saved and Reloaded"])
    else:
         ask()


crontable.append([3*60*60,'ask'])
def ask():
    if state() in (STATES['started'], STATES['blank']):
        m = len(motivate)
        outputs.append(['blog',motivate[randint(1, m*10) % m]])



#crontable.append([atTime(), 'timeit'])
#def timeit(data=None, **details)
#    outputs.append(['debug', str(datetime.now())])
