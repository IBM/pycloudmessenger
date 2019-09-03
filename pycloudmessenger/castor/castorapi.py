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
import logging
import pycloudmessenger.rabbitmq as rabbitmq
import pycloudmessenger.serializer as serializer

logging.getLogger("pika").setLevel(logging.WARNING)


class CastorContext(rabbitmq.RabbitContext):
    """
        Holds connection details for a Castor service
    """

class TimedOutException(rabbitmq.RabbitTimedOutException):
    '''Over-ride exception'''

class ConsumerException(rabbitmq.RabbitConsumerException):
    '''Over-ride exception'''


class CastorMessenger(rabbitmq.RabbitDualClient):
    """
        Communicates with a Castor service
    """
    def __init__(self, context, publish_queue: str = None, subscribe_queue: str = None):
        """
            Class initializer
        """
        super(CastorMessenger, self).__init__(context)
        self.correlation = 0
        self.client_id = str(uuid.uuid4())

        if not publish_queue:
            publish_queue = context.feeds()

        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def _msg_template(self, service_name: str = 'TimeseriesService'):
        """
            Format message template - internal only

            Throws:
                Nothing

            Returns:
                The requestor sub-info
        """
        message = {
            'serviceRequest': {
                'requestor': self._requestor(),
                'service': {
                    'name': service_name,
                    'args': {
                    }
                }
            }
        }
        return message, message['serviceRequest']['service']['args']

    def _requestor(self):
        """
            Format message for requestor information - internal only

            Throws:
                Nothing

            Returns:
                The requestor sub-info
        """
        self.correlation += 1
        req = {'replyTo': self.get_subscribe_queue()}
        req.update({'correlationID': self.correlation,
                    'clientID': self.client_id, 'transient': True})
        return req

    def invoke_service(self, message, timeout=60):
        try:
            message = serializer.Serializer.serialize(message)
            result = super(CastorMessenger, self).invoke_service(message, timeout)
        except rabbitmq.RabbitTimedOutException as exc:
            raise TimedOutException(exc) from exc
        except rabbitmq.RabbitConsumerException as exc:
            raise ConsumerException(exc) from exc

        if not result:
            raise Exception(f"Malformed object: None")
        result = serializer.Serializer.deserialize(result)

        if 'status' not in result['serviceResponse']['service']:
            raise Exception(f"Malformed object: {result}")
        status = result['serviceResponse']['service']['status']
        if status != 200:
            msg = f"({status}): {result['serviceResponse']['service']['result']}"
            raise Exception(msg)

        return result['serviceResponse']['service']['result']

    def request_sensor_data(self, meter, from_date, to_date):
        """
            Format message for retrieving sensor data

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/get_timeseries_values', 'device_id': meter,
                     'from': from_date, 'to': to_date})
        return template

    def request_sensor_list(self):
        """
            Format message for retrieving sensor listing

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/get_time_series'})
        return template

    def store_time_series(self, values):
        """
            Format message for storing sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/store_timeseries_values', 'values': values})
        return template

    def average_time_series(self, meter, from_date, to_date):
        """
            Format message for averaging sensor observations

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'ts/average_timeseries_values', 'device_id': meter,
                     'from': from_date, 'to': to_date})
        return template

    def register_model(self, model_name, entity_name, signal_name):
        """
            Format message for registering an external model

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'register_model', 'model_name': model_name,
                     'entity': entity_name, 'signal': signal_name})
        return template

    def request_model_time_series(self, model_name, entity_name, signal_name):
        """
            Format message for retrieving a models timeseries is

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template()
        args.update({'cmd':'get_model_time_series',
                     'model_name': model_name, 'entity': entity_name,
                     'signal': signal_name})
        return template

    def key_value_service(self, cmd, keys):
        """
            Format message for interacting with the key/value service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template('KeyValueService')
        args.update({'cmd': cmd, 'keys': keys})
        return template

    def weather_service_hourly(self, api_key, lat, lng):
        """
            Format message for interacting with the weather service

            Throws:
                An exception if not successful

            Returns:
                Dict - The message to send
        """
        template, args = self._msg_template('WeatherService-TwoDayHourlyForecast-External')
        args.update({'apiKey': api_key, 'latitude': lat, 'longitude': lng})
        return template
