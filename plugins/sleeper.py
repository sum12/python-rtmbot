import datetime as dt

import logging
from lib import *
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
plgn = Plugin('sleeper')

totalSleept = None
startTime = None
count = 0

@plgn.schedule(cron(second=range(0,60,5)))
def sleeper():
    global totalSleept
    global startTime
    if totalSleept == None:
        totalSleept = 0
    else:
        totalSleept = totalSleept + 5
    startTime = startTime or dt.datetime.now()
    curr = dt.datetime.now()
    calc = (dt.timedelta(seconds=totalSleept) + startTime)
    diff  = (calc - curr)

    logger.debug("Should be is {calc}, ie {diff} from {curr}".format(            
            calc = calc.strftime("%H:%M:%S"),
            diff = diff.total_seconds(),
            curr = curr.strftime("%H:%M:%S"),
            ))
    if diff.total_seconds() > 5 or diff.total_seconds() < -5:
        global count
        count += 1
        if count >= 12: # 12*5=60secs, 1min wait before reloading
            count = 0
#            plgn.outputs.append(['random', 'diff is high, reloading'+"Should be is {calc}, ie {diff} from {curr}".format(            
#            calc = calc.strftime("%H:%M:%S"),
#            diff = diff.total_seconds(),
#            curr = curr.strftime("%H:%M:%S"),
#            )])
            reload()


@plgn.command('restart')
def reload(data=None, **details):
    with open('plugins/reload.txt', 'a') as f:
        f.write(dt.datetime.now().isoformat()+'\n')
    return 'Done'



@plgn.command('slept')
def timeit(data, **details):
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


#plgn.outputs.append(['random','Reloaded'])
