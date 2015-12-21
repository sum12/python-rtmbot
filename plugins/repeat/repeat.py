import time
crontable = []
outputs = []
funcs={}
import re,youtube_dl,getpass,os



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


@command('repeat (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)', outputs)
def repeat(data, what):
    return 'repeating ' + what

@command('tell',outputs)
def tell(data,what=None):
	string = """Follow the following commands :
			download (link) a
				This function lets you download a video or audio directly. 
				'a' is optional parameter for downloading the audio file.
			queue (link) 
				This function appends the link to the download queue. Pass 'a' to download the audio.
			begin 
				This initiates the download of the queue
			ip
				This will return the ip of DJPI 
		"""		
	return string

@command('download (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)', outputs)
def download(data, what):
	user = getpass.getuser()
	location = '/home/'+user+'/bot_youtube_downloads/'
	if not os.access(location,os.F_OK):
		os.mkdir(location)
	l = list(what)
	l.remove('>')
	l.remove('<')
	what = "".join(l)
	location = location + '%(title)s.%(ext)s'
	location = unicode(location)
	y = {'outtmpl':location,'nooverwrites':'True'}
	if (what.split(" "))[1] == 'a':
		y = {'outtmpl':location,'nooverwrites':'True','format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}
	with youtube_dl.YoutubeDL(y) as ydl:
		ydl.download([what])
	return "done"

@command('queue (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)', outputs)
def queue(data,what):
	f = open('download_queue.txt','a')
	l = list(what)
	l.remove('>')
	l.remove('<')
	what = "".join(l)
	f.write(what)
	f.write('\n')
	f.close()
	return what+ 'added to download queue'

@command('begin',outputs)
def begin(data,what = None):
	if not os.access('download_queue.txt',os.F_OK):
		return "Queue does not exist. Please form a download queue first."
	f = open('download_queue.txt','r+')
	links = f.read()
	f.close()
	user = getpass.getuser()
	location = '/home/'+user+'/bot_youtube_downloads/'
        if not os.access(location,os.F_OK):
                os.mkdir(location)
	location = location + '%(title)s.%(ext)s'
        location = unicode(location)
	data = links.split("\n")
	data=data[:-1]
	for link in data:		
		print link
		if not link==" " or not link == "":
			y = {'outtmpl':location}
			if (link.split(" "))[1] == 'a':
                		y = {'outtmpl':location,'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}
	        		link =str(link.split(" ")[0])
			with youtube_dl.YoutubeDL(y) as ydl:
        	        	ydl.download([link])		
	print "OUT OF LOOP !"
	os.remove("download_queue.txt")
	return "All links have been downloaded on to your Pi"

@command('ip',outputs)
def ip(data, what=None):
	user = getpass.getuser()
	location = "/home/"+user+"/ip.txt"
	f = open(location,'r')
	data = f.read()
	f.close()    	
	return data

