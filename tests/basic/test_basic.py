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
"""
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by the European Union
under the Horizon 2020 Program.
The project started on 01/12/2018 and was completed on 30/11/2021. Thus, in accordance with article 30.3 of the
Multi-Beneficiary General Model Grant Agreement of the Program, the above limitations are in force until 30/11/2025.
"""

import argparse
import logging
import unittest
import json
import pytest
import numpy as np
import pycloudmessenger.rabbitmq as rabbitmq
import pycloudmessenger.serializer as serializer

#Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)
logging.getLogger("pika").setLevel(logging.CRITICAL)

@pytest.mark.usefixtures("credentials","feed_queue","reply_queue")
#@pytest.mark.usefixtures("credentials")
class MessengerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_numpy_serializer(self):
        a = np.array([2,3,4])

        serializer1 = serializer.JsonSerializer()

        #Standard serializer should fail for numpy
        with self.assertRaises(TypeError):
            serializer1.serialize(a)

        serializer2 = serializer.JsonPickleSerializer()
        b = serializer2.serialize(a)
        c = serializer2.deserialize(b)
        self.assertTrue(np.array_equal(a, c))

        d = serializer2.serialize(b)
        e = serializer2.deserialize(d)
        f = serializer2.deserialize(e)
        self.assertTrue(np.array_equal(a, f))

    #@unittest.skip("temporarily skipping")
    def test_timeout(self):
        context = rabbitmq.RabbitContext.from_credentials_file(self.credentials)

        with rabbitmq.RabbitClient(context) as client:
            client.start(publish=rabbitmq.RabbitQueue(context.feeds(), purge=True, durable=True),
                         subscribe=rabbitmq.RabbitQueue(context.replies(), durable=True))
            with self.assertRaises(Exception):
                message = client.receive(timeout=1)

    #@unittest.skip("temporarily skipping")
    def test_round_trip(self):
        context = rabbitmq.RabbitContext.from_credentials_file(self.credentials)

        with rabbitmq.RabbitClient(context) as client:
            client.start(publish=rabbitmq.RabbitQueue(context.feeds(), purge=True, durable=True),
                         subscribe=rabbitmq.RabbitQueue(context.replies(), durable=True))
            message = {'action': 'Outbound', 'payload': '0'*1024*100}
            #LOGGER.info(f'Client sending: {message}')
            client.publish(json.dumps(message))
            #LOGGER.info(f'Client sent: {message}')

            #Now start the server side and handle the message
            with rabbitmq.RabbitClient(context) as server:
                server.start(subscribe=rabbitmq.RabbitQueue(context.feeds()))

                recv = server.receive(timeout=.01)
                #LOGGER.info(f'Server received: {recv}')

                #And send a reply to the client
                reply = {'action': 'Inbound', 'reply': 'the reply'}
                LOGGER.info(f'Server sending: {reply}')
                server.publish(json.dumps(reply), rabbitmq.RabbitQueue(context.replies()))

            #Now catch the reply in the client
            message = client.receive(timeout=.1)
            LOGGER.info(f"Client received: {message}")


    #@unittest.skip("temporarily skipping")
    def test_round_trip(self):
        context = rabbitmq.RabbitContext.from_credentials_file(self.credentials)

        with rabbitmq.RabbitDualClient(context) as client:
            client.start_subscriber(queue=rabbitmq.RabbitQueue(context.replies(), durable=True))
            client.start_publisher(queue=rabbitmq.RabbitQueue(context.feeds(), purge=True, durable=True))
            client.send_message(json.dumps({'blah': 'blah'}))

            with rabbitmq.RabbitDualClient(context) as server:
                server.start_publisher(queue=rabbitmq.RabbitQueue(context.replies()))
                server.start_subscriber(queue=rabbitmq.RabbitQueue(context.feeds()))
                message = server.receive_message(5)
                LOGGER.info(message)
