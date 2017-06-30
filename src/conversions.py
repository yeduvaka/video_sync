# calculations.py
# 


from math import radians, degrees, cos, sin, atan2


def calculate_heading(first_latlong, second_latlong):
        """
        Function written by David Boyle
        Given a pair of lat longs, calculate the heading of the edge
        """
        long1 = first_latlong[0]
        lat1 = first_latlong[1]
        long2 = second_latlong[0]
        lat2 = second_latlong[1]
        x_coord = cos(radians(lat2)) * sin(radians(long2-long1))
        y_coord = cos(radians(lat1)) * sin(radians(lat2)) - sin(radians(lat1))\
            * cos(radians(lat2)) * cos(radians(long2-long1))

        heading = 180 + degrees(atan2(x_coord, y_coord))
        return heading

def ft_to_latlong(distance, from_latlong, to_latlong):
	'''
	Given a curb distance (ft), heading direction (degrees),
	calculate the change of latlong of object from some origin.
	Based on the Matlab script: http://pordlabs.ucsd.edu/matlab/coord.htm 
	'''
	ft_to_m = 0.3048 #ft/m

	heading = calculate_heading(from_latlong,to_latlong)
	
	# Determining latitudinal coordinate change, dlat
	y = distance*cos(radians(heading))
	rlat = radians(from_latlong[0]+to_latlong[0])*0.5
	mlat = 111132.09 - 566.05 * cos(rlat+rlat) + 1.2 * cos(4*rlat)
	dlat = y * ft_to_m / mlat

	# Determining longitudinal coordinate change, dlong
	x = distance*sin(radians(heading))
	mlong = 111415.13 * cos(rlat) - 94.55 *cos(3*rlat)
	dlong  = x * ft_to_m / mlong

	final_latlong = [from_latlong[0] + dlat , from_latlong[1] + dlong]

	return final_latlong

