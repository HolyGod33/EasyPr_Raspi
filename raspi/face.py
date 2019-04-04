from picamera import PiCamera
import time
import requests
import base64
import RPi.GPIO
##import serial
import sys
import os
import json

#获得百度API的access_token
def getaccess_token():
    host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=d0D7mrpcDQlDr4FO3UOaqL8m&client_secret=IWGoit2542ihi0ubuK52upF2GnfyrOGY'
    header_1 = {'Content-Type':'application/json; charset=UTF-8'}
    request=requests.post(host,headers =header_1)
    access_token=request.json()['access_token']
    return access_token

#拍摄当前图片
def take_picture():
    camera.start_preview()
    time.sleep(0.5)
    camera.capture('image.jpg')
    camera.stop_preview()

#打开工程拍摄的图片并转换成字符串
def open_pic():
    f = open('image.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img

#上传到百度API进行人脸检验
def go_api(img,access_token):
    data_1 = {"image":img,"image_type":"BASE64",'group_id_list':'1'}
    header_2 = {'Content-Type':'application/json'}
    pic_re=requests.post('https://aip.baidubce.com/rest/2.0/face/v3/search?access_token='+access_token,headers=header_2,data=data_1)
    print(len(pic_re.text))
    if len(pic_re.text)>130:
        print(pic_re.json())
        json_str = json.dumps(pic_re.json())
        data = json.loads(json_str)
        print(data['result']['user_list'][0]['score'])
        if data['result']['user_list'][0]['score']>66:
            return ('yes')
        else :
            return ('no')

    else:
        print(pic_re.json())
        print('error')
        return ('no')
    #return(pic_re.json()['result'][0]['scores'])

#点亮指示LED等
def led():
    print('********output open door************')
    RPi.GPIO.output(18, True)


#通过蓝牙对Arduino发出开门指令
def send():
    serial.write(bytes(2, 'UTF-8'))
    print('发出指令成功')
    serial.flushInput()

#调用相关函数进行整个程序过程
def try_api(img,access_token):
    try:
        a=go_api(img,access_token)
        if a=='yes':
            print('reday to open door')
            led()
##            send()
            time.sleep(10)
            RPi.GPIO.output(18, False)
        if a=='no':
            pass
    except:
        pass


if __name__ == '__main__':
    #程序运行配置命令---------------------------------
##    os.system('sudo rfcomm bind 0 00:21:13:01:8E:1A')
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setup(18, RPi.GPIO.OUT)
    port = "/dev/rfcomm0"
##    serial = serial.Serial(port,9600)
    count=0
    #程序运行配置命令--------------------------------
    camera = PiCamera()
    access_token=getaccess_token()
    while True :
        take_picture()
        img=open_pic()
        try_api(img,access_token)
        count=count+1
        print(count)
        print("access_token   "+access_token)
        #加入自动重启命令，防止程序运行时间过长死机
        if count == 2000 :
            os.system('sudo reboot')
            count = 0
