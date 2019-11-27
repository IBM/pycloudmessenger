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

import os
import argparse
import logging
import random
import pycloudmessenger.castor.castorapi as castorapi

#Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def main():
    parser = argparse.ArgumentParser(description='Messaging Client')
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--feed_queue', help='Defaults to credentials file')
    parser.add_argument('--reply_queue', help='Defaults to auto-generated')
    parser.add_argument('--broker_user', help='Defaults to credentials file')
    parser.add_argument('--broker_password', help='Defaults to credentials file')
    parser.add_argument('--register_model', default=False, help='Boolean setting for registering models')
    cmdline = parser.parse_args()

    LOGGER.info("Starting...")
    context = castorapi.CastorContext.from_credentials_file(cmdline.credentials, cmdline.broker_user, cmdline.broker_password)

    try:
        castor = castorapi.CastorMessenger(context, cmdline.feed_queue, cmdline.reply_queue)

        with castor:
            #List the devices
            LOGGER.info("Requesting sensor ID listing...")
            message = castor.request_sensor_list()
            reply = castor.invoke_service(message)
            sensor = random.choice(reply['ts_ids'])
            LOGGER.info("\n\nSensor IDs: " + str(reply['ts_ids']) + "\n")

        with castor:
            #Retrieve some time series
            LOGGER.info("Requesting time series for sensor ID '%s'...", sensor)
            message = castor.request_sensor_data(sensor, "2001-07-13T00:00:00+00:00", "2020-08-13T01:00:00+00:00")
            reply = castor.invoke_service(message)
            values = reply['count']
            LOGGER.info("Number of Time Series Values: %d", values)

        with castor:
            if cmdline.register_model:
                #Register external model
                LOGGER.info("Registering model...")
                message = castor.register_model('my-new-model1', 'target_entity', 'target_signal')
                reply = castor.invoke_service(message)
                ts_id = reply['ts_id']
                LOGGER.info("Time Series: %s", ts_id)
    except Exception as err:
        LOGGER.error(err)
        raise err

if __name__ == '__main__':
    main()
