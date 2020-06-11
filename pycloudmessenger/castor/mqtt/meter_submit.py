#!/usr/bin/env python
#authors john.d.sheehan@ie.ibm.com, mark_purcell@ie.ibm.com

"""MQTT client publisher.
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
import ssl
import json
import threading
import datetime
import logging
import pytz

import paho.mqtt.client as mqtt


#NOTE: FOR GOFLEX OPERATIONS DON'T CHANGE THE CONTENTS OF THIS FILE
#REQUEST BUG FIXES OR ENHANCEMENTS AS NECESSARY

METER_SUBMIT_VERSION = 1.1


class MeterSubmissionAPI():
    def __init__(self, config_file):
        config = self.config_file_parse(config_file)

        client_id = config['client_id']
        self.client = mqtt.Client(client_id=client_id, clean_session=True)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        cafile = config['cafile']
        self.client.tls_set(ca_certs=cafile, certfile=None, keyfile=None,
                            cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2)

        username = config['username']
        password = config['password']
        self.client.username_pw_set(username, password)

        address = config['address']
        self.topic = config['topic']

        self.logger = logging.getLogger()
        self._condition = threading.Condition()

        self.mqtt_status = 0
        self.client.connect(address, 8883)
        self.client.loop_start()

        with self._condition:
            self._condition.wait()

        if self.mqtt_status != 0:
            raise Exception("Broker connection issue: " + str(self.mqtt_status))


    def utc_offset(self, local_datetime_str, local_timezone_str, datetime_format):
        '''given a local datetime string, local timezone, and optional datetime format,
           return a utc, offset tuple, or None on failure
        '''

        try:
            local_tz_obj = pytz.timezone(local_timezone_str)
            basic_dt_obj = datetime.datetime.strptime(local_datetime_str, datetime_format)
            local_dt_obj = local_tz_obj.normalize(local_tz_obj.localize(basic_dt_obj))

            utc_dt_str = local_dt_obj.astimezone(pytz.utc).strftime(datetime_format)
            #offset = local_dt_obj.strftime('%z')
            #return utc_dt_str, offset)
            return utc_dt_str
        except pytz.exceptions.UnknownTimeZoneError:
            self.logger.info('unknown timezone: %s', local_timezone_str)
        return None

    def config_file_parse(self, jsonfile):
        #Parse json file for server connection details, return dict

        '''
        expected file contents
        {
          "client_id":"d:xxxxxx:xxxxxxx:xxxx",
          "address":"xxxxxx.messaging.internetofthings.ibmcloud.com",
          "username":"use-token-auth",
          "password":"xxxxxxxxxxxxxxxxxy",
          "topic":"iot-2/evt/xxxxx/fmt/xxx"
          "cafile":"ca filename"
        }
        '''
        with open(jsonfile) as config_file:
            config = json.load(config_file)

        expected_keys = ['client_id', 'address', 'username', 'password', 'topic', 'cafile']
        for key in expected_keys:
            if config.get(key) is None:
                raise KeyError('%s is missing' % key)

        cafile = config['cafile']
        if not os.path.isfile(cafile):
            raise IOError('certificate file not found {}'.format(cafile))

        return config

    def on_disconnect(self, client, userdata, reason):
        self.logger.debug('Broker: disconnected... %s', str(reason))

    def on_connect(self, client, userdata, flags, result):
        #callback when client connects to broker
        self.logger.debug('Broker: connected - %d', result)
        self.mqtt_status = result

        with self._condition:
            self._condition.notify()

    def on_publish(self, client, userdata, result):
        #Callback when publish attempted
        counter = int(result)
        if counter % 50 == 0:
            self.logger.debug('Split Published: %s', str(result))

    def publish(self, message, maximum):
        size = len(message)

        subsets = range(0, size, maximum)

        for subset in subsets:
            msg = json.dumps(message[subset:subset+maximum])
            rc = self.client.publish(self.topic, msg, qos=2)
            if not rc.is_published():
                rc.wait_for_publish()

    def close(self):
        # give time for publish to complete

        self.client.loop_stop()
        self.client.disconnect()
