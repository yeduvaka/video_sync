import math
import os
import requests

from geo import Geo

OSRM_HOST = 'osrm-staging.carmera.co'
OSRM_PORT = '80'


base_url = 'http://{}:{}'.format(OSRM_HOST, OSRM_PORT)
urls = {
    'nearest': '/nearest/v1/driving/{},{}.json?radiuses={}',
    'match': ('/match/v1/driving/{}?radiuses={}'
              '&overview=full&geometries=geojson')
}
radius_m = 300
BEARING_RANGE = 20
GPS_MAX_ACCURACY = 100
GPS_MIN_ACCURACY = 10



def handle_response( resp):
    """
    Generic OSRM response handler
    """
    if resp.status_code != 200:
        msg = "OSRM HTTP {0}: {1}".format(resp.status_code, resp.content)
        print msg
        return False
    resp_json = resp.json()
    if 'code' not in resp_json:
        msg = 'OSRM RESPONSE: Missing \'code\' from JSON response.'
        print msg
        return False
    if resp_json['code'] != 'Ok':
        msg = ('OSRM RESPONSE: Code is NOT \'Ok\'. Code: \'{}\''
               .format(resp_json['code']))
        print msg
        return False
    return True

def chunk_it( l, n):
    return [l[x:x+n] for x in range(0, len(l), n)]

def get_corrected_accuracy(accuracy):
    """
    Convert GPS accuracy to within a minimun and maximum bounds set
    """
    if accuracy is None:
        accuracy = GPS_MAX_ACCURACY
    elif accuracy < GPS_MIN_ACCURACY:
        accuracy = GPS_MIN_ACCURACY
    elif accuracy > GPS_MAX_ACCURACY:
        accuracy = GPS_MAX_ACCURACY
    return accuracy

def parse_match_results(data, results, size):
    """
    Merge chunked result sets back together. And apply the haversine
    function to the old and new coordinate to get the distance error.
    data = everything
    """
    matched = []
    chunks = chunk_it(data, size)
    group = 0
    for chunk in chunks:
        # No matches at all
        if results[group] is None:
            for c in chunk:
                c['snapped_distance'] = -1
                c['snapped_lon'] = c['longitude']
                c['snapped_lat'] = c['latitude']
                c['snapped_name'] = None
                c['group'] = group
                matched.append(c)
        elif 'tracepoints' in results[group]:
            tps = results[group]['tracepoints']
            matched.extend(_handle_tracepoints(tps, chunk, group))
        group = group + 1
    return matched

def _handle_tracepoints(tracepoints, chunk, group):
    key = 0
    rows = []
    for point in tracepoints:
        row = chunk[key]
        if point is None:
            distance = -1
            lon = chunk[key]['longitude']
            lat = chunk[key]['latitude']
            name = None
        else:
            # Compare the RAW and snapped GPS
            c1 = tuple(point['location'])
            c2 = tuple([chunk[key]['longitude'],
                       chunk[key]['latitude']])
            distance = Geo.haversine(c1, c2)
            lon = point['location'][0]
            lat = point['location'][1]
            name = point['name']
        row['snapped_lon'] = lon
        row['snapped_lat'] = lat
        row['snapped_distance'] = distance
        row['snapped_name'] = name
        row['group'] = group
        rows.append(row)
        key = key + 1
    return rows

def smart_match(data, size=30, session=None):
    """
    Match cooridnates to road network. This method will automatically
    break the coordinates up into chunks of 10 and use the GPSs
    accuracy for given point to determine where it is on the road
    network.
    """
    size = int(size)
    if len(data) ==1:
        coord = data[0]
        res = snap_coords(coord['longitude'], coord['latitude'])
        results = []
        results.append({'tracepoints': [res]})
        return parse_match_results(data, results, size)

    def handle_last_point(last_chunk, chunk):
        # 1 coordinate isn't allowed in the match API. Loop through last
        # chunk until we find a coordinate 1 meter away and calculate
        # bearing off of that.
        point = chunk[0]
        c2 = tuple([point['longitude'], point['latitude']])
        for last in last_chunk:
            c1 = tuple([last['longitude'], last['latitude']])
            if Geo.haversine(c1, c2) >= 1:
                break
        bearing = Geo.calculate_bearing(c1, c2)
        res = snap_coords(point['longitude'],
                               point['latitude'],
                               bearing)
        return {'tracepoints': [res]}

    results = []
    if len(data) <= size:
        results.append(match(data))
    else:
        last_chunk = None
        for chunk in chunk_it(data, size):
            if len(chunk) > 1:
                m = match(chunk)
            else:
                # Handle single point left in chunking
                m = handle_last_point(last_chunk, chunk)
            results.append(m)
            last_chunk = chunk
    if len(results) == 0:
        return results
    parsed = parse_match_results(data, results, size)
    return parsed

def match(data):
    """
    Call Match API, expects a list({ latitude:,longitude:,accuracy })
    """
    coords = []
    radi = []
    for line in data:
        coords.append('{},{}'.format(line['longitude'],
                                     line['latitude']))
        accuracy = get_corrected_accuracy(line['accuracy'])
        radi.append('{}'.format(accuracy))
    coords = ';'.join(coords)
    radi = ';'.join(radi)
    path = urls['match'].format(coords, radi)
    try:
        resp = requests.get('{}{}'.format(base_url, path))
    except Exception as e:
        return None
    if handle_response(resp) is False:
        return None
    return resp.json()

def snap_coords(lon, lat, bearing=None, brange=None):
    """
    For given lon + lat, query OSRM server for nearest road
    snapped road location.
    """
    url =base_url + urls['nearest'].format(lon,
                                                      lat,
                                                      radius_m)
    if bearing is not None:
        if brange is None:
            brange = BEARING_RANGE
        url = '{}&bearings={},{}'.format(url,
                                         math.floor(bearing),
                                         brange)
    try:
        resp = requests.get(url)
    except Exception as e:
        return None
    if handle_response(resp)is False:
        return None

    resp_json = resp.json()

    if len(resp_json['waypoints']) == 0:
        msg = "OSRM RESPONSE: No waypoints in response."
        return None

    return {
        'location': resp_json['waypoints'][0]['location'],
        'distance': resp_json['waypoints'][0]['distance'],
        'name': resp_json['waypoints'][0]['name']
    }