import struct
import win32pipe, win32file, pywintypes
import time
from Multiprocessing import Queue
 
# IPC parameters
PIPE_NAME = r'\\.\pipe\simple-ipc-pipe'
ENCODING = 'ascii'
 
pipe = win32pipe.CreateNamedPipe(PIPE_NAME,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT ,#| win32pipe.NMPWAIT_WAIT_FOREVER,
        1, 65536, 65536, 0, None)
while True:
    
    try:
        ''' print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")
 
        request_len = win32file.ReadFile(pipe, 4)
        request_len = struct.unpack('I', request_len[1])[0]
        request_data = win32file.ReadFile(pipe, request_len)
 
        #print(str.split(str(request_data[1], 'UTF-8'))[0])
        #print(str.split(str(request_data[1], 'UTF-8'))[1])
        # convert to bytes
        input = str(request_data[1], 'UTF-8')
        print(input.split(',')[0])
        print(input.split(',')[1])
        #print(str(request_data[1], 'UTF-8'))
        response_data =f"Order Placed for {input.split(',')[0]}".encode(ENCODING)
        response_len = struct.pack('I', len(response_data))
        win32file.WriteFile(pipe, response_len)
        win32file.WriteFile(pipe, response_data)
        time.sleep(50) '''
        queue = multiprocessing.Queue()
    except :
        pass
    finally:
        #win32file.CloseHandle(pipe)
        pass