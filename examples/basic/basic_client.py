#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""Basic RabbitMQ sample program.
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
import argparse
import logging
import json
import pycloudmessenger.rabbitmq as rabbitmq

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)
logging.getLogger("pika").setLevel(logging.WARNING)


class ServerMessageHandler():
    def __init(self):
        self.message = None

    def handler(self, message):
        self.message = json.loads(message)
        LOGGER.info(f'server got {message}')


def main():
    parser = argparse.ArgumentParser(description='Messaging Client')
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--broker_user', help='Defaults to credentials file')
    parser.add_argument('--broker_password', help='Defaults to credentials file')
    cmdline = parser.parse_args()

    LOGGER.info("Starting...")
    context = rabbitmq.RabbitContext.from_credentials_file(cmdline.credentials, cmdline.broker_user, cmdline.broker_password)

    try:
        with rabbitmq.RabbitClient(context) as client:
            client.start(publish=rabbitmq.RabbitQueue(context.feeds(), purge=True), subscribe=rabbitmq.RabbitQueue(context.replies()))
            message = {'action': 'Outbound', 'payload': 'some data'}
            LOGGER.info(f'sending {message}')
            client.publish(json.dumps(message))

            with rabbitmq.RabbitClient(context) as server:
                server.start(subscribe=rabbitmq.RabbitQueue(context.feeds()))

                mh = ServerMessageHandler()
                server.receive(mh.handler, max_messages=1)

                #And send a reply to the client
                reply = {'action': 'Inbound', 'reply': '0'*1024000}
                server.publish(json.dumps(reply), rabbitmq.RabbitQueue(context.replies()))

            #Now catch the reply in the client
            message = client.receive(timeout=0)#.01)
            #LOGGER.info(f"client got {message}")
    except Exception as err:
        LOGGER.info("Error %r", err)
        raise err

if __name__ == '__main__':
    main()
