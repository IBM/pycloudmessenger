#!/usr/bin/env python3
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

import os
import ssl
import logging
import json
from abc import ABC, abstractmethod
import pika
import pycloudmessenger.utils as utils

__rabbit_helper_version_info__ = ('0', '1', '2')
LOGGER = logging.getLogger(__package__)



class RabbitContext():
    """
        Holds connection details for a RabbitMQ service
    """
    def __init__(self, args: dict, user: str = None, password: str = None):
        self.cert_file = None
        self.args = args.copy()

        #First set up some defaults
        if 'broker_timeout' not in self.args:
            self.args['broker_timeout'] = 60.0

        self.args['broker_user'] = user if user else self.arg_value(self.args, ['broker_user', 'broker_guest_user', 'client_user'])
        self.args['broker_password'] = password if password else self.arg_value(self.args, ['broker_password', 'broker_guest_password', 'client_pwd'])

        if 'broker_cert_b64' in self.args:
            self.cert_file = utils.Certificate(args['broker_cert_b64'])
            self.args['broker_pem_path'] = self.cert_file.filename
            self.args['broker_tls'] = True
        else:
            self.args['broker_tls'] = False

        #Now check that all required fields are present
        cfg = ['broker_host', 'broker_port', 'broker_vhost',
               'broker_user', 'broker_password']
        for key in cfg:
            if not self.args.get(key):
                raise Exception(f'{key} is missing from RabbitContext initialisation.')

    def __str__(self):
        return json.dumps(self.args)

    def arg_value(self, args, possibilities):
        for p in possibilities:
            val = args.get(p)
            if val:
                return val
        raise Exception(f'{possibilities} missing from arguments.')

    @classmethod
    def from_credentials_file(self, cred_file: str, user: str = None, password: str = None):
        with open(cred_file) as creds:
            args = json.load(creds)

        #First, we need to support legacy credential formats
        if 'broker' in args:
            args['broker_host'] = args.pop('broker')
            args['broker_port'] = args.pop('port')
            args['broker_vhost'] = args.pop('vhost')
            args['broker_user'] = args.pop('client_user')
            args['broker_password'] = args.pop('client_pwd')
            args['broker_cert_b64'] = args.pop('cert_b64')

        return RabbitContext(args, user, password)

    def get(self, key: str):
        try:
            return self.args[key]
        except:
            return None

    def user(self):
        return self.get('broker_user')
    def pwd(self):
        return self.get('broker_password')
    def host(self):
        return self.get('broker_host')
    def port(self):
        return self.get('broker_port')
    def vhost(self):
        return self.get('broker_vhost')
    def cert(self):
        return self.get('broker_pem_path')
    def ssl(self):
        return self.get('broker_tls')
    def feeds(self):
        return self.get('broker_request_queue')
    def replies(self):
        return self.get('broker_response_queue')
    def timeout(self):
        return self.get('broker_timeout')


class RabbitQueue():
    """
        Holds configuration details for a RabbitMQ Queue
    """
    def __init__(self, queue: str = None, auto_delete: bool = False, durable: bool = False, purge: bool = False, prefetch: int = 1):
        self.durable = durable
        self.auto_delete = auto_delete
        self.purge = purge
        self.prefetch = prefetch

        #If no queue specified, create a temporary, exclusive queue
        #This will force a server generated queue name like 'amq.gen....'
        if queue:
            self.name = queue
            self.exclusive = False
        else:
            self.name = ''
            self.exclusive = True
        self.name = self.name.strip()


class AbstractRabbitMessenger(ABC):
    """
        Communicates with a RabbitMQ service
    """
    def __init__(self, context: RabbitContext):
        self.context = context
        self.pub_queue = None
        self.sub_queue = None
        self.inbound = 0
        self.outbound = 0
        self.connection = None
        self.channel = None
        self.cancel_on_close = False
        self.credentials = pika.PlainCredentials(self.context.user(), self.context.pwd())
        self.ssl_options = {}

        if self.context.ssl():
            self.ssl_options['ssl_version'] = ssl.PROTOCOL_TLSv1_2
        if self.context.cert():
            self.ssl_options['ca_certs'] = self.context.cert()
            self.ssl_options['cert_reqs'] = ssl.CERT_REQUIRED

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def declare_queue(self, queue: RabbitQueue) -> RabbitQueue:
        """
            Declare a queue, creating if required

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """

        if queue.exclusive or queue.durable:
            #Will not raise an exception if access rights insufficient on the queue
            #Exception only raised when channel consume takes place
            result = self.channel.queue_declare(
                queue=queue.name,
                exclusive=queue.exclusive,
                auto_delete=queue.auto_delete,
                durable=queue.durable)
            queue.name = result.method.queue

        #Useful when testing - clear the queue
        if queue.purge:
            self.channel.queue_purge(queue=queue.name)
        return queue

    def establish_connection(self, parameters: pika.ConnectionParameters):
        """
            Connect to RabbitMQ service

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def connect(self, connection_attempts: int, retry_delay: int):
        """
            Setup connection settings to RabbitMQ service

            Throws:
                An exception if connection attempt is not successful

            Returns:
                None
        """
        parameters = pika.ConnectionParameters(
                        self.context.host(), self.context.port(), self.context.vhost(),
                        self.credentials, ssl=self.context.ssl(), ssl_options=self.ssl_options,
                        connection_attempts=connection_attempts,
                        retry_delay=retry_delay)
        self.establish_connection(parameters)

    def publish(self, message, queue: str, exchange: str = '', mode: int = 1):
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
            if self.channel:
                if self.cancel_on_close:
                    self.channel.cancel()
                self.channel.close()
            if self.connection:
                self.connection.close()
        except:
            pass

    @abstractmethod
    def receive(self, handler, timeout: int, max_messages: int):
        pass

    @abstractmethod
    def start(self, publish: RabbitQueue = None, subscribe: RabbitQueue = None, connection_attempts: int = 10, retry_delay: int = 1):
        pass


class RabbitTimedOutException(Exception):
    pass

class RabbitConsumerException(Exception):
    pass


class RabbitClient(AbstractRabbitMessenger):
    """
        Communicates with a RabbitMQ service
    """
    def start(self, publish: RabbitQueue = None, subscribe: RabbitQueue = None, connection_attempts: int = 10, retry_delay: int = 1):
        if publish:
            self.pub_queue = publish

        if subscribe:
            self.sub_queue = subscribe

        self.connect(connection_attempts, retry_delay)

    def get_subscribe_queue(self):
        return self.sub_queue.name if self.sub_queue else None

    def establish_connection(self, parameters: pika.ConnectionParameters):
        super(RabbitClient, self).establish_connection(parameters)

        if self.pub_queue:
            self.declare_queue(self.pub_queue)

        if self.sub_queue:
            self.declare_queue(self.sub_queue)
            #Ensure the consumer only gets 'prefetch' unacknowledged message
            self.channel.basic_qos(prefetch_count=self.sub_queue.prefetch)

    def publish(self, message, queue: RabbitQueue = None, exchange: str = '', mode: int = 1):
        if not queue:
            queue = self.pub_queue
        super(RabbitClient, self).publish(message, queue.name, exchange, mode)

    def receive(self, handler=None, timeout: int = 30, max_messages: int = 0) -> str:
        """
            Start receiving messages, up to max_messages

            Throws:
                Exception if consume fails

            Returns:
                The last message received
        """
        msgs = 0
        body = None

        try:
            for msg in self.channel.consume(
                    self.sub_queue.name,
                    exclusive=self.sub_queue.exclusive,
                    inactivity_timeout=timeout):

                method_frame, properties, body = msg
                if not method_frame and not properties and not body:
                    raise RabbitTimedOutException("Operation timeout reached.")

                msgs += 1
                self.inbound += 1
                self.channel.basic_ack(method_frame.delivery_tag)

                if handler:
                    #body is of type 'bytes' in Python 3+
                    handler(body)
                elif not max_messages:
                    break

                #Stop consuming if message limit reached
                if msgs == max_messages:
                    break
        except pika.exceptions.AMQPError as exc:
            LOGGER.error(exc)
        finally:
            self.channel.cancel()

        if not msgs:
            raise RabbitConsumerException('Consumer cancelled prior to timeout.')

        return body


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

    def start_subscriber(self, queue: RabbitQueue, client=RabbitClient):
        """
            Connect to Castor service and create a queue

            Throws:
                An exception if connection attempt is not successful

            Returns:
                Nothing
        """
        self.subscriber = client(self.context)
        self.subscriber.start(subscribe=queue)

    def get_subscribe_queue(self):
        return self.subscriber.get_subscribe_queue()

    def start_publisher(self, queue: RabbitQueue, client=RabbitClient):
        """
            Connect to Castor service and create a queue

            Throws:
                An exception if connection attempt is not successful

            Returns:
                Nothing
        """
        self.publisher = client(self.context)
        self.publisher.start(publish=queue)

    def send_message(self, message, queue: RabbitQueue = None):
        """
            Publish a message to Castor service

            Throws:
                An exception if publish is not successful

            Returns:
                Nothing
        """
        self.publisher.publish(message, queue)

    def receive_message(self, handler, timeout: int, max_messages: int):
        """
            Receive messages from Castor service

            Throws:
                An exception if receive is not successful

            Returns:
                Nothing
        """
        self.subscriber.receive(handler, timeout, max_messages)

    def internal_handler(self, message):
        """
            Handler for invoke_service method

            Throws:
                Nothing

            Returns:
                Nothing
        """
        self.last_recv_msg = message

    def invoke_service(self, message, timeout: int = 30):
        """
            Publish a message and receive a reply

            Throws:
                An exception if not successful or timedout

            Returns:
                The reply dictionary
        """
        self.last_recv_msg = None
        LOGGER.debug(f"Sending message: {message}")
        self.send_message(message)

        LOGGER.debug("Waiting for reply...")
        #Now wait for the reply
        self.subscriber.receive(self.internal_handler, timeout, 1)
        LOGGER.debug(f"Received: {self.last_recv_msg}")
        return self.last_recv_msg

    def stop(self):
        """
            Close connection to service

            Throws:
                An exception if not successful

            Returns:
                Nothing
        """
        self.subscriber.stop()
        self.publisher.stop()
