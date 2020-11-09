#! /usr/bin/python
import numpy as np
import cv2
import PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import time
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sys
import threading
import io
import pickle
import Queue

fps = 0
prevTime = 0;

class VideoCapture: #this will make a queue that reads the latests frames from the to eliminate delay
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3,1280)
        self.camera.set(4,720)
        self.q = Queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()
    
    def _reader(self):
        while True:
            ret, frame = self.camera.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()

vidCap = VideoCapture()
frame = vidCap.read()
gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)



aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()
corners, ids, rejectedImgPoints = aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
frame_markers = aruco.drawDetectedMarkers(frame.copy(),corners,ids)
test = "test0"
class requestHandler(BaseHTTPRequestHandler):
   
    def do_GET(self):
        global gray
        global corners
        global aruco_dict
        global ids
        try:
            if self.path=="/debug": #show an image with tracked tags for setup/debug
                self.send_response(200)
                self.send_header('Content-type','image/jpeg')
#                self.send_header('Content-type','text/html')
                self.end_headers()
                toSend = aruco.drawDetectedMarkers(frame.copy(),corners,ids)
                toSend = cv2.putText(toSend,"origin",(5,25),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2,cv2.LINE_AA)
                toSend = cv2.putText(toSend,"%d" % fps,(5,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2,cv2.LINE_AA)

#                jpeg = cv2.imencode('.jpg',frame) 
                self.wfile.write(bytearray(cv2.imencode('.jpg',toSend)[1]))
#                self.wfile.write(toSend[1])
            elif "track" in self.path:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                toSend = ""
#                for i in range(0,len(ids)):
#                    toSend = toSend + "," + str(int(ids[i]))
#                toSend = toSend[1:]
#                toSend = toSend + "<br>"
                for i in range(0,len(corners)):
                    toSend = toSend + str(int(ids[i]))+","
                    cornerArray = corners[i].flatten()
                    for n in range(0,len(cornerArray)):
                        toSend = toSend + str(cornerArray[n])+","
                    toSend = toSend[:-1] + "<br>"

                self.wfile.write(toSend);

        except Exception as e:
            print(str(e))


#plt.figure()

server = HTTPServer(('',80), requestHandler)
webThread = threading.Thread(target=server.serve_forever,name='web-thread');
webThread.daemon=True;
webThread.start()
num = 0
print("web started!")
while True:
        num = num + 1
        test = "test" + str(num)
        timestamp = time.time();
        fps = 1/(time.time()-prevTime);
        prevTime = timestamp
#        print(str(time.time()));
	frame = vidCap.read();
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
	frame_markers = aruco.drawDetectedMarkers(frame.copy(),corners,ids)
#        print("ids: " + str(ids));
#        print("corners: " + str(corners));

#	cv2.imshiow("live video", frame_markers)
#        cv2.waitKey(1)
        #if ids != None:
       # 	for i in range(len(ids)):
#	            c = corners[i][0]
		    #plt.plot([c[:,0].mean()],[c[:,1].mean()],"o",label = "id={0}".format(ids[i]))
#	plt.legend()
#	plt.show()
