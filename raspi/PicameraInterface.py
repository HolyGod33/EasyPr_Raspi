'''
通过摄像头拍一张照片，然后识别出人是谁，进而控制门禁系统
@author: zutterhao
@date:2018年5月19日
'''

from aip import AipFace
from picamera import PiCamera
import urllib.request
import RPi.GPIO as GPIO
import base64
import time
import pyttsx3
import pygame

#百度人脸识别API账号信息
APP_ID = '********'
API_KEY = '*******************'
SECRET_KEY = '*********************‘
client = AipFace(APP_ID, API_KEY, SECRET_KEY)
#图像编码方式
IMAGE_TYPE='BASE64'
#用户组信息
GROUP = 'fanghao'
camera = PiCamera()
engine = pyttsx3.init()
pygame.mixer.init()
GPIO_IN_PIN = 15
GPIO_OUT_PIN1 = 11
GPIO_OUT_PIN2 = 13
#定义一个摄像头对象
def getimage():
    camera.resolution = (1024,768)
    camera.start_preview()
    time.sleep(2)
    camera.capture('faceimage.jpg')
    pygame.mixer.music.load('./voice/start.mp3')
    pygame.mixer.music.play()
    time.sleep(2)

#对图片的格式进行转换
def transimage():
    f = open('faceimage.jpg','rb')
    img = base64.b64encode(f.read())
    return img
#播放声音
def playvioce(name):
    pygame.mixer.music.load('./voice/' +name)
    pygame.mixer.music.play()
#发送信息到微信上
def sendmsg(name,main):
    # TODO: 尝试用这个方法进行通信
    url = "https://sc.ftqq.com/***********************************.send?"
    urllib.request.urlopen(url + "text="+name+"&desp="+main)

#上传到百度api进行人脸检测
def go_api(image):

    # 百度官方API,用于上传人脸信息 识别该人脸是否为用户之一
    result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP);
    if result['error_msg'] == 'SUCCESS':
        name = result['result']['user_list'][0]['user_id']
        score = result['result']['user_list'][0]['score']
        if score > 80:
            print("Welcome %s !" % name)
            if name == 'fanghao':
                sendmsg("DoorOpen",name)
                playvioce('fanghao.mp3')
                time.sleep(3)
            if name == 'chengjiayu':
                sendmsg("DoorOpen",name)
                playvioce('chengjiayu.mp3')
                time.sleep(3)
                playvioce('despacito.mp3')
                time.sleep(5)
            if name == 'zhangzhijian':
                sendmsg("DoorOpen",name)
                playvioce('zhangzhijian.mp3')
                time.sleep(3)
        else:
            print("Sorry...I don't know you !")
            playvioce('noroot.mp3')
            name = 'Unknow'
            return 0
        curren_time = time.asctime(time.localtime(time.time()))
        f = open('Log.txt','a')
        f.write("Person: " + name + "     " + "Time:" + str(curren_time)+'\n')
        f.close()
        return 1
    if result['error_msg'] == 'pic not has face':
        print('There is no face in image!')
        playvioce('face.mp3')
        time.sleep(2)
        return 0
    else:
        print(result['error_code']+' ' + result['error_code'])
        return 0
#主函数
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_IN_PIN,GPIO.IN)
    GPIO.setup(GPIO_OUT_PIN1,GPIO.OUT)
    GPIO.setup(GPIO_OUT_PIN2,GPIO.OUT)
    while True:
        print('OK')
        if True:
            #if GPIO.input(GPIO_IN_PIN) == GPIO.LOW:
            getimage()
            img = transimage()
            res = go_api(img)
            if(res == 1):
                GPIO.output(GPIO_OUT_PIN2,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(GPIO_OUT_PIN2,GPIO.LOW)
            else:
                GPIO.output(GPIO_OUT_PIN1,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(GPIO_OUT_PIN1,GPIO.LOW)
            print('waite 3 seconds to do next')
            playvioce('waite.mp3')
            time.sleep(3)