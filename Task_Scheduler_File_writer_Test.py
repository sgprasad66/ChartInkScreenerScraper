''' import csv

with open('d:\students.csv', 'w', newline='') as file:
     writer = csv.writer(file)
     
     writer.writerow(["SNo", "Name", "Subject"])
     writer.writerow([1, "Ash Ketchum", "English"])
     writer.writerow([2, "Gary Oak", "Mathematics"])
     writer.writerow([3, "Brock Lesner", "Physics"])
 '''


''' 
from multiprocessing import Process, Manager 

# Define a function that will run in a separate process 


def process1(q): 
	# Put a string into the queue 
	q.put('hello') 

# Define a function that will run in a separate process 


def process2(q): 
	# Get a message from the queue and print it to the console 
	print(q.get()) 


# The following code will only run if the script is run directly 
if __name__ == '__main__': 
	# Create an instance of the Manager 
	with Manager() as manager: 
		# Create a queue within the context of the manager 
		q = manager.Queue() 

		# Create two instances of the Process class, one for each function 
		p1 = Process(target=process1, args=(q,)) 
		p2 = Process(target=process2, args=(q,)) 

		# Start both processes 
		p1.start() 
		p2.start() 

		# Wait for both processes to finish 
		p1.join() 
		p2.join()  

import multiprocessing
import os
print("Number of cpu : ", os.cpu_count())
print("Number of cpu : ", multiprocessing.cpu_count())'''

import multiprocessing
import time
from ChartInk_Scaper_FileWatcher_Processor import Watcher

''''''
def process1(queue):
    # Your logic for process 1 here
    # Communicate with the queue as needed
    print("Process 1 started")
    watcher = Watcher() 
    watcher.run(queue)
    time.sleep(1)  # Placeholder for actual work
    print("Process 1 completed")

def process2(queue):
    # Your logic for process 2 here
    # Communicate with the queue as needed
    print("Process 2 started")
    time.sleep(1)  # Placeholder for actual work
    print("Process 2 completed")

if __name__ == "__main__":
    # Create a multiprocessing queue
    queue = multiprocessing.Queue()

    # Start the processes
    p1 = multiprocessing.Process(target=process1, args=(queue,))
    p2 = multiprocessing.Process(target=process2, args=(queue,))

    # Set the start and end times
    ''' start_time = time.strptime("09:15", "%H:%M")
    
    end_time = time.strptime("15:30", "%H:%M")

    # Wait until the start time
    current_time = time.localtime()
    import datetime
    from datetime import datetime

    current_time = datetime.now().strftime("%H:%M")
    
    while current_time < start_time:
        time.sleep(60)  # Check every minute
        current_time = time.localtime() '''
    while True:
        import datetime
        from datetime import datetime, time
        current_time = datetime.now().time()

                # Define the start and end times
        start_time = time(18, 55)#time(9, 11)
        end_time =  time(18, 58)#time(15, 30)

        # Check if the current time is between start_time and end_time
        if current_time < start_time :
            #logging.info("Current time is between 9:15 AM and 3:30 PM.")
            continue
        else:
            print("Markets open only between 9:15 AM and 3:30 PM.")
            break

    # Start the processes
    p1.start()
    p2.start()

    # Wait until the end time
    while current_time < end_time:
        import time
        time.sleep(30)  # Check every minute
        current_time = datetime.now().time()

    # Terminate the processes
    p1.terminate()
    p2.terminate()

    # Join the processes (optional)
    p1.join()
    p2.join()

    print("Main program completed")'''
    

