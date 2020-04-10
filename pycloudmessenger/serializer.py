#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""FFL message serializer.
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

import pickle
import base64
import json
import jsonpickle


class SerializerABC:
    '''Basic serialization'''

    @staticmethod
    def serialize(message: any) -> str:
        '''Convert message to serializable format'''

    @staticmethod
    def deserialize(message: bytes) -> any:
        '''Convert serialized message to dict'''


class Serializer(SerializerABC):
    '''json serialization'''

    @staticmethod
    def serialize(message: any) -> str:
        '''Convert message to serializable format'''
        return json.dumps(message)

    @staticmethod
    def deserialize(message: bytes) -> any:
        '''Convert serialized message to dict'''
        return json.loads(message)


class JsonPickleSerializer(SerializerABC):
    '''Json pickle serialization'''

    @staticmethod
    def serialize(message: any) -> str:
        '''Convert message to serializable format'''
        return jsonpickle.encode(message)

    @staticmethod
    def deserialize(message: bytes) -> any:
        '''Convert serialized message to dict'''
        return jsonpickle.decode(message)


class Base64Serializer(SerializerABC):
    '''Base64 encoder'''

    @staticmethod
    def serialize(message: any) -> str:
        '''Convert message to serializable format'''
        return base64.b64encode(pickle.dumps(message)).decode('utf-8')

    @staticmethod
    def deserialize(message: bytes) -> any:
        '''Convert serialized message to dict'''
        return pickle.loads(base64.b64decode(message))
        #return pickle.loads(base64.b64decode(message.encode()))
