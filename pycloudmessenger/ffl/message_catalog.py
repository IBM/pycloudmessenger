#!/usr/bin/env python3
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

Please note that the following code was developed for the project MUSKETEER in DRL funded by the European Union
under the Horizon 2020 Program.
"""


class MessageCatalog():
    def __init__(self, user_name: str):
        self.correlation = 0
        self.user_name = user_name

    def _requestor(self):
        self.correlation += 1
        req = {'correlationID': self.correlation}
        return req

    def _msg_template(self, service_name: str = 'AccessManager'):
        message = {
            'serviceRequest': {
                'requestor': self._requestor(),
                'service': {
                    'name': service_name,
                    'args': [
                    ]
                }
            }
        }
        return message, message['serviceRequest']['service']['args']

    def msg_assign_reply(self, message: dict, reply_to: str = None) -> dict:
        if reply_to:
            message['serviceRequest']['requestor']['replyTo'] = reply_to
        return message

    def msg_bin_upload_object(self, object_name: str) -> dict:
        template, args = self._msg_template(service_name='BinService')
        args.append({'cmd': 'upload_object', 'params': [self.user_name, object_name]})
        return template

    def msg_bin_download_object(self, object_name: str) -> dict:
        template, args = self._msg_template(service_name='BinService')
        args.append({'cmd': 'download_object', 'params': [self.user_name, object_name]})
        return template

    def msg_bin_uploader(self, object_name: str = None) -> dict:
        template, args = self._msg_template(service_name='BinService')
        args.append({'cmd': 'uploader', 'params': [self.user_name, object_name]})
        return template

    def msg_bin_downloader(self, object_name: str) -> dict:
        template, args = self._msg_template(service_name='BinService')
        args.append({'cmd': 'downloader', 'params': [self.user_name, object_name]})
        return template

    def msg_user_create(self, username: str, password: str, organisation: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'user_create', 'params': [username, password, organisation]})
        return template

    def msg_user_assignments(self) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'user_assignments', 'params': [self.user_name]})
        return template

    def msg_task_listing(self) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_listing'})
        return template

    def msg_task_create(self, task_name: str, topology: str, definition: dict) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_create', 'params': [task_name, self.user_name, topology, definition]})
        return template

    def msg_task_update(self, task_name: str, topology: str, definition: dict, status: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_update', 'params': [task_name, self.user_name, topology, definition, status]})
        return template

    def msg_task_info(self, task_name: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_info', 'params': [task_name, self.user_name]})
        return template

    def msg_task_assignments(self, task_name: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_assignments', 'params': [task_name, self.user_name]})
        return template

    def msg_task_join(self, task_name: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_join', 'params': [task_name, self.user_name]})
        return template

    def msg_task_quit(self, task_name: str) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_quit', 'params': [task_name, self.user_name]})
        return template

    def msg_task_start(self, task_name: str, model: dict = None, participant: str = None) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_start', 'params': [task_name, self.user_name, model, participant]})
        return template

    def msg_task_stop(self, task_name: str, model: dict = None) -> dict:
        template, args = self._msg_template()
        args.append({'cmd': 'task_stop', 'params': [task_name, self.user_name, model]})
        return template

    def msg_task_assignment_update(self, task_name: str, status: str = None, model: dict = None):
        template, args = self._msg_template()
        args.append({'cmd': 'task_assignment_update', 'params': [task_name, self.user_name, status, model]})
        return template

    def msg_task_assignment_info(self, task_name: str):
        template, args = self._msg_template()
        args.append({'cmd': 'task_assignment_info', 'params': [task_name, self.user_name]})
        return template
