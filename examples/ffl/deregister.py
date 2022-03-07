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
import json
import argparse
import logging
import pycloudmessenger.ffl.fflapi as fflapi
import pycloudmessenger.ffl.abstractions as ffl

#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


def main():
    parser = argparse.ArgumentParser(description='Messaging Client')
    parser.add_argument('--credentials', required=True)
    cmdline = parser.parse_args()

    LOGGER.info("Starting...")

    ffl.Factory.register('cloud', fflapi.Context, fflapi.User, fflapi.Aggregator, fflapi.Participant)
    context = ffl.Factory.context('cloud', cmdline.credentials)

    LOGGER.info("Deleting account...")
    user = ffl.Factory.user(context)
    with user:
        user.deregister()

if __name__ == '__main__':
    main()
