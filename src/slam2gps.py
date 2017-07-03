# Author: Aravind Yeduvaka
#File: slam2gps takes in a KeyFrameTrajectory(.txt) file and json file of the swarm video and converts the Slam co-ordinates
# to absolute GPS co-ordinates.

import numpy as np
import video_sync as vs
import utm
import math

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



#Pick three reasonably accurate GPS points
def sample_three(gps_data, slam_data):
    #Find all the reasonably accurate GPS points (between 0 and 5 meters)
    good_points = np.where(np.logical_and(gps_data[:,4] > 0, gps_data[:,4]<5))

    try:
        indices = np.random.random_integers(0, len(good_points),3)
    except IndexError:
        print "Couldn't find three accurate GPS data points!"

    corsp_slam = []
    for t in gps_data[indices][0]:
        idx = np.searchsorted(slam_data[:,0],t, 'left')
        if idx > 0 and (idx == len(slam_data[:,0]) or math.fabs(t - slam_data[:,0][idx - 1]) < math.fabs(t - slam_data[:,0][idx])):
            idx = idx -1
        corsp_slam.append(idx)

    return gps_data[indices][0,2,3], slam_data[corsp_slam]


def scale_and_combine(gps_data, slam_data):
    gps_samples,slam_samples = sample_three(gps_data,slam_data)

    #Eliminate one of the dimensions
    utm_samples = []
    for i in xrange(0,3):
        utm_samples.append(utm.from_latlon(gps_samples[i][1], gps_samples[i][2]))

    Bnot = np.linalg.inv(np.column_stack((utm_samples[0], utm_samples[1])))
    Xnot = np.linalg.inv(np.column_stack((slam_data[0][1:3], slam_data[1][1:3])))

    A = np.linalg.solve(Bnot,Xnot)
    Anot = np.linalg.inv(A)

    slam_converted = np.zeros(len(slam_data,3))

    for i,obv in enumerate(slam_data):
        slam_converted[i][0] = obv[0]
        ### One and Three are the two axis aligned to the plane.
        utm_conv = np.matmul(Anot, obv[1,3])
        gps_conv = utm.to_latlon(utm_conv[0], utm_conv[1],18, 'T')
        slam_converted[i][1:3] = gps_conv

    return slam_converted


def slam2gps(gps_raw, slam_raw):
    gps_data = extract_gps_data(gps_raw)
    slam_data = extract_slam_data(slam_raw)
    slam_data = time_sync(slam_data, gps_data)

    location_data_final = scale_and_combine(gps_data, slam_data)

    return location_data_final












