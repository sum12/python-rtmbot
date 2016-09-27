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
