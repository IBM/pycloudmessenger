#!/usr/bin/env python
#author mark_purcell@ie.ibm.com

"""FFL message catalog.
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


class MessageCatalog():
    def __init__(self, reply_to):
        self.correlation = 0
        if reply_to:
            self.reply_to = {'replyTo': reply_to}
        else:
            self.reply_to = {}

    def requestor(self):
        self.correlation += 1
        req = self.reply_to
        req.update({'correlationID': self.correlation})
        return req

    def msg_template(self, service_name: str = 'AccessManager'):
        message = {
            'serviceRequest': {
                'requestor': self.requestor(),
                'service': {
                    'name': service_name,
                    'args': [
                    ]
                }
            }
        }
        return message, message['serviceRequest']['service']['args']

    def msg_user_create(self, user_name: str, password: str):
        template, args = self.msg_template()
        args.append({'cmd':'user_create', 'params': [user_name, password]})
        return template

    def msg_user_assignments(self, user_name: str):
        template, args = self.msg_template()
        args.append({'cmd':'user_assignments', 'params': [user_name]})
        return template

    def msg_task_listing(self):
        template, args = self.msg_template()
        args.append({'cmd':'task_listing'})
        return template

    def msg_task_create(self, task_name: str, user_name: str, algorithm: str, quorum: int, adhoc: dict):
        template, args = self.msg_template()
        args.append({'cmd':'task_create', 'params': [task_name, user_name, algorithm, quorum, adhoc]})
        return template

    def msg_task_update(self, task_name: str, algorithm: str, quorum: int, adhoc: dict, status: str):
        template, args = self.msg_template()
        args.append({'cmd':'task_update', 'params': [task_name, algorithm, quorum, adhoc, status]})
        return template

    def msg_task_info(self, task_name: str):
        template, args = self.msg_template()
        args.append({'cmd':'task_info', 'params': [task_name]})
        return template

    def msg_task_assignments(self, task_name: str, user_name: str):
        template, args = self.msg_template()
        args.append({'cmd':'task_assignments', 'params': [task_name, user_name]})
        return template

    def msg_task_join(self, task_name: str, user_name: str):
        template, args = self.msg_template()
        args.append({'cmd':'task_join', 'params': [task_name, user_name]})
        return template
