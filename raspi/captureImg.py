# coding=utf-8
import uuid

import RPi.GPIO as GPIO
import time
import picamera
import requests


def setStep(w1, w2, w3, w4):
    IN1 = 11  # pin11
    IN2 = 12
    IN3 = 13
    IN4 = 15
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


def stop():
    setStep(0, 0, 0, 0)


def forward(delay, steps):
    for i in range(0, steps):
        setStep(1, 0, 0, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 0, 0, 1)
        time.sleep(delay)


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


def camera(uuid_name):
    photo = picamera.PiCamera()

    photo.resolution = (1920, 1080)
    photo.framerate = 60

    photo.start_preview()
    photo.capture('file_%s.jpg' % uuid_name)
    photo.stop_preview()
    photo.close()


def uuidfilename():
    uuid_name = uuid.uuid4().hex
    return uuid_name


def checkdist():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(3, GPIO.IN)
    GPIO.output(2, GPIO.HIGH)

    time.sleep(0.000015)

    GPIO.output(2, GPIO.LOW)
    while not GPIO.input(3):
        pass

    t1 = time.time()

    while GPIO.input(3):
        pass

    t2 = time.time()
    return (t2 - t1) * 340 / 2


def upload(filename):
    url = "http://192.168.43.96:8011/easy/upload"
    # TODO: 修改文件名
    file = {'file': ('test.jpg', open('test.jpg', 'rb'), 'image/jpg', {})}

    res = requests.request("POST", url, data={"type": "1"}, files=file)

    return res.text


def open_door():
    setup()
    backward(0.003, 512)
    setStep(0, 0, 0, 0)


def close_door():
    setup()
    forward(0.003, 512)
    setStep(0, 0, 0, 0)


if __name__ == '__main__':

    # 定义标记:0为锁闭合 1为打开锁 默认闭锁
    flag = 0
    while True:
        distance_1 = checkdist()
        time.sleep(0.2)

        distance_2 = checkdist()
        time.sleep(0.2)
        # 有物体靠近,开始验证
        if (distance_1 <= 1.0) & (distance_2 <= 1.0):
            distance_3 = checkdist()
            # 确认物体靠近,拍照识别有无车牌
            if (distance_3 <= 1.0) & (flag == 0):
                # uuid文件名
                uuid_name = uuidfilename()

                camera(uuid_name)
                # 当前图片内的车牌为数据库中存在的车牌信息
                if upload(uuid_name) == 'success':
                    GPIO.cleanup()
                    print "open the door"
                    setup()
                    open_door()
                    print "success"
                    GPIO.cleanup()
                    flag = 1
                    continue

            # 当前距离有车牌且锁是打开状态 防止重复操作
            elif (distance_3 <= 1.0) & (flag == 1):
                continue
        # 如果当前距离内没有车牌且该锁是打开状态 车辆已经离开
        elif (distance_1 > 1.0) & (distance_2 > 1.0) & (flag == 1):
            GPIO.cleanup()
            print "close the door"
            close_door()
            print "success"
            GPIO.cleanup()
            flag = 0

        # 如果当前距离内没有车牌且锁是闭合状态 防止重复操作
        elif (distance_1 > 1.0) & (distance_2 > 1.0) & (flag == 0):
            continue
