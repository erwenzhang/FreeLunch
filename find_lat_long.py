import requests
import json

url = 'https://maps.googleapis.com/maps/api/geocode/json'
with open('campusbuildings_refined.json') as data_file:    
    data = json.load(data_file)
keys_list = data.keys()
length = len(keys_list)
print length
lat_long = {}
kind = {}

building = "1 E 26-1/2th St, Austin TX, 78705"
params = {'sensor': 'false', 'address': building}
r = requests.get(url, params=params)
results = r.json()['results']
location = results[0]['geometry']['location']
print location['lat'], location['lng']
print results[0]['geometry']['location_type']

# for key in keys_list:
# 	building = str(data[key])+", UT Austin, Texas"
# 	params = {'sensor': 'false', 'address': building}
# 	print key
# 	print building
# 	r = requests.get(url, params=params)
# 	results = r.json()['results']
# 	#print results
# 	location = results[0]['geometry']['location']
# 	print location['lat'], location['lng']
# 	print results[0]['geometry']['location_type']

# 	lat_long[str(key)] = (location['lat'], location['lng'])
# 	kind[str(key)] = results[0]['geometry']['location_type']

# with open('result1.json', 'w') as fp:
#     json.dump(lat_long, fp)
# with open('result2.json', 'w') as fp:
#     json.dump(kind, fp)