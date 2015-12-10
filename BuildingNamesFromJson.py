__author__ = 'wenwen'
import json

with open('accurate_loc_new.json') as data_file:
    data = json.load(data_file)
keys_list = data.keys()
length = len(keys_list)
keys_list_modifiyed =[]

for key in keys_list:
    tmp_key = "<item>"+str(key)+"</item>"
    keys_list_modifiyed.append(tmp_key)
    print tmp_key

