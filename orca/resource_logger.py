import threading
import psutil
import time
import os
import subprocess

'''
    This class aims to log various resources through polling.
    This is done by creating an independent thread that sleeps during
    a given number of miliseconds between resource polls.

    Polling CPU is pretty straight-forward and not a complex issue.

    Polling GPU memory usage is done by the `nvidia-smi` bash command
    and then parsing the output. Of course this requires for CUDA and
    the NVidia CUDA Toolkit to be working properly to function.

    Polling RAM memory usage for a specific process is the most
    complicated aspect, because there are multiple possible
    interpretations for the memory usage of a process, particularly when
    analyzing shared memory usage. i.e. If a process loads a library
    into RAM, does it count? If a process reads from an library which
    was already loaded in RAM by another process, does it count? Etc.
    
    Because this logger is for general purpose, the results shown are
    two: USED memory and VIRT memory.

    * USED is Resident Set Size (non-swapped physical memory a process
    has used) + SWAP (memory that has been swapped out to disk)

    * VIRT is Virtual Memory Size: the total amount of virtual memory
    used by the process. This may include the mapping of libraries that
    will never be used, for instance.

    The recommended interpretation is to use USED as a lower bound and
    VIRT as an upper bound.
    
    Both USED and VIRT should match the results when running `TOP`.
    Please refer to the documentation of `TOP` for more information.
'''
class ResourceLogger:
    def __init__(self, memory_poll_interval=0.5, verbose=True,
        name=None, resources_to_poll=['ram']):
        assert resources_to_poll != [], \
            'At least one resource must be polled.'
        assert set(resources_to_poll).issubset({'ram', 'gpu', 'cpu'}), \
            'Resource list is invalid'
        assert memory_poll_interval and memory_poll_interval > 0, \
            'Memory poll interval should be positive'

        if name != None:
            self.name = '"' + name + '"'
        else:
            self.name = ''

        self.resources = dict()
        if 'ram' in resources_to_poll:
            self.resources['process_virtual_memory_peak'] = 0
            self.resources['process_virtual_memory_sum'] = 0
            self.resources['process_used_memory_peak'] = 0
            self.resources['process_used_memory_sum'] = 0
            self.resources['global_virtual_memory_peak'] = 0
            self.resources['global_virtual_memory_sum'] = 0
            self.resources['global_used_memory_peak'] = 0
            self.resources['global_used_memory_sum'] = 0
        
        if 'gpu' in resources_to_poll:
            self.resources['global_gpu_memory_peak'] = 0
            self.resources['global_gpu_memory_sum'] = 0
        
        if 'cpu' in resources_to_poll:
            self.resources['global_cpu_usage_peak'] = 0
            self.resources['global_cpu_usage_sum'] = 0

        self.current_process = psutil.Process(os.getpid())
        self.verbose = verbose
        self.resources_to_poll = resources_to_poll
        self.memory_poll_count = 0

        self.ended = False
        self.memory_poll_interval = memory_poll_interval

        self.print_if_verbose(
            'Starting poll of process {}, an interval of {} secs. Polling the following resources: {}' \
            .format(self.current_process, memory_poll_interval, self.resources_to_poll))

        t = threading.Thread(target=memory_polling_thread,
                             args=(self, resources_to_poll))
        t.start()

    def print_if_verbose(self, text):
        if self.verbose:
            print(text)

    def print_final_report(self):
        self.print_if_verbose(
            'Ending memory poll {}. Results:\n'
            'Used by process: Average: {} GB. Peak: {} GB.\n'
            'Virtual by process (equivalent to VIRT in TOP): Average: {} GB. Peak: {} GB.\n'
            'Used globally: Average: {} GB. Peak: {} GB.\n'
            'Virtual globally (equivalent to VIRT in TOP): Average: {} GB. Peak: {} GB.\n'.format(
                self.name,
                round(self.process_used_memory_sum /
                    self.memory_poll_count, 2),
                round(self.process_used_memory_peak, 2),
                round(self.process_virtual_memory_sum /
                    self.memory_poll_count, 2),
                round(self.process_virtual_memory_peak, 2),
                round(self.global_used_memory_sum /
                    self.memory_poll_count, 2),
                round(self.global_used_memory_peak, 2),
                round(self.global_virtual_memory_sum /
                    self.memory_poll_count, 2),
                round(self.global_virtual_memory_peak, 2)))

    def end(self):
        self.ended = True

        if self.memory_poll_count == 0:
            self.print_if_verbose("Log {} finished too quickly "
                                  "so the system virtual memory usage could not be polled".format(self.name))
            return None


        result = {}

        if 'ram' in self.resources_to_poll:
            result['process_memory_used_avg_GB'] = round(
                self.resources['process_used_memory_sum'] / self.memory_poll_count, 2)
            result['process_memory_used_peak_GB'] = round(
                self.resources['process_used_memory_peak'], 2)
            result['process_memory_virtual_avg_GB'] = round(
                self.resources['process_virtual_memory_sum'] / self.memory_poll_count, 2)
            result['process_memory_virtual_peak_GB'] = round(
                self.resources['process_virtual_memory_peak'], 2)
            result['global_memory_used_avg_GB'] = round(
                self.resources['global_used_memory_sum'] / self.memory_poll_count, 2)
            result['global_memory_used_peak_GB'] = round(
                self.resources['global_used_memory_peak'], 2)
            result['global_memory_virtual_avg_GB'] = round(
                self.resources['global_virtual_memory_sum'] / self.memory_poll_count, 2)
            result['global_memory_virtual_peak_GB'] = round(
                self.resources['global_virtual_memory_peak'], 2)
            result['total_physical_memory_GB'] = 
            result['total_swap_memory_GB'] = 
        
        if 'gpu' in self.resources_to_poll:
            result['global_gpu_memory_avg_GB'] = round(
                self.resources['global_gpu_memory_sum'] / self.memory_poll_count, 2)
            result['global_gpu_memory_peak_GB'] = round(
                self.resources['global_gpu_memory_peak'], 2)
            result['total_gpu_memory_GB'] = 
        
        if 'cpu' in self.resources_to_poll:
            result['global_gpu_memory_avg_%'] = round(
                self.resources['global_gpu_memory_sum'] / self.memory_poll_count, 2)
            result['global_gpu_memory_peak_%'] = round(
                self.resources['global_gpu_memory_peak'], 2)

        self.print_if_verbose(result)

        return result


def memory_polling_thread(a_memlog, resources_to_poll):
    while True:
        a_memlog.memory_poll_count += 1
        if 'ram' in resources_to_poll:
            rss = a_memlog.current_process.memory_full_info().rss / float(2 ** 30)
            swap = a_memlog.current_process.memory_full_info().swap / float(2 ** 30)
            process_used_memory = rss + swap
            a_memlog.resources['process_used_memory_sum'] += process_used_memory
            a_memlog.resources['process_used_memory_peak'] = max(
                a_memlog.resources['process_used_memory_peak'], process_used_memory)

            process_virtual_memory = a_memlog.current_process.memory_full_info().vms / \
                float(2 ** 30)
            a_memlog.resources['process_virtual_memory_sum'] += process_virtual_memory
            a_memlog.resources['process_virtual_memory_peak'] = max(
                a_memlog.resources['process_virtual_memory_peak'], process_virtual_memory)

            global_used_memory = psutil.virtual_memory()._asdict()["used"] / 2**30
            a_memlog.resources['global_used_memory_sum'] += global_used_memory
            a_memlog.resources['global_used_memory_peak'] = max(
                global_used_memory, a_memlog.resources['global_used_memory_peak'])

            global_virtual_memory = (psutil.virtual_memory()._asdict(
            )["total"] - psutil.virtual_memory()._asdict()["available"]) / 2**30
            a_memlog.resources['global_virtual_memory_sum'] += global_virtual_memory
            a_memlog.resources['global_virtual_memory_peak'] = max(
                global_virtual_memory, a_memlog.resources['global_virtual_memory_peak'])

        if 'gpu' in resources_to_poll:
            global_gpu_mem = obtain_gpu_memory_used_in_GB()
            a_memlog.resources['global_gpu_memory_sum'] += global_gpu_mem
            a_memlog.resources['global_gpu_memory_peak'] = max(
                a_memlog.resources['global_gpu_memory_peak'], global_gpu_mem)
        
        if 'cpu' in resources_to_poll:
            process_cpu_usage = psutil.Process(os.getpid()).cpu_percent()
            global_cpu_usage = psutil.cpu_percent()
            a_memlog.resources['process_cpu_sum'] += process_cpu_usage
            a_memlog.resources['process_cpu_peak'] = max(
                a_memlog.resources['process_cpu_peak'], process_cpu_usage)
            a_memlog.resources['global_cpu_sum'] += global_cpu_usage
            a_memlog.resources['global_cpu_peak'] = max(
                a_memlog.resources['global_cpu_peak'], global_cpu_usage)

        time.sleep(a_memlog.memory_poll_interval)
        if a_memlog.ended:
            break

def obtain_gpu_memory_used_in_GB():
    # we execute nvidia-smi to poll globalGPU memory usage
    command = ("nvidia-smi --query-gpu=memory.used --format=csv")
    assert subprocess.check_output(command.split()).decode('ascii') \
        .split('\n')[:-1][-1].split()[1] == "MiB", 'Encountered an' + \
        ' error when parsing the output of `nvidia-smi`'
    return int(subprocess.check_output(command.split()).decode('ascii')\
        .split('\n')[:-1][-1].split()[0]) * 0.00104858
