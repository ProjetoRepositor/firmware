
import pyaudio
import requests
import numpy as np
import wave,datetime,os
import gpiozero
import RPi.GPIO as GPIO
from serial import Serial
import time
import json

ser = Serial ("/dev/ttyS0", 9600) 

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
    transcribe(file_name)

botao = gpiozero.Button(3)

botao.when_pressed = button_press


def pyserial_start():
    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # Ajuste o ganho (intensidade do sinal de entrada)
    stream = audio.open(format = pyaudio_format,
                        rate = samp_rate,
                        channels = chans,
                        input_device_index = dev_index,
                        input = True,
                        frames_per_buffer=CHUNK)

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
    with open(f'data/{file_name}.wav', 'rb') as f:
        payload = f.read()

    with open('/home/victor/token.txt') as f:
        token = f.read().split()[0]

    headers = {
    'Content-Type': 'audio/wave',
    'token': token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def send_ean(ean):
    url = "https://rq0ak44zy0.execute-api.sa-east-1.amazonaws.com/Prod/api/v1/carrinho"

    with open('/home/victor/token.txt') as f:
        token = f.read().split()[0]

    payload = json.dumps({
        "codigoDeBarras": ean,
        "quantidade": 1
    })
    headers = {
        'token': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)



def loop():
    print('Esperando Leitura de código de barras')
    received_data = ser.read()              #read serial port
    time.sleep(0.03)
    data_left = ser.inWaiting()             #check for remaining byte
    received_data += ser.read(data_left)
    ean = f'{received_data.decode("utf8").split()[0]}'
    send_ean(ean)
    print(ean)


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
    
    while 1:
        loop()

    pyserial_end() # close the stream/pyaudio connection
   
