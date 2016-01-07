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


URL = 'https://intense-falls-3111.herokuapp.com/daily'

@command('exe (?P<config>(\d+,)*\d+)')
def exercise(data, **details):
    r = requests.post(URL, data={'type':'exercise', 'data':details['config']}, verify=False)
    if r.status_code == 201:
        return 'Ok'
    else:
        return 'Failed to inform the server, please try again'

