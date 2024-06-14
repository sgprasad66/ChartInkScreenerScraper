import struct
import time
import win32pipe 
import win32file 
import pywintypes
# IPC parameters
PIPE_NAME = r'\\.\pipe\simple-ipc-pipe'
ENCODING = 'ascii'
 
stock_list=['NSE:TATAMOTORS,C','NSE:OFSS,C','NSE:BPCL,P']
#while True:
pipe = win32file.CreateFile(
    PIPE_NAME,
    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
    0,
    None,
    win32file.OPEN_EXISTING,
    0,
    None
)
''' try:
    res = win32pipe.SetNamedPipeHandleState(pipe, win32pipe.PIPE_READMODE_MESSAGE, None, None)
    if res == 0:
        print(f"SetNamedPipeHandleState Return Code: {res}")   # if function fails, the return value will be zero
    while True:
        # Read the data from the named Pipe
        resp = win32file.ReadFile(pipe, 65536)
        print(f"Data Received: {resp}")   # if function fails, the return value will be zero
except pywintypes.error as e:
    if e.args[0] == 2:   # ERROR_FILE_NOT_FOUND
        print("No Named Pipe")
    elif e.args[0] == 109:   # ERROR_BROKEN_PIPE
        print("Named Pipe is broken")
    #break
#with open(PIPE_NAME , 'rb+', buffering=0) as f: '''

for index in range(3):
    data = stock_list[index].encode(ENCODING)
    data_len = struct.pack('I', len(data))

    pipe.write(data_len)
    pipe.write(data)
    pipe.seek(0)  # Necessary

    time.sleep(5)

    received_len = struct.unpack('I', pipe.read(4))[0]
    received_data = pipe.read(received_len).decode(ENCODING)
    pipe.seek(0)  # Also necessary

    print(f"Received data: {repr(received_data)}")
    time.sleep(5)
 
#print(win32pipe.CallNamedPipe(r"\\.\pipe\simple-ipc-pipe", 'NSE:TATAMOTORS,C'.encode(ENCODING), 64, 0))
#print('5')
