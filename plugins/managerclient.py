import requests

from lib import Plugin, cron
import logging
logger = logging.getLogger('bot.managerclient')
logger.setLevel(logging.DEBUG)
plgn = Plugin('managerclient')



URL = ''

@plgn.command('exe (?P<config>(\d+,)*\d+)')
def exercise(data, **details):
    """ Store exe related data """
    r = requests.post(URL, data={'type':'exercise', 'data':details['config']}, verify=False)
    if r.status_code == 201:
        return 'Ok'
    else:
        return 'Failed to inform the server, please try again'

@plgn.setupmethod
def init(config):
    global URL
    URL = config['url']

