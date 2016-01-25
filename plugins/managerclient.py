import requests

from lib import Plugin, cron
import logging
outputs = []
crontable = []
logger = logging.getLogger('bot.managerclient')
logger.setLevel(logging.DEBUG)
plgn = Plugin()
command = lambda regex : plgn.command(regex, outputs) 
process_message = plgn.process_message



URL = ''

@command('exe (?P<config>(\d+,)*\d+)')
def exercise(data, **details):
    """ Store exe related data """
    r = requests.post(URL, data={'type':'exercise', 'data':details['config']}, verify=False)
    if r.status_code == 201:
        return 'Ok'
    else:
        return 'Failed to inform the server, please try again'


def setup(config):
    global URL
    URL = config['url']

