import requests
import json

url = 'https://maps.googleapis.com/maps/api/geocode/json'
with open('campusbuildings_refined.json') as data_file:
    data = json.load(data_file)

with open('building_addresses.json') as data_file:
    building_addresses = json.load(data_file)

# with open('remain.json') as data_file:
#     data = json.load(data_file)

keys_list = data.keys()
print len(keys_list)
lat_lng = {}
kind = {}

# building = "Performing Arts Center, Austin, TX"
# params = {'sensor': 'false', 'address': building}
# r = requests.get(url, params=params)
# results = r.json()['results']
# location = results[0]['geometry']['location']
# print location['lat'], location['lng']
# print results[0]['geometry']['location_type']

for key in keys_list:
    try:
        building = building_addresses[key]
    except Exception, e:
        building = data[key] + ', Austin, TX'

    params = {'sensor': 'false', 'address': building}
    print key
    print building

    attempt = 0
    while attempt < 10:
        r = requests.get(url, params=params)
        attempt += 1
        try:
            results = r.json()['results']
            location = results[0]['geometry']['location']
            lat_lng[str(key)] = (location['lat'], location['lng'])
            kind[str(key)] = results[0]['geometry']['location_type']
            print kind[str(key)]
            break
        except Exception, e:
            pass

    # print kind[str(key)]

# with open('lat_lng.json', 'w') as fp:
#     json.dump(lat_lng, fp)
# with open('kind.json', 'w') as fp:
#     json.dump(kind, fp)

accurate_loc = {}
for key, value in kind.iteritems():
    # if value == 'ROOFTOP' or value == 'RANGE_INTERPOLATED':
    accurate_loc[key] = lat_lng[key]

with open('accurate_loc_new.json', 'w') as f:
    json.dump(accurate_loc, f)

all_buildings = set(keys_list)
remaining = all_buildings - set(accurate_loc.keys())
remain = {}
for b in remaining:
    remain[b] = data[b]

with open('remain_new.json', 'w') as f:
    json.dump(remain, f)

with open('kind.json', 'w') as f:
    json.dump(kind, f)
