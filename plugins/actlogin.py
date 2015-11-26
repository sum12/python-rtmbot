import requests
from bs4 import BeautifulSoup

from lib import Plugin, cron
import logging
import passwordfile
outputs = []
crontable = []
logger = logging.getLogger('bot.blog')
plgn = Plugin()
command = lambda regex : plgin.command(regex, outputs) 
process_message = plgn.process_message


crontable.append([cron(hour=[21], minute=[0], second=[0]), 'relogin'])
def relogin():
    logger.info('Now Logging out')
    resp = requests.get("http://portal.acttv.in/web/blr/home")
    l = resp.content
    logger.debug( "got content")
    bs = BeautifulSoup(l)
    f=bs.findAll('form')[1]
    logger.debug( "found form")
    url = f.attrs['action']
    logger.debug( "found action")
    pl = {}
    allinps = f.findAll('input')
    logger.debug( "found input")
    tag = allinps[0]
    pl[tag.attrs['name']]= tag.attrs['value']
    tag =  allinps[1]
    pl[tag.attrs['name']] = passwordfile.username
    tag = allinps[2]
    pl[tag.attrs['name']] = passwordfile.password
    logger.debug( pl)
    s = requests.session()
    r = requests.post(url,pl)
    logger.debug( r)
    logger.info('Logged Out successfully')
    time.sleep(5)
    logger.info('Logging in now')
    resp = requests.get("http://portal.acttv.in/web/blr/home")
    l = resp.content
    logger.debug( "got content")
    bs = BeautifulSoup(l)
    f=bs.findAll('form')[1]
    logger.debug( "found form")
    url = f.attrs['action']
    logger.debug( "found action")
    pl = {}
    allinps = f.findAll('input')
    logger.debug( "found input")
    tag = allinps[0]
    pl[tag.attrs['name']]= tag.attrs['value']
    s = requests.session()
    r = requests.post(url,pl)
    logger.debug( r)
    logger.info('Logged in successfully')

    outputs.append(['random', 'Relogged in successfully'])

