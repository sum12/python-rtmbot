import os
import pickle
outputs = []
crontabs = []
funcs={}

import re

def command(regex, outputs):
    global funcs
    def wrapper(func):
        funcs.setdefault(regex, (func, outputs))
        return func
    return wrapper


def process_message(data):
    global funcs
    for regex, (fnname, outputs) in funcs.items():
        if 'text' in data:
            args = re.match(regex, data['text'])
            if args:
                ret = fnname(data, **(args.groupdict()))
                print 'setting output {ret} for {fnname}'.format(ret=ret,fnname=fnname.__name__)
                outputs.append([data['channel'], ret or 'Nothing'])
                return 
    
tasks = {}

FILE="plugins/todo.data"
if os.path.isfile(FILE):
    tasks = pickle.load(open(FILE, 'rb'))

@command('tasks|fin|done|show|todo',outputs)
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
