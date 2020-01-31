#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""Castor protocol handler.
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

import logging
import pycloudmessenger.rabbitmq as rabbitmq
import pycloudmessenger.serializer as serializer
import pycloudmessenger.castor.message_catalog as catalog
import pycloudmessenger.castor.api_abc as api

logging.getLogger("pika").setLevel(logging.WARNING)


class CastorContext(rabbitmq.RabbitContext):
    """
        Holds connection details for a Castor service
    """

class TimedOutException(rabbitmq.RabbitTimedOutException):
    '''Over-ride exception'''

class ConsumerException(rabbitmq.RabbitConsumerException):
    '''Over-ride exception'''


class CastorMessenger(rabbitmq.RabbitDualClient, api.CastorABC):
    """
        Communicates with a Castor service
    """
    def __init__(self, context, publish_queue: str = None, subscribe_queue: str = None):
        """
            Class initializer
        """
        super(CastorMessenger, self).__init__()

        if not publish_queue:
            publish_queue = context.feeds()

        self.publish_queue = publish_queue
        self.subscribe_queue = subscribe_queue

    def __enter__(self):
        self.start_subscriber(queue=rabbitmq.RabbitQueue(self.subscribe_queue))
        self.start_publisher(queue=rabbitmq.RabbitQueue(self.publish_queue))
        self.catalog = catalog.MessageCatalog(self.get_subscribe_queue())
        return self

    def __exit__(self, *args):
        self.stop()
        self.catalog = None

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

