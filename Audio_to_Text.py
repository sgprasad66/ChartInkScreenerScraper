''' import speech_recognition as sr
import pyaudio
import moviepy.editor as mpe

r = sr.Recognizer()

mic = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

stream = mic.stream()

audio = stream.read(1024)
text = r.recognize_google(audio)

stream.stop_stream()
stream.close()
mic.terminate()

print(text) '''


''' 
import speech_recognition as sr

# Create a recognizer object
r = sr.Recognizer()

# Listen for speech from the microphone
with sr.Microphone() as source:
    audio = r.listen(source)

# Recognize the speech
try:
    text = r.recognize_google(audio)
    print("You said: " + text)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e)) '''

''' import speech_recognition as sr
import pyaudio
import cv2

r = sr.Recognizer()

cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Recognize the speech in the frame
    with sr.AudioFile(gray) as source:
        audio = r.record(source)
        text = r.recognize_google(audio)

    # Display the recognized text on the frame
    cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Video', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
 '''
youtubeurl = 'https://www.youtube.com/watch?v=0uDAjPzfusI'

''' import pytube
import ffmpeg
import cv2

youtube = pytube.YouTube(youtubeurl)

stream = youtube.streams.get_highest_resolution()
 
import time
import webbrowser
import pyautogui

def get_chrome_play():
    import webbrowser
    url = 'http://docs.python.org/'
    # MacOS
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    # Windows
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # Linux
    chrome_path = '/usr/bin/google-chrome %s'

    webbrowser.get(chrome_path).open(youtubeurl)

try:
    client = webbrowser.get("chrome")
    client.open("https://" + youtubeurl)
    get_chrome_play()

    time.sleep(30)       #give it a couple seconds to load
    pyautogui.press('space')
except webbrowser.Error as e:
    print(e)

    '''


''' import speech_recognition as sr
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


import speech_recognition as sr

# Create a recognizer object
r = sr.Recognizer()

# Listen for speech from the microphone
with sr.Microphone(device_index=7) as source:
    audio = r.listen(source)

# Recognize the speech
try:
    text = r.recognize_google(audio)
    print("You said: " + text)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e)) '''

"""A simple example of recording from speakers ('What you hear') using the WASAPI loopback device"""
from threading import Thread
import time


class Spinner(Thread):
    """Helper class for examples"""
    def __init__(self, spinner_style: int = 1) -> None:
        super().__init__()
        self.style = spinner_style
        self.running = False
        self.output_queue = []
        
    def start(self) -> None:
        self.running = True
        super().start()
        
    def stop(self) -> None:
        while len(self.output_queue)>0:
            time.sleep(0.05)
        self.running = False
        super().join()
        self.clear()
        
    def clear(self) -> None:
        print(f"\r{' '*20}\r", end="")
        
    def print(self, msg: str) -> None:
        self.output_queue.append(msg)
        
    def run(self) -> None:
        def spinner_generator(style: int = 0):
            sp_styles = [
                ["◌","○","●","○",],
                ["█","▓","▒","░","▒","▓",],
                ["/","|","\\",]
            ]
            sp_list = sp_styles[style % len(sp_styles)]
            last_sp_index = 0
            while True:
                yield sp_list[last_sp_index]
                last_sp_index = (last_sp_index+1)%len(sp_list)
                
        sp_gen = spinner_generator(self.style)
        
        while self.running:
            self.clear()
            if len(self.output_queue) > 0:
                print(self.output_queue.pop(0))
            print(f"\r{next(sp_gen)}", end="")    
            time.sleep(0.1)
        
    def __enter__(self) -> 'Spinner':
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

#import Spinner
# Spinner is a helper class that is in the same examples folder.
# It is optional, you can safely delete the code associated with it.

import pyaudiowpatch as pyaudio
import time
import wave

DURATION = 20.0
CHUNK_SIZE = 512

filename = "loopback_record_103.wav"
    
    
if __name__ == "__main__":
    with pyaudio.PyAudio() as p, Spinner() as spinner:
        """
        Create PyAudio instance via context manager.
        Spinner is a helper class, for `pretty` output
        """
        try:
            # Get default WASAPI info
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            spinner.print("Looks like WASAPI is not available on the system. Exiting...")
            spinner.stop()
            exit()
        
        # Get default WASAPI speakers
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                """
                Try to find loopback device with same name(and [Loopback suffix]).
                Unfortunately, this is the most adequate way at the moment.
                """
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                spinner.print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                spinner.stop()
                exit()
                
        spinner.print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")
        
        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(default_speakers["maxInputChannels"])
        wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(int(default_speakers["defaultSampleRate"]))
        #wave_file.setframerate(16000)
        
        def callback(in_data, frame_count, time_info, status):
            """Write frames and return PA flag"""
            wave_file.writeframes(in_data)
            return (in_data, pyaudio.paContinue)
        
        with p.open(format=pyaudio.paInt16,
                channels=default_speakers["maxInputChannels"],
                rate=int(default_speakers["defaultSampleRate"]),
                frames_per_buffer=CHUNK_SIZE,
                input=True,
                input_device_index=default_speakers["index"],
                stream_callback=callback
        ) as stream:
            """
            Opena PA stream via context manager.
            After leaving the context, everything will
            be correctly closed(Stream, PyAudio manager)            
            """
            spinner.print(f"The next {DURATION} seconds will be written to {filename}")
            time.sleep(DURATION) # Blocking execution while playing
        
        wave_file.close()