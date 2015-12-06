import datetime as dt
import subprocess

import logging
from lib import *
outputs = []
crontable = []
logger = logging.getLogger('bot.sleeper')
logger.setLevel(logging.DEBUG)
plgn = Plugin()
command = lambda regex : plgn.command(regex, outputs) 
process_message = plgn.process_message

totalSleept = 0
startTime = dt.datetime.now()
count = 0

crontable.append([cron(), 'sleeper'])
def sleeper():
    global totalSleept
    totalSleept = totalSleept + 1
    global startTime
    curr = dt.datetime.now()
    calc = (dt.timedelta(seconds=totalSleept) + startTime)
    diff  = (calc - curr)
    if diff.total_seconds() > 1 or diff.total_seconds() < -1:
        global count
        count += 1
        if count >= 180:
            count = 0
            outputs.append(['random', 'diff is high'])

@command('restart')
def reload(data, **details):
    with open('plugins/reload.txt', 'a') as f:
        f.write(dt.datetime.now().isoformat()+'\n')
    return 'Done'



@command('slept')
def time(data, **details):
    global totalSleept
    global startTime
    curr = dt.datetime.now()
    calc = (dt.timedelta(seconds=totalSleept) + startTime)
    diff  = (calc - curr)
    return "Should be is {calc}, ie {diff} from {curr}".format(            
            calc = calc.strftime("%H:%M:%S"),
            diff = diff.total_seconds(),
            curr = curr.strftime("%H:%M:%S"),
            )


outputs.append(['random','Reloaded'])
