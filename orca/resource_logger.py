import threading
import psutil
import time
import os
import subprocess
from datetime import datetime
from pdb import set_trace as st

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
    
    Since this logger is for general purpose, the results shown are
    two: USED memory and VIRT memory.

    * USED is Resident Set Size (non-swapped physical memory a process
    has used) + SWAP (memory that has been swapped out to disk)

    * VIRT is Virtual Memory Size: the total amount of virtual memory
    used by the process. This may include the mapping of libraries that
    will never be used, for instance.

    The recommended interpretation is to use USED as a lower bound and
    VIRT as an upper bound to get a general sense of the memory usage.
    
    Both USED and VIRT should match the results when running `TOP`.
    Please refer to the documentation of `TOP` for more information.


    Parameters
    ----------
    * memory poll interval: Float. Number of seconds between each poll. Default: .5
    * name: String that identifies the poll. Default: "unnamed_log"
    * resources to poll: List of strings of the resources to poll. Can only contain 'ram'
    'gpu' and/or 'cpu'. Default: ['ram']
    * log_filepath: Filepath to which the logs are saved. Useful to diagnose a crash. Can
    be set to "auto", in which case it will be saved at "{name}_YYYY_MM_DD__H_M_S.csv". Can
    also be set to None, in which case the log will not be saved. The best for performance
    is to set it as None to avoid disk writing operations. Default: None
    * log_write_interval: Integer. Number of polls between each time the logs are written to disk.
    The higher the number, the better the performance. Default: 1
    * append_to_log_filepath: Boolean. If True, appends to existing log file. Otherwise, it
    overwrites it. Default: True
'''
class ResourceLogger:
    def __init__(self,
        resource_poll_interval=0.5,
        name='unnamed_log',
        resources_to_poll=['ram'],
        log_filepath=None,
        log_write_interval=1,
        append_to_log_filepath=True):

        assert not (log_filepath != None and log_write_interval == None), \
            'A log filepath was provided but not an interval for it.'
        assert resources_to_poll != [], \
            'At least one resource must be polled.'
        assert set(resources_to_poll).issubset({'ram', 'gpu', 'cpu'}), \
            'Resource list is invalid'
        assert resource_poll_interval and resource_poll_interval > 0, \
            'Memory poll interval should be positive'

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
        self.resources_to_poll = resources_to_poll
        self.poll_count = 0
        self.name = name
        self.ended = False
        self.resource_poll_interval = resource_poll_interval
        self.log_filepath = log_filepath
        self.log_write_interval = log_write_interval

        starting_message = 'Starting poll of process {}, an interval of {} secs. Polling the following resources: {}.' \
            .format(self.current_process, resource_poll_interval, self.resources_to_poll)
        
        if log_filepath == 'auto':
            now = datetime.now()
            datetime_string = now.strftime("%Y_%m_%d__%H:%M:%S") # YY_mm_dd__H:M:S
            log_filepath = name + '__' + datetime_string + '.csv'

        if log_filepath:
            self.accumulated_logs = []
            starting_message += ' Saving all logs at {} for each {} polls. This may decrease performance.'\
                .format(log_filepath, log_write_interval)
            
            title_for_csv = ['name']
            if 'ram' in resources_to_poll:
                title_for_csv += ['process_used_memory',
                                'process_virtual_memory',
                                'global_used_memory',
                                'global_virtual_memory']
            if 'gpu' in resources_to_poll:
                title_for_csv += ['global_gpu_mem']
            if 'cpu' in resources_to_poll:
                title_for_csv += ['process_cpu_usage', 'global_cpu_usage']
            title_for_csv += ['time']
            if append_to_log_filepath and not os.path.exists(log_filepath):
                with open(log_filepath, 'w') as log_file:
                    log_file.write(','.join(title_for_csv)+'\n')
        print(starting_message)

        t = threading.Thread(target=memory_polling_thread,
                             args=(self, resources_to_poll))
        t.start()

    def print_final_report(self, result):
        print('Ending memory poll {}. Results:\n{}'.format(
            self.name, result))

    def end(self):
        self.ended = True

        if self.poll_count == 0:
            print("Log {} finished too quickly "
                "so the system virtual memory usage could not be polled".format(self.name))
            return None

        result = {}
        if 'ram' in self.resources_to_poll:
            result['process_memory_used_avg_GB'] = round(
                self.resources['process_used_memory_sum'] / self.poll_count, 2)
            result['process_memory_used_peak_GB'] = round(
                self.resources['process_used_memory_peak'], 2)
            result['process_memory_virtual_avg_GB'] = round(
                self.resources['process_virtual_memory_sum'] / self.poll_count, 2)
            result['process_memory_virtual_peak_GB'] = round(
                self.resources['process_virtual_memory_peak'], 2)
            result['global_memory_used_avg_GB'] = round(
                self.resources['global_used_memory_sum'] / self.poll_count, 2)
            result['global_memory_used_peak_GB'] = round(
                self.resources['global_used_memory_peak'], 2)
            result['global_memory_virtual_avg_GB'] = round(
                self.resources['global_virtual_memory_sum'] / self.poll_count, 2)
            result['global_memory_virtual_peak_GB'] = round(
                self.resources['global_virtual_memory_peak'], 2)
            result['total_physical_memory_GB'] = round(
                psutil.virtual_memory().total / 2**30, 2)
            result['total_swap_memory_GB'] = round(
                psutil.swap_memory().total / 2**30, 2)
        
        if 'gpu' in self.resources_to_poll:
            result['global_gpu_memory_avg_GB'] = round(
                self.resources['global_gpu_memory_sum'] / self.poll_count, 2)
            result['global_gpu_memory_peak_GB'] = round(
                self.resources['global_gpu_memory_peak'], 2)
            result['total_gpu_memory_GB'] = obtain_gpu_memory_in_GB('total')
        
        if 'cpu' in self.resources_to_poll:
            result['global_gpu_memory_avg_%'] = round(
                self.resources['global_gpu_memory_sum'] / self.poll_count, 2)
            result['global_gpu_memory_peak_%'] = round(
                self.resources['global_gpu_memory_peak'], 2)

        self.print_final_report(result)

        return result


def memory_polling_thread(a_memlog, resources_to_poll):
    while True:
        a_memlog.poll_count += 1
        line_for_csv = []
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
            line_for_csv += [process_used_memory,process_virtual_memory,
                            global_used_memory,global_virtual_memory]

        if 'gpu' in resources_to_poll:
            global_gpu_mem = obtain_gpu_memory_in_GB('used')
            a_memlog.resources['global_gpu_memory_sum'] += global_gpu_mem
            a_memlog.resources['global_gpu_memory_peak'] = max(
                a_memlog.resources['global_gpu_memory_peak'], global_gpu_mem)
            line_for_csv += [global_gpu_mem]

        if 'cpu' in resources_to_poll:
            process_cpu_usage = psutil.Process(os.getpid()).cpu_percent()
            global_cpu_usage = psutil.cpu_percent()
            a_memlog.resources['process_cpu_sum'] += process_cpu_usage
            a_memlog.resources['process_cpu_peak'] = max(
                a_memlog.resources['process_cpu_peak'], process_cpu_usage)
            a_memlog.resources['global_cpu_sum'] += global_cpu_usage
            a_memlog.resources['global_cpu_peak'] = max(
                a_memlog.resources['global_cpu_peak'], global_cpu_usage)
            line_for_csv += [process_cpu_usage, global_cpu_usage]

        if a_memlog.log_filepath:
            now = datetime.now()
            time_string = now.strftime("%H:%M:%S") # YY_mm_dd__H:M:S
            line_for_csv = list(map((lambda word: str(round(word, 2))), line_for_csv))
            line_for_csv = [a_memlog.name] + line_for_csv + [time_string]
            a_memlog.accumulated_logs.append(a_memlog.resources)
            if a_memlog.poll_count % a_memlog.log_write_interval == 0:
                with open(a_memlog.log_filepath, 'a') as log_file:
                    log_file.write(','.join(line_for_csv) + '\n')
                a_memlog.accumulated_logs = []

        time.sleep(a_memlog.resource_poll_interval)
        if a_memlog.ended:
            break

def obtain_gpu_memory_in_GB(used_or_total):
    assert used_or_total == 'used' or used_or_total == 'total'
    # we execute nvidia-smi to poll globalGPU memory usage
    command = ("nvidia-smi --query-gpu=memory.{} --format=csv".format(
        used_or_total))
    assert subprocess.check_output(command.split()).decode('ascii') \
        .split('\n')[:-1][-1].split()[1] == "MiB", 'Encountered an' + \
        ' error when parsing the output of `nvidia-smi`'
    return int(subprocess.check_output(command.split()).decode('ascii')\
        .split('\n')[:-1][-1].split()[0]) * 0.00104858 # MiB to GB

