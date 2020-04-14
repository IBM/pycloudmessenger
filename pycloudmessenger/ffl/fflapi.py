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

from typing import NamedTuple
import logging
import requests
import pycloudmessenger.utils as utils
import pycloudmessenger.rabbitmq as rabbitmq
import pycloudmessenger.serializer as serializer
import pycloudmessenger.ffl.message_catalog as catalog
import pycloudmessenger.ffl.abstractions as fflabc

logging.getLogger("pika").setLevel(logging.CRITICAL)


class ModelWrapper(NamedTuple):
    """Class for packaging a model prior to dispatch"""
    wrapping: dict
    blob: str

    @classmethod
    def wrap(cls, model: any, encoder: serializer.SerializerABC = None) -> dict:
        """ Wrap content in meta data """
        if encoder and model:
            blob = encoder.serialize(model)
        else:
            blob = model
        return ModelWrapper({'model': blob}, blob)

    @classmethod
    def unwrap(cls, model: dict, encoder: serializer.SerializerABC = None) -> any:
        """ Unwrap meta data """
        blob = None
        if model and 'model' in model:
            if isinstance(model['model'], dict):
                model = model['model']
            elif encoder:
                blob = encoder.deserialize(model['model'])
        return ModelWrapper(model, blob)


class Context(rabbitmq.RabbitContext):
    """
    Class holding connection details for an FFL service
        :param download_models: whether downloaded model file name or model url
                                should be returned by receive function
        :type download_models: `bool`
        :param dispatch_threshold: max model size to embed, or upload
        :type dispatch_threshold: `int`
    """
    def __init__(self, args: dict, user: str = None, password: str = None,
                 encoder: serializer.SerializerABC = serializer.JsonPickleSerializer,
                 download_models: bool = True, dispatch_threshold: int = 1024*1024*5):
        super().__init__(args, user, password)
        self.args['download_models'] = download_models
        self.args['dispatch_threshold'] = dispatch_threshold
        self.model_encoder = encoder()
        self.encoder = serializer.JsonPickleSerializer()

    def serializer(self):
        """ Return serializer"""
        return self.encoder

    def model_serializer(self):
        """ Return serializer"""
        return self.model_encoder

    def download_models(self):
        """ Return setting, default to False"""
        return self.args.get('download_models', False)

    def dispatch_threshold(self):
        """ Return setting default to None"""
        return self.args.get('dispatch_threshold', None)


class TimedOutException(rabbitmq.RabbitTimedOutException):
    """Over-ride exception"""


class ConsumerException(rabbitmq.RabbitConsumerException):
    """Over-ride exception"""


class Messenger(rabbitmq.RabbitDualClient):
    """
    Class for communicating with an FFL service
    """

    def __init__(self, context: Context, publish_queue: str = None,
                 subscribe_queue: str = None):
        """
        Class initializer
        :param context: connection details
        :type context: :class:`.Context`
        :param publish_queue: name of the publish queue
        :type publish_queue: `str`
        """
        super(Messenger, self).__init__(context)

        # Keep a copy here - lots of re-use
        self.timeout = context.timeout()

        # Initialise the catalog
        self.catalog = catalog.MessageCatalog(context.user())

        if not publish_queue:
            # Publish not over-ridden so use context version
            publish_queue = context.feeds()

        self.start_subscriber(queue=rabbitmq.RabbitQueue(subscribe_queue))
        self.start_publisher(queue=rabbitmq.RabbitQueue(publish_queue))

        if subscribe_queue:
            self.command_queue = super().mktemp_queue()
        else:
            self.command_queue = self.subscriber.sub_queue

        # List of messages/models downloaded
        self.model_files = []

    def __enter__(self):
        """
        Context manager enters.
        Throws: An exception on failure
        :return: self
        :rtype: :class:`.Messenger`
        """
        return self

    def __exit__(self, *args):
        """
        Context manager exits - call stop.
        Throws: An exception on failure
        """
        self.stop()

    def _send(self, message: dict, queue: str = None) -> None:
        """
        Send a message and return immediately.
        Throws: An exception on failure
        :param message: message to be sent
        :type message: `dict`
        :param queue: name of the publish queue
        :type queue: `str`
        """
        message = self.context.serializer().serialize(message)
        pub_queue = rabbitmq.RabbitQueue(queue) if queue else None
        super(Messenger, self).send_message(message, pub_queue)

    def receive(self, timeout: int = 0) -> dict:
        """
        Wait for a message to arrive or until timeout.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `dict`
        """
        if not timeout:
            timeout = self.timeout

        try:
            super(Messenger, self).receive_message(self.internal_handler, timeout, 1)
        except rabbitmq.RabbitTimedOutException as exc:
            raise TimedOutException(exc) from exc
        except rabbitmq.RabbitConsumerException as exc:
            raise ConsumerException(exc) from exc
        return self.context.serializer().deserialize(self.last_recv_msg)

    def _invoke_service(self, message: dict, timeout: int = 0) -> dict:
        """
        Send a message and wait for a reply or until timeout.
        Throws: An exception on failure
        :param message: message to be sent
        :type message: `dict`
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `dict`
        """
        if not timeout:
            timeout = self.timeout

        try:
            #Need a reply, so add this to the request message
            message = self.catalog.msg_assign_reply(message, self.command_queue.name)

            message = self.context.serializer().serialize(message)
            result = super(Messenger, self).invoke_service(message, timeout,
                                                           queue=self.command_queue)
        except rabbitmq.RabbitTimedOutException as exc:
            raise TimedOutException(exc) from exc
        except rabbitmq.RabbitConsumerException as exc:
            raise ConsumerException(exc) from exc

        if not result:
            raise Exception(f"Malformed object: None")
        result = self.context.serializer().deserialize(result)

        if 'error' in result:
            raise Exception(f"Server Error ({result['activation']}): {result['error']}")

        if 'calls' not in result:
            raise Exception(f"Malformed object: {result}")

        results = result['calls'][0]['count']  # calls[0] will always succeed
        return result['calls'][0]['data'] if results else []

    def _dispatch_model(self, task_name: str = None, model: dict = None) -> dict:
        """
        Dispatch a model and determine its download location.
        Throws: An exception on failure
        :param model: model to be sent
        :type model: `dict`
        :return: download location information
        :rtype: `dict`
        """

        wrapper = ModelWrapper.wrap(model, self.context.model_serializer())
        if not model:
            return wrapper.wrapping

        # First, obtain the upload location/keys
        if task_name:
            message = self.catalog.msg_bin_upload_object(task_name)
        else:
            if len(wrapper.blob) > self.context.dispatch_threshold():
                message = self.catalog.msg_bin_uploader()
            else:
                #Small model - embed it
                return wrapper.wrapping

        upload_info = self._invoke_service(message)

        if 'key' not in upload_info['fields']:
            raise Exception('Update Error: Malformed URL.')

        key = upload_info['fields']['key']

        try:
            with rabbitmq.RabbitHeartbeat(self.subscriber):
                # And then perform the upload
                response = requests.post(upload_info['url'],
                                         files={'file': wrapper.blob},
                                         data=upload_info['fields'],
                                         headers=None)
                response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise Exception(f'Update Error: {err.response.status_code}')
        except:
            raise Exception(f'General Update Error')

        # Now obtain the download location/keys
        if task_name:
            message = self.catalog.msg_bin_download_object(key)
        else:
            message = self.catalog.msg_bin_downloader(key)

        download_info = self._invoke_service(message)
        wrapper = ModelWrapper.wrap({'url': download_info, 'key': key})
        return wrapper.wrapping

    # Public methods

    def user_create(self, user_name: str, password: str, organisation: str) -> dict:
        """
        Register a new user on the platform.
        Throws: An exception on failure
        :param user_name: user name (must be a non-empty string and unique;
                                     if a user with this name has registered
                                     before, an exception is thrown).
        :type user_name: `str`
        :param password: password (must be a non-empty string)
        :type password: `str`
        :param organisation: name of the user's organisation
        :type organisation: `str`
        """
        message = self.catalog.msg_user_create(user_name, password, organisation)
        return self._invoke_service(message)

    def user_assignments(self) -> list:
        """
        Returns all the tasks the user is participating in.
        :return: list of all the tasks, each of which is a dictionary
        :rtype: `list`
        """
        message = self.catalog.msg_user_assignments()
        return self._invoke_service(message)

    def task_assignment_info(self, task_name: str) -> dict:
        """
        Returns the details of the participant's task assignment.
        :return: details of the task assignment
        :rtype: `dict`
        """
        message = self.catalog.msg_task_assignment_info(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_assignment_join(self, task_name: str) -> dict:
        """
        As a potential task participant, try to join the task.
        This will fail if the task status isn't 'CREATED'.
        Throws: An exception on failure
        :param task_name: name of the task to be joined
        :type task_name: `str`
        :return: details of the task assignment
        :rtype: `dict`
        """
        message = self.catalog.msg_task_join(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_assignment_update(self, task_name: str, model: dict = None) -> None:
        """
        Sends an update with the respect to the given task assignment.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param model: update to be sent
        :type model: `dict`
        """
        self.model_files.clear()
        model_message = self._dispatch_model(model=model)

        message = self.catalog.msg_task_assignment_update(
                        task_name, model=model_message)
        self._send(message)

    def task_assignments(self, task_name: str) -> list:
        """
        Returns a list with all the assignments for the owned task.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :return: list of all the participants assigned to the task
        :rtype: `list`
        """
        message = self.catalog.msg_task_assignments(task_name)
        return self._invoke_service(message)

    def task_listing(self) -> dict:
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        message = self.catalog.msg_task_listing()
        return self._invoke_service(message)

    def task_create(self, task_name: str, topology: str, definition: dict) -> dict:
        """
        Creates a task with the given definition and returns a dictionary with the
        details of the created tasks.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: definition of the task to be created
        :type definition: `dict`
        :return: details of the created task
        :rtype: `dict`
        """
        message = self.catalog.msg_task_create(task_name, topology, definition)
        message = self._invoke_service(message)
        return message[0]

    def task_update(self, task_name: str, status: str, topology: str = None,
                    definition: dict = None) -> dict:
        """
        Updates a task with the given details.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param status: task status (must be either 'CREATED', 'STARTED', 'FAILED', 'COMPLETE')
        :type status: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: task definition
        :type definition: `dict`
        :return: details of the updated task
        :rtype: `dict`
        """
        message = self.catalog.msg_task_update(task_name, topology, definition, status)
        return self._invoke_service(message)

    def task_info(self, task_name: str) -> dict:
        """
        Returns the details of a given task.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :return: details of the task
        :rtype: `dict`
        """
        message = self.catalog.msg_task_info(task_name)
        message = self._invoke_service(message)
        return message[0]

    def task_quit(self, task_name: str) -> None:
        """
        As a task participant, leave the given task.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        """
        message = self.catalog.msg_task_quit(task_name)
        return self._invoke_service(message)

    def task_start(self, task_name: str, model: dict = None, participant: str = None) -> None:
        """
        As a task creator, start the given task and optionally send message
        including the given model to all task
        participants. The status of the task will be changed to 'STARTED'.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param model: model to be sent as part of the message
        :type model: `dict`
        """
        self.model_files.clear()
        model_message = self._dispatch_model(model=model)
        message = self.catalog.msg_task_start(task_name, model_message, participant)
        self._send(message)

    def task_stop(self, task_name: str, model: dict = None) -> None:
        """
        As a task creator, stop the given task.
        The status of the task will be changed to 'COMPLETE'.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        """
        model_message = self._dispatch_model(task_name=task_name, model=model)
        message = self.catalog.msg_task_stop(task_name, model_message)
        return self._invoke_service(message)


    def task_notification(self, timeout: int = 0, flavours: list = None) -> dict:
        """
        Wait for a message to arrive or until timeout.
        If message is received, check whether its notification type matches
        element in given list of notification flavours.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :param flavours: expected notification types
        :type flavours: `list`
        :return: received message
        :rtype: `dict`
        """
        msg = self.receive(timeout)

        if 'notification' not in msg:
            raise Exception(f"Malformed object: {msg}")

        if 'type' not in msg['notification']:
            raise Exception(f"Malformed object: {msg['notification']}")

        try:
            if fflabc.Notification(msg['notification']['type']) not in flavours:
                raise ValueError
        except:
            raise Exception(f"Unexpected notification " \
                f"{msg['notification']['type']}, expecting {flavours}")

        if 'params' not in msg:
            raise Exception(f"Malformed payload: {msg}")

        model = None

        if msg['params']:
            model = ModelWrapper.unwrap(msg['params'], self.context.model_serializer())

            if model.blob:
                #Embedded model
                model = model.blob
            else:
                #Download from bin store
                url = model.wrapping.get('url', None)
                if not url:
                    raise Exception(f"Malformed wrapping: {model.wrapping}")

                #Download from bin store
                if self.context.download_models():
                    self.model_files.append(utils.FileDownloader(url))

                    with open(self.model_files[-1].name(), 'rb') as model_file:
                        buff = model_file.read()
                        model = self.context.model_serializer().deserialize(buff)
                else:
                    #Let user decide what to do
                    model = model.wrapping

        return fflabc.Response(msg['notification'], model)


class BasicParticipant():
    """ Base class for an FFL general user """

    def __init__(self, context: Context):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: connection details
        :type context: :class:`.Context`
        """
        if not context:
            raise Exception('Credentials must be specified.')

        self.messenger = None
        self.context = context
        self.queue = None

    def __enter__(self):
        """
        Context manager enters - call connect.
        Throws: An exception on failure
        :return: self
        :rtype: :class:`.BasicParticipant`
        """
        return self.connect()

    def __exit__(self, *args):
        """
        Context manager exits - call close
        Throws: An exception on failure
        """
        self.close()

    def connect(self):
        """
        Connect to the messaging system.
        Throws: An exception on failure
        :return: self
        :rtype: :class:`.BasicParticipant`
        """
        self.messenger = Messenger(self.context, subscribe_queue=self.queue)
        return self

    def close(self) -> None:
        """
        Close the connection to the messaging system.
        Throws: An exception on failure
        """
        self.messenger.stop()
        self.messenger = None


class User(fflabc.AbstractUser, BasicParticipant):
    """ Class that allows a general user to avail of the FFL platform services """

    def create_user(self, user_name: str, password: str, organisation: str) -> dict:
        """
        Register a new user on the platform.
        Throws: An exception on failure
        :param user_name: user name (must be a non-empty string and unique;
                                     if a user with this name has registered
                                     before, an exception is thrown).
        :type user_name: `str`
        :param password: password (must be a non-empty string)
        :type password: `str`
        :param organisation: name of the user's organisation
        :type organisation: `str`
        """
        return self.messenger.user_create(user_name, password, organisation)

    def create_task(self, task_name: str, topology: str, definition: dict) -> dict:
        """
        Creates a task with the given definition and returns a dictionary
        with the details of the created tasks.
        Throws: An exception on failure
        :param task_name: name of the task to create
        :type task_name: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: definition of the task to be created
        :type definition: `dict`
        :return: details of the created task
        :rtype: `dict`
        """
        return self.messenger.task_create(task_name, topology, definition)

    def join_task(self, task_name: str) -> dict:
        """
        As a potential task participant, try to join an existing task that has yet to start.
        Throws: An exception on failure
        :param task_name: name of the task to join
        :type task_name: `str`
        :return: details of the task assignment
        :rtype: `dict`
        """
        return self.messenger.task_assignment_join(task_name)

    def task_info(self, task_name: str) -> dict:
        """
        Returns the details of a given task.
        Throws: An exception on failure
        :param task_name: name of the task to join
        :type task_name: `str`
        :return: details of the task
        :rtype: `dict`
        """
        return self.messenger.task_info(task_name)

    def get_tasks(self) -> list:
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        return self.messenger.task_listing()

    def get_joined_tasks(self) -> list:
        """
        Returns a list with all the joined tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        return self.messenger.user_assignments()


class Participant(fflabc.AbstractParticipant, BasicParticipant):
    """ This class provides the functionality needed by the
        participants of a federated learning task.  """

    def __init__(self, context: Context, task_name: str = None):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: connection details
        :type context: :class:`.Context`
        :param task_name: name of the task (the user needs to be a participant of this task).
        :type task_name: `str`
        """
        super().__init__(context)

        self.task_name = task_name
        messenger = Messenger(self.context)
        result = messenger.task_assignment_info(self.task_name)

        if 'queue' not in result:
            raise Exception("Task not joined by this user.")

        self.queue = result['queue']
        messenger.stop()

    def send(self, message: dict = None) -> None:
        """
        Send a message to the aggregator and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent (needs to be serializable)
        :type message: `dict`
        """
        self.messenger.task_assignment_update(self.task_name, message)

    def receive(self, timeout: int = 0) -> fflabc.Response:
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `class Response`
        """
        return self.messenger.task_notification(timeout, [
                        fflabc.Notification.aggregator_started,
                        fflabc.Notification.aggregator_stopped
                ])

    def leave_task(self) -> None:
        """
        As a task participant, leave the given task.
        Throws: An exception on failure
        """
        return self.messenger.task_quit(self.task_name)


class Aggregator(fflabc.AbstractAggregator, BasicParticipant):
    """ This class provides the functionality needed by the
        aggregator of a federated learning task. """

    def __init__(self, context: Context, task_name: str = None):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: Connection details
        :type context: :class:`.Context`
        :param task_name: Name of the task (note: the user must be the creator of this task)
        :type task_name: `str`
        """
        super().__init__(context)

        self.task_name = task_name
        messenger = Messenger(self.context)

        # Get the task info for subscribe queue etc
        result = messenger.task_info(self.task_name)

        if 'status' in result and result['status'] == 'COMPLETE':
            raise Exception("Task is already finished.")

        if 'queue' not in result:
            raise Exception("Task not created by this user.")

        self.queue = result['queue']

        # Now get the list of already joined participants
        self.participants = {}

        assignments = messenger.task_assignments(self.task_name)
        for ass in assignments:
            self._add_participant(ass['participant'], ass)

        # Ready now for steady state modelling
        messenger.stop()

    def send(self, message: dict = None, participant: str = None) -> None:
        """
        Send a message to all task participants and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent (needs to be serializable)
        :type message: `dict`
        """
        self.messenger.task_start(self.task_name, message, participant)

    def receive(self, timeout: int = 0) -> fflabc.Response:
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `class Response`
        """
        msg = self.messenger.task_notification(timeout, [
            fflabc.Notification.participant_joined,
            fflabc.Notification.participant_updated,
            fflabc.Notification.participant_left
        ])

        flavour = msg.notification
        if flavour is fflabc.Notification.participant_left:
            self._del_participant(flavour['participant'])
        else:
            self._add_participant(flavour['participant'], flavour)
        return msg

    def _del_participant(self, participant) -> None:
        """
        Delete a given task participant from the list of participants.
        Throws: An exception on failure
        :param participant: participant to be deleted
        :type participant: `str`
        """
        del self.participants[participant]

    def _add_participant(self, participant, attributes: dict) -> None:
        """
        Add a given task participant to the list of participants.
        Throws: An exception on failure
        :param participant: participant to be added
        :type participant: `str`
        """
        self.participants.update({participant: attributes})

    def get_participants(self) -> dict:
        """
        Return a list of participants.
        Throws: An exception on failure
        :return participant: list of participants
        :rtype participant: `dict`
        """
        return self.participants

    def stop_task(self, model: dict = None) -> None:
        """
        As a task creator, stop the given task.
        The status of the task will be changed to 'COMPLETE'.
        Throws: An exception on failure
        """
        self.messenger.task_stop(self.task_name, model)
