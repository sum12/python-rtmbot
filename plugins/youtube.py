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
        return e


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

@plgn.command('queue <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)> *(?P<param>[aA]+)?')
def queue(data,what,param):
    final = str(what) + " " + str(param)
    with open(plgn.queued_links,'a') as f:
        f.write(final)
        f.write('\n')
    return '{0} added to download queue'.format(str(what))

@plgn.command('begin')
def begin(data,what = None):
    if not os.access(plgn.queued_links,os.F_OK):
        return "Queue does not exist. Please form a download queue first."
    with open(plgn.queued_links,'r+') as f:
        links = f.read()
    if not os.access(plgn.location,os.F_OK):
        os.mkdir(plgn.location)
    data = links.split("\n")
    data = data[:-1]
    #count = len(data)
    plgn.old=os.listdir(plgn.location)
    output=[]
    for link in data:       
        if not link==" " or not link == "":
            output.append(link_downloader(link))
         #           count = count - 1
    os.remove(plgn.queued_links)
    plgn.new = os.listdir(plgn.location)
    # final = set(plgn.new) - set(plgn.old) ??????
    final = [i for i in plgn.new if i not in plgn.old]
    # error = filter(lambda x:x!=, output)  ??????
    error = [i for i in output if i!=1]
    if len(error)==0:
        msg = "Done downloading \n {0}".format("\n".join(final))
    else:
        msg = "\n".join(["Following errors were reccorded for this queue",
                            "\n".join(error),
                            "Done downloading",
                            "\n".join(final)])
    return msg

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
