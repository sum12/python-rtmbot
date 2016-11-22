import time,os,subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
import re,youtube_dl,getpass,os
from lib import Plugin, cron
logger = logging.getLogger('bot.youtube')
logger.setLevel(logging.DEBUG)
plgn = Plugin('youtube')

ydl_logger = logging.getLogger('youtubedl')
if len(ydl_logger.handlers) < 1:
    ydl_handler = RotatingFileHandler('youtubedl.log', 'a', 2 * 1024 * 1024)
    ydl_handler.propagate = False
    ydl_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    ydl_logger.addHandler(ydl_handler)
    ydl_logger.setLevel(logging.DEBUG)

# downloaded_list is a global variable for storing the names of the videos which are downloaded
# by link_downloader. This is used for parsing video names form downloader_hook to the download
# function so that it can be returned to inform the user. This is just a temporary solution.
# In the long run, may be modifying the thread class to include a list would be a better option.
downloaded_list = []

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

class DownloadException(Exception):
 def __init__(self, msg, exc_info=None):
        """ exc_info, if given, is the original exception that caused the trouble (as returned by sys.exc_info()). """
        super(DownloadException, self).__init__(msg)
        self.exc_info = exc_info

def downloader_hook(d):
    global downloaded_list
    if d['status']=='finished' and d.get('downloaded_bytes', False):
        downloaded_list.append(os.path.split(os.path.abspath(d['filename']))[1])


def makeoptions(*a):
    args = [None]+[str(i) for i in a]
    y = {
            'outtmpl':plgn.location_video,
            'logger':ydl_logger,
            'nooverwrites':'True',
            'progress_hooks':[downloader_hook],
            }
    if len(args)>1 and (args[1] == 'a' or args[1]=='A'):
        y.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'nopostoverwrites':'True',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',}]
                })
    if len(args)>2 and ('k' in args[2].lower()): y.update({ 'keepvideo':True })
    if len(args)>3 and ('i' in args[3].lower()): y.update({ 'ignoreerrors':True })
    return y

#This function will help reduce the redundacny of youtube_dl part of downloader everywhere !
def link_downloader(args, options):
    link = str(args)
    ydl= youtube_dl.YoutubeDL(options)
    try:
        ydl.download([link])
    except Exception as e:
        logger.debug(str(e))
        exc_info = sys.exc_info()
        raise DownloadException(str(e),exc_info)

@plgn.command('download <(?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)> *(?P<param>[aA]+)?')
def download(data, what,param):
    global downloaded_list
    if not os.access(plgn.location,os.F_OK):
        os.mkdir(plgn.location)
    plgn.old=os.listdir(plgn.location)
    try:
        link_downloader(what,makeoptions(param))
    except DownloadException as e:
        logger.debug(str(e))
        return str(e) 
    plgn.new = os.listdir(plgn.location)
    #final = [i for i in plgn.new if i not in plgn.old]
    if downloaded_list:
        final = "\n".join(downloaded_list)
        downloaded_list=[]
    return "Done downloading "+ "\n" + final

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


@plgn.command('save <(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?.*?(?:list)=(?P<playid>.*?)>')
def saveplaylist(data, playid):
    """ save playlist for recurring download"""
    if playid in  [i for i in open(plgn.playlistsfile,'r').read().split('\n') if i != None]:
        return 'playid {0} exists'.format(playid)
    open(plgn.playlistsfile,'a').write('\n{0}'.format(playid))
    return 'Saved playid {0}'.format(playid)

@plgn.schedule(cron(hour=range(2,6)+range(10,18), minute=[0],second=[0]), maximum=1)
@plgn.command('startplaylist')
def continueplaylist(*args, **kwargs):
    """ DONT USE THIS """
    global downloaded_list
    playids = [i for i in open(plgn.playlistsfile,'r').read().split('\n') if i ]
    logger.debug(playids)
    for i in  playids:
        try:
            logger.info('starting for id->' + i)
            link_downloader(i, makeoptions(*'aki'))
        except:
            pass
        finally:
            logger.info('Done downloading id->' +i)
            if downloaded_list:
                final  = "\n".join(downloaded_list)
                downloaded_list=[]
                return "Done downloading. New downloads include "+final
            else:
                return "No New Downloads"

            
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
    output=[]
    for link in data:       
        if not link==" " or not link == "":
            try:
                link_downloader(link)
                output.append((link,'1'))
                data.remove(link)
            except DownloadException as e:
                output.append((link,str(e)))
    if data == []:            
        os.remove(plgn.queued_links)
    else:
        with open(plgn.queued_links,'w') as f:
            f.write(",".join(data))
            f.write(",")
    global downloaded_list
    final = downloaded_list
    downloaded_list = []
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
    files =os.listdir(plgn.location)
    output = "No downloads"
    if not files == []:
        output = "\n".join(os.listdir(plgn.location))
    return output


@plgn.setupmethod
def init(config=None):
    if config is not None:  # Anything except None will let you in.
        plgn.location = unicode(config['location'])
        plgn.location_video = os.sep.join([plgn.location , config['outtmpl']])
        plgn.queued_links = config.get('queue_file', 'queue.txt')
        plgn.playlistsfile = config.get('playlistsfile', 'playlists.txt')
        if not os.path.exists(plgn.playlistsfile):
            open(plgn.playlistsfile,'w')

@plgn.command('ip')
def ip(data, what=None):
    user = getpass.getuser()
    location = "/home/"+user+"/Heroku_ip_sending/ip.txt"
    with open(location,'r') as f:
        data = f.read()
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

