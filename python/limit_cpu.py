import signal
import resource
import os

def set_max_runtime(seconds):
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    resource.setrlimit(resource.RLIMIT_CPU, (seconds, soft) )
    signal.signal(signal.SIGXCPU, time_exceeded)

if __name__ == '__main__':
    # soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    # resource.setrlimit(resource.RLIMIT_CPU, (15, hard))
    while True:
        pass