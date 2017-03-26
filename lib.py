import time
import os
import logging
from datetime import datetime, timedelta, date
from  random import randint, randrange
from collections import namedtuple, defaultdict
import re
from functools import wraps

# DOC(sumitj) Randomizer function allowing to select a
# random value from a series of ranges, the selected values
# are from continuous ranges i.e. from # a-b, b-c, ... 
# where lst=[a,b,c]
# Returning a function so that it can be reinitialized when
# lst is exhausted.

logger = logging.getLogger('bot.lib')


def rr(lst):
    def rry(*args, **kwargs):
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
        for i in curnt(rt): 
            yield i,rt
        if nxt:
            rt = nxt.next() 
        else:
            raise StopIteration()

# DOC(sumitj) just rotating the would not help as it would miss the stop iteration exception
# at the standard end of listi, ie at 59 in case of seconds. thus hours wont advance gnerating
# negative date. Also if the script started at 43 sec then the list would always start from
# 43 sec thus 0-43 would be always missed.

def rotrng(limit,rotBy=None,rotTo=None):
    def gnr(limit, rotBy, rotTo):
        lst = None
        try:
            int(limit)
            lst = range(limit)
        except:
            lst=limit
        if not rotBy and rotTo:
            if rotTo in lst:
                rotBy = lst.index(rotTo)
            else:
                prev = lst[0]
                for cur in lst[1:]:
                    if cur < rotTo:
                        prev = cur
                    else:
                        break
                rotBy = lst.index(prev) + 1
        yield lst[rotBy:]
        while 1:
            yield lst
    return (lambda prevbits,z=gnr(limit, rotBy, rotTo): next(z))

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
                bit=recr(lambda prevbits, act=lst : range(act),bit)
            except:
                try:
                    iter(lst)   
                    bit=recr(lambda prevbits, act=lst: act, bit)
                except:
                    raise Exception('Unable to make cron for %s' % lst) 
    return bit

def getdays(mnth, year):
    # + 1 to make it compatible for range
    if mnth == 2 :
        if (year % 400 == 0 or year % 4 == 0):
            return 29 + 1
        else:
            return 28 + 1
    elif mnth in [1,3,5,7,8,10,12]:
            return 31 + 1
    else:   
        return 30 + 1


def cron(**dt):
    # TODO: 
    # (2) while iterating the days can go invalid eg: when iterating
    #     from jan to feb, the days will keep on counting till 31. since
    #     the range once decided it is not reevaluted.
    #     Partially fixed.
    def checker():
        
        rotatr = datetime.now()
        d = [ 
                ('year',rotrng(range(2015,2115),rotTo=rotatr.year), range(2015,2115)) ,
                ('month',rotrng(range(1,13),rotTo=rotatr.month), range(1,13)),
                ('hour',rotrng(24,rotBy=rotatr.hour), 24),
                ('minute',rotrng(60,rotBy=rotatr.minute), 60),
                ('second',rotrng(60,rotBy=rotatr.second), 60) ]
        # datetime expects days of month to start from 1 and not 0
        # for february fix the progam needs to be restarted once in feb 
        # so that 'day' is back to 28/29. And fix for iteration purpose
        # will be, start rotating list.
        totdays = range(1,getdays(rotatr.month,rotatr.year))
        day = ('day',rotrng(totdays,rotTo=rotatr.day), totdays)
        d.insert(2, day)

        # if rotation should only be done so that we arrive at current time,
        # but if minute=[22] and second=None, then second means *, so its range will be
        # [0-60], now rotating that does not make sense, As it has to start form 0 and
        # not from 'rotated second'.
        # So if found, set the non-rotated-value, else keep use rotated value
        found = False
        for k,rv,nrv in d:
            if k in dt :
                found = True
                continue
            elif found and k not in dt:
                dt[k] = nrv
            else:
                dt[k] = rv
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
                nxt = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=0)
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
            global SELECTEDDATE
            SELECTEDDATE = nxt
            logger.debug('returning once from checker should never print negative or invalid date, unless restarted')
            # global SELECTEDDATE
            # SELECTEDDATE = nxt
            yield wait_time
    return checker()

SELECTEDDATE = None



def rangecreater(d, realrange):
    
    starrex = "^(?P<star>\*)/(?P<freq>\d+)$"
    rangerex = "^(?P<start>\d+)-(?P<end>\d+)(/(?P<freq>\d+))?$"
    if d['star']:
        return range(*realrange)
    if d['starfreq']:
        z = re.match(starrex, d['starfreq'])
        if z:
            freq = z.groupdict()['freq']
            freq = int(freq)
            realrange.append(freq)
            return range(*realrange)
    if d['range'] or d['rangefreq']:
        z = re.match(rangerex, d['range'] or d['rangefreq'])
        if z:
            vals = z.groupdict()
            freq = int(vals['freq'] or 1)
            start = max(realrange[0], int(vals['start']))
            # +1 is cox realrange[1] is adjusted,
            # range(1,10), will not give 10
            end = min(realrange[1], int(vals['end'])+1)
            if start and end and start <= end:
                if start == end: 
                    return [start]
                return range(start, end, freq)
    if d['lov']:
        provided = sorted(map(int, d['lov'].split(',')))
        provided[-1] = provided[-1] + 1
        start = max(realrange[0], min(provided))
        end = min(realrange[1], max(provided))
        if start == end: 
            return [start]
        return range(start, end)
    raise Exception('Could not categorize cron piece')


# Ranges of values are not checked, but rather automcatically truncated if
# found outside of the range.
# In case static values are provided and turn out to be invalid dates. make_cron
# will generate a negative or invalid date. Thus leading to a controlled failure.
#
# Divide the cronstring by space, and scan-check all parts are present and
# have no negative values. 
# Generate range_string for each part, using rotrng the ranges to correct position
# and return the corresponding generators for each
#
def cronfromstring(cronstr):
    """
    pasrse and create cron flipflop
    """
    rex =    "^(?P<starfreq>\*/\d+)$|\
^(?P<star>\*)$|\
^(?P<rangefreq>\d+-\d+/\d+)$|\
^(?P<range>\d+-\d+)$|\
^(?P<lov>(\d+,?)+)$"
    order = ('minute', 'hour', 'dom', 'month', 'dow')
    ranges = [[0,60], [0,24], None, [1,13], [0,8]]
    cronstr = cronstr.split()

    # parse and store the groupdict of the parse parts of the cronstring
    todict = dict(zip(order, map(
            lambda x: re.match(rex,x).groupdict() if re.match(rex, x) else None,
            cronstr)))
    # if either not all parts are present or if any part is none ie all parts
    # should have 'True' value. (bool(None) is False)
    if set(order) != set(todict.keys()) or not all(todict.values()):
        raise Exception('Invalid cronstring')

    def calcdays(prevbits):
        # every bit of recr function receives input.
        # these are outputs from bits before it.
        # cronbits are: year, month, day, minute, second
        # print prevbits
        (month, (year, endofbits)) = prevbits
        #cron send number from 0-7, where 0 and 7 both mean sunday
        #  0,1,2,3,4,5,6
        #0,1,2,3,4,5,6,7

        # daysinthismonth = rotrng(rangecreater(daysparsed, [1,getdays(year, month)]), rotTo=now.day)
        daysinthismonth = (rangecreater(daysparsed, [1,getdays(month, year)]))
        # print daysinthismonth, getdays(month, year)

        # this loop iterate maximum 7 times before yielding a value
        # not worth optimizing

        # print daysofweek
        for day in daysinthismonth:
            if date( year, month, day).weekday() + 1 not in daysofweek:
#                print '%s,'% day,
#                print daysofweek,
#                print date( year, month, day),date( year, month, day).weekday()
                continue
            yield day

    now = datetime.now()
    kwargs = {}
    if not todict['minute']['star']: 
        kwargs['minute'] = rangecreater(todict['minute'], ranges[0])
    if not todict['hour']['star']:
        kwargs['hour'] = rangecreater(todict['hour'], ranges[1])
    if not todict['month']['star']:
        kwargs['month'] = rangecreater(todict['month'], ranges[3])

    kwargs['day'] = calcdays 
    daysparsed = todict['dom']
    kwargs['second'] = [1]
    daysofweek = rangecreater(todict['dow'], ranges[4])
    

    return cron(**kwargs)


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

Func = namedtuple('Func', ['fn', 'help', 'private_only', 'restrict_to'])
def NOOP(*a,**kw): 
    pass
class Plugin(object):
    def __init__(self, name):
        self.funcs = defaultdict(Func)
        self.outputs = []
        self.crontable = []
        self.name = name 
        self.maxcount = {}
        self.schedules = {}
        self.funcids = {}

        @self.command('help( (?P<plugin>\w+)( (?P<action>\w+))?)?', help = 'help')
        def helper(data, plugin, action):
            """usage: help
usage: help   "plgin-name or plgn-number"
usage: help   "plgin-name or plgn-number"    "command-name or command-number"
        """
            ret = []
            fn = None
            if plugin and plugin.lower() in {self.name, str(self.plgnid)} and action:
                try:
                    action = int(action)
                except ValueError:
                    for fntuple in self.funcs.values():
                        if fntuple[1] == action and fntuple[0] != helper:
                            fn = fntuple[0]
                            ret = fn.__doc__ or 'Nope, not documented'
                else:
                    try:
                        fn = self.funcs.values()[action-1][0]
                        ret = fn.__doc__ or 'Nope, not documented'
                    except IndexError :
                        ret = 'Cant you even read numbers'
                    except :
                        ret = 'Something is wrong with the plugin'
            elif plugin and plugin.lower() in {self.name, str(self.plgnid)}:
                ret = [
                        ("*" if fntuple[2] else "") + ("#" if fntuple[3] else "") + fntuple[1] 
                        for fntuple in self.funcs.values()
                        ]
                ret = "\n".join(["%2i. %s" % (ind +1, s) for ind,s in enumerate(ret)])
                ret += ("\n\n* - Private/Direct message only \n # - Restricted Access")
            elif not plugin:
                ret = "%2i. %s\n%s" %(self.plgnid, self.name, self.__doc__ or "")
            return ret


    def setup(self, config=None):
        if not config:
            self.plgnid = getattr(self, 'plgnid', self.name)
            self.cronconfig = {}
        else:
            self.plgnid = config['plgnid']
            self.cronconfig = config.get('cron', None)
            print self.schedules.values()
            for funcid, schfunc in self.schedules.items()[:]:
                func = self.funcids[funcid]
                try:
                    self.schedules[funcid] = schfunc or cronfromstring(self.cronconfig[func.__name__])
                except KeyError:
                    log.error('%s from %s has no cron, cron will not be scheduled' % (func.__name__, self.name))
                except Exception:
                    raise Exception('unable to create an schedule for %s' % func.__name__)
            

    def setupmethod(self, func):
        def wrapper(config=None):
            self._setup(config)
            func(config)
        self._setup = self.setup
        self.setup = wrapper 
        return wrapper

    def command(self, regex, help='', private_only=False, restrict_to=None):
        def wrapper(func):
            rx = regex
            if regex[0].lower() in 'qwertyuiopasdfghjklzxcvbnm':
                rx ='['+regex[0]+regex[0].upper()+']'+regex[1:] 
            self.funcs.setdefault(rx , (func, help or regex.split()[0], private_only, restrict_to))
            return func
        return wrapper

    def process_message(self, data):
        for regex, (fn, _, private_only, restrict_to) in self.funcs.items():
            if 'text' in data:
                args = re.match(regex, data['text'])
                if not args: continue
                if private_only and not data['channel'].lower().startswith('d'): continue
                if restrict_to:
                    if not hasattr(self, restrict_to):
                        logger.info('restrict_to (%s) defined, but is not available' % restrict_to)
                        continue
                    restrict_to = getattr(self, restrict_to)
                    by = data['user_object'].name if data.get('user_object') else data['user']
                    if by not in restrict_to:
                        continue
                ret = fn(data, **(args.groupdict()))
#                print 'setting output {ret} for {fnname}'.format(ret=ret,fnname=fnname.__name__)
                if ret:
                    self.outputs.append([data['channel'], ret ])

    def schedule(self, schfunc=None, maximum=None, prestart=NOOP, postdone=NOOP):
        def wrapper(func, schfunc=schfunc):
            self.maxcount[id(func)] = maximum
            self.schedules[id(func)] = schfunc
            self.funcids[id(func)] = func
            def limittomax():
                for t in self.schedules[id(func)]:
                    while self.maxcount[id(func)] != None and not self.maxcount[id(func)]:
                        t = max(t-2, 1)
                        # logger.debug('delaying %s' % func.__name__)
                        yield -2
                    if self.maxcount[id(func)] != None:
                        self.maxcount[id(func)] -= 1
                    yield t
            @wraps(func)
            def context():
                prestart()
                ret = func()
                if ret:
                    self.outputs.append( ["random", ret])
                postdone()
                if self.maxcount[id(func)] != None:
                    self.maxcount[id(func)] += 1
            self.crontable.append([limittomax(), context])
            return func
        return wrapper
