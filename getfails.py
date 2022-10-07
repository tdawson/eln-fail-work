#!/usr/bin/python3

import datetime
import json
import koji
import os
import requests
import rpm

WORK_DIR = os.getcwd()+"/"
TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
JSON_URL = "http://distrobuildsync-eln-ops.apps.stream.rdu2.redhat.com/status.json"
OUTPUT_FILE = "failed."+TODAY
OLD_FILE = "failed.last"
TAG = "eln"

# Get our data
print("Getting current status")
status_data = {}
status_data = json.loads(requests.get(JSON_URL, allow_redirects=True).text)
#with open('status.json', 'r') as jsonfile:
#  status_data = json.load(jsonfile)

old_data = {}
with open(OLD_FILE, 'r') as jsonfile:
  old_data = json.load(jsonfile)

print("Getting latest builds")
latest_input = {}
koji_session = koji.ClientSession('https://koji.fedoraproject.org/kojihub')
latest_input = koji_session.listTagged(TAG, latest=True)
#with open('latest.json', 'r') as jsonfile:
#  latest_input = json.load(jsonfile)
latest_builds = {}
for pkg in latest_input:
  latest_builds[pkg['package_name']]=pkg['nvr']

## tmp testing helpers
#print(dir(status_data))
#print(status_data['bash'])
#print()
#print(dir(status_data['bash']))
#print(status_data['bash']['status'])
#with open('latest.json','w') as output:
#  json.dump(latest_builds, output)
#print(latest_builds)

def rpm_compare(rpm1, rpm2):
  try:
    n1, v1, r1 = rpm1.rsplit('-', 2)
    n2, v2, r2 = rpm2.rsplit('-', 2)
    return rpm.labelCompare(('1', v1, r1), ('1', v2, r2))
  except ValueError:
    print("ERROR - bad names: " + rpm1 + " " + rpm2)

# Process data
print("Processing data")
checked_failures = {}
for json_entry in status_data:
  try:
    if status_data[json_entry]["status"] == "BuildStatus.FAILED":
      failed = True
      latest_nvr = latest_builds[json_entry]
      if '.fc3' in latest_nvr:
        # print(json_entry + " " + status_data[json_entry]["status"] + " " + status_data[json_entry]["nvr"] + " " + latest_nvr)
        #print(" FAIL - Rawhide package" + json_entry)
        pass
      else:
        test_result = rpm_compare(latest_nvr, status_data[json_entry]["nvr"])
        if test_result == 0:
          failed = False
          #print(" PASS - nvrs match " + json_entry)
        elif test_result == 1:
          failed = False
          #print(" PASS - latest is newer " + json_entry)
        elif test_result == -1:
          #print(" FAIL - latest is older " + json_entry)
          pass
        else:
          print(" ERROR - Something is wrong " + json_entry)
      if failed:
        this_failure = {}
        this_failure['name'] = json_entry
        this_failure['nvr'] = status_data[json_entry]["nvr"]
        try:
          this_failure['notes'] = old_data[json_entry]['notes']
        except:
          this_failure['notes'] = "NEW " + TODAY
          print("  NEW " + json_entry)
        checked_failures[json_entry] = this_failure
  except TypeError:
    pass

print("Total Failures: " + str(len(checked_failures)))
with open(OUTPUT_FILE, 'w') as output:
  json.dump(checked_failures, output, indent=4, sort_keys=True)
#    for sname in checked_failures:
#      output.write("%s %s\n" % (sname, checked_failures[sname]))
