import multiprocessing


def brute(worker, data_list, processes=8):
    """
    Run multiprocess workers
    :param worker: worker function
    :param data_list: data to distribute between workers, one entry per worker
    :param processes: number of parallel processes
    :return: list of worker return values
    """
    pool = multiprocessing.Pool(processes=processes)
    result = pool.map(worker, data_list)
    pool.close()
    return result
