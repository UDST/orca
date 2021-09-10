import threading
import psutil
import time
import os
import numpy as np

DEBUG = False

def memory_polling_thread(a_memlog):
    while True:
        # ======== Poll current process memory usage
        rss = a_memlog.current_process.memory_full_info().rss / float(2 ** 30)
        swap = a_memlog.current_process.memory_full_info().swap / float(2 ** 30)
        process_used_memory = rss + swap
        a_memlog.memory_poll_count += 1
        a_memlog.process_used_memory_sum += process_used_memory
        a_memlog.process_used_memory_peak = max(a_memlog.process_used_memory_peak, process_used_memory)

        process_allocated_memory = a_memlog.current_process.memory_full_info().vms / float(2 ** 30)
        a_memlog.process_allocated_memory_sum += process_allocated_memory
        a_memlog.process_allocated_memory_peak = max(a_memlog.process_allocated_memory_peak, process_allocated_memory)

        # ======== Poll global memory usage
        global_used_memory = psutil.virtual_memory()._asdict()["used"] / 2**30
        a_memlog.global_used_memory_sum += global_used_memory
        a_memlog.global_used_memory_peak = max(global_used_memory, a_memlog.global_used_memory_peak)

        global_allocated_memory = (psutil.virtual_memory()._asdict()["total"] - psutil.virtual_memory()._asdict()["available"]) / 2**30
        a_memlog.global_allocated_memory_sum += global_allocated_memory
        a_memlog.global_allocated_memory_peak = max(global_allocated_memory, a_memlog.global_allocated_memory_peak)

        if DEBUG:
            print('############################### MEMORY USAGE ##################################')
            print('Polled globally: {} GB used memory (RSS + swap), and {} GB allocated memory\n'
                'Polled for process: {} GB used memory (total - available) and {} GB allocated memory, '\
                .format(round(global_used_memory, 2), round(global_allocated_memory, 2),
                        round(process_used_memory, 2), round(process_allocated_memory, 2)))
            print('###############################################################################')
        
        time.sleep(a_memlog.memory_poll_interval)
        if a_memlog.ended:
            break
        
        

class memlog:
    def __init__(self, memory_poll_interval = 0.5, verbose = True, name = None):
        assert memory_poll_interval and memory_poll_interval > 0, 'Memory poll interval should be positive'
        self.current_process = psutil.Process(os.getpid())
        self.verbose = verbose
        self.print_if_verbose('Starting memory poll of process {} with an interval of {} secs'.format(
            self.current_process, memory_poll_interval))
        
        if name != None:
            self.name = '"' + name + '"'
        else:
            self.name = ''

        # Initialization
        self.global_used_memory_sum = 0
        self.global_used_memory_peak = 0
        self.global_allocated_memory_sum = 0
        self.global_allocated_memory_peak = 0

        self.process_used_memory_sum = 0
        self.process_used_memory_peak = 0
        self.process_allocated_memory_sum = 0
        self.process_allocated_memory_peak = 0
        self.memory_poll_count = 0

        self.ended = False
        self.memory_poll_interval = memory_poll_interval

        t = threading.Thread(target=memory_polling_thread, args=(self,))
        t.start()
    
    def print_if_verbose(self, text):
        if self.verbose:
            print(text)

    def print_final_report(self):
        self.print_if_verbose('Ending memory poll {}. Results:\n'
            'Used by process: Average: {} GB. Peak: {} GB.\n'
            'Allocated by process (equivalent to VIRT in TOP): Average: {} GB. Peak: {} GB.\n'
            'Used globally: Average: {} GB. Peak: {} GB.\n'
            'Allocated globally (equivalent to VIRT in TOP): Average: {} GB. Peak: {} GB.\n'.format(
            self.name,
            round(self.process_used_memory_sum/self.memory_poll_count, 2),
            round(self.process_used_memory_peak, 2),
            round(self.process_allocated_memory_sum/self.memory_poll_count, 2),
            round(self.process_allocated_memory_peak, 2),
            round(self.global_used_memory_sum/self.memory_poll_count, 2),
            round(self.global_used_memory_peak, 2),
            round(self.global_allocated_memory_sum/self.memory_poll_count, 2),
            round(self.global_allocated_memory_peak, 2)))

    def end(self):
        self.ended = True

        if self.memory_poll_count == 0:
            self.print_if_verbose("Log {} finished too quickly "
                "so the system virtual memory usage could not be polled".format(self.name))
            return None

        self.print_final_report()

        result =    {'process_used_avg': round(self.process_used_memory_sum / self.memory_poll_count, 2),
                    'process_used_peak': round(self.process_used_memory_peak, 2),
                    'process_allocated_avg': round(self.process_allocated_memory_sum / self.memory_poll_count, 2),
                    'process_allocated_peak': round(self.process_allocated_memory_peak, 2),
                    'global_used_avg': round(self.global_used_memory_sum / self.memory_poll_count, 2),
                    'global_used_peak': round(self.global_used_memory_peak, 2),
                    'global_allocated_avg': round(self.global_allocated_memory_sum / self.memory_poll_count, 2),
                    'global_allocated_peak': round(self.global_allocated_memory_peak, 2)}

        return result