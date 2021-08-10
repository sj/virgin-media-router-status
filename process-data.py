#!/usr/bin/python3

import json
import os
import csv
from dateutil import parser

datadir="data"
outputfile=os.path.join(datadir, "summary.csv")

## Identifiers to look for in the JSON files (patterns for input to str.format)
json_dbmv_id="1.3.6.1.2.1.10.127.1.1.1.1.6.{0}"
json_pre_rs_errors_id="1.3.6.1.2.1.10.127.1.1.4.1.3.{0}"
json_post_rs_errors_id="1.3.6.1.2.1.10.127.1.1.4.1.4.{0}"

# List all '.json. files in data directory
jsonfiles = sorted([f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir,f)) and f.endswith('.json')])

with open (outputfile, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['date and time', 'min dBmV', 'max dBmV', 'avg dBmV', 'Pre RS Errors (cuml, all channels)', 'Post RS Errors (cuml, all channels)'])

    # Parse the files one by one
    for jsonfile in jsonfiles:
        # Parse date from filename (e.g. virgin-media-router-status-2021-08-07T23:00+01:00.json)
        datetime_iso8601='-'.join(os.path.splitext(jsonfile)[0].split("-")[4:7])
        datetime = parser.isoparse(datetime_iso8601)

        with open(os.path.join(datadir,jsonfile)) as f:
            print("Processing " + jsonfile + " (" + datetime_iso8601 + ")...")
            json_data = json.load(f)

            sum_dbmv=0
            min_dbmv=100
            max_dbmv=-100

            sum_pre_rs_errors=0
            sum_post_rs_errors=0

            # Process downstream bonded channels
            for channel_index in range(1,25):
                dbmv = float(json_data[str.format(json_dbmv_id,channel_index)]) / 10.0
                pre_rs_errors = int(json_data[str.format(json_pre_rs_errors_id,channel_index)])
                post_rs_errors = int(json_data[str.format(json_post_rs_errors_id,channel_index)])

                #print("dbmv for channel " + str(channel_index) + ": " + str(dbmv))
                print(f"channel {channel_index}: {dbmv} dBmV, pre_rs={pre_rs_errors}, post_rs={post_rs_errors}")

                sum_dbmv = sum_dbmv + dbmv
                min_dbmv = min(dbmv, min_dbmv)
                max_dbmv = max(dbmv, max_dbmv)

                sum_pre_rs_errors = sum_pre_rs_errors + pre_rs_errors
                sum_post_rs_errors = sum_post_rs_errors + post_rs_errors

            avg_dbmv = sum_dbmv / 24.0
            #csvwriter.writerow(['date and time', 'min dBmV', 'max dBmV', 'avg dBmV', 'Pre RS Errors (cuml, all channels)', 'Post RS Errors (cuml, all channels)'])
            csvwriter.writerow([datetime.strftime("%Y-%m-%d %H:%M:%S"), min_dbmv, max_dbmv, f"{avg_dbmv:.2f}", sum_pre_rs_errors, sum_post_rs_errors])


