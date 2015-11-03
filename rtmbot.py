#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True

import glob
import yaml
import json
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import watchdog
import importlib
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from argparse import ArgumentParser

from slackclient import SlackClient
import threadpool
from threadpool import ThreadPool

logger = logging.getLogger('bot')
logger.propagate = False

def setup_logger(cfg):
    if 'LOGFILE' in cfg:
        file_handler = RotatingFileHandler(cfg['LOGFILE'], 'a', 1 * 1024 * 1024, 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(getattr(logging, cfg['DEBUG']))
    logger.setLevel(getattr(logging, cfg['DEBUG']))
    logger.addHandler(file_handler)

def vvvv(*args, **kwargs):
    logger.debug(*args, **kwargs)

def vv(*args, **kwargs):
    logger.info(*args, **kwargs)

POOL = ThreadPool(3)

class RtmBot(FileSystemEventHandler):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.bot_plugins = []
        self.plugin_dir = directory+'/plugins'
        self.slack_client = None
        self.reload = True
        self.pool = POOL

        for plugin in glob.glob(self.plugin_dir+'/*'):
            sys.path.insert(0, plugin)
        sys.path.insert(0, self.plugin_dir)
        
    def on_modified(self, event):
        self.reload = True

    def connect(self):
        """Convenience method that creates Server instance"""
        self.slack_client = SlackClient(self.token)
        self.connected = False
        if self.slack_client.rtm_connect():
            self.connected = True

    def start(self):
        self.connect()
        self.load_plugins()
        while True:
            try:
                for reply in self.slack_client.rtm_read():
                    self.input(reply)
                self.crons()
            except:
                self.connected = False
                self.connect()
                self.crons()
            else:
                self.autoping()
                self.output()
            time.sleep(.1)
            if self.reload:
                self.bot_plugins = []
                vvvv('reloading') 
                self.load_plugins()
            
    def autoping(self):
        #hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now
    def input(self, data):
        if 'type' in data:
            function_name = 'process_' + data['type']
            vvvv('got {}'.format(function_name))
            for plugin in self.bot_plugins:
                plugin.register_jobs()
                vvvv('doing plugin %s' % plugin.name)
                plugin.do(function_name, data)
    def output(self):
        for plugin in self.bot_plugins:
            limiter = False
            for output in plugin.do_output():
                channel = self.slack_client.server.channels.find(output[0])
                if channel != None and output[1] != None:
                    if limiter == True:
                        time.sleep(.1)
                        limiter = False
                    message = output[1].encode('ascii','ignore')
                    channel.send_message('{}'.format(message))
                    limiter = True
    def crons(self):
        for plugin in self.bot_plugins:
            plugin.do_jobs()
    def load_plugins(self):
        for plugin in glob.glob(self.plugin_dir+'/*.py') + glob.glob(self.plugin_dir+'/*/*.py'):
            vv("Plugin:"+plugin)
            name = plugin.split('/')[-1][:-3]
            plg = None
            try:
                plg = Plugin(self, name) 
            except Exception, e:
                logging.exception('error loading plugin %s' % name)
                continue
            self.bot_plugins.append(plg)
        self.reload = False

class Plugin(object):
    def __init__(self, bot, name, plugin_config={}):
        self.name = name
        self.jobs = []
        self.pool = bot.pool
        if name in sys.modules:  
            old_module = sys.modules.pop(name)
        try:
            self.module = __import__(name)
        except Exception, e:
            print 'Error imporrting %s' % name
            print str(e)
            raise e
        self.register_jobs()
        self.outputs = []
        if name in config:
            vv('config found for: ' + name)
            self.module.config = config[name]
        if 'setup' in dir(self.module):
            self.module.setup()
    def register_jobs(self):
        if 'crontable' in dir(self.module):
            for checker, function in self.module.crontable:
                job = Job(checker, eval('self.module.'+function))  
                if job.isScheduled:
                    self.pool.schedule_task(job.checker, job.function)
                else:
                    self.jobs.append(job)
            if self.module.crontable:
                vv("crontable:"+ str(self.module.crontable))
            self.module.crontable = []
        else:
            self.module.crontable = []

    def do(self, function_name, data):
        if function_name in dir(self.module):
            #this makes the plugin fail with stack trace in debug mode
            if debug:
                try:
                    vvvv('calling %s'%function_name)
                    eval('self.module.'+function_name)(data)
                except Exception, e:
                    logging.exception('problem in module {} {}'.format(function_name, data))
            else:
                eval('self.module.'+function_name)(data)
        if 'catch_all' in dir(self.module):
            try:
                self.module.catch_all(data)
            except Exception, e:
                logging.exception('problem in catch all')

    def do_jobs(self):
        for job in self.jobs:
            # TODO: this should be like cron and not like poll
            if not job.isScheduled and job.check():
                self.pool.add_task(job.function)

    def do_output(self):
        output = []
        while True:
            if 'outputs' in dir(self.module):
                if len(self.module.outputs) > 0:
                    vv('output from {}'.format(self.module))
                    output.append(self.module.outputs.pop(0))
                else:
                    break
            else:
                self.module.outputs = []
        return output

class Job(object):
    def __init__(self, checker, function):
        self.function = function
        self.checker = checker
        try:
            iter(checker)
            self.isScheduled = True
        except:
            self.isScheduled = False
        self.lastrun = 0
    def __str__(self):
        return '{} {} {}'.format(self.function, self.checker, self.lastrun)
    def __repr__(self):
        return self.__str__()
    def check(self):
        if not self.isScheduled:
            if self.lastrun + self.checker < time.time():
                self.lastrun = time.time()
                return True
        return False

class UnknownChannel(Exception):
    pass


def main_loop():
    vv("Directory:"+ directory)
    try:
        observer = Observer()
        observer.schedule(bot, bot.plugin_dir, recursive=True)
        observer.start()
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        logging.exception('OOPS')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        help='Full path to config file.',
        metavar='path'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    directory = os.path.dirname(sys.argv[0])
    if not directory.startswith('/'):
        directory = os.path.abspath('{}/{}'.format(os.getcwd(),
                                directory
                                ))

    config = yaml.load(file(args.config or 'rtmbot.conf', 'r'))
    debug = config['DEBUG'] == 'DEBUG'
    setup_logger(config)
    bot = RtmBot(config['SLACK_TOKEN'])
    site_plugins = []
    files_currently_downloading = []
    job_hash = {}

    if config.has_key('DAEMON'):
        if config['DAEMON']:
            import daemon
            with daemon.DaemonContext():
                main_loop()
    main_loop()

