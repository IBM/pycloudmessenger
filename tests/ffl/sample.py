#!/usr/bin/env python
#author markpurcell@ie.ibm.com

"""FFL API sample program.
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

# Suppress too-many-lines
# pylint: disable=C0301, W0703

import os
import argparse
import logging
import random
import pycloudmessenger.ffl.fflapi as fflapi

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def main():
    parser = argparse.ArgumentParser(description='Messaging Client')
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--feed_queue', help='Defaults to credentials file')
    parser.add_argument('--reply_queue', help='Defaults to auto-generated')
    parser.add_argument('--broker_user', help='Defaults to credentials file')
    parser.add_argument('--broker_password', help='Defaults to credentials file')
    cmdline = parser.parse_args()

    LOGGER.info("Starting...")
    context = fflapi.Context.from_credentials_file(cmdline.credentials, cmdline.broker_user, cmdline.broker_password)

    try:
        with fflapi.Messenger(context, cmdline.feed_queue, cmdline.reply_queue) as ffl:
            result = ffl.task_listing()
            LOGGER.info(f"Received: {result}")
            LOGGER.info(f"Received: {result[0]['TASK_NAME']}")
            result = ffl.task_info(result[0]['TASK_NAME'])
            LOGGER.info(f"Received: {result}")
            result = ffl.user_assignments()
            LOGGER.info(f"Received: {result}")
    except Exception as err:
        LOGGER.error(err)
        raise err

if __name__ == '__main__':
    main()
