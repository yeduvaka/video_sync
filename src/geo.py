
import math


class Geo:

    @staticmethod
    def space_nodes(nodes, spacing_m=0.0):
        """
        Space node list by spacing_m
        """
        spaced = []
        dangling = []
        last_node = None
        for node in nodes:
            cur_node = [node['longitude'], node['latitude']]
            if last_node is not None:
                meters = Geo.haversine(last_node, cur_node)
                if meters < spacing_m:
                    dangling.append(node)
                    continue
                else:
                    spaced.append(node)
            else:
                spaced.append(node)
            last_node = cur_node
        return spaced, dangling

    @staticmethod
    def calculate_bearing(point_a, point_b):
        if (type(point_a) != tuple) or (type(point_b) != tuple):
            raise TypeError("Only tuples are supported as arguments")

        lat1 = math.radians(float(point_a[1]))
        lat2 = math.radians(float(point_b[1]))

        diff_long = math.radians(float(point_b[0]) - float(point_a[0]))

        x = math.sin(diff_long) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) *
                                               math.cos(lat2) *
                                               math.cos(diff_long))

        initial_bearing = math.atan2(x, y)

        # Now we have the initial bearing but math.atan2 return values
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    @staticmethod
    def haversine(c1, c2, units="m"):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians,
                                     [float(c1[0]),
                                      float(c1[1]),
                                      float(c2[0]),
                                      float(c2[1])])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * (math.cos(lat2) *
                                                    math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        # Radius of earth in kilometers. Use 3956 for miles
        r = 6371
        m = (c * r) * 1000
        if units == 'km':
            return m / 1000
        return m