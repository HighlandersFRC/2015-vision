from paho.mqtt import client
import binascii
import cv2
import numpy
import socket

UDP_IP = "DriverStation.local"
UDP_PORT = 5801

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


def on_message(client, userdata, message):
    if message.topic == 'Robot/AutoChoice':
        print "Chosen Autonomous:", message.payload

def on_connect(client, userdata, flags, rc) :
    print "connected with result code", rc
    client.subscribe("Vision/Frame")
def on_disconnect(client, userdata, rc) :
    print "disconnected with code", rc
mqttclient = client.Client()

mqttclient.on_message = on_message
mqttclient.on_connect = on_connect
mqttclient.on_disconnect = on_disconnect

while True:
    data, addr = sock.recvfrom(1024000)
    #print "recieved frame"
    data2 = numpy.fromstring(data, dtype='uint8')
    decimg = cv2.imdecode(data2, 1)
    cv2.rectangle(decimg, cv2.Point(decimg.rows/3.0, decimg.cols/3.0), cv2.Point(decimg.rows*2.0/3.0, decimg.cols*2.0/3.0), cv2.Color(255, 0, 0), 3)
    cv2.imshow('frame', decimg)
    cv2.waitKey(1)
    #print "finished frame"
    mqttclient.loop()
