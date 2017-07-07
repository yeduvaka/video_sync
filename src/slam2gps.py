# Author: Aravind Yeduvaka
#File: slam2gps takes in a KeyFrameTrajectory(.txt) file and json file of the swarm video and converts the Slam co-ordinates
# to absolute GPS co-ordinates.

import sys
import preprocess as pp
import convert2 as cvt


def SaveSlamData(location_data_final,jsonfile):
    file = open(jsonfile[:-5]+"-slam.txt",'w')
    for run in location_data_final:
        for x in run:
            file.write(str(x[1]) + "," + str(x[2]) + "\n" )

def SaveGPSData(gps_data, jsonfile):
    file = open(jsonfile[:-5] + "-gps.txt", 'w')
    for x in gps_data: 
        file.write(str(x[2]) + "," +str(x[3]) + "\n")


def slam2gps():   
    jsonfile = sys.argv[1]
    frametrajectory = sys.argv[2]

    gps_data, slam_runs = pp.preprocess(jsonfile, frametrajectory)
    
    location_data_final = []

    for slam_data in slam_runs:
        if len(slam_data) > 50:        
            slam_converted = cvt.scale_and_combine(gps_data, slam_data)
            location_data_final.append(slam_converted)

    SaveSlamData(location_data_final, jsonfile)
    SaveGPSData(gps_data,jsonfile)

    return True

if __name__ == '__main__':
    slam2gps()









