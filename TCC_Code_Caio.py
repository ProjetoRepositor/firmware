
import pyaudio
import requests
import numpy as np
import wave,datetime,os
import gpiozero
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21,GPIO.OUT)

GPIO.output(21,GPIO.LOW)

def button_press():
    record_length =  4
    data_chunks,data_frames,t_0 = data_grabber(record_length) # grab the data
    print('Salvando..')
    file_name= data_saver(t_0, data_frames, data_chunks) # save the data as a .wav file
    print(f'Salvo {file_name}')

botao = gpiozero.Button(3)

botao.when_pressed = button_press


def pyserial_start():
    audio = pyaudio.PyAudio() # create pyaudio instantiation
  

    stream = audio.open(format = pyaudio_format,rate = samp_rate,channels = chans, input_device_index = dev_index,input = True,frames_per_buffer=CHUNK)
                        
    stream.stop_stream() # stop stream to prevent overload
    return stream,audio

def pyserial_end():
    stream.close() # close the stream
    audio.terminate() # close the pyaudio connection

def data_grabber(rec_len):
    stream.start_stream() # start data stream
    stream.read(CHUNK,exception_on_overflow=False) # flush port first 
    t_0 = datetime.datetime.now() # get datetime of recording start
    print('Recording Started.')
    GPIO.output(21, GPIO.HIGH)
    data,data_frames = [],[] # variables
    for frame in range(0,int((samp_rate*rec_len)/CHUNK)):
        # grab data frames from buffer
        stream_data = stream.read(CHUNK,exception_on_overflow=False)
        data_frames.append(stream_data) # append data
        data.append(np.frombuffer(stream_data,dtype=buffer_format))
    stream.stop_stream() # stop data stream
    GPIO.output(21, GPIO.LOW)
    print('Recording Stopped.')
    return data,data_frames,t_0

def data_saver(t_0, data_frames, data_chunks):
    data_folder = './data/' # folder where data will be saved locally
    if os.path.isdir(data_folder)==False:
        os.mkdir(data_folder) # create folder if it doesn't exist
    filename = datetime.datetime.strftime(t_0,
                                          '%Y_%m_%d_%H_%M_%S_pyaudio') # filename based on recording time
    wf = wave.open(data_folder+filename+'.wav','wb') # open .wav file for saving
    wf.setnchannels(chans) # set channels in .wav file 
    wf.setsampwidth(audio.get_sample_size(pyaudio_format)) # set bit depth in .wav file
    wf.setframerate(samp_rate) # set sample rate in .wav file
    wf.writeframes(b''.join(data_frames)) # write frames in .wav file
    wf.close() # close .wav file
    return filename
#
##############################################
# Main Data Acquisition Procedure
##############################################
#

def transcribe(file_name):
    url = "http://localhost:800/api/audio"
#token 7f4e2164a8e8ef0be122d2cbd1ff61e79d4973cfd29cc9917fb4b8ff3d87bd7b
    with open(f'data/{file_name}.wav', 'rb') as f:
        payload = f.read()

    headers = {
    'Content-Type': 'audio/wave',
    'token': '7f4e2164a8e8ef0be122d2cbd1ff61e79d4973cfd29cc9917fb4b8ff3d87bd7b'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def loop():
    pass


if __name__=="__main__":
    #
    ###########################
    # acquisition parameters
    ###########################
    #
    CHUNK          = 44100  # frames to keep in buffer between reads
    samp_rate      = 44100 # sample rate [Hz]
    pyaudio_format = pyaudio.paInt16 # 16-bit device
    buffer_format  = np.int16 # 16-bit for buffer
    chans          = 1 # only read 1 channel
    dev_index      = 1 # index of sound device    
    #
    #############################
    # stream info and data saver
    #############################
    #
    stream,audio = pyserial_start() # start the pyaudio stream   
     # seconds to record
    
    while 1:
        loop()

    # transcribe(file_name)
    pyserial_end() # close the stream/pyaudio connection
   