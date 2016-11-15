import requests
from itertools import repeat

from lib import Plugin, cron
import logging
logger = logging.getLogger('bot.managerclient')
logger.setLevel(logging.DEBUG)
plgn = Plugin('managerclient')



URL = ''

@plgn.command('exe (?P<config>(\d+,)*\d+)')
def exercise(data, **details):
    """ Store exe related data """
    URL = plgn.URL + '/daily' 
    r = requests.post(URL, data={'type':'exercise', 'data':details['config']}, verify=False)
    if r.status_code == 201:
        return 'Ok'
    else:
        return 'Failed to inform the server, please try again'

@plgn.schedule(repeat(25), maximum=1)
def ping(data, **details):
    r = requests.get(URL, verify=False)


@plgn.setupmethod
def init(config):
    plgn.URL = config['url']

