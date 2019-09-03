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

# pylint: disable=W1203

import json


class Serializer:
    '''Basic json serialization'''

    @staticmethod
    def serialize(message: dict) -> str:
        '''Convert message to serializable format'''
        return json.dumps(message)

    @staticmethod
    def deserialize(message) -> dict:
        '''Convert serialized message to dict'''
        return json.loads(message)
