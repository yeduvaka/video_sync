import json
import numpy as np

def object_init(filename):
    data = []
    with open(filename) as dfile:
        for line in dfile:
            data.append(json.loads(line))
    return data

def extract_attribute(j_object,attr):
    attr_values = []
    for i in xrange(0, len(j_object)):
        attr_values.append(j_object[i][attr])
    return attr_values


def extract_gps_data(jsonfile) :
    data = object_init(jsonfile)
    lat = extract_attribute(data,"latitude")
    lon = extract_attribute(data,"longitude")
    acc = extract_attribute(data,"accuracy")
    time = np.array(extract_attribute(data,"timestamp"))/1000
    frame = extract_attribute(data, "frame")

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

def preprocess(jsonfile, frametrajectory):
    gps_data = extract_gps_data(jsonfile)
    slam_runs = extract_slam_data(frametrajectory)
    slam_runs= time_sync(gps_data,slam_runs)

    return gps_data, slam_runs
