#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""Castor API sample program.
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
import random
import logging
import pycloudmessenger.castor.castor_rest as castorapi

#Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def main():
    parser = argparse.ArgumentParser(description='Messaging Client')
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--proxies', required=False)
    cmdline = parser.parse_args()

    try:
        castor = castorapi.CastorREST(cmdline.credentials, cmdline.proxies)

        with castor:
            #List the devices
            LOGGER.info("Requesting sensor ID listing...")
            message = castor.request_sensor_list()
            reply = castor.invoke_service(message)
            sensor = random.choice(reply['ts_ids'])
            #LOGGER.info("\n\nSensor IDs: " + str(reply['ts_ids']) + "\n")

        with castor:
            #Retrieve some time series
            LOGGER.info("Requesting time series for sensor ID '%s'...", sensor)
            message = castor.request_sensor_data(sensor, "2001-07-13T00:00:00+00:00", "2020-08-13T01:00:00+00:00")
            reply = castor.invoke_service(message)
            values = reply['count']
            LOGGER.info("Number of Time Series Values: %d", values)
    except Exception as err:
        LOGGER.error(err)
        raise err

if __name__ == '__main__':
    main()

