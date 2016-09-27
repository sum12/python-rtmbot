Plug-ins are python scripts with functions with which take actions when a regex matching them is passed.

[repeat.py](./../example-plugin/repeat/repeat.py)  
```
## Import the Plugin class. 
## Create an instance, with a name.
from lib import Plugin  
plgn = Plugin(__file__[:-3])

## REgex     : Used while selecting a matching command.
##             its a python regex, used for string matching any text coming in.
##             All the NAMED-GROUPS in the regex are passed as **kwargs to the handler.
## Return    : And whatever the handler returns is given sent back on the same channel.
## DocString : The doc string is used to provides usage and any help on the command.
@plgn.command('repeat (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\]\\n]+)')
def repeat(data, what):
    """usage: repeat I would like this to be repeat. Can you?
This command echos back any string it receives"""
    return 'repeating ' + what

```


[actlogin.py](./../example-plugin/actlogin.py)  
My ISP logsout once every 24hours. (Relogging in when browsing is painfully slow).
So at 5am everyday the command will logout and login.
```
from lib import Plugin, cron
plgn = Plugin(__file__[:-3])

## SCHEDULE  : The command is scheduled to be run every day
@plgn.schedule(cron(hour=[5], minute=[0], second=[0]))
def relogin():
    logout()
    time.sleep(10)
    login()
    return 'Relogged in successfully.'

## SCHEDULE  :  check every 5 mins, if we have internet connection.
@plgn.schedule(cron(minute=range(0,60,5),second=[0]))
def checkAndLogin():
    if isLoggedOut():
        login()
        return 'Relogged in successfully'

## SETUP  : Get config values from the conf file.
##          and setup copy values locally.
@plgn.setupmethod
def init(config):
    plgn.URL = config['url']
    plgn.username = config['username']
    plgn.password = config['password']
```


Create Plugins
--------

####Incoming data
Plugins are callback based and respond to any event sent via the rtm websocket. To act on an event, create a function definition called process_(api_method) that accepts a single arg. For example, to handle incoming messages:

    def process_message(data):
        print data

This will print the incoming message json (dict) to the screen where the bot is running.

Plugins having a method defined as ```catch_all(data)``` will receive ALL events from the websocket. This is useful for learning the names of events and debugging.

####Outgoing data
Plugins can send messages back to any channel, including direct messages. This is done by appending a two item array to the outputs global array. The first item in the array is the channel ID and the second is the message text. Example that writes "hello world" when the plugin is started:

    outputs = []
    outputs.append(["C12345667", "hello world"])
        
*Note*: you should always create the outputs array at the start of your program, i.e. ```outputs = []```

####Timed jobs
Plugins can also run methods on a schedule. This allows a plugin to poll for updates or perform housekeeping during its lifetime. This is done by appending a two item array to the crontable array. The first item is the interval in seconds and the second item is the method to run. For example, this will print "hello world" every 10 seconds.

    outputs = []
    crontable = []
    crontable.append([10, "say_hello"])
    def say_hello():
        outputs.append(["C12345667", "hello world"])

####Plugin misc
The data within a plugin persists for the life of the rtmbot process. If you need persistent data, you should use something like sqlite or the python pickle libraries.

####Todo:
Some rtm data should be handled upstream, such as channel and user creation. These should create the proper objects on-the-fly.
