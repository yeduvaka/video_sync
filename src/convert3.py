import numpy as np
import math
import utm
import random
import cv2

def sample_three(gps_data, slam_data):
    #Find all the reasonably accurate GPS points (between 0 and 5 meters)    
    start = np.searchsorted(gps_data[:,0],slam_data[0][0],'left')
    end = np.searchsorted(gps_data[:,0], slam_data[-1][0],'left')
    
    good_points = np.where(np.logical_and(gps_data[start:end,4] > 0, gps_data[start:end,4]<10))
    indices = np.array(random.sample(good_points[0],3)) + start

    corsp_slam = []
    for t in gps_data[:,0][indices]:
        idx = np.searchsorted(slam_data[:,0],t, 'left')
        corsp_slam.append(idx)

    return gps_data[indices][:,[0,2,3]], slam_data[corsp_slam]


def transform_pt(point, trans_mat):
    a  = np.array([point[0], point[1], point[2], 1])
    ap = np.dot(a, trans_mat)[:3]
    return [ap[0], ap[1], ap[2]]

def best_three(gps_data, slam_data):
    start = np.searchsorted(gps_data[:,0],slam_data[0][0],'left')
    end = np.searchsorted(gps_data[:,0], slam_data[-1][0],'left')
    
    good_points = gps_data[start:end,4].argsort()[:3]
    indices = start + good_points

    corsp_slam = []
    for t in gps_data[:,0][indices]:
        idx = np.searchsorted(slam_data[:,0],t, 'left')
        corsp_slam.append(idx)

    return gps_data[indices][:,[0,2,3]], slam_data[corsp_slam]

def sample_and_solve(gps_data, slam_data):
    while(True):
        try:
            gps_samples,slam_samples =  best_three(gps_data, slam_data)
            utm_samples = []

            for i in xrange(0,3):
                u = list(utm.from_latlon(gps_samples[i][1], gps_samples[i][2]))[:2]
                utm_samples.append(u)

            trans_mat = cv2.getAffineTransform(np.float32(slam_samples[:,[1,3]]),np.float32(utm_samples))
        except np.linalg.linalg.LinAlgError:
            print "Trying again!"
            continue
        break

    return trans_mat

def convert(gps_data, slam_data):
    A = sample_and_solve(gps_data, slam_data)
    slam_converted = np.zeros((len(slam_data),3))
    #utm_conv = cv2.transform(np.float32(slam_data[:,[1,3]]),A)
    
    for i,obv in enumerate(slam_data):
        slam_converted[i][0] = obv[0]
        utm_conv = np.matmul(A,np.array([obv[1], obv[3],1]))
        gps_conv = utm.to_latlon(utm_conv[0], utm_conv[1],18, 'T') 
        slam_converted[i][1] = round(gps_conv[0],7)
        slam_converted[i][2] = round(gps_conv[1],7)

    return slam_converted

def scale_and_combine(gps_data, slam_data):
    s1 = convert(gps_data, slam_data)
    #s2 = convert(gps_data, slam_data)
    #s3 = convert(gps_data, slam_data)

    #final = (s1+s2+s3)/3

    return s1