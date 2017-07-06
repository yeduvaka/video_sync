# Author: Aravind Yeduvaka
#File: slam2gps takes in a KeyFrameTrajectory(.txt) file and json file of the swarm video and converts the Slam co-ordinates
# to absolute GPS co-ordinates.
import numpy as np
import video_sync as vs
import utm
import math
import random
import sys

def extract_gps_data(jsonfile):
    data = vs.object_init(jsonfile)
    lat = vs.extract_attribute(data,"latitude")
    lon = vs.extract_attribute(data,"longitude")
    acc = vs.extract_attribute(data,"accuracy")
    time = np.array(vs.extract_attribute(data,"timestamp"))/1000
    frame = vs.extract_attribute(data, "frame")

    data_final = np.column_stack((time,frame,lat,lon,acc))
    return data_final

def extract_slam_data(trajectory):
    f = open(trajectory, "r")
    runs = []
    data = []
    for i,line in enumerate(f):
        if line == "################################################## \n":
            if len(data) != 0:
                runs.append(np.array(data,dtype='float'))
                data = []
        else:
            l = line.split(" ")
            data.append(l[0:4])
    runs.append(np.array(data,dtype='float'))
    return runs

def time_sync(gps_data, slam_runs):
    t1 = gps_data[0][0]
    t2 = slam_runs[0][0][0]

    offset = t2 - t1
    for slam_data in slam_runs:
        slam_data[:,0] = slam_data[:,0] - offset

    return slam_runs

def find_affine_transformation(p, p_prime):
    '''
    Find the unique homogeneous affine transformation that
    maps a set of 3 points to another set of 3 points in 3D
    space:

        p_prime == np.dot(p, R) + t

    where `R` is an unknown rotation matrix, `t` is an unknown
    translation vector, and `p` and `p_prime` are the original
    and transformed set of points stored as row vectors:

        p       = np.array((p1,       p2,       p3))
        p_prime = np.array((p1_prime, p2_prime, p3_prime))

    The result of this function is an augmented 4-by-4
    matrix `A` that represents this affine transformation:

        np.column_stack((p_prime, (1, 1, 1))) == \
            np.dot(np.column_stack((p, (1, 1, 1))), A)

    Source: https://math.stackexchange.com/a/222170 (robjohn)
    '''

    # construct intermediate matrix
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

def sample_three(gps_data, slam_data):
    #Find all the reasonably accurate GPS points (between 0 and 5 meters)    
    start = np.searchsorted(gps_data[:,0],slam_data[0][0],'left')
    end = np.searchsorted(gps_data[:,0], slam_data[-1][0],'left')
    
    good_points = np.where(np.logical_and(gps_data[start:end,4] > -1, gps_data[start:end,4]<20))
    indices = np.array(random.sample(good_points[0],3)) + start
    corsp_slam = []
    for t in gps_data[indices][:,0]:
        idx = np.searchsorted(slam_data[:,0],t, 'left')
        corsp_slam.append(idx)

    return gps_data[indices][:,[0,2,3]], slam_data[corsp_slam]


def sample_once(gps_data, slam_data):
    while(True):
        try:
            gps_samples,slam_samples =  sample_three(gps_data, slam_data)
            utm_samples = []
            for i in xrange(0,3):
                u = list(utm.from_latlon(gps_samples[i][1], gps_samples[i][2]))[:2]
                u.append(0)
                utm_samples.append(u)
            slam_samples = np.around(slam_samples,5)
            A = find_affine_transformation(np.array(slam_samples[:,1:4]),np.array(utm_samples))  
        except np.linalg.linalg.LinAlgError:
            print "Trying again!"
            continue
        break
    return A

def sample_and_convert(gps_data, slam_data):
    A = sample_once(gps_data, slam_data)
    slam_converted = np.zeros((len(slam_data),3))
    
    for i,obv in enumerate(slam_data):
        slam_converted[i][0] = obv[0]
        utm_conv = transform_pt(obv[1:],A)
        gps_conv = utm.to_latlon(utm_conv[0], utm_conv[1],18, 'T') 
        slam_converted[i][1] = round(gps_conv[0],7)
        slam_converted[i][2] = round(gps_conv[1],7)

    return slam_converted

def scale_and_combine(gps_data, slam_data):
    s1 = sample_and_convert(gps_data, slam_data)
    s2 = sample_and_convert(gps_data, slam_data)
    s3 = sample_and_convert(gps_data, slam_data)

    final = (s1+s2+s3)/3

    return s1

def slam2gps():   
    jsonfile = sys.argv[1]
    frametrajectory = sys.argv[2]
    gps_data = extract_gps_data(jsonfile)
    slam_runs = extract_slam_data(frametrajectory)
    slam_runs= time_sync(gps_data,slam_runs)
    
    location_data_final = []
    file = open(jsonfile[:-5]+"-slam.txt",'w')
    file2 = open(jsonfile[:-5] + "-gps.txt", 'w')

    for slam_data in slam_runs:
        if len(slam_data) > 50:        
            slam_converted = scale_and_combine(gps_data, slam_data)
            location_data_final.append(slam_converted)

    for x in gps_data:
        file2.write(str(x[2]) + "," +str(x[3]) + "\n")

    for run in location_data_final:
        for x in run:
            file.write(str(x[1]) + "," + str(x[2]) + "\n" )

if __name__ == '__main__':
    slam2gps()









