import time
import re

from lib import Plugin, cron
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
plgn = Plugin('repeat')
plgn.__doc__ = "Demo/Dummy plugin"


@plgn.command('repeat (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def repeat(data, what):
    return 'repeating ' + what



#@plgn.schedule(cron(second=range(0,60,5)), maximum = 2)
#def logr(*args, **kwargs):
#    plgn.myid =myid= getattr(plgn,'myid',0) + 1
#    logger.info('start myid is %s' % myid)
#    time.sleep(20)
#    logger.info('end myid is %s' % myid)

