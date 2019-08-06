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

    '''
        Users
    '''
    def msg_users(self):
        template, args = self.msg_template()
        args.append({'cmd':'get_users'})
        return template

    def msg_create_user(self, user_name):
        template, args = self.msg_template()
        args.append({'cmd':'create_user', 'params': [user_name]})
        return template

    '''
        Tasks
    '''
    def msg_tasks(self):
        template, args = self.msg_template()
        args.append({'cmd':'get_tasks'})
        return template

    def msg_create_task(self, task_name: str, algorithm: str, quorum: int, adhoc: dict):
        template, args = self.msg_template()
        args.append({'cmd':'create_task', 'params': [task_name, algorithm, quorum, adhoc]})
        return template

    def msg_update_task(self, task_name: str, algorithm: str, quorum: int, adhoc: dict, status: str):
        template, args = self.msg_template()
        args.append({'cmd':'update_task', 'params': [task_name, algorithm, quorum, adhoc, status]})
        return template

    '''
        Participants
    '''
    def msg_participants(self):
        template, args = self.msg_template()
        args.append({'cmd':'get_participants'})
        return template

    def msg_task_participants(self, task_name: str):
        template, args = self.msg_template()
        args.append({'cmd':'get_task_participants', 'params': [task_name]})
        return template


