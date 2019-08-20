#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""FFL protocol handler.
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
import pycloudmessenger.ffl.serializer as serializer
import pycloudmessenger.ffl.message_catalog as catalog

logging.getLogger("pika").setLevel(logging.WARNING)


class Context(rabbitmq.RabbitContext):
    """
        Holds connection details for an FFL service
    """


class Messenger(rabbitmq.RabbitDualClient):
    """
        Communicates with an FFL service
    """
    def __init__(self, context: Context, publish_queue: str = None, subscribe_queue: str = None):
        """
            Class initializer
        """
        super(Messenger, self).__init__(context)

        #Keep a copy here - lots of re-use
        self.timeout = context.timeout()

        #Publish not over-ridden so use context version
        if not publish_queue:
            publish_queue = context.feeds()

        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue))

        #Initialise the catalog with the target subscribe queue
        self.catalog = catalog.MessageCatalog(self.get_subscribe_queue())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def _invoke_service(self, message: dict) -> dict:
        result = super(Messenger, self).invoke_service(serializer.Serializer.serialize(message), self.timeout)
        if not result:
            raise Exception(f"Malformed object: None")

        result = serializer.Serializer.deserialize(result)

        if 'error' in result:
            raise Exception(result['error'])

        if 'calls' not in result:
            raise Exception(f"Malformed object: {result['error']}")

        results = result['calls'][0]['count'] #calls[0] will always succeed
        return result['calls'][0]['data'] if results else None


    ######## Public methods

    def user_create(self, user_name: str, password: str) -> dict:
        message = self.catalog.msg_user_create(user_name, password)
        return self._invoke_service(message)

    def user_assignments(self) -> dict:
        message = self.catalog.msg_user_assignments(self.context.user())
        return self._invoke_service(message)

    def task_listing(self) -> dict:
        message = self.catalog.msg_task_listing()
        return self._invoke_service(message)

    def task_create(self, task_name: str, algorithm: str, quorum: int, adhoc: dict) -> dict:
        message = self.catalog.msg_task_create(task_name, self.context.user(), algorithm, quorum, adhoc)
        return self._invoke_service(message)

    def task_update(self, task_name: str, algorithm: str, quorum: int, adhoc: dict, status: str) -> dict:
        message = self.catalog.msg_task_update(task_name, algorithm, quorum, adhoc, status)
        return self._invoke_service(message)

    def task_info(self, task_name: str) -> dict:
        message = self.catalog.msg_task_info(task_name)
        return self._invoke_service(message)

    def task_assignments(self, task_name: str) -> dict:
        message = self.catalog.msg_task_assignments(task_name, self.context.user())
        return self._invoke_service(message)

    def task_join(self, task_name: str) -> dict:
        message = self.catalog.msg_task_join(task_name, self.context.user())
        return self._invoke_service(message)

    def task_result(self, task_name: str, b64_result: str = None) -> dict:
        message = self.catalog.msg_task_result(task_name, self.context.user(), b64_result)
        return self._invoke_service(message)

