#! /usr/bin/python
#  -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time


def checkdist():
    # 发出触发信号
    GPIO.output(2, GPIO.HIGH)
    # 保持15us的超声波发射，避免能量太低无法返回
    time.sleep(0.000015)
    # 然后置位2号管脚低电平，即停止发射超声波
    GPIO.output(2, GPIO.LOW)
    while not GPIO.input(3):
        pass

    t1 = time.time()
    # 如果有检测到反射返回的超声波，那么就持续计时，否则就跳出循环，计时结束
    while GPIO.input(3):
        pass
        # 高电平结束停止计时
    t2 = time.time()
    # 返回距离，单位为米
    return (t2 - t1) * 340 / 2




GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(3, GPIO.IN)
time.sleep(2)
try:
    while True:
        print 'Distance: %0.2f m' % checkdist()
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
