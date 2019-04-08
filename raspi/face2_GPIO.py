# coding=utf-8
from picamera import PiCamera
import time
import requests
import base64
import RPi.GPIO as GPIO
##import serial
import sys
import os
import json


# 获得百度API的access_token
def getaccess_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=nHiCsVZDtKH1gIeN5GDQPwMI&client_secret=MakNAT5ndMACLdUsDrxjSBT61E85Mmdw'
    header_1 = {'Content-Type': 'application/json; charset=UTF-8'}
    request = requests.post(host, headers=header_1)
    access_token = request.json()['access_token']
    return access_token


# 拍摄当前图片
def take_picture():
    camera.start_preview()
    time.sleep(0.5)
    camera.capture('image.jpg')
    camera.stop_preview()


# 打开工程拍摄的图片并转换成字符串
def open_pic():
    f = open('image.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img


# 上传到百度API进行人脸检验
def go_api(img, access_token):
    data_1 = {"image": img, "image_type": "BASE64", 'group_id_list': 'BST_Demo'}
    header_2 = {'Content-Type': 'application/json'}
    pic_re = requests.post('https://aip.baidubce.com/rest/2.0/face/v3/search?access_token=' + access_token,
                           headers=header_2, data=data_1)
    print(len(pic_re.text))
    if len(pic_re.text) > 130:
        print(pic_re.json())
        json_str = json.dumps(pic_re.json())
        data = json.loads(json_str)
        print(data['result']['user_list'][0]['score'])
        if data['result']['user_list'][0]['score'] > 66:
            return ('yes')
        else:
            return ('no')

    else:
        print(pic_re.json())
        print('error')
        return ('no')
    # return(pic_re.json()['result'][0]['scores'])


# 设置
def setup():
    IN1 = 11  # pin11
    IN2 = 12
    IN3 = 13
    IN4 = 15
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(IN1, GPIO.OUT)  # Set pin's mode is output
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)


def open_door():
    setup()
    backward(0.003, 512)
    setStep(0, 0, 0, 0)


def setStep(w1, w2, w3, w4):
    IN1 = 11  # pin11
    IN2 = 12
    IN3 = 13
    IN4 = 15
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


# 开门
def backward(delay, steps):
    for i in range(0, steps):
        setStep(0, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 0, 0, 0)
        time.sleep(delay)


# 调用相关函数进行整个程序过程
def try_api(img, access_token):
    try:
        a = go_api(img, access_token)
        if a == 'yes':
            print('reday to open door')
            open_door()
            GPIO.clean()
            time.sleep(5)
        if a == 'no':
            pass
    except:
        pass


if __name__ == '__main__':
    # 程序运行配置命令---------------------------------
    ##    os.system('sudo rfcomm bind 0 00:21:13:01:8E:1A')
    port = "/dev/rfcomm0"
    ##    serial = serial.Serial(port,9600)
    count = 0
    # 程序运行配置命令--------------------------------
    camera = PiCamera()
    access_token = getaccess_token()
    while True:
        take_picture()
        img = open_pic()
        try_api(img, access_token)
        count = count + 1
        print(count)
        print("access_token   " + access_token)
        # 加入自动重启命令，防止程序运行时间过长死机
        if count == 2000:
            os.system('sudo reboot')
            count = 0
