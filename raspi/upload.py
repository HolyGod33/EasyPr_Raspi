import requests
import time
import RPi.GPIO as GPIO

IN1 = 11  # pin11
IN2 = 12
IN3 = 13
IN4 = 15


def setStep(w1, w2, w3, w4):
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
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(IN1, GPIO.OUT)  # Set pin's mode is output
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)


if __name__ == '__main__':

    url = "http://192.168.43.96:8011/easy/upload"

    file = {'file': ('test.jpg', open('test.jpg', 'rb'), 'image/jpg', {})}

    res = requests.request("POST", url, data={"type": "1"}, files=file)

    if res.text == 'success':
        print "start"
        backward(0.003, 512)
        setStep(0, 0, 0, 0)
        print "stop"
        GPIO.cleanup()
