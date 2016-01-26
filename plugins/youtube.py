import time
import logging
import re,youtube_dl,getpass,os

from lib import Plugin, cron
logger = logging.getLogger('bot.youtube')
logger.setLevel(logging.DEBUG)
plgn = Plugin('youtube')


@plgn.command('tell')
def tell(data,what=None):
	string = """Follow the following commands :
			download (link) a
				This function lets you download a video or audio directly. 
				'a' is optional parameter for downloading the audio file.
			queue (link) 
				This function appends the link to the download queue. Pass 'a' to download the audio.
			begin 
				This initiates the download of the queue.
			list all downloads
				This function will simply return all the items that are present in the downloads directory on raspberry pi.
			ip
				This will return the ip of DJPI. 
		"""		
	return string

#This function will help reduce the redundacny of youtube_dl part of downloader everywhere !
def link_downloader(link,location):
	y = {'outtmpl':location,'nooverwrites':'True'}
        x = link.split(" ")
	if len(x)>1 and x[1] == 'a':
                y = {'outtmpl':location,'nooverwrites':'True','format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}
       		link = str(x[0])
	print "Hi"
	with youtube_dl.YoutubeDL(y) as ydl:
                ydl.download([link])
        return "done"

@plgn.command('download (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
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
	
	output = link_downloader(what,location)
	return output

@plgn.command('queue (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
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

@plgn.command('begin')
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
	count = len(data)
	for link in data:		
		print str(count) + " videos/audios are to yet be downloaded"
		if not link==" " or not link == "":
			link_downloader(link,location)
		count = count - 1
	os.remove("download_queue.txt")
	return "All links have been downloaded on to your Pi"

@plgn.command('list all downloads')
def listings(data,what=None):
	print "Hi"
	user = getpass.getuser()
	location = '/home/'+user+'/bot_youtube_downloads/'
	output = "\n".join(os.listdir(location))
	print location , output
	return output

@plgn.command('ip')
def ip(data, what=None):
	user = getpass.getuser()
	location = "/home/"+user+"/ip.txt"
	f = open(location,'r')
	data = f.read()
	f.close()    	
	return data

