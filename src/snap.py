
from mapbox import MapMatcher
from geojson import Feature, LineString
import geojson
from math import ceil
import numpy as np
import sys

token = "pk.eyJ1IjoieWVkdXZha2EiLCJhIjoiY2o1OG8yOWE3MWcwbDJxcjB6d28yaXpyaCJ9.Qks_4si0WhJCE2psV3zL0w"

def SaveSnappedData(location_data_final,jsonfile):
    file = open(jsonfile[:-4]+"-snap.txt",'w')
    for x in location_data_final:
            file.write(str(x[1]) + "," + str(x[0]) + "\n" )

def snap_gps(slam_converted):
    service = MapMatcher(access_token=token)
    coords, coordTimes = restrict_points(slam_converted)
    properties = {"coordTimes":coordTimes}
    route = Feature(geometry=coords,properties=properties)
    result = service.match(route, profile='mapbox.driving')
    new_path = result.geojson()['features'][0]
    new_path = list(geojson.utils.coords(new_path))
    return new_path

def restrict_points(slam_converted):
    slam_restricted = [(round(slam_converted[i][2],7),round(slam_converted[i][1],7)) for i in xrange(0,len(slam_converted),4)]
    time_restricted = [round(slam_converted[i][0],2) for i in xrange(0,len(slam_converted),4)]
    slam_restricted = LineString(slam_restricted)
    return slam_restricted,time_restricted

def snap_slam(slam_file):    
    service = MapMatcher(access_token=token)
    f = open(slam_file,'r')
    snapped = []
    data = []
    print slam_file
    for line in f:
        x = np.float32(line.split(','))
        data.append((np.asscalar(x[1]),np.asscalar(x[0])))

        if len(data) % 100== 0 and len(data) != 0:
            route = Feature(geometry=LineString(data))
            result = service.match(route, profile='mapbox.driving')
            new_path = result.geojson()['features'][0]
            new_path = list(geojson.utils.coords(new_path))
            snapped.extend(new_path)
            data = new_path[-5:]

    SaveSnappedData(snapped,slam_file)


def main():
    slam_file = sys.argv[1]
    snap_slam(slam_file)

if __name__ == '__main__':
    main()





