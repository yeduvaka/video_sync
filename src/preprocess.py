import json
import numpy as np
import psycopg2 as psql

hostname='localhost'
username='carmera'
password='carmera123'
database='carmera'

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

    start_frame = 0
    for i in xrange(0, len(frame)):
        if   0 < frame[i] < 100:
            start_frame = i
            break

    data_final = np.column_stack((time[start_frame:],frame[start_frame:],lat[start_frame:],lon[start_frame:],acc[start_frame:]))
    return data_final

def extract_gps_from_sensor_data(jsonfile):
    video = jsonfile.split('/')[-1]
    conn = psql.connect(host=hostname, user=username, password=password,dbname= database)
    cur = conn.cursor()
    cmd =  "SELECT extract(epoch FROM timestamp),frame_number,st_y(snapped_location), st_x(snapped_location),accuracy FROM sensor_data WHERE filename='" + video + "'"
    cur.execute(cmd)
    data = cur.fetchall()
    data = np.array(data)

    start_frame = 0
    for i in xrange(0, len(data)):
        if   0 < data[i,1] < 100:
            start_frame = i
            break

    return data[start_frame:]


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
            ## Discarding the y-coordinate, might need to change this.
            l[2] = 0
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
    #gps_data = extract_gps_data(jsonfile)
    gps_data = extract_gps_from_sensor_data(jsonfile)
    slam_runs = extract_slam_data(frametrajectory)
    slam_runs= time_sync(gps_data,slam_runs)

    return gps_data, slam_runs
