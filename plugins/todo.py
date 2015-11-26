import os
import pickle
import re
from lib import Plugin
import logging
outputs = []
crontable = []
logger = logging.getLogger('bot.blog')
plgn = Plugin()
command = lambda regex : plgn.command(regex, outputs) 
process_message = plgn.process_message



    
tasks = {}

FILE="todo.data"
if os.path.isfile(FILE):
    tasks = pickle.load(open(FILE, 'rb'))

@command('tasks|fin|done|show|todo')
def todo(data, **args):
    global tasks
    channel = data["channel"]
    text = data["text"]
    #only accept tasks on DM channels
    if channel.startswith("D"):
        if channel not in tasks.keys():
            tasks[channel] = []
        #do command stuff
        if text.startswith("todo"):
            tasks[channel].append(text[5:])
            return 'added'
        if text == "tasks":
            output = ""
            counter = 1
            for task in tasks[channel]:
                output += "%i) %s\n" % (counter, task)
                counter += 1
            return output 
        if text == "fin":
            tasks[channel] = []
            return 'OK'
        if text.startswith("done"):
            num = int(text.split()[1]) - 1
            tasks[channel].pop(num)
            return 'OK'
        if text == "show":
            print tasks
        pickle.dump(tasks, open(FILE,"wb"))
