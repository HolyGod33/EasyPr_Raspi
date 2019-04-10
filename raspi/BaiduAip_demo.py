# coding=utf-8
from aip import AipSpeech
import os

text='胖子'
APP_ID = '15975668'
API_KEY = 'wtmjsVeExme8AcTAu06ovMlB'
SECRET_KEY = 'j9BGMv08N5o6fLegad0q581mdTpbVuCv'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

result = client.synthesis(text, 'zh', 1, {
    'vol': 5,
})

if not isinstance(result, dict):
    with open('auido.mp3', 'wb') as f:
        f.write(result)
        
cmd1="/home/pi/Desktop/PythonProgram"

cmd2="omxplayer -o local auido.mp3"
os.system(cmd1)
os.system(cmd2)
