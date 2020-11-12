#! /usr/bin/python
import numpy as np
import cv2
import PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sys
import threading
import io
import pickle
import Queue

fps = 0
prevTime = 0;

cam_matrix = pickle.load(open("cam_matrix.p","rb"));
dist_matrix = pickle.load(open("dist_matrix.p","rb"));


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
                if(len(corners) > 0):
                    for i in range(0,len(corners)):
                        ret =  aruco.estimatePoseSingleMarkers(corners[i],.1016,cam_matrix,dist_matrix);
                        (rot_vec,trans_vec) = (ret[0][0,0,:],ret[1][0,0,:]);
                        axis = np.float32([[4,0,0],[0,4,0],[0,0,-4]]).reshape(-1,3);
                        imgpts, jac = cv2.projectPoints(axis,rot_vec,trans_vec,cam_matrix,dist_matrix);
                        toSend = aruco.drawAxis(toSend,cam_matrix,dist_matrix,rot_vec,trans_vec,.1);
                self.wfile.write(bytearray(cv2.imencode('.jpg',toSend)[1]))
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
            elif "3D" in self.path:
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
                    
                    if(len(corners) > 0):
                        ret = aruco.estimatePoseSingleMarkers(corners[i],.1016,cam_matrix,dist_matrix);
                        (rot_vec,trans_vec) = (ret[0][:],ret[1][0][0][:]);
                        axis = np.float32([[4,0,0],[0,4,0],[0,0,-4]]).reshape(-1,3);
                        imgpts, jac = cv2.projectPoints(axis,rot_vec,trans_vec,cam_matrix,dist_matrix);
                        toSend = toSend + str(trans_vec[0]) + "," + str(trans_vec[1]) + "," + str(trans_vec[2])
                        toSend = toSend + "<br>"

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
