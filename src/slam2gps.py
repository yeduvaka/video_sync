# Author: Aravind Yeduvaka
#File: slam2gps takes in a KeyFrameTrajectory(.txt) file and json file of the swarm video and converts the Slam co-ordinates
# to absolute GPS co-ordinates.

import numpy as np
import json
import video_sync as vs

def extract_gps_data(jsonfile):
    data = vs.object_init(jsonfile)
    lat = vs.extract_attribute(data,"latitude")
    lon = vs.extract_attribute(data,"longitude")
    acc = vs.extract_attribute(data,"accuracy")
    time = vs.extract_attribute(data,"timestamp")
    frame = vs.extract_attribute(data, "frame")

    data_final = np.column_stack((time,frame,lat,lon,acc))
    return data_final


def extract_slam_data(trajectory):
    f = open(trajectory, "r")
    count = sum(1 for line in f)
    f = open(trajectory, "r")

    data = np.zeros((count,4))

    for i,line in enumerate(f):
        l = line.split(" ")
        data[i] = l[0:4]
    return data

def time_sync(gps_data, slam_data):
    t1 = gps_data[0][0]
    t2 = gps_data[0][0]

    offset = t2 - t1
    slam_data[:,0] = slam_data[:,0] - offset

    return gps_data, slam_data

def 






