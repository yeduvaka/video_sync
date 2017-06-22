#File to extract required attributes from Json files

#Extract attribute values from the json object (list of dicts)
def extract_attribute(j_object,attr):
    attr_values = []
    for i in xrange(0, len(j_object)):
        attr_values.append(j_object[i][attr])
    return attr_values


def object_init(filename):
    data = []
    with open(filename) as dfile:
        for line in dfile:
            data.append(json.loads(line))
    return data