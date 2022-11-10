#!/usr/bin/env python

"""This python script requests all sampled finding data for a specific company via the BitSight "GET: Finding Details"
api endpoint and writes it to a CSV file.

This is primarily useful when there are over 9,000 findings and the export option on the web page is disabled. The
documentation for the api endpoint being used can be found at this link:
https://help.bitsighttech.com/hc/en-us/articles/360022913734-GET-Finding-Details

To run, download script, execute script, provide company guid and api token, and an export file will be created in the
same directory as the script file.

Please note, the recordCount is set to 5000 and unsampled is set to false. You can adjust these values below if needed.
If the script is timing out, then reducing the recordCount should help as the server response should be faster."""

import requests
import math
import time
import os
import sys

# variables, adjust if needed
recordCount = 5000 # decrease if api requests are timing out
unsampledQ = 'false' # set to true to get unsampled data as well

# collect user input
companyGuidInput = input("Please enter the target company GUID: ")
apiTokenInput = input("Please enter your admin api token: ")

# variables, do NOT adjust
cwd = os.getcwd()
fieldsQ = 'risk_vector_label,evidence_key,first_seen,last_seen,details.grade,affects_rating,remaining_decay,severity_category,assets.category,assets.asset,details.details_summary,comments,details.country'
payload = {'limit': recordCount, 'offset': 0, 'affects_rating': 'true', 'unsampled': unsampledQ, 'sort': '-last_seen', 'fields': fieldsQ}
payloadr2 = {'limit': '1', 'affects_rating': 'true', 'unsampled': unsampledQ}
authValues = (apiTokenInput, 'blank_password')
head = {'accept': "text/csv"}
apiEndpoint = 'https://api.bitsighttech.com/ratings/v1/companies/'+companyGuidInput+'/findings'

# print initial script message
print('\n' + "Requesting data batch #1 from api... (offset: 0)")

# request finding data in text format
r = requests.get(url=apiEndpoint, auth=authValues, params=payload, headers=head)
# request json data from endpoint for only one finding, so we can get the total count of findings
r2 = requests.get(url=apiEndpoint, auth=authValues, params=payloadr2, headers=None)

# display error if api calls fail
r.raise_for_status()
r2.raise_for_status()

# create variable to find how many loops are needed for the full data export
modulus = math.ceil(r2.json()['count']/recordCount)

# print http status code, total number of findings, and loops needed
print("Request completed: ", r, "| Total findings " + str(r2.json()['count']), "|", "Batches required " + str(modulus))

# open file to write data, creates file if it does not exist, or overwrites existing file
with open(cwd+'/exportFile.csv', 'w+b') as f:
    # initial write that adds first set of finding data to file with disclaimer removed
    f.write(r.content[:-280])

    # initialize variables for loop
    counter = 2
    offset = recordCount

    # loop to request finding data sequentially in batches
    while counter <= modulus:
        # 2-second pause to avoid rate limiting from destination server
        time.sleep(2)

        # print current batch number and offset
        print("Requesting data batch #" + str(counter) + " from api...", "(offset: " + str(offset) + ")")

        # request to get finding data with sequential offset
        payloadr3 = {'limit': recordCount, 'offset': offset, 'affects_rating': 'true', 'unsampled': unsampledQ, 'sort': '-last_seen', 'fields': fieldsQ}
        r3 = requests.get(url=apiEndpoint, auth=authValues, params=payloadr3, headers=head, timeout=None)

        # secondary write to add remaining finding data to file with column headers and disclaimer removed
        f.write(r3.content[177:-280])

        # print http response of most recent api request
        print('Request completed:', r3)

        # increment offset and counter
        counter += 1
        offset += recordCount

    else:
        # close file
        f.close()

# initialize variable for row check
rowCount = 0

# iterate csv file to count rows
for row in open(cwd+"/exportFile.csv"):
    rowCount += 1

    # close file
    f.close()

# check if the total findings exported matches the total findings count
if rowCount-1 == r2.json()['count']:
    print("PROCESS COMPLETE! File location: " + cwd+"/exportFile.csv")
else:
    print("Process complete, however finding counts do NOT match, check for errors...")

# exit script
sys.exit()

__author__ = "dh_tester"
__status__ = "retired"
__version__ = "1.01"
