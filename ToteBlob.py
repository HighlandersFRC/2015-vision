from cv2 import *
import numpy
import binascii
from paho.mqtt import client
import time
import socket

cam = VideoCapture(0)

frame = None
hsv = None
hue = None
sat = None
val = None
remapHue = None
matchPlane = None

startTime = time.clock()

mqttclient = client.Client()

mqttclient.connect("tegra-ubuntu.local", 5800)
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

while (True) :
    startTime = time.clock()
    retval, frame = cam.read(frame)
    if not retval:
        print "failed to read frame"
        time.sleep(1)
        continue
    frameTime = time.clock()
    hsv =  cvtColor(frame, COLOR_BGR2HSV, hsv)
    hsvTime = time.clock()
    [hue, sat, val] = split(hsv, [hue, sat, val])
    splitTime = time.clock()
    remapHue = absdiff(hue, 30, remapHue)
    remapHue = absdiff(remapHue, 90, remapHue)
    remapTime = time.clock()
    matchPlane = multiply(remapHue, sat, matchPlane, 1.0/90.0)
    matchPlane = multiply(matchPlane, val, matchPlane, 1.0/256.0)
    matchTime = time.clock()
    retval, matchPlane = threshold(matchPlane, 160, 255, THRESH_BINARY, matchPlane)
    threshTime = time.clock()
    mu = moments(matchPlane)
    momentsTime = time.clock()
    #print mu
    if mu['m00'] >= 1000 :
        x = mu['m10']/mu['m00']
        y = mu['m01']/mu['m00']
        mqttclient.publish("Vision/Center", str(x) + ", "+str(y))
        #print "center is at (", x, ", ", y,")"
    retval, data = imencode(".jpg", frame, [IMWRITE_JPEG_QUALITY, 10])
    encodeTime = time.clock()
    datastr = data.tostring()
    try:
        sock.sendto(datastr, ("DriverStation.local" ,5801))
    except socket.error:
        print "Failed to send frame"
        time.sleep(1)
    publishTime = time.clock()
    frameDelta = frameTime - startTime
    hsvDelta = hsvTime - frameTime
    splitDelta = splitTime - hsvTime
    remapDelta = remapTime - splitTime
    matchDelta = matchTime - remapTime
    threshDelta = threshTime - matchTime
    momentsDelta = momentsTime - threshTime
    encodeDelta = encodeTime - momentsTime
    publishDelta = publishTime - encodeTime
    #print "frame", frameDelta, "hsv", hsvDelta, "split", splitDelta, "remap", remapDelta, "match", matchDelta, "thresh", threshDelta, "moments", momentsDelta, "encode", encodeDelta, "publish", publishDelta
    key = waitKey(20)
    if key != -1 :
        print "quitting with key ", key
        break
