#!/usr/bin/env python3
#author markpurcell@ie.ibm.com

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

        #Standard serializer should fail for numpy
        with self.assertRaises(TypeError):
            serializer.Serializer.serialize(a)

        b = serializer.JsonPickleSerializer.serialize(a)
        c = serializer.JsonPickleSerializer.deserialize(b)
        self.assertTrue(np.array_equal(a, c))

        d = serializer.Serializer.serialize(b)
        e = serializer.Serializer.deserialize(d)
        f = serializer.JsonPickleSerializer.deserialize(e)
        self.assertTrue(np.array_equal(a, f))

    #@unittest.skip("temporarily skipping")
    def test_users(self):
        context = rabbitmq.RabbitContext.from_credentials_file(self.credentials)

        try:
            with rabbitmq.RabbitClient(context) as client:
                client.start(publish=rabbitmq.RabbitQueue(context.feeds(), purge=True),
                             subscribe=rabbitmq.RabbitQueue(context.replies()))
                message = {'action': 'Outbound', 'payload': 'some data'}
                LOGGER.info(f'Client sending: {message}')
                client.publish(json.dumps(message))

                #Now start the server side and handle the message
                with rabbitmq.RabbitClient(context) as server:
                    server.start(subscribe=rabbitmq.RabbitQueue(context.feeds()))

                    recv = server.receive()
                    LOGGER.info(f'Server received: {recv}')

                    #And send a reply to the client
                    reply = {'action': 'Inbound', 'reply': 'the reply'}
                    LOGGER.info(f'Server sending: {reply}')
                    server.publish(json.dumps(reply), rabbitmq.RabbitQueue(context.replies()))

                #Now catch the reply in the client
                message = client.receive()
                LOGGER.info(f"Client received: {message}")
        except Exception as err:
            LOGGER.info("Error %r", err)
            raise err

