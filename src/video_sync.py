import numpy as np
import cv2
import sys
import subprocess
import MySQLdb
import json


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

def get_timeoffset(jsonfile1, jsonfile2):
    db = MySQLdb.connect('localhost','root','carmera123','db_pings')

    v1 = object_init(jsonfile1)
    v2 = object_init(jsonfile2)

    t1 = extract_attribute(v1, "timestamp")[0]/1000
    t2 = extract_attribute(v2, "timestamp")[0]/1000

    f1 = extract_attribute(v1, "file")[0]
    f2 = extract_attribute(v2, "file")[0]

    sensor_id1 = f1.split('-')[1]
    sensor_id2 = f2.split('-')[1]

    cur = db.cursor()

    cmd1 = "SELECT * FROM raw_pings WHERE (" + "sensor_id=\'" + str(sensor_id1)
    cmd1 += "\'" + " AND timestamp>" + str(t1 - 100000)
    cmd1 += " AND timestamp<" + str(t1)
    cmd1 += " AND json_blob LIKE \'%POWER_CHANGE%\') ORDER BY timestamp ASC LIMIT 1"


    cmd2 = "SELECT * FROM raw_pings WHERE (" + "sensor_id=\'" + str(sensor_id2)
    cmd2 += "\'" + " AND timestamp>" + str(t2 - 100000)
    cmd2 += " AND timestamp<" + str(t2)
    cmd2 += " AND json_blob LIKE \'%POWER_CHANGE%\') ORDER BY timestamp ASC LIMIT 1"

    res1 = cur.execute(cmd1)[1]
    res2 = cur.execute(cmd2)[1]

    return res1-res2

def extract_images(file1, offset1, file2, offset2):
    cmd1 = ["ffmpeg", "-ss", str(offset1/1000),"-t", str(30), "-i", str(file1),"-r",
            "15.0","img-%4d.jpg"]
    cmd2 = ["ffmpeg", "-ss", str(offset2/1000),"-t", str(30), "-i", str(file2),"-r",
            "15.0","img-%4d_.jpg"]
    subprocess.call(cmd1)
    subprocess.call(cmd2)



def main():
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    vid1 = cv2.VideoCapture(file1)
    vid2 = cv2.VideoCapture(file2)

    fps = 15    # int(vid.get(cv2.cv.CV_CAP_PROP_FPS))

    for i in xrange(0, 2*fps):
        ret, img = vid1.read()
    off1 = vid1.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    off2 = closest(img, vid2)

    extract_images(file1,off1, file2, off2)
    return True


if __name__ == "__main__": main()
