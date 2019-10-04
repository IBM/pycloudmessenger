#!/usr/bin/env python3
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

Please note that the following code was developed for the project MUSKETEER
in DRL funded by the European Union under the Horizon 2020 Program.
"""

# pylint: disable=R0903, R0913

import json
import logging
from enum import Enum
import requests
import pycloudmessenger.utils as utils
import pycloudmessenger.rabbitmq as rabbitmq
import pycloudmessenger.serializer as serializer
import pycloudmessenger.ffl.message_catalog as catalog

logging.getLogger("pika").setLevel(logging.WARNING)


class Notification(str, Enum):
    aggregator_started = 'aggregator_started'
    aggregator_stopped = 'aggregator_stopped'
    participant_joined = 'participant_joined'
    participant_updated = 'participant_updated'
    participant_left = 'participant_left'


class Context(rabbitmq.RabbitContext):
    '''Holds connection details for an FFL service'''

class TimedOutException(rabbitmq.RabbitTimedOutException):
    '''Over-ride exception'''

class ConsumerException(rabbitmq.RabbitConsumerException):
    '''Over-ride exception'''


class Messenger(rabbitmq.RabbitDualClient):
    '''Communicates with an FFL service'''

    def __init__(self, context: Context, publish_queue: str = None,
                 subscribe_queue: str = None, max_msg_size: int = 2*1024*1024):
        '''Class initializer'''
        super(Messenger, self).__init__(context)

        #Max size of a message for dispatch
        self.max_msg_size = max_msg_size

        #Keep a copy here - lots of re-use
        self.timeout = context.timeout()

        if not publish_queue:
            #Publish not over-ridden so use context version
            publish_queue = context.feeds()

        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue))

        #Initialise the catalog with the target subscribe queue
        self.catalog = catalog.MessageCatalog(context.user(), self.get_subscribe_queue())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def _send(self, message: dict, queue: str = None) -> dict:
        '''
        Send a message and return immediately
        Throws: An exception on failure
        Returns: dict
        '''
        message = serializer.Serializer.serialize(message)
        if len(message) > self.max_msg_size:
            raise BufferError(f"Messenger: payload too large: {len(message)}.")

        pub_queue = rabbitmq.RabbitQueue(queue) if queue else None
        super(Messenger, self).send_message(message, pub_queue)

    def receive(self, timeout: int = 0) -> dict:
        '''
        Wait for timeout seconds for a message to arrive
        Throws: An exception on failure
        Returns: dict
        '''
        if not timeout:
            timeout = self.timeout

        try:
            super(Messenger, self).receive_message(self.internal_handler, timeout, 1)
        except rabbitmq.RabbitTimedOutException as exc:
            raise TimedOutException(exc) from exc
        except rabbitmq.RabbitConsumerException as exc:
            raise ConsumerException(exc) from exc
        return serializer.Serializer.deserialize(self.last_recv_msg)

    def _invoke_service(self, message: dict, timeout: int = 0) -> dict:
        '''
        Send a message and wait for a reply
        Throws: An exception on failure
        Returns: dict
        '''

        result = None
        if not timeout:
            timeout = self.timeout

        try:
            message = serializer.Serializer.serialize(message)
            if len(message) > self.max_msg_size:
                raise BufferError(f"Messenger: payload too large: {len(message)}.")
            result = super(Messenger, self).invoke_service(message, timeout)
        except rabbitmq.RabbitTimedOutException as exc:
            raise TimedOutException(exc) from exc
        except rabbitmq.RabbitConsumerException as exc:
            raise ConsumerException(exc) from exc

        if not result:
            raise Exception(f"Malformed object: None")
        result = serializer.Serializer.deserialize(result)

        if 'error' in result:
            raise Exception(result['error'])

        if 'calls' not in result:
            raise Exception(f"Malformed object: {result}")

        results = result['calls'][0]['count'] #calls[0] will always succeed
        return result['calls'][0]['data'] if results else None

    def _dispatch_model(self, model: dict = None) -> dict:
        '''
        Dispatch a model and determine its download location
        Throws: An exception on failure
        Returns: dict
        '''

        if not model:
            return {}

        #First, obtain the upload location/keys
        message = self.catalog.msg_bin_uploader()
        upload_info = self._invoke_service(message)

        #And then perform the upload
        response = requests.post(
                        upload_info['url'],
                        files={'file': json.dumps(model)},
                        data=upload_info['fields'],
                        headers=None)

        if not response.ok:
            raise Exception(f'Upload Error: {response.status_code}')

        if 'key' not in upload_info['fields']:
            raise Exception('Malformed URL.')

        #Now obtain the download location/keys
        message = self.catalog.msg_bin_downloader(upload_info['fields']['key'])
        download_info = self._invoke_service(message)
        return {'url': download_info}

    ######## Public methods

    def user_create(self, user_name: str, password: str, organisation: str) -> dict:
        '''
        Register as a new user on the platformr
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_user_create(user_name, password, organisation)
        return self._invoke_service(message)

    def user_assignments(self) -> dict:
        '''
        Return all tasks joined by the current user
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_user_assignments()
        return self._invoke_service(message)

    def task_assignment_info(self, task_name: str) -> dict:
        '''
        As a task participant, get my participation details
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_assignment_info(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_assignment_join(self, task_name: str) -> dict:
        '''
        As a potential task participant, try to join the task
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_join(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_assignment_update(self, task_name: str, status: str, model: dict = None) -> None:
        '''
        Sends an update, including a model dict, no reply wanted
        Throws: An exception on failure
        Returns: Nothing
        '''

        model_message = self._dispatch_model(model)

        message = self.catalog.msg_task_assignment_update(
                        task_name, status, model_message)
        self._send(message)

    def task_assignment_wait(self, timeout: int = 0) -> dict:
        '''
        Wait for a message, until timeout seconds
        Throws: An exception on failure
        Returns: dict
        '''
        return self.receive(timeout)

    def task_assignments(self, task_name: str) -> dict:
        '''
        Return all assignments for the owned task
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_assignments(task_name)
        return self._invoke_service(message)

    def task_listing(self) -> dict:
        '''
        Return a list of all tasks available
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_listing()
        return self._invoke_service(message)

    def task_create(self, task_name: str, algorithm: str, quorum: int, adhoc: dict) -> dict:
        '''
        A new task created by the current user
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_create(task_name, algorithm, quorum, adhoc)
        message = self._invoke_service(message)
        return message[0]

    def task_update(self, task_name: str, status: str, algorithm: str = None,
                    quorum: int = -1, adhoc: dict = None) -> dict:
        '''
        Change task details
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_update(task_name, algorithm, quorum, adhoc, status)
        return self._invoke_service(message)

    def task_info(self, task_name: str) -> dict:
        '''
        Return info on a task
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_info(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_quit(self, task_name: str) -> dict:
        '''
        As a task participant, leave the task
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_quit(task_name)
        return self._invoke_service(message)

    def task_start(self, task_name: str, model: dict = None) -> None:
        '''
        As a task owner, start the task
        Throws: An exception on failure
        Returns: Nothing
        '''
        model_message = self._dispatch_model(model)
        message = self.catalog.msg_task_start(task_name, model_message)
        self._send(message)

    def task_stop(self, task_name: str) -> None:
        '''
        As a task owner, stop the task
        Throws: An exception on failure
        Returns: dict
        '''
        message = self.catalog.msg_task_stop(task_name)
        self._send(message)


class BasicParticipant():
    '''Base class for an FFL user/participant'''

    def __init__(self, context: Context, task_name: str = None,
                 download_models: bool = True):
        if not context:
            raise Exception('Credentials must be specified.')

        self.messenger = None

        #List of messages/models downloaded
        self.model_files = []

        self.context = context
        self.task_name = task_name
        self.queue = None
        self.download = download_models

    def __enter__(self):
        return self.connect()

    def __exit__(self, *args):
        self.close()

    def connect(self):
        self.messenger = Messenger(self.context, subscribe_queue=self.queue)
        return self

    def close(self) -> None:
        self.messenger.stop()
        self.messenger = None

    def _receive(self, timeout: int = 0, flavours: list = None) -> dict:
        msg = self.messenger.receive(timeout)

        if 'notification' not in msg:
            raise Exception(f"Malformed object: {msg}")

        if 'type' not in msg['notification']:
            raise Exception(f"Malformed object: {msg['notification']}")

        try:
            if Notification(msg['notification']['type']) not in flavours:
                raise ValueError
        except:
            raise Exception(f"Unexpected notification " \
                f"{msg['notification']['type']}, expecting {flavours}")

        if self.download:
            msg = self.get_model(msg)
        return msg

    def get_model(self, model_info: dict) -> dict:
        if 'params' in model_info:
            if model_info['params'] and 'url' in model_info['params']:
                self.model_files.append(utils.FileDownloader(model_info['params']['url']))
                model_info['params'].update({'model': self.model_files[-1].name()})
        return model_info


class Participant(BasicParticipant):
    '''An FFL task participant'''
    def __init__(self, context: Context, task_name: str = None,
                 download_models: bool = True):
        super().__init__(context, task_name, download_models)

        messenger = Messenger(self.context)
        result = messenger.task_assignment_info(self.task_name)

        if 'QUEUE' not in result:
            raise Exception("Task not joined by this user.")

        self.queue = result['QUEUE']
        messenger.stop()

    def send(self, status: str, model: dict = None) -> None:
        self.model_files.clear()
        self.messenger.task_assignment_update(self.task_name, status, model)

    def receive(self, timeout: int = 0) -> dict:
        return self._receive(timeout, [Notification.aggregator_started,
                                       Notification.aggregator_stopped])

    def leave_task(self):
        return self.messenger.task_quit(self.task_name)


class Aggregator(BasicParticipant):
    '''An FFL task aggregator'''
    def __init__(self, context: Context, task_name: str = None,
                 download_models: bool = True):
        super().__init__(context, task_name, download_models)

        messenger = Messenger(self.context)
        result = messenger.task_info(self.task_name)

        if 'QUEUE' not in result:
            raise Exception("Task not created by this user.")

        self.queue = result['QUEUE']
        messenger.stop()

    def send(self, model: dict = None) -> None:
        self.model_files.clear()
        self.messenger.task_start(self.task_name, model)

    def receive(self, timeout: int = 0) -> dict:
        return self._receive(timeout, [Notification.participant_joined,
                                       Notification.participant_updated,
                                       Notification.participant_left])

    def task_assignments(self) -> dict:
        return self.messenger.task_assignments(self.task_name)

    def task_update(self, status: str, algorithm: str = None,
                    quorum: int = -1, adhoc: dict = None) -> dict:
        return self.messenger.task_update(self.task_name, status, algorithm, quorum, adhoc)

    def stop_task(self) -> None:
        self.messenger.task_stop(self.task_name)


class User(BasicParticipant):
    '''A generic FFL user'''

    def create_user(self, user_name: str, password: str, organisation: str) -> dict:
        return self.messenger.user_create(user_name, password, organisation)

    def create_task(self, algorithm: str, quorum: int, adhoc: dict) -> dict:
        return self.messenger.task_create(self.task_name, algorithm, quorum, adhoc)

    def join_task(self) -> dict:
        return self.messenger.task_assignment_join(self.task_name)

    def task_info(self) -> dict:
        return self.messenger.task_info(self.task_name)

    def get_tasks(self) -> dict:
        return self.messenger.task_listing()
