# http://code.activestate.com/recipes/577187-python-thread-pool/
from Queue import Queue, Full
from threading import Thread
import logging
import time

logger = logging.getLogger('bot.pool')
logger.setLevel(logging.DEBUG)


ALLOW_SCALLING = not False
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks, burst=False):
        Thread.__init__(self)
        self.tasks = tasks
        self.burst = burst
        self.daemon = True
        self.start()
    
    def run(self):
        while True :
            func, args, kargs = self.tasks.get()
            try: 
                func(*args, **kargs)
            except Exception, e: 
                logger.exception(' Exception in worker for task: func={func}\nargs={args}\nkwargs {kargs}'.format(func=func,args=args,kargs=kargs))
            self.tasks.task_done()
            if self.burst:
                logger.info('Burst Thread now exiting')
                break

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.max_threads = num_threads
        self.tasks = Queue()
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        logger.info('added tasks')
        try:
            logger.debug("name :%s"%func.__name__)
            self.tasks.put((func, args, kargs), block=False)
        except Full, e:
            if ALLOW_SCALLING:
                logger.debug('SCALLLING WORKER')
                for _ in range(self.max_threads - self.tasks.qsize() ): 
                    Worker(self.tasks, burst=True)
            else:
                if self.max_threads < self.tasks.qsize():
                    logger.warn('QUEUE is full')

    def schedule_task(self, checker, func, *args, **kwargs):
        def waiter():
            while True:
                t = checker()
                logger.debug("waiting for %s"% t)
                time.sleep(t)
                self.add_task(func, *args, **kwargs)
        self.add_task(waiter)

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

#if __name__ == '__main__':
#    from random import randrange
#    delays = [randrange(1, 10) for i in range(100)]
#    
#    from time import sleep
#    def wait_delay(d):
#        print 'sleeping for (%d)sec' % d
#        sleep(d)
#    
#    # 1) Init a Thread pool with the desired number of threads
#    pool = ThreadPool(20)
#    
#    for i, d in enumerate(delays):
#        # print the percentage of tasks placed in the queue
#        print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')
#        
#        # 2) Add the task to the queue
#        pool.add_task(wait_delay, d)
#    
#    # 3) Wait for completion
#    pool.wait_completion()
