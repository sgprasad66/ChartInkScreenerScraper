from threading import Thread
from queue import Queue
import PySimpleGUI as sg
import time
import pyaudiowpatch as pyaudio
import wave

messages= Queue()
recordings = Queue()

def start_recording(data):
    '''  messages.put(True)
    record = Thread(target=record_microphone)
    record.start()
    transcribe = Thread(target=start_transcribing)
    transcribe.start() '''
    record_microphone()

data_format = pyaudio.paInt16
RECORD_SECONDS=2
RATE=0

DURATION = 20
CHUNK_SIZE = 512
filename = "loopback_record_103.wav"

def record_microphone(CHUNK_SIZE=512):
   
    with pyaudio.PyAudio() as p :
        """
        Create PyAudio instance via context manager.
        Spinner is a helper class, for `pretty` output
        """
        try:
            # Get default WASAPI info
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            pass
        
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
                pass
                
                
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
            time.sleep(DURATION) # Blocking execution while playing
        
        wave_file.close()

    start_transcribing()
   
import subprocess
import json
from vosk import Model, KaldiRecognizer
import time

#model = Model(model_path='D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\vosk-model-en-us-0.22',model_name="vosk-model-en-us-0.22")
#rec = KaldiRecognizer(model, RATE)
#rec.SetWords(True)
    
def speech_recognition():
    
    while not messages.empty():
        frames = recordings.get()
        
        #rec.AcceptWaveform(b''.join(frames))
        #result = rec.Result()
        #text = json.loads(result)["text"]
        print('text')
        #cased = subprocess.check_output('python recasepunc/recasepunc.py predict recasepunc/checkpoint', shell=True, text=True, input=text)
        #output.append_stdout(cased)
        time.sleep(1)      

  
def update_progress(window, progress):
    window['progress_bar'].update(progress)

def do_work():
    for i in range(100):
        update_progress(window, i)
        time.sleep(0.1)

def translate_hindi_to_english(texttotranslate):
        # Import the Google Translate library
        from googletrans import Translator

        # Create a translator object
        translator = Translator()

        # Translate the text from Hindi to English
        #translation = translator.translate("नमस्ते", dest='en')
        translation = translator.translate(texttotranslate,dest='en')

        # Print the translated text
        print(translation.text)
        return translation.text
def start_transcribing():

    import speech_recognition as sr
    from moviepy.editor import VideoFileClip
    #recognizer = sr.Recognizer()
    ''' while not messages.empty():
        frames = recordings.get() '''
        
    text=''
    from pydub import AudioSegment as am
    sound = am.from_file("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\loopback_record_103.wav", format='wav', frame_rate=44100)
    sound = sound.set_frame_rate(16000)
    sound.export("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\loopback_record_103_16000.wav", format='wav')
    r = sr.Recognizer()
    with sr.AudioFile("loopback_record_103_16000.wav") as source:
# listen for the data (load audio to memory)
        audio_data = r.record(source)
# recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
    #text = r.recognize_google(audio_data, language="hi-IN")
        trans_text = translate_hindi_to_english(text)
        print(text)
        window['INPUT'].update(text)
        time.sleep(1)


    ''' text=''
    from pydub import AudioSegment as am
    sound = am.from_file("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\loopback_record_103.wav", format='wav', frame_rate=44100)
    sound = sound.set_frame_rate(16000)
    sound.export("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\loopback_record_103_16000.wav", format='wav')
    r = sr.Recognizer()
    with sr.AudioFile("loopback_record_103_16000.wav") as source:
    # listen for the data (load audio to memory)
        audio_data = r.record(source)
    # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        #text = r.recognize_google(audio_data, language="hi-IN")
        print(text)
        window['INPUT'].update(text) '''
    
        
window = sg.Window('Progress Bar', [[sg.ProgressBar(100, orientation='h', key='progress_bar')],
                                     [sg.Button('  Record  ')],
                                     [sg.Button('   Stop   ',key='-stop-')],
                                     [sg.Text('Transcribed Text Here:')], 
                                     [sg.Multiline(size=(40, 10),key='INPUT')]])

event, values = window.read()

if event == '  Record  ':
    start_recording(data='data from record')
if event == '-stop-':
    start_transcribing()

    

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()