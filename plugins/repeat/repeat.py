import time
crontable = []
outputs = []
funcs={}
import re


def command(regex, outputs):
    global funcs
    def wrapper(func):
        funcs.setdefault('['+regex[0]+regex[0].upper()+']'+regex[1:], (func, outputs))
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
    
    

@command('repeat (?P<what>[-a-zA-Z0-9 ,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]]+)', outputs)
def repeat(data, what):
    return 'repeating ' + what

