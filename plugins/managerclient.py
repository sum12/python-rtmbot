import requests
from itertools import repeat

from lib import Plugin, cron
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
plgn = Plugin('managerclient')




@plgn.command('exe (?P<config>(\d+,)*\d+)')
def exercise(data, **details):
    """ Store exe related data """
    URL = plgn.managerurl + '/daily' 
    r = requests.post(URL, data={'type':'exercise', 'data':details['config']}, verify=False)
    if r.status_code == 201:
        return 'Ok'
    else:
        return 'Failed to inform the server, please try again'

@plgn.schedule(maximum=1)
def ping():
    for url in plgn.URLS:
        logger.info('pinging %s' % url)
        r = requests.get(url, verify=False)


@plgn.setupmethod
def init(config):
    plgn.URLS = config.get( 'urls' ,[config.get('url')])
    plgn.managerurl = config.get('managerurl', config.get('url'))

