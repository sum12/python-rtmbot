import time,os,subprocess
import logging
import re,youtube_dl,getpass,os
from lib import Plugin, cron
logger = logging.getLogger('bot.youtube')
logger.setLevel(logging.DEBUG)
plgn = Plugin('youtube')

@plgn.command('tell')
def tell(data,what=None):
    string = """Follow the following commands :
            download (link) [a]
                This function lets you download a video or audio directly. 
                'a' is optional parameter for downloading the audio file.
            queue
                Returns a list of all links that are noted in download_queue.txt
            queue add (link) [a]
                This function appends the link to the download queue. Pass 'a' to download the audio.
            begin 
                This initiates the download of the queue.
            list all downloads
                This function will simply return all the items that are present in the downloads directory on raspberry pi.
            ip
                This will return the ip of DJPI. 
            memory
                gives the present space usage in pi
            update youtube downloader
                pip install --upgrade youtube_dl
        """     
    return string

#This function will help reduce the redundacny of youtube_dl part of downloader everywhere !
def link_downloader(*a):
    args = [str(i) for i in a]
    y = {
            'outtmpl':plgn.location_video,
            'logger':logger,
            'nooverwrites':'True'
    }
    if len(args)>1 and (args[1] == 'a' or args[1]=='A'):
        y.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',}]
                })
    link = str(args[0])
    ydl= youtube_dl.YoutubeDL(y)
    try:
        ydl.download([link])
        return '1'
    except Exception as e:
        logger.debug(str(e))
        return str(e)


@plgn.command('download <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)> *(?P<param>[aA]+)?')
def download(data, what,param):
    if not os.access(plgn.location,os.F_OK):
        os.mkdir(plgn.location)
    plgn.old=os.listdir(plgn.location)
    output=link_downloader(what,param)
    plgn.new = os.listdir(plgn.location)
    final = [i for i in plgn.new if i not in plgn.old]
    if output != '1':
        return str(output)
    return "Done downloading "+ "\n" +"\n".join(final)

@plgn.command('queue add <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)> *(?P<param>[aA]+)?')
def queue(data,what,param):
    final = str(what) + " " + str(param)
    mode = 'a'
    if not os.access(plgn.queued_links,os.F_OK):
        mode = 'w' 
    with open(plgn.queued_links,mode) as f:
        f.write(final)
        f.write(',')
    return '{0} added to download queue'.format(str(what))

@plgn.command('begin')
def begin(data,what = None):
    if not os.access(plgn.queued_links,os.F_OK):
        return "Queue does not exist. Please form a download queue first."
    with open(plgn.queued_links,'r+') as f:
        links = f.read()
    if not os.access(plgn.location,os.F_OK):
        os.mkdir(plgn.location)
    data = links.split(",")
    data = data[:-1]
    plgn.old=os.listdir(plgn.location)
    output=[]
    for link in data:       
        if not link==" " or not link == "":
            r = link_downloader(link)
            output.append((link,r))
            if r=='1':
                data.remove(link)
    if data == []:            
        os.remove(plgn.queued_links)
    else:
        with open(plgn.queued_links,'w') as f:
            f.write(",".join(data))
            f.write(",")
    plgn.new = os.listdir(plgn.location)
    final = set(plgn.new) - set(plgn.old) 
    errors = ['Link = '+str(i) + '\n' + 'Error = '+str(j) for i,j in output if j!='1' ]
    if len(errors)==0:
        msg = "Done downloading \n {0}".format("\n".join(final))
    elif len(final)>0:
        msg = "\n".join(["Following errors were reccorded for this queue",
                            "\n".join(errors),
                            "Done downloading",
                            "\n".join(final)])
    else:
        msg = "\n".join(["Following errors were recorded for the given queue","\n".join(errors)])
    return msg

@plgn.command('queue\Z')
def show(data,what=None):
    if not os.access(plgn.queued_links,os.F_OK):
        return "Queue does not exist. Please form a download queue first."
    with open(plgn.queued_links,'r+') as f:
        links = f.read()
    temp = links.split(",")[:-1]
    final = []
    data = [str(j) for j in temp if j!='' or j!=' ' or j!='\n']
    print data
    if len(temp)==1 and temp[0]=='':
        return "Please initiate a queue. Either your queue is empty or uninitialized !"
    else:
        for i,j in enumerate(data):
            if j!='' or j!=' ' or j!='\n':
                i+=1
                final.append(str(i)+" "+ str(j))
    return "\n".join(final)

@plgn.command('queue remove (?P<what>[0-9]+)')
def remove(data,what):
    if not os.access(plgn.queued_links,os.F_OK):
        return "Queue does not exist. Please form a download queue first."
    with open(plgn.queued_links,'r+') as f:
        links = f.read()
    data = links.split(",")[:-1]
    temp =""
    for i,link in enumerate(data):
        i+=1
        if str(what) == str(i):
            temp = link
            data.remove(link)
    
    with open(plgn.queued_links,'w') as f:
        f.write(",".join(data))
        f.write(",")
    if temp=="":
        return "Invalid remove execution! Please review the documentation!"
    return str(temp) + " has been removed from the queue"

@plgn.command('list all downloads')
def listings(data,what=None):
    output = "\n".join(os.listdir(plgn.location))
    return output


@plgn.setupmethod
def init(config):
    plgn.location = unicode(config['location'])
    plgn.location_video = plgn.location + config['outtmpl']
    plgn.queued_links = config['queue_file']
    #plgn.playlists o= open(config['playlists']).read().split('/n')
    plgn.old = []
    plgn.new = []

@plgn.command('ip')
def ip(data, what=None):
    user = getpass.getuser()
    location = "/home/"+user+"/ip.txt"
    f = open(location,'r')
    data = f.read()
    f.close()       
    return data
@plgn.command('memory')
def memory(data,what=None):
    proc = subprocess.Popen(['df','-h'],stdout = subprocess.PIPE)
    temp = (proc.communicate()[0])
    data = temp.split("\n")
    for line in data:
        if '/dev/root' in line:
            final = line
    return str(final)
@plgn.command('update youtube downloader')
def update(data,what=None):
    proc = subprocess.Popen(['pip','install','--upgrade','youtube_dl'],stdout = subprocess.PIPE)
    temp = (proc.communicate()[0])
    logger.debug(str(temp))
    return str(temp)

