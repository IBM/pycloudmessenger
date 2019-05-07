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

# Suppress too-many-lines
# pylint: disable=C0301, W0703

import os
import logging
from . import castorapi

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def getenv(var, default=None):
    """ fetch environment variable,
        throws:
            exception if value and default are None
        returns:
            environment value
    """
    value = os.getenv(var, default)
    if not value:
        if not default:
            raise Exception(var + " environment variable must have a value")
        value = default
    return value


def main():
    """main"""
    host = getenv('RABBIT_BROKER')
    port = int(getenv('RABBIT_PORT'))
    user = getenv('RABBIT_USER')
    password = getenv('RABBIT_PWD')
    vhost = getenv('RABBIT_VHOST')
    cert = getenv('CERT', 'cert.pem')
    feed_queue = getenv('PUBLISH_QUEUE')
    reply_queue = getenv('SUBSCRIBE_QUEUE', ' ')

    LOGGER.info("Starting...")

    context = castorapi.CastorContext(host, port, user, password, vhost, cert=cert)

    try:
        with castorapi.CastorMessenger(context, feed_queue, reply_queue) as castor:
            #List the devices
            LOGGER.info("Requesting sensor listing...")
            message = castor.request_sensor_list()
            reply = castor.invoke_service(message)
            sensor = reply['serviceResponse']['service']['result']['ts_ids'][0]
            LOGGER.info("First sensor: %s", sensor)

            #Retrieve some time series
            LOGGER.info("Requesting time series for sensor '%s'...", sensor)
            message = castor.request_sensor_data(sensor, "2001-07-13T00:00:00+00:00", "2020-08-13T01:00:00+00:00")
            reply = castor.invoke_service(message)
            values = reply['serviceResponse']['service']['result']['count']
            LOGGER.info("Time series values: %d", values)
    except Exception as err:
        LOGGER.info("Error %r", err)

if __name__ == '__main__':
    main()
