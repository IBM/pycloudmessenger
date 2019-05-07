#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""RabbitMQ helper class.
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

import ssl
import logging
from abc import ABC, abstractmethod
import pika

__rabbit_helper_version_info__ = ('0', '1', '2')
LOGGER = logging.getLogger(__package__)


class RabbitContext():
    """
        Holds connection details for a RabbitMQ service
    """
    def __init__(self, host, port, user, password, vhost, ssl=True, cert=None):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = password
        self.vhost = vhost
        self.ssl = ssl
        self.cert = cert


class RabbitQueue():
    """
        Holds configuration details for a RabbitMQ Queue
    """
    def __init__(self, queue='', auto_delete=False, durable=False, exclusive=False, purge=False):
        self.name = queue
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.purge = purge


class AbstractRabbitMessenger(ABC):
    """
        Communicates with a RabbitMQ service
    """
    def __init__(self, context):
        self.context = context
        self.inbound = 0
        self.outbound = 0
        self.connection = None
        self.channel = None
        self.cancel_on_close = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def declare_queue(self, queue):
        """
            Declare a queue, creating if required

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """

        #Will not raise an exception if access rights insufficient on the queue
        #Exception only raised when channel consume takes place
        result = self.channel.queue_declare(
                        queue=queue.name,
                        exclusive=queue.exclusive,
                        auto_delete=queue.auto_delete,
                        durable=queue.durable)
        #Useful when testing - clear the queue
        if queue.purge is True:
            self.channel.queue_purge(queue=queue.name)
        queue.name = result.method.queue
        return queue

    def establish_connection(self, parameters):
        """
            Connect to RabbitMQ service

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        #Ensure the consumer only gets 1 unacknowledged message
        self.channel.basic_qos(prefetch_count=1)

    def connect(self, connection_attempts, retry_delay):
        """
            Setup connection settings to RabbitMQ service

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """

        ssl_options = {}

        if self.context.ssl is True:
            ssl_options['ssl_version'] = ssl.PROTOCOL_TLSv1_2
        if self.context.cert is not None:
            ssl_options['ca_certs'] = self.context.cert
            ssl_options['cert_reqs'] = ssl.CERT_REQUIRED

        credentials = pika.PlainCredentials(self.context.user, self.context.pwd)
        parameters = pika.ConnectionParameters(
                        self.context.host, self.context.port, self.context.vhost,
                        credentials, ssl=self.context.ssl, ssl_options=ssl_options,
                        connection_attempts=connection_attempts,
                        retry_delay=retry_delay)
        self.establish_connection(parameters)

    def publish(self, message, queue, exchange='', mode=1):
        """
            Publish a message to a queue

            Throws:
                Exception - maybe access rights are insufficient on the queue

            Returns:
                None
        """
        self.channel.basic_publish(
            exchange=exchange, routing_key=queue, body=message,
            properties=pika.BasicProperties(delivery_mode=mode)
        )
        self.outbound += 1

    def stop(self):
        """
            Closes open channels and connections

            Throws:
                Nothing

            Returns:
                None
        """
        try:
            if self.channel is not None:
                if self.cancel_on_close is True:
                    self.channel.cancel()
                self.channel.close()
            if self.connection is not None:
                self.connection.close()
        except:
            pass

    @abstractmethod
    def receive(self, handler, timeout, max_messages):
        pass


class RabbitClient(AbstractRabbitMessenger):
    """
        Communicates with a RabbitMQ service
    """
    def __init__(self, context, queue, connection_attempts=10, retry_delay=1):
        super(RabbitClient, self).__init__(context)
        #This will force a server generated queue name like 'amq.gen....'
        if not queue.name:
            queue.name = ''
        queue.name = queue.name.strip()
        self.queue = queue

        self.connect(connection_attempts, retry_delay)

    def establish_connection(self, parameters):
        super(RabbitClient, self).establish_connection(parameters)
        self.declare_queue(self.queue)

    def publish(self, message, queue=None, exchange='', mode=1):
        if queue is None:
            queue = self.queue
        super(RabbitClient, self).publish(message, queue.name, exchange, mode)

    def receive(self, handler, timeout=30, max_messages=0):
        """
            Start receiving messages, up to max_messages

            Throws:
                Exception if consume fails

            Returns:
                The number of messages consumed
        """
        msgs = 0

        for msg in self.channel.consume(
                self.queue.name,
                exclusive=self.queue.exclusive,
                inactivity_timeout=timeout):

            method_frame, properties, body = msg
            if not method_frame:
                break

            msgs += 1
            self.inbound += 1

            #body is of type 'bytes' in Python 3+
            state = handler(body)
            if (state is None) or (state is not False):
                #Only ack message if handler successfully dealt with message
                #This could fail if the connection was closed by the broker
                self.channel.basic_ack(method_frame.delivery_tag)

            #Stop consuming if message limit reached
            if msgs == max_messages:
                break

        self.channel.cancel()
        return msgs


class RabbitDualClient():
    """
        Communicates with a RabbitMQ service
    """
    def __init__(self, context):
        """
            Class initializer
        """
        self.context = context
        self.subscriber = None
        self.publisher = None
        self.last_recv_msg = None

    def start_subscriber(self, queue, client=RabbitClient):
        """
            Connect to Castor service and create a queue

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """
        self.subscriber = client(self.context, queue)

    def get_subscribe_queue(self):
        return self.subscriber.queue.name

    def start_publisher(self, queue, client=RabbitClient):
        """
            Connect to Castor service and create a queue

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """
        self.publisher = client(self.context, queue)

    def send(self, message):
        """
            Publish a message to Castor service

            Throws:
                An exception if publish is not successful

            Returns:
                None
        """
        self.publisher.publish(message)

    def receive(self, handler, timeout, max_messages):
        """
            Receive messages from Castor service

            Throws:
                An exception if receive is not successful

            Returns:
                None
        """
        self.subscriber.receive(handler, timeout, max_messages)

    def internal_handler(self, message):
        """
            Handler for invoke_service methode

            Throws:
                Nothing

            Returns:
                None
        """
        self.last_recv_msg = message

    def invoke_service(self, message, timeout=30):
        """
            Publish a message and receive a reply

            Throws:
                An exception if not successful

            Returns:
                The reply dictionary
        """
        self.last_recv_msg = None
        LOGGER.info("Sending message: %s", message)
        self.send(message)

        LOGGER.info("Waiting for reply...")
        #Now wait for the reply
        messages = self.subscriber.receive(self.internal_handler, timeout, 1)
        if messages == 0:
            raise Exception('Timed out waiting for reply.')
        return self.last_recv_msg

    def stop(self):
        """
            Close connection to Castor service

            Throws:
                An exception if not successful

            Returns:
                None
        """
        self.subscriber.stop()
        self.publisher.stop()
