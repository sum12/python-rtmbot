import os
from itertools import repeat

from lib import Plugin, cron
plgn = Plugin('watch')
logger = plgn.logger



"""
http://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python
"""
if os.name == 'posix':
    def pid_exists(pid):
        """Check whether pid exists in the current process table."""
        import errno
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True
else:
    def pid_exists(pid):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x100000

        process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        else:
            return False



@plgn.command('watchprocess (?P<pid>(\d+))')
def add_pid(data, **details):
    try:
        plgn.pids.append(int(details['pid']))
    except Exception as e:
        logger.debug(str(e))
        return 'Sorry, Could not add'
    else:
        return 'Okay'


@plgn.schedule(maximum=1)
def process_exists_check():
    """Keep an eye on a process, and inform if is dead"""
    ret = []
    for pid in plgn.pids[:]:
        try:
            if not pid_exists(pid):
                ret.append(str(plgn.pids.pop(plgn.pids.index(pid))))
        except Exception as e:
            logger.info('Something is wrong with pid checking: '+str(e))
            return 'Process watching is broken'
    if ret:
        return "Following pids are dead: %s" % ",".join(ret)

@plgn.setupmethod
def init(config):
    plgn.pids = []
