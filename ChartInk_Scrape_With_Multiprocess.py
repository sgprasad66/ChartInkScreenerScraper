import random
import time
from multiprocessing import Pool
from chartink_through_python import GetDataFromChartink
from chartink_through_python import ChartInkScraper


screenmapper={
    '1': 'bullish-screeners',
    '2': 'bearish-screeners',
    '3': 'intraday-bearish-screeners',
    '4': 'intraday-bullish-screeners',
    '5': 'top-loved-screeners'
}

''' def worker(name: str) -> None:

    print(f'Started worker {name}')

    #worker_time = random.choice(range(1, 5))

    #time.sleep(worker_time)
    ChartInkScraper(name)

    print(f'{name} worker finished')

if __name__ == '__main__':

    process_names = [screenmapper.get(str(i+1)) for i in range(5)]

    pool = Pool(processes=4)

    pool.map(worker, process_names)

    pool.terminate() '''

    # worker_thread_subclass.py

import random
import multiprocessing
import time
from datetime import datetime
import schedule

class WorkerProcess(multiprocessing.Process):
    def __init__(self, name):
        multiprocessing.Process.__init__(self)
        self.name = name

    def run(self):
        worker(self.name)

def worker(name: str) -> None:
    print(f'Started worker {name}')
    #worker_time = random.choice(range(1, 5))
    #time.sleep(worker_time)
    ChartInkScraper(name)
    print(f'{name} worker finished ')


def chartinkscrapeprocess():
    while True:
        processes = []
        for i in range(4):
            process = WorkerProcess(name=screenmapper.get(str(i+1)))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()

        endtime=datetime.now()
        if endtime.hour < 15 or endtime.hour >= 15 and endtime.minute <32:
            continue
        else:
            pass #break

if __name__ == '__main__':
    
    #schedule.every().day.at("19:26:00").do(chartinkscrapeprocess)

    try:
        #while True:
     
    # Checks whether a scheduled task
    # is pending to run or not
            #schedule.run_pending()
            #time.sleep(1)
        chartinkscrapeprocess()

    except Exception as e:
        pass


''' if __name__ == '__main__':
    while True:
        for index in range(0,5):
            ChartInkScraper(screenmapper.get(str(index+1))) '''
