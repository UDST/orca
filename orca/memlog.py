import threading
import psutil
import time
import os

VERBOSE = False

def memory_polling_thread(a_memlog):
    while True:
        current_memory_usage = a_memlog.current_process.memory_info()[0] / float(2 ** 30)
        a_memlog.memory_poll_count += 1
        a_memlog.memory_sum += current_memory_usage
        a_memlog.memory_peak = max(a_memlog.memory_peak, current_memory_usage)
        if VERBOSE:
            print('############################### MEMORY USAGE ##################################')
            print('Polled {} GB of memory usage, sleeping for {} secs'.format(
                current_memory_usage, a_memlog.memory_poll_interval))
            print('###############################################################################')
        time.sleep(a_memlog.memory_poll_interval)
        if a_memlog.ended:
            break

class memlog:
    def __init__(self, memory_poll_interval = 0.5):
        assert memory_poll_interval and memory_poll_interval > 0, 'Memory poll interval should be positive'
        self.current_process = psutil.Process(os.getpid())
        print('Starting memory poll of process {} with an interval of {} secs'.format(
            self.current_process, memory_poll_interval))
        self.memory_sum = 0
        self.memory_poll_count = 0
        self.memory_peak = 0
        self.ended = False
        self.memory_poll_interval = memory_poll_interval

        t = threading.Thread(target=memory_polling_thread, args=(self,))
        t.start()
    
    def end(self):
        self.ended = True
        print('Ending memory poll of current process. Average usage: {} GB. Peak usage: {} GB.'.format(
            self.memory_sum/self.memory_poll_count, self.memory_peak))
