import picamera
import time
import uuid

camera = picamera.Picamera()

camera.resolution = (1920, 1080)
camera.framerate = 60
uuid_str = uuid.uuid4().hex

camera.start_preview()
camera.capture('tem_file%s.jpg' % uuid_str)
camera.stop_preview()
