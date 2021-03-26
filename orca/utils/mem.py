# Adapted from https://github.com/ActivitySim/activitysim/blob/master/activitysim/core/mem.py

import psutil
import gc


def _force_garbage_collect():
    was_disabled = not gc.isenabled()
    if was_disabled:
        gc.enable()
    gc.collect()
    if was_disabled:
        gc.disable()


def _GB(bytes):
    gb = (bytes / (1024 * 1024 * 1024.0))
    return round(gb, 2)


def log_memory_info():

    _force_garbage_collect()

    current_process = psutil.Process()
    rss = current_process.memory_info().rss
    for child in current_process.children(recursive=True):
        try:
            rss += child.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            pass

    print("%.2f GB real memory in use" % _GB(rss))


# TODO
# - add back high-water-mark tracing?
# - add back virtual memory reporting?
# - align logging with orca