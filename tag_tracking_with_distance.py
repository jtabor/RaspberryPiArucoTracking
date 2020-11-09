#! /usr/bin/python
import numpy as np
import cv2
import PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import pickle

    

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280);
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,960);

plt.figure()

cam_matrix = pickle.load(open("cam_matrix.p","rb"))
dist_matrix = pickle.load(open("dist_matrix.p","rb"))

while True:
        retval, frame = camera.read()
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        print(gray.shape)
	aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
	parameters = aruco.DetectorParameters_create()
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
        if (len(corners) > 0):
            rot_vec, trans_vec, _ = aruco.estimatePoseSingleMarkers(corners,.1016,cam_matrix,dist_matrix);
            axis = np.float32([[4,0,0],[0,4,0],[0,0,-4]]).reshape(-1,3)
            imgpts, jac = cv2.projectPoints(axis,rot_vec,trans_vec,cam_matrix,dist_matrix);
            print(imgpts)
            frame = aruco.drawAxis(frame,cam_matrix,dist_matrix,rot_vec,trans_vec,.1)
            #frame = draw(frame,corners,imgpts)
            print("Rotation Vector:" )
            print(rot_vec)
            print ("translation vector: ")
            print(trans_vec)
            frame = cv2.putText(frame,"X: " + str(trans_vec[0][0][0]) + " Y: " + str(trans_vec[0][0][1]) + " Z: " + str(trans_vec[0][0][2]),(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),4)
        frame_markers = aruco.drawDetectedMarkers(frame.copy(),corners,ids)
	cv2.imshow("live video", frame_markers)
        cv2.waitKey(1)
