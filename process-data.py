#!/usr/bin/python3

import json
import os
import csv
from dateutil import parser

datadir="/home/bas/virgin-media-router-status/data"
outputfile=os.path.join(datadir, "summary.csv")

## Identifiers to look for in the JSON files (patterns for input to str.format)
json_down_dbmv_id="1.3.6.1.2.1.10.127.1.1.1.1.6.{0}"
json_down_rxmer_id="1.3.6.1.2.1.10.127.1.1.4.1.5.{0}"
json_up_dbmv_id="1.3.6.1.4.1.4491.2.1.20.1.2.1.1.{0}"
json_pre_rs_errors_id="1.3.6.1.2.1.10.127.1.1.4.1.3.{0}"
json_post_rs_errors_id="1.3.6.1.2.1.10.127.1.1.4.1.4.{0}"

# List all '.json. files in data directory
jsonfiles = sorted([f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir,f)) and f.endswith('.json')])

with open (outputfile, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['date and time', 
        'downstream: min dBmV', 'downstream: max dBmV', 'downstream: avg dBmV', 
        'downstream: min RxMER (dB)', 'downstream: max RxMER (dB)', 'downstream: avg RxMER (dB)',
        'downstream: pre RS Errors (cuml, all channels)', 'downstream: post RS Errors (cuml, all channels)',
        'upstream: min dBmV', 'upstream: max dBmV', 'upstream: avg dBmV'])

    # Parse the files one by one
    for jsonfile in jsonfiles:
        # Parse date from filename (e.g. virgin-media-router-status-2021-08-07T23:00+01:00.json)
        datetime_iso8601='-'.join(os.path.splitext(jsonfile)[0].split("-")[4:7])
        datetime = parser.isoparse(datetime_iso8601)

        with open(os.path.join(datadir,jsonfile)) as f:
            print("Processing " + jsonfile + " (" + datetime_iso8601 + ")...")
            try:
                json_data = json.load(f)
            except:
                print("Error parsing " + jsonfile + "; skipping...")
                continue


            # dBmV is signal power level. Should be between -6 and 10
            sum_down_dbmv=0
            min_down_dbmv=100
            max_down_dbmv=-100

            # RxMER (receive modulation error ratio) is signal-to-noise ratio. Should be above 34.5 (even 34 is problematic).
            sum_down_rxmer=0
            min_down_rxmer=100
            max_down_rxmer=-100

            sum_pre_rs_errors=0
            sum_post_rs_errors=0

            # Process downstream bonded channels (assuming there's 24 of them)
            for channel_index in range(1,25):
                down_dbmv = float(json_data[str.format(json_down_dbmv_id,channel_index)]) / 10.0
                down_rxmer = float(json_data[str.format(json_down_rxmer_id,channel_index)]) / 10.0
                pre_rs_errors = int(json_data[str.format(json_pre_rs_errors_id,channel_index)])
                post_rs_errors = int(json_data[str.format(json_post_rs_errors_id,channel_index)])


                print(f"channel {channel_index}: {down_dbmv} dBmV, rxMER={down_rxmer}, pre_rs={pre_rs_errors}, post_rs={post_rs_errors}")

                sum_down_dbmv = sum_down_dbmv + down_dbmv
                min_down_dbmv = min(down_dbmv, min_down_dbmv)
                max_down_dbmv = max(down_dbmv, max_down_dbmv)

                sum_down_rxmer = sum_down_rxmer + down_rxmer
                min_down_rxmer = min(down_rxmer, min_down_rxmer)
                max_down_rxmer = max(down_rxmer, max_down_rxmer)

                sum_pre_rs_errors = sum_pre_rs_errors + pre_rs_errors
                sum_post_rs_errors = sum_post_rs_errors + post_rs_errors

            # Process upstream bonded channels (assuming there's 4 of them)

            # dBmV is signal power level (decibels per millivolt). Upstream should be between 33 and 51
            sum_up_dbmv=0
            min_up_dbmv=100
            max_up_dbmv=-100
            for channel_index in range(1,5):
                up_dbmv = float(json_data[str.format(json_up_dbmv_id,channel_index)]) / 10.0
                sum_up_dbmv = sum_up_dbmv + up_dbmv
                min_up_dbmv = min(up_dbmv, min_up_dbmv)
                max_up_dbmv = max(up_dbmv, max_up_dbmv)


            avg_down_dbmv = sum_down_dbmv / 24.0
            avg_down_rxmer = sum_down_rxmer / 24.0
            avg_up_dbmv = sum_up_dbmv / 4.0

            csvwriter.writerow([datetime.strftime("%Y-%m-%d %H:%M:%S"), 
                    min_down_dbmv, max_down_dbmv, f"{avg_down_dbmv:.2f}", 
                    min_down_rxmer, max_down_rxmer, f"{avg_down_rxmer:.2f}",
                    sum_pre_rs_errors, sum_post_rs_errors,
                    min_up_dbmv, max_up_dbmv, f"{avg_up_dbmv:.2f}"])


