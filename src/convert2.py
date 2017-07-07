import numpy as np
import math
import utm
import random


def sample(gps_data, slam_data):
    #Find all the reasonably accurate GPS points (between 0 and 5 meters)    
    start = np.searchsorted(gps_data[:,0],slam_data[0][0],'left')
    end = np.searchsorted(gps_data[:,0], slam_data[-1][0],'left')
    
    good_points = np.where(np.logical_and(gps_data[start:end,4] > 0, gps_data[start:end,4]<5))
    indices = good_points[0] + start
    #indices = np.array(random.sample(good_points[0],4)) + start

    corsp_slam = []
    for t in gps_data[:,0][indices]:
        idx = np.searchsorted(slam_data[:,0],t, 'left')
        corsp_slam.append(idx)

    return gps_data[indices][:,[0,2,3]], slam_data[corsp_slam]


def find_affine_transformation(p,p_prime):
    pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
    unpad = lambda x: x[:,:-1]
    X = pad(p)
    Y = pad(p_prime)

    A, res, rank, s = np.linalg.lstsq(X,Y)

    return A

def transform_pt(point,trans_mat):
    pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
    unpad = lambda x: x[:,:-1]
    transform = lambda x:unpad(np.dot(pad(x),trans_mat))
    return transform(point)


def sample_and_convert(gps_data, slam_data):
    gps_samples,slam_samples =  sample(gps_data, slam_data)

    utm_samples = []
    for i in xrange(0,len(gps_samples)):
        u = list(utm.from_latlon(gps_samples[i][1], gps_samples[i][2]))[:2]
        u.append(0)
        utm_samples.append(u)

    A = find_affine_transformation(np.array(slam_samples[:,1:4]),np.array(utm_samples))
    slam_converted = np.zeros((len(slam_data),3))
    utm_conv = transform_pt(slam_data[:,[1,2,3]],A)
    
    for i,obv in enumerate(slam_data):
        slam_converted[i][0] = obv[0]
        ### One and Three are the two axis aligned to the plane.
        gps_conv = utm.to_latlon(utm_conv[i][0], utm_conv[i][1],18, 'T')
        slam_converted[i][1:3] = gps_conv
    return slam_converted


def scale_and_combine(gps_data, slam_data):
    s1 = sample_and_convert(gps_data, slam_data)
    #s2 = sample_and_convert(gps_data, slam_data)
    #s3 = sample_and_convert(gps_data, slam_data)

    #final = (s1+s2+s3)/3
    return s1