import random
import time
from multiprocessing import Pool
from chartink_through_python import GetDataFromChartink
from chartink_through_python import ChartInkScraper
import logging
from datetime import datetime, time

screenmapper={
    '1': 'bullish-screeners',
    '2': 'bearish-screeners',
    '3': 'intraday-bearish-screeners',
    '4': 'intraday-bullish-screeners',
    '5': 'top-loved-screeners'
}

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
    #print(f'Started worker {name}')
    logging.info('Inside worker of workerprocess')
    #worker_time = random.choice(range(1, 5))
    #time.sleep(worker_time)
    ChartInkScraper(name)
    #print(f'{name} worker finished ')


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

''' if __name__ == '__main__':
    
    #schedule.every().day.at("19:26:00").do(chartinkscrapeprocess)
    logging.basicConfig(filename=r"D:\scraper\output.log",level=logging.DEBUG)

    try:
        #while True:
     
    # Checks whether a scheduled task
    # is pending to run or not
            #schedule.run_pending()
            #time.sleep(1)
        logging.info("Inside Main of ChartInk_With_Multiprocess.py")
        chartinkscrapeprocess()

    except Exception as e:
        pass
 '''

if __name__ == '__main__':
   #logging.basicConfig(filename=r"D:\scraper\output.log",format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=20)
    while True:
        #logging.basicConfig(filename=r"D:\scraper\output.log",format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=20)
        try:
            for index in range(0,4):
                ChartInkScraper(screenmapper.get(str(index+1)))

            # Get the current time
            current_time = datetime.now().time()

            # Define the start and end times
            start_time = time(9, 15)
            end_time = time(15, 30)

            # Check if the current time is between start_time and end_time
            if start_time <= current_time <= end_time:
                #logging.info("Current time is between 9:15 AM and 3:30 PM.")
                continue
            else:
                print("Markets open only between 9:15 AM and 3:30 PM.")
                break
        except Exception as e:
            logging.error("Encountered some Error")
