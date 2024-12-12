import csv
import glob
import json

for csvfile in glob.glob("linkedin-profile/*.csv"):
    jsondoc = []
    with open(csvfile, 'r') as read_file:
        header = read_file.readline().strip().split(',')
        reader = csv.DictReader(read_file, fieldnames=header)
        jsonfile = open(csvfile.replace('csv', 'json'), 'w')
        for row in reader:
            jsondoc.append(row)
            
    json.dump(jsondoc, jsonfile, indent=2)
