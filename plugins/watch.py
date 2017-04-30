import os
from itertools import repeat

from lib import Plugin, cron
import logging
logger = logging.getLogger('bot.managerclient')
logger.setLevel(logging.DEBUG)
plgn = Plugin('watch')



"
http://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python
"
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
    plgn.pid.append(details['pid'])


def process_exists_check(data, **details):
    """Keep an eye on a process, and inform if is dead"""
    ret = []
    for pid in plgn.pids[:]:
        if not pid_exists(pid):
            ret.append(plgn.pids.pop(pid))
    if ret:
        return "Following pids are dead: %s" % ",".join(ret)

@plgn.setupmethod
def init(config):
    plgn.pids = []
