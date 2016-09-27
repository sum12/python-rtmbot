import requests
import time
import logging
from bs4 import BeautifulSoup
from lib import Plugin, cron


logger = logging.getLogger('bot.actlogin')
logger.setLevel(logging.DEBUG)
plgn = Plugin('actlogin')


plgn.password = plgn.username = plgn.URL = ''

@plgn.schedule(cron(hour=[5], minute=[0], second=[0]))
def relogin():
    logger.info('Now Logging out')
    logout()
    logger.info('Logged Out successfully')
    time.sleep(10)
    logger.info('Logging in now')
    login()
    logger.info('Logged in successfully')

    #plgn.outputs.append(['random', 'Relogged in successfully'])

def login():
    resp = requests.get(plgn.URL)
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
    pl[tag.attrs['name']] = plgn.username
    tag = allinps[2]
    pl[tag.attrs['name']] = plgn.password
    logger.debug( pl)
    s = requests.session()
    r = requests.post(url,pl)
    logger.debug( r)


def logout():
    resp = requests.get(URL)
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


# this is the default cron, that executes every 120 sec.
# it is executed my main thread directly
@plgn.schedule(cron(minute=range(0,60,5),second=[0]))
def checkAndLogin():
    if isLoggedOut():
        try:
            login()
        except Exception, e:
            logger.exception('Error in logging in')
            #plgn.outputs.append(['random', 'Currently logged out, will try to login'])
        else:
            pass
            #plgn.outputs.append(['random', 'Had to relogin'])


def isLoggedOut():
    try:
        resp = requests.get(URL, timeout=10)
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
        for tag in allinps:
            if tag.attrs.get('name') and tag.attrs['name'] == 'loggedInUser':
                logger.debug("Already logged in")
                return False
        return True
    except requests.exceptions.ConnectionError,e:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception,e:
        logger.exception('error getting logon status')
        return False

@plgn.setupmethod
def init(config):
    plgn.URL = config['url']
    plgn.username = config['username']
    plgn.password = config['password']
