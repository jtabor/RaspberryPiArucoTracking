#! /usr/bin/python
import requests
import time
import numpy as np

refresh_rate = .5
trackerIds = [1,2,5]; #center, x marker, y marker
trackerID = 7;

trackedArea_x = 4; #width of the tracked area
trackedArea_y = 3; #height of the tracked area

def getCenter(index,corner_array):
    x_ave = 0;
    y_ave = 0;
    cornerArray = corner_array[index];
    for i in range(0,len(cornerArray)/2):
        x_ave = cornerArray[i*2] + x_ave;
        y_ave = cornerArray[i*2+1] + y_ave;
    return np.array([x_ave/(len(cornerArray)/2),y_ave/(len(cornerArray)/2)])

def getProjectedCoords(center_location,x_location,y_location,valueToProject):
    valueToProject = np.subtract(valueToProject,center_location);
    x_vec = np.subtract(x_location,center_location)
    y_vec = np.subtract(y_location,center_location)
    x_hat = x_vec/np.linalg.norm(x_vec);
    y_hat = y_vec/np.linalg.norm(y_vec);
    x_meters = (np.dot(valueToProject,x_hat)/np.linalg.norm(x_vec))#*trackedArea_x;
    y_meters = (np.dot(valueToProject,y_hat)/np.linalg.norm(y_vec))#*trackedArea_y;
    return np.array([x_meters,y_meters]);

while True:
    r = requests.get('http://192.168.11.23/track')
    reply = r.text
    reply = reply.replace("<br>","\n",100)
    ids = []
    corners = []
    for line in reply.splitlines():
        oneDetect = line.split(',');
        ids.append(float(oneDetect[0]))
        cornerFloats = []
        for i in range(1,len(oneDetect)):
            cornerFloats.append(float(oneDetect[i]))
        corners.append(cornerFloats);
    try:
        centerIndex = ids.index(trackerIds[0]);
        leftIndex = ids.index(trackerIds[1]);
        rightIndex = ids.index(trackerIds[2]);
        trackedIndex = ids.index(trackerID);
        center_marker = getCenter(centerIndex,corners);
        x_marker = getCenter(leftIndex,corners);
        y_marker = getCenter(rightIndex,corners);
        tracker_marker = getCenter(trackedIndex,corners);
        tracked_pos = getProjectedCoords(center_marker,x_marker,y_marker,tracker_marker);
        print(str(tracked_pos))
    except ValueError:
        print("some markers missing")
    time.sleep(refresh_rate)


