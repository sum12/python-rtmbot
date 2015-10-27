import time
import os
from datetime import datetime
from  random import randint
outputs = []
crontables = []
# This is testcode for threadpool.py
# counter = 0
#def test():
#    global counter
#    counter +=1
#    time.sleep(5)
#    outputs.append(('debug',str(counter)))


#crontables = [( 2, 'test'), ]
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
    



template = """---
layout: post
title: Daily-log
date: {dt}
path: /home/pi/blog/whispering-forest-1331/source/_posts/{dt}-daily-log.markdown
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
    if not os.path.exists('blog.txt'):
        with open('blog.txt','w') as f:
            f.write(template.format(dt=datetime.now().strftime('%Y-%m-%d')))
    if not os.path.exists('state'):
        f=open('state','w')
        f.close()

@command('blog (?P<what>[-a-zA-Z0-9 ,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]]+)', outputs)
def blogging(data, **details):
    state(STATES['started'])
    fs = '`{dt}`: {what}\n\n\n'.format(dt=datetime.now().strftime('%Y-%m-%d'), what=details['what'])
    with open('blog.txt','a') as f:
        f.write(fs)
    return 'Thanks a lot, have a wonderfull day'



def state(now=''):
    if now == '':
        with open('state','r') as f:
            st = f.readline()
            return STATES[st] if st in STATES else STATES['blank']
    else:
        with open('state', 'w') as f:
            f.write(now)


@command('saveblog',outputs)
def save(data, **details):
    orig_name = 'blog.txt'
    if os.path.exists(orig_name):
        new_name='/home/pi/blog/whispering-forest-1331/source/_posts/{dt}-daily-log.markdown'.format(dt=datetime.now().strftime('%Y-%m-%d'))
        if os.path.exists(new_name):
#            outputs.append(['blog', "Cant Save, a file already exists"])
            return 'Cant Save, a file already exists'
        os.rename(orig_name, new_name)
        with open(orig_name,'w') as f:
            f.write(template.format(dt=datetime.now().strftime('%Y-%m-%d')))
            return 'Saved and reloaded'


crontables.append([3*60,'ask'])
def ask():
    if state() in (STATES['started'], STATES['blank']):
        m = len(motivate)
        outputs.append(['blog',motivate[randint(1, m*10) % m]])
