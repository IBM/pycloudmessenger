#!/usr/bin/env python3
#author mark_purcell@ie.ibm.com

"""FFL abstract base class.
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

import json
from enum import Enum
from abc import ABC, abstractmethod


class Topology(str):
    """ Class representing FFL task topologies """

    star = "STAR"

    def __str__(self):
        return self.value


class Notification(str, Enum):
    """ Notifications that can be received """

    aggregator_started = 'aggregator_started'
    aggregator_stopped = 'aggregator_stopped'
    participant_joined = 'participant_joined'
    participant_updated = 'participant_updated'
    participant_left = 'participant_left'

    @classmethod
    def is_notification(cls, msg: dict, notification) -> bool:
        """
        Check if msg is a particular notification.
        :param msg: message to be checked
        :type msg: `dict`
        :param notification: notification to be compared against
        :type notification: `str`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        try:
            ntype = msg['notification']['type']
            return cls(ntype) is notification
        except:
            # not a notification
            pass

        return False

    @classmethod
    def is_aggregator_started(cls, msg: dict) -> bool:
        """
        Check if msg is an 'aggregator_started' notification.
        :param msg: message to be checked
        :type msg: `dict`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        return cls.is_notification(msg, cls.aggregator_started)

    @classmethod
    def is_aggregator_stopped(cls, msg: dict) -> bool:
        """
        Check if msg is an 'aggregator_stopped' notification.
        :param msg: message to be checked
        :type msg: `dict`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        return cls.is_notification(msg, cls.aggregator_stopped)


    @classmethod
    def is_participant_joined(cls, msg: dict) -> bool:
        """
        Check if msg is a 'participant_joined' notification.
        :param msg: message to be checked
        :type msg: `dict`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        return cls.is_notification(msg, cls.participant_joined)

    @classmethod
    def is_participant_left(cls, msg: dict) -> bool:
        """
        Check if msg is a 'participant_left' notification.
        :param msg: message to be checked
        :type msg: `dict`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        return cls.is_notification(msg, cls.participant_left)

    @classmethod
    def is_participant_updated(cls, msg: dict) -> bool:
        """
        Check if msg is a 'participant_updated' notification.
        :param msg: message to be checked
        :type msg: `dict`
        :return: True if yes, False otherwise
        :rtype: `bool`
        """
        return cls.is_notification(msg, cls.participant_updated)

    def __str__(self):
        return self.value


class AbstractContext(ABC):
    """Class for basic context management"""
    def __init__(self):
        self.classes = None


class AbstractUser(ABC):
    """ Class that allows a general user to avail of the FFL platform services """

    @abstractmethod
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

    @abstractmethod
    def create_task(self, topology: str, definition: dict) -> dict:
        """
        Creates a task with the given definition and returns a dictionary
        with the details of the created tasks.
        Throws: An exception on failure
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: definition of the task to be created
        :type definition: `dict`
        :return: details of the created task
        :rtype: `dict`
        """

    @abstractmethod
    def join_task(self) -> dict:
        """
        As a potential task participant, try to join an existing task that has yet to start.
        Throws: An exception on failure
        :return: details of the task assignment
        :rtype: `dict`
        """

    @abstractmethod
    def task_info(self) -> dict:
        """
        Returns the details of a given task.
        Throws: An exception on failure
        :return: details of the task
        :rtype: `dict`
        """

    @abstractmethod
    def get_tasks(self) -> list:
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """

    @abstractmethod
    def get_joined_tasks(self) -> list:
        """
        Returns a list with all the joined tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """


class AbstractParticipant(ABC):
    """ This class provides the functionality needed by the
        participants of a federated learning task.  """


    @abstractmethod
    def send(self, message: dict = None) -> None:
        """
        Send a message to the aggregator and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent (needs to be serializable)
        :type message: `dict`
        """

    @abstractmethod
    def receive(self, timeout: int = 0) -> dict:
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `dict`
        """

    @abstractmethod
    def leave_task(self) -> None:
        """
        As a task participant, leave the given task.
        Throws: An exception on failure
        """


class AbstractAggregator(ABC):
    """ This class provides the functionality needed by the
        aggregator of a federated learning task. """

    @abstractmethod
    def send(self, message: dict = None, participant: str = None) -> None:
        """
        Send a message to all task participants and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent (needs to be serializable)
        :type message: `dict`
        """

    @abstractmethod
    def receive(self, timeout: int = 0) -> dict:
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :param timeout: timeout in seconds
        :type timeout: `int`
        :return: received message
        :rtype: `dict`
        """

    @abstractmethod
    def get_participants(self) -> dict:
        """
        Return a list of participants.
        Throws: An exception on failure
        :return participant: list of participants
        :rtype participant: `dict`
        """

    @abstractmethod
    def stop_task(self, model: dict = None) -> None:
        """
        As a task creator, stop the given task.
        The status of the task will be changed to 'COMPLETE'.
        Throws: An exception on failure
        """



class Factory():
    """ Implements factory methods for registering implementations and
    constructing concrete instances of the abstract base classes """

    types = {}

    @classmethod
    def register(cls, key: str, context: AbstractContext, user: AbstractUser,
                 aggr: AbstractAggregator, part: AbstractParticipant):
        """
        Registers a platform implementation, with concrete classes
        Throws: An exception on failure
        """
        if not key:
            raise Exception('A registration key must be provided')

        cls.types[key] = {'context': context, 'user': user, 'aggregator': aggr, 'participant': part}
        return cls

    @classmethod
    def context(cls, key: str, config_file: str = None, *args, **kwargs) -> AbstractContext:
        """
        Constructs a concrete instance of AbstractContext
        Throws: An exception on failure
        """
        if not key:
            raise Exception('A registration key must be provided')

        target = cls.types[key]['context']
        if not target:
            raise Exception('A context class must be provided')

        config = {}
        if config_file:
            if isinstance(config_file, str):
                with open(config_file) as cfg:
                    config = json.load(cfg)
            elif isinstance(config_file, dict):
                config = config_file

        context = target(config, *args, **kwargs)
        context.classes = cls.types[key]
        return context

    @classmethod
    def _instantiate(cls, context: AbstractContext, class_name: str, base_class, *args, **kwargs):
        """
        Helper to construct a concrete instances of Abstract base classes
        Throws: An exception on failure
        """
        target = context.classes[class_name]
        if not target:
            raise Exception(f'Class must be provided: {base_class}')

        if not issubclass(target, base_class):
            raise Exception(f'Not a subclass: {target} of {base_class}')

        return target(context, *args, **kwargs)

    @classmethod
    def user(cls, context: AbstractContext, *args, **kwargs) -> AbstractUser:
        """
        Constructs a concrete instance of AbstractUser
        Throws: An exception on failure
        """
        return cls._instantiate(context, 'user', AbstractUser, *args, **kwargs)

    @classmethod
    def aggregator(cls, context: AbstractContext, *args, **kwargs) -> AbstractAggregator:
        """
        Constructs a concrete instance of AbstractAggregator
        Throws: An exception on failure
        """
        return cls._instantiate(context, 'aggregator', AbstractAggregator, *args, **kwargs)

    @classmethod
    def participant(cls, context: AbstractContext, *args, **kwargs) -> AbstractParticipant:
        """
        Constructs a concrete instance of AbstractParticipant
        Throws: An exception on failure
        """
        return cls._instantiate(context, 'participant', AbstractParticipant, *args, **kwargs)
