import time,requests
crontable = []
outputs = []
funcs={}
a= []
import re,getpass,os,time,csv

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

@command('Url (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)', outputs)
def experiment(data, what):
	if not os.access('data.csv',os.F_OK):
		data_write(' ',' ', ' ')
	a = time.asctime(time.localtime(time.time()))
	x = what.split(" ")
	if len(x)>1:
		description = " ".join(x[1:])
		what = x[0]
	else:
		description = " "
	
	temp = list(what)
	if '>' in temp:
		temp.remove('>')
	if '<' in temp:
		temp.remove('<')	
	what = "".join(temp)
	#filter to check if the link exists and is valid
	if requests.get(what).status_code != 200:
		return "Not a valid link"		
	
	#the following three lines help in changing the default date format of the type Jan  9 to Jan 9 thereby facilitating date search for URL
	temp=a.split("  ")
	a = "".join(temp)
	
	#filter to check if the link already exixsts in the database. 
	if not search(data,what):
		print a,what,description
		data_write(a,what,description)
		return "Noted to database"
	else:
		return search(data,what)
def data_write(timestamp,link,description):
	with open('data.csv','a') as f:
		fieldnames = ['Time-Stamp','Link','Description']
		writer = csv.DictWriter(f,fieldnames=fieldnames)
		if link == ' ' and timestamp == ' ' and description == ' ': 
			writer.writeheader()
		elif not link == ' ' or not link =='':
			writer.writerow({'Time-Stamp':timestamp,'Link':link,'Description':description})
		else:
			return 'None'

def reading():
	with open('data.csv','r') as f:
		reader = csv.DictReader(f)
		for row in reader:
			yield  str(row['Time-Stamp'])+"   "+str(row['Link'])+"   "+ str(row['Description']) + "\n"
@command('search (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)', outputs)
def search(data, what):
		global a
		final = ""
		x = what.split(" ")
		x = map(str,x)
		define()
		print x
		if x[0]=='all' and len(x)==1:
			while 1:
				try:
					 temp = a.next()
				except:
					break
				else:
					final = final+temp
		else:
			string  = " ".join(x[0:])
			temp = list(string)
			if '>' in temp or '<' in temp:
				temp.remove('<')
				temp.remove('>')
				string  = "".join(temp)
			while 1:
				try:
					 temp = a.next()
				except:
					break
				else:
					print string , temp, final
					if string in temp:
						final = final+temp
		return final
def define(*var):
	global a
	a = reading()

