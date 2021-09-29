#!/usr/bin/env python
import pprint
import sys
import timeit

from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)
from itertools import repeat

from timing_decorators import (
    run_timed_async,
    run_timed_sync
)


TENS_OF_MILLIONS_TO_COUNT_TO = [9, 5, 11, 7]


def count_to_n_million(n, results):
    count = 0
    for i in range((10**6) * n):
        count += i
    print(n, end=', ')
    results.append(n)


def print_results(results):
    print('\norder as reported in shared object:')
    print(', '.join(str(x) for x in results))


@run_timed_sync
def run_cpu_heavy_sync():
    """
    Run cpu-heavy tasks with shared results object synchronously in loop and display results.
    """
    print('Synchronous')
    print('order as printed by tasks:')
    results = []
    for n in TENS_OF_MILLIONS_TO_COUNT_TO:
        count_to_n_million(n, results)
    print_results(results)


@run_timed_sync
def run_cpu_heavy_multithread():
    """
    Run cpu-heavy tasks in a pool of worker threads with a shared results object and display results.
    """
    print('Multithreaded')
    print('order as printed by tasks:')
    results = []

    # ThreadPoolExecutor creates a 'pool' of threads in which to do tasks (i.e. a set you can use).
    # the max_workers argument (the number of threads in the pool) is optional, and will by default be set to something
    # sensibly scaled to the specs of the machine you are running the code on. Here we set it to one thread per
    # task in order to ensure the comparison with multiprocessing is fair.
    # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(TENS_OF_MILLIONS_TO_COUNT_TO)) as executor:

        # ThreadPoolExecutor.map takes a function and one or more iterables (lists, tuples, dicts, whatever) that
        # contain the arguments for your function (one iterable for each argument, if your function has multiple
        # arguments). ThreadPoolExecutor.map will then schedule the function call as a task to be executed using the
        # pool of worker threads. The size of the argument iterable(s) will determine the number of tasks scheduled.
        # NB - the iterables must therefore all be the same length. Here we use itertools.repeat to pass the same
        # argument in as many times as needed (repeat creates a generator object that always returns the same thing when
        # 'next' is called on it).
        # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.map
        executor.map(count_to_n_million, TENS_OF_MILLIONS_TO_COUNT_TO, repeat(results))

    print_results(results)


@run_timed_sync
def run_cpu_heavy_multiproc():
    """
    Run cpu-heavy tasks in a pool of worker processes with a shared results object and display results.
    """
    print('Multiprocessed')
    print('order as printed by tasks:')
    results = []

    # ProcessPoolExecutor creates a 'pool' of processes in which to do tasks (i.e. a set you can use).
    # the max_workers argument (the number of processes in the pool) is optional, and will by default be set to the
    # number of processors in the machine you are running the code on (). Here we set it to one process per
    # task in order to ensure the comparison with multithreading is fair.
    # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=len(TENS_OF_MILLIONS_TO_COUNT_TO)) as executor:

        # ProcessPoolExecutor.map takes a function and one or more iterables (lists, tuples, dicts, whatever) that
        # contain the arguments for your function (one iterable for each argument, if your function has multiple
        # arguments). ProcessPoolExecutor.map will then schedule the function call as a task to be executed using the
        # pool of worker processes. The size of the argument iterable(s) will determine the number of tasks scheduled.
        # NB - the iterables must therefore all be the same length. Here we use itertools.repeat to pass the same
        # argument in as many times as needed (repeat creates a generator object that always returns the same thing when
        # 'next' is called on it).
        # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.map
        executor.map(count_to_n_million, TENS_OF_MILLIONS_TO_COUNT_TO, repeat(results))

    # NB - the results stored in the shared object given to each worker process will be blank! This is because by
    # default separate processes do not share memory with each other! You need to do something fancy to get that to
    # work: https://docs.python.org/3/library/multiprocessing.shared_memory.html
    print_results(results)


def main():
    run_cpu_heavy_sync()
    run_cpu_heavy_multithread()
    run_cpu_heavy_multiproc()


if __name__=="__main__":
    main()