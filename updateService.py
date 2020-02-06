#!/usr/bin/env python
import requests
import csv
import argparse
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--api', help="pagerduty api token")
parser.add_argument('-f', '--file', help="csv filename with Services Name and Services Obfuscated ID fields")
parser.add_argument('-o', '--object', help="object to change. eg service, escalation policy, etc")
parser.add_argument('-c', '--change', help="change to service 'feature:setting', eg 'alert_creation:create_incidents' or 'acknowledgement_timeout:1'")
parser.add_argument('-d', '--debug', dest='debug', action='store_true')
args = parser.parse_args()

debug = False
### Initialize required variables
# User can add API Token here or use the -a commandline argument
apiToken = ''
# User can add services to change here, like so: services = ['PBUDURC','PR1POT7']
# or can add a csv file as an argument to the Script
services = []
# User can add what changes to make or use -c argument
serviceNames = []
# reference: https://api-reference.pagerduty.com/#!/Services/put_services_id
changes = 'alert_creation:create_alerts_and_incidents'
#changes = 'acknowledgement_timeout:60'
object = ''
### ^ Initialize required variables


# Check that we have all of the required variables, if not then exit()
if not args.api and not apiToken:
    print("An API Token is required. either hardcode it in apiToken variable or use -a commandline argument.")
    exit()
else:
    apiToken = args.api
if args.change:
    changes = args.change
if args.debug:
    debug = True

headers = { 'Content-Type': 'application/json', 'Accept': 'application/vnd.pagerduty+json;version=2', 'Authorization': 'Token token='+apiToken}

# if file argument then open file and extract Services Obfuscated ID
if args.file:
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

    services = data['Services Obfuscated ID']

if args.object:
    print (args.object)
    object = args.object
else:
    object = 'services'

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

# Function for a Yes/No result based on the answer provided as an arguement
def yes_no(answer):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])

    while True:
        choice = input(answer).lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           print ("Please respond with 'yes' or 'no'")

url = 'https://api.pagerduty.com/'+object+'/'
print (url)
### This is from experiments.py
responseJson = requests.get(url, headers=headers).json()
print('\nCurrent service settings: ')
for s in responseJson[object]:
    ### Previously printed a few interesting settings, not print only change to be made
    #print(s['id'] + " : " + s['name'] + " -> " + s['alert_creation'] + " , " + str(s['acknowledgement_timeout'])  + " , " + str(s['auto_resolve_timeout']))
    print(s['id'] + " : " + s['name'] + " -> " + str(changes.split(':')[0]) + " = " + str(s[changes.split(':')[0]]))
    if str(s[changes.split(':')[0]]) != str(changes.split(':')[1]):
        services.append(str(s['id']))
        serviceNames.append(str(s['name']))
print ('\nMaking changes to these services: ')
for (s, n) in zip(services, serviceNames):
    print(s + " -> " +n)
if not yes_no('\nContinue? '):
    exit()
else:
    print ('\n')
### ^^^ This is from experiments.py
# iterate through the service ids and send out api request to update service
try:
    for (s, n) in zip(services, serviceNames):
        print('Updating service id: '+s + " -> " +n)
        # send API  request
        if not debug:
            r = requests.put(url+s, data=changes, headers=headers)



            # print some details for troubleshooting and to confirm success
            print('Status Code: {code}'.format(code=r.status_code))
            print('Changed ' + str(extract_values(r.json(), 'name')) + ' ' + changes.split(':')[0] + ' to ' + str(extract_values(r.json(), changes.split(':')[0])))
            print('-----------------------------------------------\n')
except Exception as e:
    print(e)
