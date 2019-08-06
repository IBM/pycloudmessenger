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

        #If no subscribe queue, create a temporary, auto-delete queue
        exclusive = False if subscribe_queue else True

        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue, exclusive=exclusive))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue, durable=True))

        #Initialise the catalog with the target subscribe queue
        self.catalog = catalog.MessageCatalog(self.get_subscribe_queue())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def _invoke_service(self, message: dict) -> dict:
        return serializer.Serializer.deserialize(super(Messenger, self).invoke_service(serializer.Serializer.serialize(message), self.timeout))


    ######## Public methods

    def get_users(self) -> dict:
        message = self.catalog.msg_users()
        return self._invoke_service(message)

    def create_user(self, user_name) -> dict:
        message = self.catalog.msg_create_user(user_name)
        return self._invoke_service(message)

    def get_tasks(self) -> dict:
        message = self.catalog.msg_tasks()
        return self._invoke_service(message)

    def create_task(self, task_name: str, algorithm: str, quorum: int, adhoc: dict) -> dict:
        message = self.catalog.msg_create_task(task_name, algorithm, quorum, adhoc)
        return self._invoke_service(message)

    def update_task(self, task_name: str, algorithm: str, quorum: int, adhoc: dict, status: str) -> dict:
        message = self.catalog.msg_update_user(task_name, algorithm, quorum, adhoc, status)
        return self._invoke_service(message)

    def get_participants(self) -> dict:
        message = self.catalog.msg_participants()
        return self._invoke_service(message)

    def get_task_participants(self, task_name: str) -> dict:
        message = self.catalog.msg_task_participants(task_name)
        return self._invoke_service(message)
