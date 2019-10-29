#!/usr/bin/env python
import requests
import csv
import argparse
from config import *

### from internets, for arguments
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--api', help="pagerduty api token")
parser.add_argument('-f', '--file', help="csv filename with Services Name and Services Obfuscated ID fields")
parser.add_argument('-c', '--change', help="change to service 'feature:setting', eg 'alert_creation:create_incidents' or 'acknowledgement_timeout:1'")

args = parser.parse_args()
### ^ from internets, for arguments
# print out arguments for debugging
#print(args.api)
#print(args.file)
#print(args.change)

### Initialize required variables
# User can add API TOken here or use the -a commandline argument
apiToken = ''
# User can add services to change here, like so: services = ['PBUDURC','PR1POT7']
# or can add a csv file as an argument to the Script
services = []
# User can add what changes to make or use -c argument
# reference: https://api-reference.pagerduty.com/#!/Services/put_services_id
#changes = 'alert_creation:create_alerts_and_incidents'
changes = 'acknowledgement_timeout:60'
url = 'https://api.pagerduty.com/services/'
### ^ Initialize required variables

# Check that we have all of the required variables, if not then exit()
if not args.api and not apiToken:
    print("An API Token is required. either hardcode it in apiToken variable or use -a commandline argument.")
    exit()
if not args.file and not services:
    print("A list of Service IDs is required. Either hardcode in services variable or use -f commandline argument.")
    exit()
if not args.change and not changes:
    print("A feature to change is required. Either hardcode in changes variable or use -c commandline argument.")
    exit()
# if api argument then set apiToken
if args.api:
    apiToken = args.api
headers = { 'Content-Type': 'application/json', 'Accept': 'application/vnd.pagerduty+json;version=2', 'Authorization': 'Token token='+apiToken}
# if change argument then set changes
if args.change:
    changes = args.change
    #changes = str(args.change)

# if file argument then open file and extract Services Obfuscated ID
if args.file:
    ### from internets:
    # open the file in universal line ending mode
    with open(args.file, 'r') as infile:
      # read the file as a dictionary for each row ({header : value})
      reader = csv.DictReader(infile)
      data = {}
      for row in reader:
        for header, value in row.items():
          try:
            data[header].append(value)
          except KeyError:
            data[header] = [value]
    # print out what was read for debugging
    #print(data['Services Name'])
    #print(data['Services Obfuscated ID'])
    ### ^ from internets
    services = data['Services Obfuscated ID']
# print out Service IDs for debugging
#print(services)

### from internets
# extract values from request response for verification of succedd/failure
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results
#  print out the request being sent for verification purposes
def pretty_print_PUT(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))
### ^ from internets

# iterate through the service ids and send out api request to update service
try:
    for s in services:
        print('Updating service id: '+s)
        # send API  request
        r = requests.put(url+s, data=changes, headers=headers)
        # print some details for troubleshooting and to confirm success
        pretty_print_PUT(r.request)
        print('Status Code: {code}'.format(code=r.status_code))
        print('Changed ' + str(extract_values(r.json(), 'name')) + ' ' + changes.split(':')[0] + ' to ' + str(extract_values(r.json(), changes.split(':')[0])) + '\n\n')
except Exception as e:
    print(e)
