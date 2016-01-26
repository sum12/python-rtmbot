import time
import re

from lib import Plugin
plgn = Plugin('repeat')


@plgn.command('repeat (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def repeat(data, what):
    return 'repeating ' + what

