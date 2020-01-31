#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""Castor REST protocol handler.
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

import json
import requests
import logging
from http.client import HTTPConnection
import pycloudmessenger.castor.api_abc as api

#logging.basicConfig(level=logging.DEBUG)
#HTTPConnection.debuglevel = 1

#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True


class CastorREST(api.CastorABC):
    def __init__(self, cred_file = None, proxies = None):
        super(CastorREST, self).__init__()

        if not cred_file:
            raise Exception(f"No configuration arguments specified.")

        with open(cred_file) as creds:
            args = json.load(creds)

        self.args = args
        self.apikey = self.args.get('apikey', None)
        self.proxies = None

        if proxies:
            with open(proxies) as creds:
                proxy = json.load(creds)

            self.user = proxy.get('user', None)
            self.password = proxy.get('password', None)
            self.proxy = proxy.get('proxy', None)
            self.use_proxy = (str(proxy.get('use_proxy',False)).lower() == 'true')

            if self.proxy and self.use_proxy:
                auth = f"{self.user}:{self.password}@" if self.user else ''

                print('Using Proxy: %s' % self.proxy)
                self.proxies = {
                    "http": f"http://{auth}{self.proxy}",
                    "https": f"http://{auth}{self.proxy}"
                }

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        self.session = requests.Session()
        self.session.headers.update({'content-type': 'application/json'})
        self.session.headers.update({'castor-api-key': self.apikey})

    def close(self):
        self.session.close()

    def exception_handler(self, exc):
        #Something went wrong - could be a general error
        self.close()
        self.start()
        raise exc

    def invoke_service(self, message, timeout=60):
        service = message['serviceRequest']['service']['name']
        url = self.args.get(service)

        try:
            result = self.session.post(url, proxies=self.proxies, json=message, verify=False)
            result.raise_for_status()
        except Exception as exc:
            return self.exception_handler(exc)

        if not result:
            raise Exception(f"Malformed object: None")

        result = result.json()

        if 'status' not in result['serviceResponse']['service']:
            raise Exception(f"Malformed object: {result}")
        status = result['serviceResponse']['service']['status']
        if status != 200:
            msg = f"({status}): {result['serviceResponse']['service']['result']}"
            raise Exception(msg)

        return result['serviceResponse']['service']['result']

