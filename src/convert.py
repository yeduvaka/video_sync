import numpy as np
import math
import utm
import random

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


def recover_affine_transformation(p, p_prime):
    Q       = p[1:]       - p[0]
    Q_prime = p_prime[1:] - p_prime[0]

    # calculate rotation matrix
    R = np.dot(np.linalg.inv(np.row_stack((Q, np.cross(*Q)))),
               np.row_stack((Q_prime, np.cross(*Q_prime))))

    # calculate translation vector
    t = p_prime[0] - np.dot(p[0], R)

    # calculate affine transformation matrix
    return np.column_stack((np.row_stack((R, t)),
                            (0, 0, 0, 1)))


def transform_pt(point, trans_mat):
    a  = np.array([point[0], point[1], point[2], 1])
    ap = np.dot(a, trans_mat)[:3]
    return [ap[0], ap[1], ap[2]]


def sample_and_solve(gps_data, slam_data):
    while(True):
        try:
            gps_samples,slam_samples =  sample_three(gps_data, slam_data)
            utm_samples = []

            for i in xrange(0,3):
                u = list(utm.from_latlon(gps_samples[i][1], gps_samples[i][2]))[:2]
                u.append(0)
                utm_samples.append(u)

            slam_samples = np.around(slam_samples,5)
            trans_mat = recover_affine_transformation(np.array(slam_samples[:,1:4]),np.array(utm_samples))  

        except np.linalg.linalg.LinAlgError:
            print "Trying again!"
            continue

        break

    return trans_mat

def convert(gps_data, slam_data):
    A = sample_and_solve(gps_data, slam_data)
    slam_converted = np.zeros((len(slam_data),3))
    
    for i,obv in enumerate(slam_data):
        slam_converted[i][0] = obv[0]
        utm_conv = transform_pt(obv[1:],A)
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