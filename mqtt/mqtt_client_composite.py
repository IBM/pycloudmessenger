#!/usr/bin/env python
#authors john.d.sheehan@ie.ibm.com, markpurcell@ie.ibm.com

"""CSV parser for MQTT client.
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

import argparse
import os
import fnmatch
import csv
import json
import sys
import datetime
import logging
from dateutil.tz import tzutc
from meter_submit import MeterSubmissionAPI

MQTT_CLIENT_VERSION = 1.1

#MQTT publish sample. Read a row from a csv file and publish it to an MQTT broker


LOGGER = logging.getLogger(__package__)

def logger(verbose=False):
    if not LOGGER.handlers:
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(stream=sys.stdout, level=level,
                            format='%(asctime)s.%(msecs)03d %(levelname)-6s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    return LOGGER



class DataParser():
    def __init__(self, client, flavour, batch, max_lines, split, column_config):
        self.client = client
        self.flavour = flavour
        self.batch = batch
        self.max_lines = max_lines
        self.split = split
        self.column_config = column_config
        self.header = None
        self.finished = False
        self.start = None
        self.device = None
        self.last_processed_line = 0
        #Update your date format as appropriate
        self.date_format = '%Y/%m/%d %H:%M:%S'
        self.date_format = '%Y-%m-%d %H:%M:%S'
        #If your date format is different, please change, for example
        #01/09/2015 00:00 requires the following change
        #self.date_format = '%d/%m/%Y %H:%M'
        #Update your timezone as appropriate
        self.timezone = 'Europe/Zurich'
        #If your timestamp is already UTC the following line is appropriate
        #self.timezone = 'UTC'


    def anonymize(self, row):
        #Funtion to anoymize a row
        #Modify as appropriate
        return row

    def parse_sample_line(self, row, line, target_line, separator=','):
        if line <= target_line:
            return None

        #split a csv row into values and insert into dictionary
        values = row.split(separator)

        #Call our function to remove sensitive personal data, if any
        values = self.anonymize(values)

        #Note: the observed_timestamp field should be iso8601 UTC prior to submission
        #The following code assumes a local timestamp and converts to UTC

        timestamp = self.client.utc_offset(values[self.column_config['timestamp']], self.timezone, self.date_format)
        timestamp = datetime.datetime.strptime(timestamp, self.date_format).replace(tzinfo=tzutc()).isoformat()

        data = []
        for i in range(len(self.column_config['value_column_names'])):
            data.append({"observed_timestamp": timestamp,
                         "device_id":          values[self.column_config['sensor_id']] + '-' + self.column_config['value_column_names'][i],
                         "value":              values[self.column_config['value_column_idxs'][i]]})
        self.last_processed_line = line
        return data


    def read_row(self, filename):
        #Open csv file and yield a new row on each call

        with open(filename, 'r') as csvfile:
            csvreader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=',', quotechar='"')

            for row in csvreader:
                yield row


    def publish(self, filename, target_line):
        count = 0
        line = 0
        data = []

        #Iterate over csv file and upload to server
        for row in self.read_row(filename):
            line += 1
            latest = None
            row_str = ','.join(row)

            #Lets convert our comma separated values to json and add to upload
            if self.flavour == 1:
                latest = self.parse_sample_line(row_str, line, target_line)
            else:
                logger().info("Flavour not supported")

            if latest is None:
                continue

            data = data + latest

            count += 1
            if count % self.batch == 0:
                #Now upload
                logger().debug("Publishing : %d (%d measurements)", count, len(data))
                self.client.publish(data, self.split)
                #logger().info(json.dumps(data))
                data = []

            if count >= self.max_lines:
                break

        if data:
            logger().debug("Publishing : %d (%d measurements)", count, len(data))
            self.client.publish(data, self.split)
            #logger().info(json.dumps(data))

        return (self.last_processed_line, count)


def sort_key(to_sort):
    return str(os.path.getmtime(to_sort)) + '::' + to_sort.lower()

def parse_csv_column_config(csv_column_config_file):

    column_config = json.load(csv_column_config_file)

    expected_keys = ['sensor_id', 'timestamp', 'value_column_names', 'value_column_idxs']
    for key in expected_keys:
        if column_config.get(key) is None:
            raise KeyError('CSV column configuration file missing expected key: ' + key)

    if len(column_config['value_column_names']) < 1:
        raise KeyError("CSV column configuration file must define one or more 'value_column_names'")

    if len(column_config['value_column_names']) != len(column_config['value_column_names']):
        raise KeyError("CSV column configuration file must define equal number of 'value_column_names' and 'value_column_idxs'")

    return column_config


def main(argv=None):
    parser = argparse.ArgumentParser(description='submit data to ingestion service')
    parser.add_argument('--broker', action='store', dest='broker',
                        required=True, help='broker configuration file')
    parser.add_argument('--dir', action='store', dest='dir',
                        required=True, help='data directory')
    parser.add_argument('--pattern', action='store', dest='pattern',
                        required=True, help='file filter')
    parser.add_argument('--state', action='store', dest='state',
                        required=True, help='state file')
    parser.add_argument('--flavour', action='store', dest='flavour',
                        required=True, help='file format style')
    parser.add_argument('--batch', action='store', dest='batch',
                        required=True, help='batch x messages')
    parser.add_argument('--column_config_path', action='store', dest='column_config_path',
                        required=False, default='column_config.json', help='Path to CSV column configuration JSON file')
    parser.add_argument('--max', action='store', dest='max_lines',
                        required=False, default=100000, help='process max lines')
    parser.add_argument('--split', action='store', dest='split',
                        required=False, default=25, help='process max columns per message')
    parser.add_argument('-v', '--verbose', help="increase output verbosity",
                        required=False, default=False, action='store_true', dest='verbose')

    args = parser.parse_args()
    client = None
    state = {}

    logger(args.verbose)
    logger().info("=============================Starting==============================")

    try:
        #Connect to the broker
        client = MeterSubmissionAPI(args.broker)
    except Exception as e:
        logger().error("CRITICAL: Cannot connect to broker : %r", e)
        logger().error("CRITICAL: Please check network/firewall... exiting.")
        quit()

    try:
        with open(args.state) as state_file:
            state = json.load(state_file)
            logger().info("Loading from state : %s:%d", state['file'], state['line'])
    except:
        logger().info("No state file found, providing default.")
        state['file'] = None
        state['line'] = 0

    try:
        with open(args.column_config_path) as csv_column_config_file:
            column_config = parse_csv_column_config(csv_column_config_file)
            logger().info("Loading CSV column config file: " + args.column_config_path)
    except:
        logger().info("No CSV column config file found; exiting...")
        quit()

    try:
        args.state = os.path.abspath(args.state)
        os.chdir(args.dir)

        for fname in fnmatch.filter(sorted(os.listdir('.'), key=sort_key), args.pattern):
            fname = os.path.join('.', fname)
            if os.path.isfile(fname) == 0:
                continue

            if state['line'] == 0:
                line = 0 #A new file, start at the beginning
                logger().info("Processing : %s...", fname)
            elif fname == state['file']:
                line = state['line'] #Lets try to start from the last point
                logger().info("Processing from : %s:%d", fname, line)
            else:
                logger().debug("Skipping file: %s", fname)
                continue

            try:
                #Now lets upload our meter data
                parser = DataParser(client, int(args.flavour), int(args.batch), int(args.max_lines), int(args.split), column_config)
                line, count = parser.publish(fname, line)
                if line in (0, state['line']):
                    logger().info("No additional data at : %s:%d", fname, state['line'])
                    state['line'] = 0 #Now we drop state to process next file
                    continue

                logger().info("Processed : %s", fname)

                with open(args.state, 'w') as state_file:
                    json.dump({'file': fname, 'line': line}, state_file)

                if count == parser.max_lines:
                    #Quit all file processing, large file encountered
                    logger().info("Max lines reached : %s:%d:%d", fname, line, count)
                    break
            except Exception as e:
                logger().info("WARNING: %s", str(e))
                logger().info("WARNING: Not writing to state file : %s", args.state)
                logger().info("WARNING: State will not be preserved : %s:%d", fname, line)
                raise e
    except Exception as e:
        logger().error("ERROR: %r", e)
        logger().error("ERROR: aborting.")
    finally:
        if client is not None:
            logger().debug("Disconnecting from broker...")
            client.close()
        logger().info("=============================Finished==============================")


if __name__ == '__main__':
    main(sys.argv)
