import time
import re,urbandict

from lib import Plugin
plgn = Plugin('dictionay')


@plgn.command('define (?P<what>[-a-zA-Z]+)')
def temp(data, what):
	final=""
	d=urbandict.define(str(what))
	for item in d:
		final =final + item['def'] 
	return final

@plgn.command('use (?P<what>[-a-zA-Z]+)')
def temp(data, what):
	final=""
	d=urbandict.define(str(what))
	for item in d:
		final =final + item['example'] 
	return final
