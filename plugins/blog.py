import time
import os
import logging
from datetime import datetime, timedelta
from  random import randint, randrange

outputs = []
crontable = []

# This is testcode for threadpool.py
# counter = 0
#def test():
#    global counter
#    counter +=1
#    time.sleep(5)
#    outputs.append(('debug',str(counter)))

logger = logging.getLogger('bot.blog')
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
#                print 'setting output {ret} for {fnname}'.format(ret=ret,fnname=fnname.__name__)
                outputs.append([data['channel'], ret or 'Nothing'])
                return 


# HACK HACK HACK !!!!!
datetime.strptime("01","%H")
# http://bugs.python.org/issue7980

# DOC(sumitj) Randomizer function allowing to select a
# random value from a series of ranges, the selected values
# are from continuous ranges i.e. from # a-b, b-c, ... 
# where lst=[a,b,c]
# Returning a function so that it can be reinitialized when
# lst is exhausted.


def rr(lst):
    def rry():
        x = lst[0]
        for y in lst[1:]:
            yield randrange(x,y)
            x=y
    return rry

# DOC(sumitj) : This is something similar to counter
# where the bits toggle one after other, leading to a
# cron like behaviour
#
# curnt should be a callable, which return something iterable,
# it can be a list, or a generator

def recr(curnt,nxt=None):
    rt = nxt.next() if nxt!=None else 0
    while 1:
        for i in curnt(): 
            yield i,rt
        if nxt:
            rt = nxt.next() 
        else:
            raise StopIteration()

def rotrng(limit,rotBy=None,rotTo=None):
    lst = None
    try:
        int(limit)
        lst = range(limit)
    except:
        lst=limit
    if rotBy:
        return lst[rotBy:]+lst[:rotBy]
    elif rotTo:
        rotBy = lst.index(rotTo)
        return lst[rotBy:]+lst[:rotBy]
    return lst

# DOC(sumitj) helper function 
def make_cron(*s):
    bit=None 
    for lst in s: 
        if hasattr(lst, '__call__'):
            bit=recr(lst, bit)
        else:
            try:
                # DOC(sumitj) lambdas are always lazy evaluated,
                # since loop iteration cause lst to change, the lazy
                # evaluation leads to wrong values being evalated,
                # this is one way to have the values stuck to function.
                int(lst)
                bit=recr(lambda act=lst : range(act),bit)
            except:
                try:
                    iter(lst)   
                    bit=recr(lambda act=lst: act, bit)
                except:
                    raise Exception('Unable to make cron for %s' % lst) 
    return bit

def getdays(mnth, year):
    if mnth == 2 :
        if (year % 400 == 0 or year % 4 == 0):
            return 29
        else:
            return 28
    elif mnth in [1,3,5,7,8,10,11]:
            return 31
    else:   
        return 30


def cron(**dt):
    # TODO: 
    # (1) if the supplied values are nearer to current time, 
    #     then the evaluation willl be faster
    #     possibel fix: start iterating from `now`
    # (2) while iterating the days can go invalid eg: when iterating
    #     from jan to feb, the days will keep on counting till 31. since
    #     the range once decided it is not reevaluted.
    def checker():
        
        rotatr = datetime.now()
        d = { 
                'second':rotrng(60,rotBy=rotatr.second),
                'minute':rotrng(60,rotBy=rotatr.minute),
                'hour':rotrng(24,rotBy=rotatr.hour),
                'month':rotrng(range(1,13),rotTo=rotatr.month),
                'year':rotrng(range(2015,2115),rotTo=rotatr.year)
                }
        # datetime expects days of month to start from 1 and not 0
        # for february fix the progam needs to be restarted once in feb 
        # so that 'day' is back to 28/29. And fix for iteration purpose
        # will be, start rotating list.

        d['day'] = rotrng(range(1,getdays(d['month'], d['year'])+1),rotTo=rotatr.day)
        for k,v in d.items():
            dt.setdefault(k,v)
        z = make_cron(
                dt['year'], dt['month'], dt['day'], dt['hour'], dt['minute'], dt['second']
                )
        logger.debug('making generator')
        logged = False
        logged2 = False
        for i in z:
#            print i
            n = datetime.now()
            (second, (minute, (hour, (day, (month, (year, _)))))) = i
            nxt = datetime.now()
            try:
                nxt = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
            except Exception,e:
                if not logged:  # okay we have not logged, lets log it
                    logger.debug('date is incorrect')
                    logged = True
                continue
            if logged:
                logged = False # but this will never get that exception again since the cron has moved ahead
                logger.debug('incorect date loop has been pased once,')
            wait_time = (nxt - n).total_seconds() 
            if wait_time < 0 :
#                print 'negative', wait_time
                if not logged2:
                    logger.debug('got negative')
                    logged2 = True
                continue
            logger.info('returning once from checker should never print negative or invalid date, unless restarted')
            yield wait_time
    return checker()


# DOC(sumitj) awaiting deprecation
def atTime(*dt):
    def wrap():
        d = 0
        i = 0
        a = datetime.today().date()
        b = datetime.strptime(dt,"%H:%M").time()
        while(d <= 0.0):
            i += 1
            c = datetime.combine(a,b)
            d = time.mktime(c.timetuple()) - time.time()
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




crontable.append([cron(
        hour=[23]
    ),'save'])
@command('saveblog',outputs)
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



#crontable.append([cron(second=rr(range(0,60,5))), 'timeit'])
#def timeit(data=None, **details):
#    print "timeit", str(datetime.now().ctime())
#    outputs.append(['debug', str(datetime.now())])
