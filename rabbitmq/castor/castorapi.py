#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""Castor message formmatter and protocol handler.
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

# pylint: disable=R0903, R0913

import uuid
import json
import logging
from messenger import rabbitmq

logging.getLogger("pika").setLevel(logging.WARNING)


class CastorContext(rabbitmq.RabbitContext):
    """
        Holds connection details for a Castor service
    """
    def __init__(self, host, port, user, password, vhost, cert):
        super(CastorContext, self).__init__(host, port, user, password, vhost, cert=cert)


class CastorMessenger(rabbitmq.RabbitDualClient):
    """
        Communicates with a Castor service
    """
    def __init__(self, context, publish_queue, subscribe_queue):
        """
            Class initializer
        """
        super(CastorMessenger, self).__init__(context)
        self.correlation = 0
        self.client_id = str(uuid.uuid4())
        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue, exclusive=True))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue, durable=True))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def invoke_service(self, message, timeout=30):
        return json.loads(super(CastorMessenger, self).invoke_service(message, timeout))

    def requestor(self):
        """
            Format message for requestor information - internal only

            Throws:
                Nothing

            Returns:
                The requestor sub-info
        """
        self.correlation += 1
        return {
            'replyTo': self.get_subscribe_queue(),
            'clientID': self.client_id,
            'transient': True,
            'correlationID': self.correlation
        }

    def request_sensor_data(self, meter, from_date, to_date):
        """
            Format message for retrieving sensor data

            Throws:
                An exception if not successful

            Returns:
                The message to send as a json string
        """
        req = self.requestor()
        return json.dumps({
            'serviceRequest': {
                'requestor': req,
                'service': {
                    'name': 'TimeseriesService',
                    'args': {
                        'cmd': 'ts/get_timeseries_values',
                        'device_id': meter,
                        'from': from_date,
                        'to': to_date
                    }
                }
            }
        })

    def request_sensor_list(self):
        """
            Format message for retrieving sensor listing

            Throws:
                An exception if not successful

            Returns:
                The message to send as a json string
        """
        req = self.requestor()
        return json.dumps({
            'serviceRequest': {
                'requestor': req,
                'service': {
                    'name': 'TimeseriesService',
                    'args': {
                        'cmd': 'ts/get_time_series'
                    }
                }
            }
        })
