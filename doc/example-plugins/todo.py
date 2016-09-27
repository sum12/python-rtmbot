import os
import pickle
from lib import Plugin
plgn = Plugin('todo')

plgn.tasks = {}
logger = logging.getLogger('bot.todo')

FILE="todo.data"
if os.path.isfile(FILE):
    plgn.tasks = pickle.load(open(FILE, 'rb'))

@plgn.command('tasks|fin|done|show|todo')
def todo(data, **args):
    channel = data["channel"]
    text = data["text"]
    #only accept tasks on DM channels
    if channel.startswith("D"):
        if channel not in plgn.tasks.keys():
            plgn.tasks[channel] = []
        #do command stuff
        if text.startswith("todo"):
            plgn.tasks[channel].append(text[5:])
            return 'added'
        if text == "tasks":
            output = ""
            counter = 1
            for task in plgn.tasks[channel]:
                output += "%i) %s\n" % (counter, task)
                counter += 1
            return output 
        if text == "fin":
            plgn.tasks[channel] = []
            return 'OK'
        if text.startswith("done"):
            num = int(text.split()[1]) - 1
            plgn.tasks[channel].pop(num)
            return 'OK'
        if text == "show":
            print plgn.tasks
        pickle.dump(plgn.tasks, open(FILE,"wb"))
