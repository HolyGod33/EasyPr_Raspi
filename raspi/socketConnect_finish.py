# coding=utf-8
import uuid
import requests
import RPi.GPIO as GPIO
import picamera
import time
import timeit
import socket
import threading
from multiprocessing import Process, Lock, Value
import os

threadLock = threading.Lock()
threads = []


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


def setStep(w1, w2, w3, w4):
    IN1 = 11  # pin11
    IN2 = 12
    IN3 = 13
    IN4 = 15
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


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


def open_door():
    setup()
    backward(0.003, 512)
    setStep(0, 0, 0, 0)


def close_door():
    setup()
    forward(0.003, 512)
    setStep(0, 0, 0, 0)


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


def captureProcess(lock, flag):
    while True:
        print("当前运行进程 captureProcess: %s " % (os.getpid()))

        if flag.value == 1:
            print("当前车辆是否可进入: 是")
        elif flag.value == 0:
            print("当前车辆是否可进入: 否")

        distance_1 = checkdist()
        time.sleep(0.2)

        distance_2 = checkdist()
        time.sleep(0.2)
        # 有物体靠近,开始验证
        if (distance_1 <= 1.0) & (distance_2 <= 1.0):
            distance_3 = checkdist()
            print("当前距离: %f" % distance_3)
            # 确认物体靠近,拍照识别有无车牌
            if (distance_3 <= 1.0) & (flag.value == 0):
                # uuid文件名
                uuid_name = uuidfilename()

                camera(uuid_name)
                t = timeit.timeit(upload(uuid_name))

                if t >= 5:
                    print ("服务器未响应!")
                    continue
                # 当前图片内的车牌为数据库中存在的车牌信息
                if upload(uuid_name) == 'success':
                    # TODO 获取进程锁
                    lock.acquire()
                    GPIO.cleanup()
                    print ("open the door")
                    setup()
                    open_door()
                    print ("success")
                    GPIO.cleanup()
                    flag.value = 1
                    # 释放锁
                    lock.release()
                    continue
                else:
                    print ("警告! 非授权用户进入")
                    continue

            # 当前距离有车牌且锁是打开状态 防止重复操作
            elif (distance_3 <= 1.0) & (flag.value == 1):
                continue
        # 如果当前距离内没有车牌且该锁是打开状态 车辆已经离开
        elif (distance_1 > 1.0) & (distance_2 > 1.0) & (flag.value == 1):
            # TODO 获取线程锁
            lock.acquire()
            GPIO.cleanup()
            print ("close the door")
            close_door()
            print ("success")
            GPIO.cleanup()
            flag.value = 0
            # 释放锁
            lock.release()

        # 如果当前距离内没有车牌且锁是闭合状态 防止重复操作
        elif (distance_1 > 1.0) & (distance_2 > 1.0) & (flag.value == 0):
            continue


def socketProcess(lock, flag):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 8080

    print("当前运行线程:socketProcess %s" % (os.getpid()))

    serversocket.bind(('192.168.43.18', port))

    serversocket.listen(5)

    while True:
        # 建立客户端连接
        clientsocket, addr = serversocket.accept()

        try:

            print("当前运行线程:socketProcess %s" % (os.getpid()))

            print("连接地址: %s" % str(addr))

            clientsocket.send("%d".encode() % flag.value)

            msg = clientsocket.recv(1024).decode("gbk")

            print (msg)

            if msg == '1':
                if flag.value == 1:
                    # TODO 线程锁
                    lock.acquire()
                    clientsocket.send("{code: '1',msg: 'open'}".encode("gbk"))
                    flag.value = 0
                    clientsocket.close()
                    print("断开连接")
                    # 释放锁
                    lock.release()
            elif msg == '0':
                if flag.value == 0:
                    # TODO 线程锁
                    lock.acquire()
                    clientsocket.send("{code: '0',msg: 'close'}".encode("gbk"))
                    flag.value = 1
                    clientsocket.close()
                    print("断开连接")
                    # 释放锁
                    lock.release()

        except Exception as e:
            clientsocket.send("{code: '500',msg: 'error'}".encode("gbk"))
            break


if __name__ == '__main__':
    # 意义:1为车辆可以进入,即地锁三角为放下 0为车辆不可以进入 地锁三角为升起
    flag = Value('i', 1)

    lock = Lock()
    p1 = Process(target=captureProcess, args=(lock, flag))
    p2 = Process(target=socketProcess, args=(lock, flag))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
