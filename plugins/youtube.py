import time,os,subprocess
import logging
import re,youtube_dl,getpass,os

from lib import Plugin, cron
logger = logging.getLogger('bot.youtube')
logger.setLevel(logging.DEBUG)
plgn = Plugin('youtube')

location = '/home/'+'pi'+'/bot_youtube_downloads/'
location = unicode(location)
location_video = location +'%(title)s.%(ext)s'

queued_links = 'download_queue.txt'

old,new = [],[]
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
def link_downloader(link):
        y = {'outtmpl':location_video,'logger':logger,'nooverwrites':'True'}
        x  = link.split(" ")
	if len(x)>1 and x[1] == 'a':
            y = {'outtmpl':location_video, 'logger':logger,'nooverwrites':'True','format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}
	link = str(x[0])
        ydl= youtube_dl.YoutubeDL(y)
        try:
            ydl.download([link])
            return 1
        except Exception as e:
            logger.debug(e)
            return e


@plgn.command('download <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)>')
def download(data, what):
	global old,new
        if not os.access(location,os.F_OK):
		os.mkdir(location)
        old=os.listdir(location)
	output=link_downloader(what)
        new = os.listdir(location)
        final = [i for i in new if i not in old]
        if output != 1:
            return output
	return "Done downloading "+ "\n" +"\n".join(final)

@plgn.command('queue <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)>')
def queue(data,what):
	f = open('download_queue.txt','a')
        with open(queued_links,'a') as f:
                f.write(what)
	return what+ 'added to download queue'

@plgn.command('begin')
def begin(data,what = None):
	if not os.access(queued_links,os.F_OK):
		return "Queue does not exist. Please form a download queue first."
        with open(queued_links,'r+') as f:
                links = f.read()
        if not os.access(location,os.F_OK):
                os.mkdir(location)
	data = links.split("\n")
	data=data[:-1]
	#count = len(data)
        old=os.listdir(location)
        output=[]
	for link in data:		
		if not link==" " or not link == "":
                    output.append(link_downloader(link))
         #           count = count - 1
	os.remove("download_queue.txt")
        new = os.listdir(location)
        final = [i for i in new if i not in old]
        error = [i for i in output if i!=1]
        if len(error)==0:
            return "Done downloading "+ "\n" +"\n".join(final)
        else:
            return "Following errors were reccorded for this queue"+"\n"+"\n".join(error) +"\n" + "Done downloading \n" + "\n".join(final) 

@plgn.command('list all downloads')
def listings(data,what=None):
	output = "\n".join(os.listdir(location))
	return output

@plgn.command('ip')
def ip(data, what=None):
	user = getpass.getuser()
	location = "/home/"+user+"/ip.txt"
	f = open(location,'r')
	data = f.read()
	f.close()    	
	return data

