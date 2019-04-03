# coding=utf-8
import socket
import sys
import socketserver
import requests
import threading

reload(sys)
sys.setdefaultencoding('utf-8')
flag = 1


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        global flag
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host = socket.gethostname()

        port = 9999 + self.counter

        serversocket.bind(('localhost', port))

        serversocket.listen(5)

        while True:
            # 建立客户端连接
            clientsocket, addr = serversocket.accept()

            try:
                print("连接地址: %s" % str(addr))

                msg = clientsocket.recv(1024).decode("gbk")

                print msg

                if msg == '1':
                    if flag == 1:
                        # TODO
                        clientsocket.send("{code: '1',msg: 'open'}".encode("gbk"))
                        flag = 0
                        clientsocket.close()
                elif msg == '0':
                    if flag == 0:
                        # TODO
                        clientsocket.send("{code: '0',msg: 'close'}".encode("gbk"))
                        flag = 1
                        clientsocket.close()

            except Exception as e:
                clientsocket.send("{code: '500',msg: 'error'}".encode("gbk"))
                break


class socketdemo(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            self.datax = self.request.recv(1024).decode("gbk")
            if self.datax == '1':
                self.request.send("hello world".encode("gbk"))


if __name__ == '__main__':
    thread1 = myThread(1, "mythread_1", 1)
    thread2 = myThread(2, "mythread_2", 2)
    thread1.start()
    thread2.start()
