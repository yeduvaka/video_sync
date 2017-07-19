# Author: Aravind Yeduvaka
#File: slam2gps takes in a KeyFrameTrajectory(.txt) file and json file of the swarm video and converts the Slam co-ordinates
# to absolute GPS co-ordinates.

import sys
import preprocess as pp
import convert2 as cvt
import subprocess
import snap



def SaveSlamData(location_data_final,jsonfile):
    file = open(jsonfile[:-5]+"-slam.txt",'w')
    for x in location_data_final:
        file.write(str(x[1]) + "," + str(x[2]) + "\n" )

def SaveGPSData(gps_data, jsonfile):
    file = open(jsonfile[:-4] + "-gps.txt", 'w')
    for x in gps_data: 
        #"," +str(x[4]) +
        file.write(str(x[2]) + "," +str(x[3]) + "\n")

def SaveKeyFrame(jsonfile):
    filename = jsonfile[:-5] + "-keyframe.txt"
    cmd = ["mv", "/home/carmera/KeyFrame-test.txt", filename]
    subprocess.call(cmd)


def slam2gps():   
    jsonfile = sys.argv[1]
    frametrajectory = sys.argv[2]

    gps_data, slam_runs = pp.preprocess(jsonfile, frametrajectory)
    location_data_final = []
    snapped_data = []

    for slam_data in slam_runs:
        if len(slam_data) > 30:        
            slam_converted = cvt.scale_and_combine(gps_data, slam_data)
            #slam_snap = snap.snap_gps(slam_converted)
            if len(slam_converted) > 1:
                location_data_final.extend(slam_converted)
                #snapped_data.append(slam_snap)

    SaveSlamData(location_data_final, jsonfile)
    SaveGPSData(gps_data,jsonfile)
    #snap.SaveSnappedData(snapped_data,jsonfile)
    if len(sys.argv) < 4:
        SaveKeyFrame(jsonfile)

    return True

if __name__ == '__main__':
    slam2gps()









