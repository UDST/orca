import threading
import psutil
import time
import os

VERBOSE = False

def memory_polling_thread(a_memlog):
    while True:
        rss = a_memlog.current_process.memory_full_info().rss / float(2 ** 30)
        swap = a_memlog.current_process.memory_full_info().swap / float(2 ** 30)
        used_memory = rss + swap
        a_memlog.memory_poll_count += 1
        a_memlog.used_memory_sum += used_memory
        a_memlog.used_memory_peak = max(a_memlog.used_memory_peak, used_memory)

        virtual_memory = a_memlog.current_process.memory_full_info().vms / float(2 ** 30)
        a_memlog.virtual_memory_sum += virtual_memory
        a_memlog.virtual_memory_peak = max(a_memlog.virtual_memory_peak, used_memory)

        if VERBOSE:
            print('############################### MEMORY USAGE ##################################')
            print('Polled {} GB used memory (RSS + swap), and {} GB virtual memory, sleeping for {} secs'.format(
                used_memory, virtual_memory, a_memlog.memory_poll_interval))
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
        self.used_memory_sum = 0
        self.used_memory_peak = 0
        self.virtual_memory_sum = 0
        self.virtual_memory_peak = 0
        self.memory_poll_count = 0
        self.ended = False
        self.memory_poll_interval = memory_poll_interval

        t = threading.Thread(target=memory_polling_thread, args=(self,))
        t.start()
    
    def end(self):
        self.ended = True
        print('Ending memory poll of current process.\nUSED: Average: {} GB. Peak: {} GB.\nVIRTUAL: Average: {} GB. Peak: {} GB.'.format(
            self.used_memory_sum/self.memory_poll_count,
            self.used_memory_peak,
            self.virtual_memory_sum/self.memory_poll_count,
            self.virtual_memory_peak))
