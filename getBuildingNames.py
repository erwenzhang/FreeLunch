# from numpy import loadtxt
import json

txtfile = 'campus.txt'
buildings = {}

def main():
    lines = open(txtfile, 'r')
    for line in lines:
        if len(line) > 2:
            abbr = line[4:7]
            buildings[abbr] = line[8:-1] # last one is '\n', just ignored

    # with open('campusbuildings.json', 'w') as fp:
    #     json.dump(buildings, fp)
    print len(buildings)

if __name__ == '__main__':
    main()
